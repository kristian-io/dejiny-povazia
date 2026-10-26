"""Inline the project data into the page.

  python site/build.py          site/page.html (Artifact publish) + site/index.html (open locally)
  python site/build.py --dist   also dist/: the public website for Netlify, with the feedback form switched on
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SITE = ROOT / "site"
ASSETS = ["maps", "img", "wiki", "peek"]  # folders the page loads pictures from

HEAD = """<!doctype html>
<html lang="sk">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
"""
# extra head tags for the public website (the Artifact viewer adds its own)
PUBLIC_HEAD = """<meta name="description" content="Interaktívna mapa dejín Šale, Galanty, Matúškova a Sládkovičova – od neandertálcov po dnešok. An interactive history map of the lower Váh, SW Slovakia.">
<meta property="og:title" content="Šaľa · Galanta · Matúškovo · Sládkovičovo">
<meta property="og:description" content="Dejiny Dolného Považia od neandertálcov po dnešok – 17 období, dobové mapy, príbehy a obrázky.">
<meta property="og:type" content="website">
<meta property="og:image" content="peek/peek-1.jpg">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%231d6670'/%3E%3Cpath d='M4 22c5-6 8 2 13-4s8-1 11-6' stroke='%23fff' stroke-width='3' fill='none' stroke-linecap='round'/%3E%3C/svg%3E">
"""


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def parse_sources():
    """Read the source table rows (| S001 | title | ... | link | ...) from sources/sources.md."""
    out = {}
    for line in (ROOT / "sources" / "sources.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 5 and re.fullmatch(r"[SM]\d{3}", cells[0]):
            url = re.search(r"https?://\S+", cells[4])
            out[cells[0]] = {"title": re.sub(r"\*", "", cells[1]), "url": url.group(0) if url else None}
    return out


def full_document(page, extra_head=""):
    return HEAD + extra_head + page.replace("<div class=\"app\">", "</head>\n<body>\n<div class=\"app\">", 1) + "\n</body>\n</html>\n"


def main():
    data = {
        "periods": load("periods.json"),
        "events": load("events.json"),
        "places": load("places.json"),
        "population": load("population.json"),
        "layers": load("layers.json"),  # made by site/tools/build_layers.py
        "terms": load("terms.json"),
        "wiki": load("wiki.json"),  # made by site/tools/fetch_wiki.py
        "images": load("images.json"),  # pictures downloaded by site/tools/fetch_images.py
        "voices": load("voices.json"),  # "Hlas doby" cards: real, sourced voices
        "sources": parse_sources(),
    }
    template = (SITE / "template.html").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = template.replace("/*DATA*/null", payload)
    # page.html is the body-only version for the Artifact publish (it adds its own skeleton);
    # index.html is a full document for opening locally.
    (SITE / "page.html").write_text(page, encoding="utf-8")
    (SITE / "index.html").write_text(full_document(page), encoding="utf-8")
    print(f"site/page.html + index.html written: {len(data['periods'])} periods, {len(data['events'])} events, {len(data['sources'])} sources")

    if "--dist" in sys.argv:
        dist = ROOT / "dist"
        shutil.rmtree(dist, ignore_errors=True)
        dist.mkdir()
        public = page.replace("/*FEEDBACK*/false", "true")
        (dist / "index.html").write_text(full_document(public, PUBLIC_HEAD), encoding="utf-8")
        for folder in ASSETS:
            shutil.copytree(SITE / folder, dist / folder)
        print("dist/ written (Netlify build, feedback form on)")


if __name__ == "__main__":
    main()
