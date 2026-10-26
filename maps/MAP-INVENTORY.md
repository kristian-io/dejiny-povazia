# Map inventory

Which historical maps exist for this area, which ones the site uses, their licences, and whether they are already lined up with modern coordinates.

**Legend:**
- **Georef:** ✅ already georeferenced (it drops straight onto the web map) · 🟡 a scan we would have to align ourselves · ❌ image only
- **Access:** 🆓 free & open · 💶 paid / restricted · 👁 free to view, reuse unclear

---

## 1. Core sources found

### A. ZBGIS historical WMS — Slovak state geodesy (GKÚ Bratislava / ÚGKK SR) ⭐ main source
Free, **CC BY 4.0**, and it already serves **EPSG:3857**, so it works directly in Leaflet or MapLibre.

| Layer | Endpoint | Content | Georef | Access |
|---|---|---|---|---|
| **3rd military survey** (*HM_III_VM*, layer `1`) | `https://zbgisws.skgeodesy.sk/hm_III_vm/service.svc/get` | Habsburg 1:25 000 sheets (survey 1872–1887). Some sheets are later revisions with Slovak names (e.g. *Kráľová n. V.*, *Diakovce*), so the area shows a mix of editions. | ✅ | 🆓 CC BY 4.0 |
| **Topographic maps** (*RETM*: `1` = TM25, `5` = TM50) | `https://zbgisws.skgeodesy.sk/retm_wms/service.svc/get` | Czechoslovak military topographic maps. The test image shows the Kráľová reservoir, so this edition is from **1985 or later**. Edition years still to check. | ✅ | 🆓 CC BY 4.0 |
| **Former base maps** (*ZMSR*: ZM10…ZM1mil) | `https://zbgisws.skgeodesy.sk/zmsr_wms/service.svc/get` | Base Map of Slovakia, roughly 1980s–2000s | ✅ | 🆓 CC BY 4.0 |
| Current ZBGIS & orthophoto | see the skgeodesy.sk geoportal | Today's map and aerial imagery | ✅ | 🆓 CC BY 4.0 |

The 3rd-survey sheet clearly shows *Galánta*, *Taksony (Pt.)*, *Sala (Sellye)*, *Veča*, the Váh's meanders and the 1850 railway.

Attribution used on the site: "© GKÚ Bratislava / ÚGKK SR, CC BY 4.0".

### B. Arcanum Maps (formerly Mapire) — Hungarian historical map portal
Habsburg **1st military survey** (Hungary 1782–1785), **2nd military survey** (Hungary c. 1819–1869), 3rd survey, *Europe in the 19th century*, cadastral maps, county and city maps. All are already georeferenced.

Free guest access shows **low-resolution** maps only; high resolution and tile embedding need a paid subscription. The site shows no Arcanum maps: the free low-resolution views were used only as a reference when drawing our own layers.

Arcanum's newspaper archive would also be very useful for research (Hungarian local press, e.g. *Mátyusföldi Lapok* 1919–1921).

### C. Hungaricana map library (maps.hungaricana.hu) — scans of individual maps
Free to view at high resolution. Mostly **not georeferenced** (🟡/❌). Directly relevant items found:

| Item | Date | Use |
|---|---|---|
| Cadastral map copies: **Galánta** (S 76 No. 420), **Hodi** (No. 459), **Nebojsza** (No. 831) | 1903–1904 | Exact plots and streets c. 1900 (period 13) |
| **Sellye mezőváros** boundary regulation map (S 13 No. 345) | 18th–19th c. | Šaľa town plan, market square |
| Vágsellye–Vágkirályfa / Vágsellye–Pered estate maps (S 13 No. 501, 503) | late 19th c. | The Váh, the railway and the University Fund estates (successor to the Jesuits) |
| Sellye plot map (OSZK TK 492) | ? | Town plots |
| *Galantai Kastelinak Delineatioja* (Esterházy family fond, T 59 No. 4) | 18th c.? | Drawing of the Esterházy manor in Galanta: an illustration, not a map |
| Mikoviny / Homann, *Comitatus Posoniensis* (HTI 1420) | 1735 / 1757 | First accurate map of Pozsony County (period 11) |

⚠ When searching for "Taksony", most hits are the **other** Taksony in Pest County, Hungary. Search for "Taksony Pozsony" instead.

