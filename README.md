# Šaľa · Galanta · Matúškovo · Sládkovičovo

**An interactive history map of the lower Váh, SW Slovakia – from the Neanderthals to today.**
*Interaktívna mapa dejín Dolného Považia – od neandertálcov po dnešok.*

17 periods on a timeline. Each one has a map of its time (historical survey maps or our own landscape reconstruction), the story of who ruled here and what happened, census numbers, period pictures and short "voice of the time" cards. Terms in the text link to Wikipedia with a preview. Slovak by default, English too. Every fact is sourced and marked with how certain it is.

Made with ❤️ by [Kristian](https://kristian-io.github.io/cv/) + [Claude](https://claude.ai).

## How it works
The site is one static HTML page. All content lives in `data/*.json`; `site/build.py` inlines it into `site/template.html`.

```
data/            content: periods, events, places, census, map layers, pictures, Wikipedia previews, voices
research/        research notes per period, with sources and confidence levels
sources/         source list (S001…, M001…) referenced from the data
maps/            map inventory and licence notes
site/
  template.html  the page (HTML, CSS, JS – no framework)
  build.py       builds site/index.html (local), site/page.html, and dist/ (public site)
  tools/         one-off scripts: map layers, Wikipedia previews, picture download, AI illustrations, CREDITS.md
  maps/ img/ wiki/ peek/   pictures used by the page
```

### Research & sources
The facts on the site come from the notes in [research/](research/) – one file per group of periods, each fact with its sources and a confidence mark (**C** confirmed, **L** likely, **U** uncertain), plus the open questions we couldn't answer yet. All sources are listed in [sources/sources.md](sources/sources.md); the maps and how the drawn map was made are described in [maps/MAP-INVENTORY.md](maps/MAP-INVENTORY.md). The data format is in [data/SCHEMA.md](data/SCHEMA.md).

### Build and preview
Python 3 only, no packages needed for the build:

```bash
python site/build.py --dist
python -m http.server 8000 --directory dist
```

The tools in `site/tools/` need `requests`, `Pillow` (and `numpy` for the map layers).

### AI illustrations
Some periods have no possible photos, so they show AI illustrations (Google Gemini), always marked "AI" on the page. To make new ones, copy `.env.example` to `.env`, add your own `GEMINI_API_KEY`, add a prompt to `data/ai_prompts.json` and run `python site/tools/aigen.py <prompt-id>`.

## Deploy (Netlify)
`netlify.toml` builds with `python3 site/build.py --dist` and publishes `dist/`. The public build switches on a small feedback form (Netlify Forms) – turn on form detection in the Netlify site settings.

## Licences
- **Code:** [MIT-0](LICENSE) – no attribution needed.
- **Our texts, research notes and AI illustrations:** [CC0 1.0](LICENSE-content) – public domain.
- **Everything else keeps its own licence**, listed in [CREDITS.md](CREDITS.md): historical maps (CC BY 4.0, GKÚ Bratislava), map data (ODbL, © OpenStreetMap contributors), Wikipedia texts (CC BY-SA 4.0), and each photo under its own free licence.

## Corrections
Found a mistake or know a source, photo or story? Use the feedback form on the site, or open an issue here.
