"""AI illustrations for periods without real pictures (Gemini image model).

Needs a Gemini API key: GEMINI_API_KEY in the environment or in .env at the project root (see .env.example).
Prompts live in data/ai_prompts.json; every result is saved to site/img/<id>.jpg (+ _t thumbnail),
added to data/images.json with kind "ai", and its estimated cost is logged in ai_ledger.json (git-ignored).

  python site/tools/aigen.py <prompt-id> [<prompt-id> ...]      generate the given prompts
  python site/tools/aigen.py --list                             show prompts and whether they exist
"""
import base64
import io
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ENV = ROOT / ".env"  # GEMINI_API_KEY=... (copy .env.example); an environment variable wins
MODEL = "gemini-3-pro-image"
EST_USD = 0.14  # estimated price of one 2K image; check against the Google billing page
STYLE = (
    "Style: a quiet, historically careful illustration in muted watercolour and ink, like a plate in a regional museum guide. "
    "Soft natural daylight, earthy palette (ochre, reed green, river grey-blue, warm clay), gentle paper texture, no dramatic fantasy lighting. "
    "Landscape of the flat Danubian lowland in south-west Slovakia: wide sky, reeds, willows, sandy dunes and slow river arms of the Váh. "
    "People are small in the scene, dressed accurately for the period, no heroic poses, no gore. "
    "Wells are simple timber-lined shafts without cranks or windlasses unless the period is late medieval or later. "
    "The painting fills the whole canvas edge to edge: no paper margin, no drawn border line, no frame. "
    "Never draw any text, letters, captions, signatures, logos, borders or frames."
)


def key():
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
    if ENV.exists():
        for line in ENV.read_text(encoding="utf-8").splitlines():
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("Set GEMINI_API_KEY in the environment or in .env (see .env.example)")


def generate(p):
    body = {"contents": [{"parts": [{"text": f"{p['prompt']}\n\n{STYLE}"}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9", "imageSize": "2K"}}}
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
                      headers={"x-goog-api-key": key()}, json=body, timeout=300)
    if not r.ok:
        raise RuntimeError(f"{p['id']}: {r.status_code} {r.text[:300]}")
    for cand in r.json().get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            data = part.get("inline_data") or part.get("inlineData")
            if data:
                return Image.open(io.BytesIO(base64.b64decode(data["data"]))).convert("RGB")
    raise RuntimeError(f"{p['id']}: no image in response")


def trim_paper(im):
    """The model sometimes paints on a cream paper sheet with a margin or a thin frame line. Cut every side inward
    until most of the line is painting rather than plain paper, then a few pixels more to drop any frame stroke."""
    import numpy as np
    g = np.asarray(im.convert("L")).astype(float)
    h, w = g.shape
    # a plain paper margin is almost flat (brightness spread along the line ~2–6); painted lines vary more
    def first(spread, limit):
        for i, s in enumerate(spread[:limit]):
            if s > 7:
                return i
        return limit
    lim_y, lim_x = int(h * 0.10), int(w * 0.10)
    rows, cols = g.std(axis=1), g.std(axis=0)
    top, bottom = first(rows, lim_y), first(rows[::-1], lim_y)
    left, right = first(cols, lim_x), first(cols[::-1], lim_x)
    pad = 6 if max(top, bottom, left, right) > 3 else 0
    return im.crop((left + pad, top + pad, w - right - pad, h - bottom - pad))


def main(args):
    if args and args[0] == "--trim":  # re-trim already generated pictures
        for pid in args[1:]:
            path = ROOT / "site" / "img" / f"{pid}.jpg"
            im = trim_paper(Image.open(path)); im.save(path, quality=84, optimize=True)
            t = im.copy(); t.thumbnail((420, 420)); t.save(ROOT / "site" / "img" / f"{pid}_t.jpg", quality=78, optimize=True)
            print(pid, "trimmed to", im.size)
        return
    prompts = {p["id"]: p for p in json.loads((ROOT / "data" / "ai_prompts.json").read_text(encoding="utf-8"))}
    if args == ["--list"]:
        for pid, p in prompts.items():
            print(("done " if (ROOT / "site" / "img" / f"{pid}.jpg").exists() else "todo ") + pid, "-", p["caption"]["en"][:70])
        return
    images_path, ledger_path = ROOT / "data" / "images.json", ROOT / "ai_ledger.json"
    images = json.loads(images_path.read_text(encoding="utf-8"))
    ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else []
    for pid in args:
        p = prompts[pid]
        im = trim_paper(generate(p))
        big = im.copy(); big.thumbnail((1600, 1600)); big.save(ROOT / "site" / "img" / f"{pid}.jpg", quality=84, optimize=True)
        small = im.copy(); small.thumbnail((420, 420)); small.save(ROOT / "site" / "img" / f"{pid}_t.jpg", quality=78, optimize=True)
        images = [i for i in images if i["id"] != pid] + [{
            "id": pid, "period": p["period"], "kind": "ai", "cover": p.get("cover", False), "event": p.get("event"),
            "caption": p["caption"], "credit": {"author": f"Google Gemini ({MODEL})", "license": "—", "site": "", "url": None},
            "prompt": p["prompt"], "size": big.size}]
        ledger.append({"when": datetime.now().isoformat(timespec="seconds"), "id": pid, "model": MODEL, "usd_est": EST_USD})
        print(pid, "saved", big.size, f"(est. ${EST_USD})")
    images_path.write_text(json.dumps(images, ensure_ascii=False, indent=1), encoding="utf-8")
    ledger_path.write_text(json.dumps(ledger, indent=1), encoding="utf-8")
    print("estimated total so far: $%.2f" % sum(x["usd_est"] for x in ledger))


if __name__ == "__main__":
    main(sys.argv[1:])
