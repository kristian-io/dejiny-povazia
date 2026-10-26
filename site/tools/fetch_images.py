"""Download the gallery pictures listed in data/images.json (field "source") into site/img/.

Each entry has either  "commons": "<File title>"  or  "fortepan": <photo id>.
For Commons files the licence, author and description page are read from the Commons API and stored back
into images.json, so captions always carry correct credits. Fortepan photos are CC BY-SA 3.0.

Usage:  python site/tools/fetch_images.py
"""
import io
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "site" / "img"
UA = {"User-Agent": "SalaGalantaHistory/0.1 (private history map)"}


def get(url, as_json=True):
    for attempt in range(5):
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            return json.loads(raw) if as_json else raw
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(4 + attempt * 4)
    return None


def save(raw, stem):
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    big = im.copy(); big.thumbnail((1600, 1600)); big.save(OUT / f"{stem}.jpg", quality=82, optimize=True)
    small = im.copy(); small.thumbnail((420, 420)); small.save(OUT / f"{stem}_t.jpg", quality=78, optimize=True)
    return big.size


def main():
    path = ROOT / "data" / "images.json"
    items = json.loads(path.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    for it in items:
        if (OUT / f"{it['id']}.jpg").exists() and it.get("credit"):
            continue
        if "commons" in it:
            q = urllib.parse.urlencode({"action": "query", "titles": "File:" + it["commons"], "prop": "imageinfo",
                                        "iiprop": "url|extmetadata|size", "iiurlwidth": 1600, "format": "json", "formatversion": 2})
            d = get("https://commons.wikimedia.org/w/api.php?" + q)
            page = (d or {}).get("query", {}).get("pages", [{}])[0]
            if page.get("missing") or not page.get("imageinfo"):
                print("MISSING", it["commons"]); continue
            ii = page["imageinfo"][0]; em = ii.get("extmetadata", {})
            clean = lambda k: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", em.get(k, {}).get("value", ""))).strip()
            # Wikimedia asks bots to use its standard thumbnail widths (originals get throttled)
            width = max([s for s in (640, 960, 1280) if s < ii.get("width", 0)] or [320])
            q2 = q.replace("iiurlwidth=1600", f"iiurlwidth={width}")
            d2 = get("https://commons.wikimedia.org/w/api.php?" + q2)
            thumb = d2["query"]["pages"][0]["imageinfo"][0]["thumburl"] if d2 else None
            raw = get(thumb, as_json=False) if thumb else None
            it["credit"] = {"author": clean("Artist")[:120] or "unknown", "license": clean("LicenseShortName"),
                            "url": ii.get("descriptionurl"), "site": "Wikimedia Commons"}
        else:
            raw = get(f"https://fortepan.download/file/fortepan-eu/1600/fortepan_{it['fortepan']}.jpg", as_json=False)
            it["credit"] = {"author": f"Fortepan / {it['donor']}" if it.get("donor") else "Fortepan", "license": "CC BY-SA 3.0",
                            "url": f"https://fortepan.hu/hu/photos/?id={it['fortepan']}", "site": "Fortepan"}
        if not raw:
            print("DOWNLOAD FAILED", it["id"]); continue
        it["size"] = save(raw, it["id"])
        print(it["id"], it["credit"]["license"], it["size"])
        time.sleep(1.5)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
