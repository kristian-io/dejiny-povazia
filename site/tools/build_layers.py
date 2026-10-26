"""Build the hand-made historical map layer (data/layers.json).

Inputs (downloaded once, kept outside the project):
  osm.json   – Overpass export of waterways, water, wetlands, places and admin boundaries for the map bbox
  dem.npy    – 1800×1170 elevation grid (AWS Terrain Tiles, z13) in the same EPSG:3857 frame as the map images

Usage:  python site/tools/build_layers.py <osm.json> <dem.npy>

What is real data and what is reconstruction:
  rivers, old arms (oxbows), wetlands, village positions  – OpenStreetMap (today's geometry)
  Váh under the Kráľová reservoir                          – traced by hand from the 3rd military survey (1880s)
  floodplain / marsh zones                                 – low ground near water, from a heavily smoothed elevation model (approximate)
  county border                                            – modern municipal boundaries grouped by pre-1918 county (approximate)
  archaeological sites                                     – placed from excavation descriptions (approximate unless noted)
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage as nd
from shapely.geometry import LineString, Polygon, MultiPolygon, mapping, shape
from shapely.ops import polygonize, unary_union, linemerge
from skimage import measure

ROOT = Path(__file__).resolve().parents[2]
BBOX = dict(x0=1958000, y1=6149600, w=44000, h=28600, pw=1800, ph=1170)
R = 6378137.0


def to_px(lon, lat):
    x = math.radians(lon) * R
    y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * R
    return (x - BBOX["x0"]) / BBOX["w"] * BBOX["pw"], (BBOX["y1"] - y) / BBOX["h"] * BBOX["ph"]


def to_ll(px, py):
    x = BBOX["x0"] + px / BBOX["pw"] * BBOX["w"]
    y = BBOX["y1"] - py / BBOX["ph"] * BBOX["h"]
    return math.degrees(x / R), math.degrees(2 * math.atan(math.exp(y / R)) - math.pi / 2)


def rnd(coords):
    return [[round(x, 5), round(y, 5)] for x, y in coords]


# Váh between the top of the map and Kráľová, traced from the 3rd military survey (pixel frame of maps/survey3.jpg)
VAH_1880_PX = [(1025, 0), (997.5, 30), (982.5, 65), (1005, 100), (1022.5, 125), (992.5, 150), (985, 185), (997.5, 220),
               (987.5, 260), (991, 300), (1010, 325), (997.5, 345), (1020, 357.5), (1055, 350), (1070, 375), (1090, 400),
               (1102.5, 430), (1107.5, 460), (1117.5, 485), (1140, 510), (1165, 532.5), (1190, 555), (1215, 575),
               (1240, 595), (1260, 612.5)]
RESERVOIR_BOX = (930, 0, 1265, 615)  # px: x0, y0, x1, y1 – modern Váh/reservoir geometry here is replaced by the trace


def in_box(px, box):
    return box[0] <= px[0] <= box[2] and box[1] <= px[1] <= box[3]


# Pre-1918 county of each municipality (hu.wikipedia "… vármegye … járásához tartozott"); others left out
POZSONY = {"Galanta", "Matúškovo", "Topoľnica", "Tomášikovo", "Kajal", "Košúty", "Mostová", "Čierna Voda", "Čierny Brod",
           "Vozokany", "Horné Saliby", "Dolné Saliby", "Diakovce", "Tešedíkovo", "Žihárec", "Sládkovičovo", "Gáň",
           "Váhovce", "Veľká Mača", "Malá Mača", "Abrahám"}
NYITRA = {"Šaľa", "Kráľová nad Váhom", "Dlhá nad Váhom", "Trnovec nad Váhom", "Horná Kráľová", "Hájske", "Močenok",
          "Selice", "Jatov", "Šoporňa"}

# First written mention (sk.wikipedia infobox "Prvá zmienka"; hamlets from research notes)
FIRST = {"Galanta": 1237, "Šaľa": 1002, "Gáň": 1113, "Čierny Brod": 1223, "Šoporňa": 1251, "Topoľnica": 1307,
         "Veľká Mača": 1326, "Malá Mača": 1326, "Matúškovo": 1138, "Horné Saliby": 1233, "Dolné Saliby": 1158,
         "Váhovce": 1259, "Dlhá nad Váhom": 1113, "Hájske": 1113, "Horná Kráľová": 1113, "Močenok": 1113,
         "Tešedíkovo": 1237, "Žihárec": 1251, "Trnovec nad Váhom": 1113, "Kráľová nad Váhom": 1237, "Diakovce": 1002,
         "Selice": 1078, "Kajal": 1297, "Jatov": 1236, "Sládkovičovo": 1252,
         "Veča": 1113, "Hetmín": 1113, "Paľovce": 1214, "Hody": 1291, "Nebojsa": 1405}
CORE = {"Galanta", "Šaľa", "Matúškovo", "Sládkovičovo"}

SITES = [
    # id, periods, coords (lon, lat), sk, en, approximate?, sources
    ("neanderthal", ["p01"], (17.883, 48.128), "Nález neandertálcov Šaľa 1 a 2", "Neanderthal finds Šaľa 1 and 2", True, ["S033"]),
    ("lbk-sala", ["p02"], (17.900, 48.163), "Osada s lineárnou keramikou", "Linear Pottery settlement", True, ["S004"]),
    ("nebojsa-neo", ["p02", "p03", "p04"], (17.733, 48.217), "Nebojsa: osídlenie doby kamennej, hroby Keltov", "Nebojsa: Stone Age settlement, Celtic graves", True, ["S034", "S031"]),
    ("corded-sala", ["p03"], (17.893, 48.172), "Pohrebiská so šnúrovou keramikou", "Corded Ware burials", True, ["S004"]),
    ("unetice-mat", ["p03"], (17.738, 48.171), "Únětické pohrebisko", "Únětice cemetery", True, ["S006", "S017"]),
    ("latene-veca", ["p04"], (17.888, 48.170), "Keltská osada Šaľa-Veča", "Celtic village Šaľa-Veča", True, ["S004"]),
    ("quadi-sala", ["p05"], (17.893, 48.165), "Kvádske sídlisko", "Quadi settlement", True, ["S004"]),
    ("pod-zahradami", ["p05"], (17.733, 48.217), "Germánska dedina Pod záhradami (6 zemníc, pec, studňa)", "Germanic village Pod záhradami (6 pit houses, kiln, well)", False, ["S031"]),
    ("avar-veca", ["p06"], (17.886, 48.172), "Avarsko-slovanské pohrebisko", "Avar–Slavic cemetery", True, ["S004"]),
    ("slav-mat", ["p06"], (17.740, 48.165), "Ranoslovanské žiarové pohrebisko", "Early Slavic cremation cemetery", True, ["S006"]),
    ("veca-pieskovisko", ["p07"], (17.880, 48.173), "Pohrebisko vo Veči: hrob bojovníka so sekerou", "Veča cemetery: warrior's grave with axe", True, ["S032"]),
    ("richtarske", ["p07", "p08"], (17.745, 48.190), "Osada Richtárske (9.–11. stor.)", "Richtárske settlement (9th–11th c.)", True, ["S031"]),
    ("papfold", ["p08"], (17.716, 48.198), "Staromaďarské pohrebisko Papföld", "Old Hungarian cemetery Papföld", False, ["S032"]),
    ("kertalja", ["p08"], (17.737, 48.171), "Pohrebisko Kertalja (100+ hrobov)", "Kertalja cemetery (100+ graves)", True, ["S032"]),
    ("andelok", ["p08"], (17.905, 48.160), "Pohrebisko Andelok (90 hrobov)", "Andelok cemetery (90 graves)", True, ["S032"]),
    ("kluciaren", ["p08"], (17.973, 48.177), "Staromaďarské pohrebisko Kľučiareň", "Old Hungarian cemetery Kľučiareň", False, ["S032"]),
    ("diakovce-church", ["p08", "p09", "p10", "p11", "p12"], (17.8414, 48.1338), "Románsky kostol v Diakovciach (1228)", "Romanesque church, Diakovce (1228)", False, ["S037"]),
    ("sala-ford", ["p09"], (17.880, 48.156), "Brod na Českej ceste, vodný hrad", "Ford on the Bohemian Road, moated castle", True, ["S004", "S029"]),
    ("sala-castle", ["p10", "p11", "p12"], (17.8735, 48.1505), "Hrad v Šali, jezuitské kolégium; 1663–1686 turecký", "Šaľa castle, Jesuit college; Ottoman 1663–1686", False, ["S029"]),
    ("galanta-manor", ["p10", "p11", "p12"], (17.7271, 48.1905), "Renesančný kaštieľ Esterháziovcov", "Esterházy Renaissance manor", True, ["S027"]),
    ("rakoczi-mat", ["p11"], (17.7333, 48.1667), "Rákóczi v Taksoni (1704)", "Rákóczi in Taksony (1704)", False, ["S003"]),
    ("battle-ziharec", ["p12"], (17.8800, 48.0800), "Bitka pri Žihárci 16. 6. 1849 (južne, mimo mapy)", "Battle of Žihárec 16 Jun 1849 (south, off map)", True, ["S004"]),
]


def main(osm_path, dem_path):
    osm = json.loads(Path(osm_path).read_text(encoding="utf-8"))["elements"]
    out = {"rivers": [], "water": [], "wetlands": [], "floodplain": [], "upland": [], "county": [], "villages": [], "sites": []}

    # --- rivers (natural watercourses only; canals are modern drainage) ---
    river_px_lines = []
    bx = RESERVOIR_BOX
    box_ll = Polygon([to_ll(bx[0], bx[1]), to_ll(bx[2], bx[1]), to_ll(bx[2], bx[3]), to_ll(bx[0], bx[3])])
    for e in osm:
        t = e.get("tags", {})
        if e["type"] != "way" or t.get("waterway") not in ("river", "stream"):
            continue
        geom = LineString([(g["lon"], g["lat"]) for g in e["geometry"]])
        if t.get("name") == "Váh" or (t.get("waterway") == "river" and not t.get("name")):
            geom = geom.difference(box_ll)  # modern Váh, reservoir and its channels; the 1880 trace replaces them
        for part in getattr(geom, "geoms", [geom]):
            if part.is_empty or part.length < 0.0005:
                continue
            line = part.simplify(0.00015)
            out["rivers"].append({"name": t.get("name"), "major": t.get("waterway") == "river", "coords": rnd(line.coords)})
            river_px_lines.append([to_px(*p) for p in line.coords])
    vah = [to_ll(*p) for p in VAH_1880_PX]
    out["rivers"].append({"name": "Váh (1880)", "major": True, "traced": True, "coords": rnd(vah)})
    river_px_lines.append(VAH_1880_PX)

    # --- water bodies: oxbows, natural lakes, river areas (no reservoirs, fishponds, gravel pits) ---
    for e in osm:
        t = e.get("tags", {})
        if e["type"] != "way" or t.get("natural") not in ("water", "wetland"):
            continue
        pts = [(g["lon"], g["lat"]) for g in e["geometry"]]
        if len(pts) < 4 or pts[0] != pts[-1]:
            continue
        poly = Polygon(pts)
        if not poly.is_valid:
            poly = poly.buffer(0)
        centre = to_px(poly.centroid.x, poly.centroid.y)
        if t.get("natural") == "wetland":
            out["wetlands"].append(rnd(poly.simplify(0.0001).exterior.coords))
            continue
        kind = t.get("water")
        name = (t.get("name") or "").lower()
        keep = kind in ("oxbow", "lake") or "rameno" in name or (kind == "river" and not in_box(centre, RESERVOIR_BOX))
        if keep:
            out["water"].append({"oxbow": kind == "oxbow" or "rameno" in name, "coords": rnd(poly.simplify(0.0001).exterior.coords)})

    # --- floodplain & upland from the elevation model ---
    dem = np.load(dem_path).astype(np.float32)
    smooth = nd.gaussian_filter(dem, 8)
    trend = nd.gaussian_filter(nd.median_filter(dem, size=61), 80)
    rel = smooth - trend
    water_mask = np.zeros(dem.shape, bool)
    yy, xx = np.mgrid[0:dem.shape[0], 0:dem.shape[1]]
    for line in river_px_lines:
        for (x0, y0), (x1, y1) in zip(line, line[1:]):
            n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
            for k in range(n + 1):
                x = int(round(x0 + (x1 - x0) * k / n)); y = int(round(y0 + (y1 - y0) * k / n))
                if 0 <= x < dem.shape[1] and 0 <= y < dem.shape[0]:
                    water_mask[y, x] = True
    dist = nd.distance_transform_edt(~water_mask) * (BBOX["w"] / BBOX["pw"])  # metres
    marsh = (rel < -0.5) & (dist < 1500) & (smooth < 125)
    bx = RESERVOIR_BOX
    # the reservoir basin was the Váh floodplain
    res_area = (xx >= bx[0] + 40) & (xx <= bx[2] - 60) & (yy <= 470) & (dist < 1200)
    marsh |= res_area
    marsh = nd.binary_closing(nd.binary_opening(marsh, iterations=3), iterations=6)
    lab, n = nd.label(marsh)
    sizes = nd.sum(marsh, lab, range(1, n + 1))
    marsh = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 400])
    upland = nd.binary_opening(smooth > 130, iterations=4)

    def polys(mask, tol):
        res = []
        for c in measure.find_contours(np.pad(mask.astype(float), 1), 0.5):
            pts = [to_ll(p[1] - 1, p[0] - 1) for p in c]
            if len(pts) < 4:
                continue
            poly = Polygon(pts).buffer(0).simplify(tol)
            for g in (poly.geoms if isinstance(poly, MultiPolygon) else [poly]):
                if g.area > 1e-6:
                    res.append(rnd(g.exterior.coords))
        return res

    out["floodplain"] = polys(marsh, 0.0006)
    out["upland"] = polys(upland, 0.0008)

    # --- county border: shared edge of the Pozsony and Nyitra municipality groups ---
    def municipality(rel_el):
        lines = [LineString([(g["lon"], g["lat"]) for g in m["geometry"]]) for m in rel_el.get("members", [])
                 if m["type"] == "way" and m.get("role") in ("outer", "") and m.get("geometry")]
        return unary_union(list(polygonize(unary_union(lines))))

    groups = {"P": [], "N": []}
    for e in osm:
        t = e.get("tags", {})
        if e["type"] == "relation" and t.get("boundary") == "administrative" and t.get("admin_level") == "8":
            nm = t.get("name")
            if nm in POZSONY:
                groups["P"].append(municipality(e))
            elif nm in NYITRA:
                groups["N"].append(municipality(e))
    P, N = unary_union(groups["P"]).buffer(0.0003), unary_union(groups["N"]).buffer(0.0003)
    # the groups touch along the old county line; the part of P's outline lying inside (slightly grown) N is that line
    edge = P.boundary.intersection(N.buffer(0.0001))
    edge = linemerge(edge) if edge.geom_type in ("MultiLineString", "GeometryCollection") else edge
    geoms = getattr(edge, "geoms", [edge])
    for g in geoms:
        if g.geom_type == "LineString" and g.length > 0.002:
            out["county"].append(rnd(g.simplify(0.0003).coords))
    out["countyLabels"] = {
        "pozsony": rnd([P.representative_point().coords[0]])[0],
        "nyitra": rnd([N.representative_point().coords[0]])[0],
    }

    # --- villages ---
    seen = set()
    for e in osm:
        t = e.get("tags", {})
        if e["type"] != "node" or t.get("place") not in ("town", "village", "hamlet", "suburb"):
            continue
        nm = t.get("name")
        if nm in FIRST and nm not in seen:
            seen.add(nm)
            out["villages"].append({"sk": nm, "hu": t.get("name:hu") or nm, "first": FIRST[nm], "core": nm in CORE,
                                    "coords": [round(e["lon"], 5), round(e["lat"], 5)]})

    for sid, per, (lon, lat), sk, en, approx, src in SITES:
        out["sites"].append({"id": sid, "periods": per, "coords": [lon, lat], "label": {"sk": sk, "en": en}, "approx": approx, "sources": src})

    path = ROOT / "data" / "layers.json"
    path.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print({k: len(v) for k, v in out.items()}, f"{path.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
