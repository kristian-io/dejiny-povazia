"""Download Wikipedia previews for the terms in data/terms.json → data/wiki.json + site/wiki/<id>.jpg

For each term (English title in "wiki"): find its Slovak and Czech versions via language links,
then take the summary in Slovak (else Czech, else English) for the SK page and in English for the EN page.

Usage:  python site/tools/fetch_wiki.py
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
UA = {"User-Agent": "SalaGalantaHistory/0.1 (private history map; contact via project owner)"}
IMG_DIR = ROOT / "site" / "wiki"


def get_json(url):
    for attempt in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(10 * (attempt + 1))  # 10, 20, 30, 40 s: Wikipedia rate limits are short
    return None


def langlinks(title):
    q = urllib.parse.urlencode({"action": "query", "titles": title, "prop": "langlinks", "lllimit": 500,
                                "redirects": 1, "format": "json", "formatversion": 2})
    d = get_json(f"https://en.wikipedia.org/w/api.php?{q}")
    if d is None:
        # a failed lookup must not look like "no Slovak article" (that silently produced English links before)
        raise RuntimeError(f"language links for {title!r} could not be fetched (rate limit?) — run again later")
    page = d.get("query", {}).get("pages", [{}])[0]
    if page.get("missing"):
        return None, {}
    return page.get("title"), {l["lang"]: l["title"] for l in page.get("langlinks", []) if l["lang"] in ("sk", "cs")}


def summary(lang, title):
    d = get_json(f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title.replace(' ', '_'))}")
    if not d or d.get("type") == "disambiguation" or not d.get("extract"):
        return None
    text = d["extract"]
    # keep the first two or three sentences, at most ~320 characters
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-ZÁČĎÉÍĽĹŇÓÔŔŠŤÚÝŽ0-9])", text)
    out = ""
    for s in sentences:
        if len(out) + len(s) > 320 and out:
            break
        out = (out + " " + s).strip()
    return {"lang": lang, "title": d.get("titles", {}).get("normalized") or d.get("title"), "extract": out,
            "url": d.get("content_urls", {}).get("desktop", {}).get("page"), "thumb": (d.get("thumbnail") or {}).get("source")}


def commons_credit(thumb_url):
    """Author and licence of a Commons picture, from its thumbnail URL (CC licences require the credit)."""
    m = re.search(r"/commons/(?:thumb/)?[0-9a-f]/[0-9a-f]{2}/([^/?]+)", thumb_url or "")
    if not m:
        return None
    name = urllib.parse.unquote(m.group(1)).replace("_", " ")
    q = urllib.parse.urlencode({"action": "query", "titles": "File:" + name, "prop": "imageinfo", "iiprop": "extmetadata",
                                "iiextmetadatafilter": "LicenseShortName|Artist", "format": "json", "formatversion": 2})
    d = get_json("https://commons.wikimedia.org/w/api.php?" + q)
    page = (d or {}).get("query", {}).get("pages", [{}])[0]
    if page.get("missing") or not page.get("imageinfo"):
        return None
    em = page["imageinfo"][0].get("extmetadata", {})
    author = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", em.get("Artist", {}).get("value", ""))).strip()
    return {"file": name, "license": em.get("LicenseShortName", {}).get("value", ""), "author": author if len(author) < 45 else "",
            "url": "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(name.replace(" ", "_"))}


def backfill_credits(out):
    """Add picture credits to entries that have a picture but no credit yet."""
    for k, v in out.items():
        if v.get("img") and not v.get("imgCredit"):
            for side in ("en", "sk"):
                s = summary(v[side]["lang"], v[side]["title"])
                c = commons_credit((s or {}).get("thumb"))
                time.sleep(0.5)
                if c:
                    v["imgCredit"] = c
                    print("credit", k, c["license"], c["author"])
                    break


def main():
    terms = json.loads((ROOT / "data" / "terms.json").read_text(encoding="utf-8"))
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    path = ROOT / "data" / "wiki.json"
    out = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}  # resume: only fetch terms not done yet
    for t in terms:
        if t["id"] in out:
            continue
        time.sleep(2)
        en_title, links = langlinks(t["wiki"])
        if t.get("skwiki"):
            # a hand-checked Slovak article wins over the language links (some are missing or point elsewhere)
            links["sk"] = t["skwiki"]
        if not en_title and t.get("skwiki"):
            # no English article: use the Slovak one for both languages
            en_title, links = None, {"sk": t["skwiki"]}
        elif not en_title:
            print("MISSING", t["wiki"]); continue
        en = summary("en", en_title) if en_title else None; time.sleep(0.3)
        sk = None
        for lang in ("sk", "cs"):
            if lang in links:
                sk = summary(lang, links[lang]); time.sleep(0.3)
                if sk:
                    break
        sk = sk or en
        en = en or sk
        if not en:
            print("NO SUMMARY", en_title or t["wiki"]); continue
        entry = {"sk": {k: sk[k] for k in ("lang", "title", "extract", "url")},
                 "en": {k: en[k] for k in ("lang", "title", "extract", "url")}}
        thumb = en.get("thumb") or sk.get("thumb")
        if thumb:
            try:
                raw = urllib.request.urlopen(urllib.request.Request(thumb, headers=UA), timeout=30).read()
                im = Image.open(io.BytesIO(raw)).convert("RGB")
                im.thumbnail((180, 180))
                im.save(IMG_DIR / f"{t['id']}.jpg", quality=80, optimize=True)
                entry["img"] = f"wiki/{t['id']}.jpg"
            except Exception as ex:
                print("IMG FAIL", t["id"], ex)
        out[t["id"]] = entry
        print(t["id"], "| sk:", entry["sk"]["lang"], entry["sk"]["title"], "| img:", "img" in entry)
        path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")  # save as we go, so a re-run resumes
        time.sleep(0.3)
    backfill_credits(out)
    (ROOT / "data" / "wiki.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(out), "of", len(terms), "terms")


if __name__ == "__main__":
    main()