### D. Data for drawing our own layers
| Source | Content | Licence |
|---|---|---|
| **DARE – Digital Atlas of the Roman Empire** (imperium.ahlfeldt.se) | Roman roads, forts, the Danube Limes (Gerulata, Kelemantia / Iža, Brigetio) as tiles and data | CC BY (2012) or CC BY-SA (catalogue says so): needs checking |
| **Pleiades** | Ancient places as point data | CC BY |
| **HistoGIS** (ÖAW) | Austro-Hungarian borders 1870 & 1910; districts | CC BY 4.0 (derived products) |
| **MPIDR / Census Mosaic** | Austria-Hungary 1910 court districts | free for non-commercial research with registration |
| **OpenHistoricalMap** | Crowd-sourced historical borders (Vienna Award line etc.: to check) | CC0 |
| **ZBGIS terrain (DMR) / Copernicus DEM** | Relief: shows the higher, dry ground people settled on | CC BY / open |

### E. Not found (yet)
- **Historical aerial photos of Slovakia, 1949–1950s:** they exist (Geodis / TU Zvolen colourisation project), but **no public web service found**. The Czech equivalent is open; the Slovak one is not.
- **Lazius 1556, early modern Hungary maps:** many are on Wikimedia Commons or OSZK, but none show detail at village scale. Usable only as decorative images.
- **US Army AMS maps (1940s–50s, public domain):** not checked yet. They might give a WWII-era layer.

---

## 2. Map used for each period
| # | Period | Map on the site | Source |
|---|---|---|---|
| 1–12 | Prehistory → 1867 | **Our drawn reconstruction**: relief, rivers and marshes, county border, villages, archaeological sites (see below) | OpenStreetMap, AWS Terrain Tiles, research notes |
| 13–15 | 1867 → 1945 | **3rd military survey** (1872–87, some sheets revised later) | ZBGIS (CC BY 4.0) |
| 16 | 1945 → 1989 | **Czechoslovak topographic map TM25** | ZBGIS RETM (CC BY 4.0) |
| 17 | Today | **Base Map of Slovakia ZM50** | ZBGIS ZMSR (CC BY 4.0) |

No real maps exist for the oldest periods, and the free 1st/2nd military surveys (Arcanum) are too low-resolution to show, so periods 1–12 use the drawn map.

---

## Arcanum free version (checked 2026-10-25)
Checked the 2nd military survey on Arcanum Maps without a subscription, over Šaľa–Galanta:
- **Whole-area view (~40–80 km wide):** good. Colours separate fields, wet meadows and marshes (green), forests and villages, and the Váh's old meanders show clearly.
- **Village view (~20 km wide):** blurry. Village outlines, roads and river channels are still visible, but **place names and small details can't be read**.
- **Verdict:** the free version is enough to **trace our own layers** for periods 1–12 (rivers, marshes, forests, village extents). It is not good enough as a map shown on the site. Upscaling would not help. High resolution is only needed if we want the real 1780s/1840s maps visible on the site or need to read field names.

## Our drawn map (periods 1–12)
Made by [site/tools/build_layers.py](../site/tools/build_layers.py) → `data/layers.json`. The page draws it as SVG.

| Layer | How it was made | Reliability |
|---|---|---|
| Rivers & streams | OpenStreetMap natural watercourses (modern drainage canals left out) | good, but these are today's courses |
| Váh at Kráľová | traced by hand from the 3rd military survey (1880s); the reservoir and its channels are removed | approximate |
| Old arms, lakes, wetlands | OpenStreetMap (oxbows, natural lakes, wetlands) | good, today's remnants |
| Floodplain / marsh zone | low ground within 1.5 km of water, from a heavily smoothed elevation model (AWS Terrain Tiles); plus the reservoir basin | **approximate** |
| Loess upland (NE corner) | ground above 130 m | good |
| **County border** | modern municipal boundaries grouped by pre-1918 county (Hungarian Wikipedia per village) | approximate |
| Villages | OSM positions; first-mention years from the Slovak Wikipedia infoboxes | likely |
| Archaeological sites | placed from the excavation descriptions; most positions approximate (marked *) | approximate |

**Finding:** the Pozsony / Nitra county border did **not** follow the Váh. Šaľa, Kráľová, Dlhá, Trnovec and Šoporňa were in Nitra County. Diakovce, Tešedíkovo and Žihárec, right next to Šaľa, plus Galanta, Matúškovo and Topoľnica, were in Pozsony County.

**Improvements later:** trace the 1780s/1840s Váh meanders and marshes from the Arcanum maps (free low-res is enough); place sites exactly using Točík's map-sheet references.

## 3. Possible improvements
1. Trace the 1780s/1840s Váh meanders and marshes from the 1st/2nd military surveys.
2. Confirm the edition years of the ZBGIS 3rd-survey and topographic sheets for this area.
3. Add the 1938 Vienna Award border (OpenHistoricalMap may have it) and a WWII-era map (US Army AMS sheets).
4. Load live map tiles instead of fixed images on the public website.
