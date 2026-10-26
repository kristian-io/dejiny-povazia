"""One-off: add Sládkovičovo (Diószeg) as the 4th core town, from research/18-sladkovicovo.md."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data"
load = lambda n: json.loads((D / n).read_text(encoding="utf-8"))
save = lambda n, x: (D / n).write_text(json.dumps(x, ensure_ascii=False, indent=1 if n != "layers.json" else None,
                                                   separators=None if n != "layers.json" else (",", ":")), encoding="utf-8")
C = [17.64405, 48.2053]  # town centre (OSM)

# --- place ---------------------------------------------------------------------------
places = [p for p in load("places.json") if p["id"] != "sladkovicovo"]
places.append({"id": "sladkovicovo",
               "names": {"sk": "Sládkovičovo", "hu": "Diószeg", "de": "Diosek",
                         "historical": ["Gyozyg (1326)", "Dyosec (1332–37)", "Magyardiószeg / Németdiószeg (19th c.)",
                                        "Veľký Diosek / Malý Diosek (1927)", "Diószeg (1943)", "Sládkovičovo (1948)"]},
               "coords": C, "firstMention": {"year": 1326, "source": "S041", "note": "1252 (Béla IV) is cited but unverified"},
               "county": "Pozsony (Bratislava), Galánta district", "role": "core"})
save("places.json", places)

# --- historical names per period ------------------------------------------------------
NAMES = {"p09": "Diószeg", "p10": "Diószeg", "p11": "Diószeg", "p12": "Magyardiószeg", "p13": "Magyardiószeg",
         "p14": "Veľký Diosek", "p15": "Diószeg", "p16": "Sládkovičovo", "p17": "Sládkovičovo"}
periods = load("periods.json")
for p in periods:
    k = p["id"].split("-")[0]
    if k in NAMES:
        p.setdefault("names", {})["sladkovicovo"] = NAMES[k]
save("periods.json", periods)

# --- census (two municipalities summed before 1943; 1991/2001 include Malá Mača) ------
pop = load("population.json")
pop["sladkovicovo"] = [
    {"year": 1910, "total": 3745, "hu": 2932, "sk": 350},
    {"year": 1930, "total": 4474, "hu": 2430, "sk": 1255},
    {"year": 1938, "total": 4808, "hu": 4055, "sk": 448},
    {"year": 1991, "total": 5874, "hu": 2715, "sk": 3114},
    {"year": 2001, "total": 6078, "hu": 2340, "sk": 3614},
    {"year": 2011, "total": 5479, "hu": 1737, "sk": 3524},
    {"year": 2021, "total": 5415, "hu": 1376, "sk": 3838}]
pop["_note"] = pop.get("_note", "") + " Sládkovičovo: S039/S040/S045 (1910–1938 = Magyar- + Németdiószeg; 1991/2001 include Malá Mača)."
save("population.json", pop)

# --- events ------------------------------------------------------------------------------
def ev(id, per, date, tsk, ten, xsk, xen, conf, src, co=C):
    return {"id": id, "period": per, "date": date, "title": {"sk": tsk, "en": ten}, "text": {"sk": xsk, "en": xen},
            "place": "sladkovicovo", "coords": co, "confidence": conf, "sources": src}

NEW = [
 ev("e-sl-bell-beaker", "p03-bronze-age", {"year": -2300, "approx": True}, "Hrob kultúry zvoncovitých pohárov", "A Bell Beaker grave",
    "Pri stavbe cesty v rokoch 1966–67 preskúmal A. Točík v polohe Nové diely v Sládkovičove hrob kultúry zvoncovitých pohárov s dvoma pohárikmi a štvornožkovou misou, najreprezentatívnejší svojho druhu na juhozápadnom Slovensku.",
    "During road building in 1966–67, A. Točík excavated a Bell Beaker grave at Nové diely in Sládkovičovo, with two cups and a four-footed bowl: the most representative of its kind in south-west Slovakia.",
    "confirmed", ["S046", "S039"]),
 ev("e-sl-germanic-cemetery", "p05-romans-quadi", {"year": 100, "approx": True}, "Germánske pohrebisko v Diószegu", "A Germanic cemetery at Diószeg",
    "Germánska osada a pohrebisko z 1.–2. storočia s pochovávaním spaľovaním aj kostrovým hrobom, z čias, keď tu žili Kvádi.",
    "A Germanic settlement and a cemetery of the 1st–2nd centuries with both cremation and inhumation graves, from the time of the Quadi.",
    "confirmed", ["S041", "S039"]),
 ev("e-sl-rider-grave", "p08-early-hungary", {"year": 950, "approx": True}, "Hrob staromaďarského jazdca", "An Old Hungarian rider's grave",
    "V roku 1967 sa pri stavbe cesty v Sládkovičove našli hroby z 10. storočia. V jednom ležal mladý jazdec s lebkou a prednými nohami koňa pri nohách. Točík ho považoval za stopu staromaďarskej vojenskej hranice voči mladému štátu Přemyslovcov.",
    "In 1967 road works at Sládkovičovo uncovered 10th-century graves. One held a young rider with the skull and forelegs of his horse at his feet. Točík read it as a trace of the Old Hungarian military frontier facing the young Přemyslid state.",
    "likely", ["S032"]),
 ev("e-sl-first-mention", "p09-high-middle-ages", {"year": 1326}, "Gyozyg – Orechový kút", "Gyozyg, the walnut corner",
    "Diószeg (maď. „orechový kút“) sa isto spomína v roku 1326 ako Gyozyg; častejšie uvádzaný rok 1252 nie je overený. V roku 1301 patril Mikulášovi Dudvágymu, neskôr Petrovi Orrosovi a Stiborovi zo Stiboríc.",
    "Diószeg (Hungarian for 'walnut corner') is securely recorded in 1326 as Gyozyg; the often-quoted 1252 is unverified. In 1301 it belonged to Nicholas Dudvágy, later to Peter Orros and Stibor of Stiboricz.",
    "likely", ["S041", "S039", "S042"]),
 ev("e-sl-poor-clares", "p10-ottoman-frontier", {"year": 1582}, "Mestečko klarisiek", "A market town of the Poor Clares",
    "Diószeg asi 230 rokov (okolo 1553 – 1782) vlastnili rehoľníčky klarisky z Budína a neskôr z Bratislavy. Rudolf II. mu v roku 1582 udelil trhové právo. Ležal na kráľovskej ceste Bratislava – Nitra s brodom cez Dudváh.",
    "For about 230 years (c. 1553–1782) Diószeg belonged to the Poor Clare nuns of Buda and later of Pressburg. Rudolf II granted it market rights in 1582. It lay on the royal road Pressburg–Nitra, with a crossing of the Dudváh.",
    "confirmed", ["S042", "S039", "S044"]),
 ev("e-sl-ottomans", "p10-ottoman-frontier", {"year": 1530}, "Turecké nájazdy", "Ottoman raids",
    "Turci Diószeg vypálili v roku 1530 a vyplienili v roku 1599. Susedná dedina Dudvágszeg zanikla v rokoch 1673–83; zostal po nej len názov poľa.",
    "The Ottomans burned Diószeg in 1530 and looted it in 1599. The neighbouring village of Dudvágszeg was destroyed in 1673–83; only a field name remains.",
    "confirmed", ["S039", "S044", "S042"]),
 ev("e-sl-1709-fire", "p11-18th-century", {"year": 1707}, "Starhemberg a požiar", "Starhemberg and the great fire",
    "Počas Rákócziho povstania obsadil cisársky generál Guido Starhemberg v roku 1707 mestečko a opevnil ho proti kurucom. V roku 1709 celé vyhorelo.",
    "During Rákóczi's uprising the imperial general Guido Starhemberg occupied the town in 1707 and fortified it against the kuruc. In 1709 the whole town burned down.",
    "confirmed", ["S044", "S039"]),
 ev("e-sl-german-colony", "p11-18th-century", {"year": 1786}, "Nemeckí kolonisti", "The German colonists",
    "V rokoch 1786–87 sa za Jozefa II. na pustatine Újhely usadilo okolo 60 nemeckých rodín (asi 321 ľudí) z Breisgau, Württemberska, Bamberska či Mohuča. Ich osada Németdiószeg bola v rokoch 1853 – 1943 samostatnou obcou.",
    "In 1786–87, under Joseph II, about 60 German families (some 321 people) from Breisgau, Württemberg, Bamberg and Mainz settled on the Újhely estate. Their village, Németdiószeg, was a separate municipality from 1853 to 1943.",
    "likely", ["S043", "S039", "S042"], co=[17.5967, 48.2160]),
 ev("e-sl-railway", "p12-19th-century", {"year": 1850}, "Stanica v nemeckej časti", "A station in the German part",
    "Trať Bratislava – Pešť prešla v roku 1850 aj cez Diószeg; stanica stála v nemeckej časti. Fényes (1851) opisuje maďarsko-nemecké mestečko s veľkým hostincom, tisícovými stádami oviec a dobrými koňmi.",
    "The Pressburg–Pest railway reached Diószeg in 1850; the station stood in the German part. Fényes (1851) describes a Hungarian–German market town with a large inn, flocks of thousands of sheep and fine horses.",
    "confirmed", ["S039", "S043"], co=[17.62969, 48.19555]),
 ev("e-sl-sugar-factory", "p13-austria-hungary", {"year": 1867}, "Kuffnerov cukrovar", "Kuffner's sugar factory",
    "Viedenská firma Kuffner & Guttmann tu v roku 1867 spustila cukrovar. Viedol ho Karl Kuffner, ktorý prišiel ako 22-ročný, stal sa barónom „z Diószegu“ a premenil mestečko: kaštieľ (1885–86), mlyn Mária (1912), robotnícka kolónia, park a rodinné mauzóleum. Závod zamestnával vyše 1 000 ľudí.",
    "The Viennese firm Kuffner & Guttmann opened a sugar factory here in 1867. It was run by Karl Kuffner, who arrived aged 22, became Baron Kuffner 'of Diószeg' and reshaped the town: the manor (1885–86), the Mária mill (1912), a workers' colony, the park and the family mausoleum. The factory employed over 1,000 people.",
    "confirmed", ["S043", "S049", "S048", "S016"], co=[17.650, 48.202]),
 ev("e-sl-darwin", "p13-austria-hungary", {"year": 1876}, "Diószeg v albume pre Darwina", "Diószeg in Darwin's album",
    "Fotografia Karla Kuffnera „z Dioszeghu v Uhorsku“ je v albume, ktorý v roku 1876 poslali Charlesovi Darwinovi jeho nemeckí a rakúski obdivovatelia.",
    "A photograph of Karl Kuffner 'of Dioszegh, Hungary' is in the album that Charles Darwin's German and Austrian admirers sent him in 1876.",
    "likely", ["S050"]),
 ev("e-sl-1919", "p14-first-republic", {"year": 1919, "month": 1, "day": 6}, "Československé vojsko v Diószegu", "Czechoslovak troops at Diószeg",
    "V nedeľu 6. januára 1919 obsadilo Diószeg československé vojsko; miestna národná garda odovzdala zbrane bez odporu. V roku 1927 dostali obe obce mená Veľký a Malý Diosek.",
    "On Sunday 6 January 1919 Czechoslovak troops occupied Diószeg; the local national guard handed over its weapons without resistance. In 1927 the two villages were named Veľký and Malý Diosek.",
    "likely", ["S016", "S041"]),
 ev("e-sl-1938", "p15-vienna-award-ww2", {"year": 1938, "month": 11, "day": 10}, "Diószeg znova v Maďarsku", "Diószeg back in Hungary",
    "Maďarské vojsko prevzalo obe obce 10. novembra 1938. Mali 4 808 obyvateľov, z toho 84 % Maďarov a 152 Židov. V roku 1943 sa Magyardiószeg a Németdiószeg zlúčili do jednej obce Diószeg.",
    "Hungarian troops took over both villages on 10 November 1938. They had 4,808 inhabitants, 84% Hungarian and 152 Jewish. In 1943 Magyardiószeg and Németdiószeg were merged into one municipality, Diószeg.",
    "likely", ["S045", "S043"]),
 ev("e-sl-holocaust", "p15-vienna-award-ww2", {"year": 1944}, "Deportácia diószegských Židov", "The deportation of Diószeg's Jews",
    "Miestni Židia boli v roku 1944 deportovaní, pravdepodobne ako galantskí cez geto v Nových Zámkoch do Auschwitzu. Na židovskom cintoríne je 81 náhrobkov z rokov 1848–1942 a pamätník obetiam holokaustu.",
    "The local Jews were deported in 1944, probably like those of Galanta, via the Nové Zámky ghetto to Auschwitz. The Jewish cemetery has 81 gravestones from 1848–1942 and a Holocaust memorial.",
    "likely", ["S040", "S047"], co=[17.6314, 48.20541]),
 ev("e-sl-1946", "p16-communism", {"year": 1946}, "Vyhnanie, reslovakizácia, výmena", "Expulsion, re-Slovakisation, exchange",
    "Na jar 1946 vyhnali asi 60 Nemcov. Zo 4 725 obyvateľov sa 2 586 „reslovakizovalo“. Na jeseň odvliekli niekoľko rodín na práce do Čiech a od roku 1947 bolo 144 maďarských rodín určených na presídlenie do Maďarska. Prišlo asi 140 slovenských rodín z Pitvarošu.",
    "In spring 1946 about 60 Germans were expelled. Of 4,725 inhabitants, 2,586 were 're-Slovakised'. In the autumn several families were taken to forced labour in Bohemia, and from 1947, 144 Hungarian families were listed for transfer to Hungary. About 140 Slovak families arrived from Pitvaros.",
    "likely", ["S043", "S041"]),
 ev("e-sl-renamed", "p16-communism", {"year": 1948}, "Z Diosku je Sládkovičovo", "Diosek becomes Sládkovičovo",
    "Mesto dostalo meno po básnikovi Andrejovi Sládkovičovi, hoci s ním nemalo nič spoločné. Starší obyvatelia premenovanie dodnes nazývajú „zlým vtipom“. Mestom je od roku 1983.",
    "The town was named after the poet Andrej Sládkovič, although he had no connection with it. Older residents still call the renaming a 'bad joke'. It has been a town since 1983.",
    "confirmed", ["S043", "S040"]),
 ev("e-sl-memorial-1997", "p17-today", {"year": 1997}, "Pamätník vyhnaných", "A memorial to the expelled",
    "Na cintoríne stojí pamätník Nemcom vyhnaným v roku 1946 a Maďarom vysídleným v roku 1947, s nápisom po slovensky, maďarsky a nemecky.",
    "In the cemetery stands a memorial to the Germans expelled in 1946 and the Hungarians resettled in 1947, inscribed in Slovak, Hungarian and German.",
    "likely", ["S043"], co=[17.63785, 48.20664]),
 ev("e-sl-factory-closed", "p17-today", {"year": 2000}, "Koniec cukrovaru", "The sugar factory closes",
    "Cukrovar po 133 rokoch ukončil výrobu v roku 2000; jeho budovy chátrajú. Pripomína ho Kuffnerov kaštieľ, mauzóleum a park.",
    "After 133 years the sugar factory closed in 2000; its buildings are decaying. The Kuffner manor, mausoleum and park remain.",
    "confirmed", ["S039", "S052", "S048"]),
]
events = [e for e in load("events.json") if e["place"] != "sladkovicovo"] + NEW
order = {p["id"]: p["order"] for p in periods}
events.sort(key=lambda e: (order[e["period"]], e["date"]["year"]))
save("events.json", events)

# --- pictures -------------------------------------------------------------------------
images = [i for i in load("images.json") if not i["id"].startswith("sl-")]
for i in images:
    if i["id"] == "p13-dioszeg-sugar":
        i.update({"place": "sladkovicovo", "coords": [17.650, 48.202], "approx": True, "event": "e-sl-sugar-factory"})
images += [
 {"id": "sl-p13-factory-1904", "period": "p13-austria-hungary", "kind": "photo", "dated": 1904, "place": "sladkovicovo", "coords": [17.650, 48.202], "approx": True,
  "commons": "Cukorgyár Diószeg.png", "caption": {"sk": "Cukrovar v Diószegu okolo roku 1904 (z monografie Pozsony vármegye).", "en": "The Diószeg sugar factory around 1904 (from the Pozsony County monograph)."}},
 {"id": "sl-p13-kuffner", "period": "p13-austria-hungary", "kind": "portrait", "event": "e-sl-darwin",
  "commons": "Plate 18 Karl Kuffner, Photograph album of German and Austrian scientists (cropped).png",
  "caption": {"sk": "Karl Kuffner, 1876, z albumu pre Charlesa Darwina (foto Emil Rade).", "en": "Karl Kuffner, 1876, from the album for Charles Darwin (photo Emil Rade)."}},
 {"id": "sl-p13-manor", "period": "p13-austria-hungary", "kind": "building", "place": "sladkovicovo", "coords": [17.64614, 48.20612],
  "commons": "Sládkovičovo 17 Slovakia9.jpg", "caption": {"sk": "Kuffnerov kaštieľ v Sládkovičove (prestavba 1885–86).", "en": "The Kuffner manor in Sládkovičovo (rebuilt 1885–86)."}},
 {"id": "sl-p12-stamp", "period": "p12-19th-century", "kind": "find",
  "commons": "1863issue TJ Dioszegh Slovakia.jpg", "caption": {"sk": "Novinová kolková známka z roku 1863 s pečiatkou pošty DIOSZEGH.", "en": "An 1863 newspaper-tax stamp cancelled by the DIOSZEGH post office."}},
 {"id": "sl-p11-church", "period": "p11-18th-century", "kind": "building", "place": "sladkovicovo", "coords": [17.64505, 48.20542],
  "commons": "Diószeg templom 3.JPG", "caption": {"sk": "Kostol Nanebovzatia Panny Márie v Sládkovičove, prestavaný v rokoch 1736 a 1786.", "en": "The Church of the Assumption in Sládkovičovo, rebuilt in 1736 and 1786."}},
 {"id": "sl-p11-ujhely", "period": "p11-18th-century", "kind": "building", "place": "sladkovicovo", "coords": [17.5967, 48.2160], "approx": True, "event": "e-sl-german-colony",
  "commons": "Diószeg Újhely kereszt 1.JPG", "caption": {"sk": "Kríž na mieste Újhely, kde sa v rokoch 1786–87 usadili nemeckí kolonisti.", "en": "A cross at Újhely, where the German colonists settled in 1786–87."}},
 {"id": "sl-p16-sladkovic", "period": "p16-communism", "kind": "portrait", "event": "e-sl-renamed",
  "commons": "Andrej Sládkovič.png", "caption": {"sk": "Básnik Andrej Sládkovič (portrét J. B. Klemensa, 1872), po ktorom mesto v roku 1948 premenovali.", "en": "The poet Andrej Sládkovič (portrait by J. B. Klemens, 1872), after whom the town was renamed in 1948."}},
]
save("images.json", images)

# --- drawn map: Sládkovičovo village becomes a core town (no duplicate small dot) --------
layers = load("layers.json")
for v in layers["villages"]:
    if v["sk"] == "Sládkovičovo":
        v["core"] = True
save("layers.json", layers)

# --- Wikipedia terms ------------------------------------------------------------------
terms = [t for t in load("terms.json") if t["id"] not in
         ("sladkovic", "bell-beaker", "poor-clares", "rudolf-ii", "joseph-ii", "starhemberg", "dudvah", "pitvaros")]
terms += [
 {"id": "sladkovic", "wiki": "Andrej Sládkovič", "sk": ["Andrej\\p{L}* Sládkovič\\p{L}*", "básnik\\p{L}* Sládkovič\\p{L}*"], "en": ["Andrej Sládkovič"]},
 {"id": "bell-beaker", "wiki": "Bell Beaker culture", "skwiki": "Kultúra zvoncovitých pohárov", "sk": ["kultúr\\p{L}* zvoncovitých pohárov"], "en": ["Bell Beaker"]},
 {"id": "poor-clares", "wiki": "Poor Clares", "skwiki": "Klarisky", "sk": ["klarisk\\p{L}*"], "en": ["Poor Clares?"]},
 {"id": "rudolf-ii", "wiki": "Rudolf II, Holy Roman Emperor", "sk": ["Rudolf\\p{L}* II\\."], "en": ["Rudolf II"]},
 {"id": "joseph-ii", "wiki": "Joseph II, Holy Roman Emperor", "sk": ["Jozef\\p{L}* II\\."], "en": ["Joseph II"]},
 {"id": "starhemberg", "wiki": "Guido Starhemberg", "sk": ["Guido Starhemberg\\p{L}*"], "en": ["Guido Starhemberg"]},
 {"id": "dudvah", "wiki": "Dudváh", "skwiki": "Dudváh", "sk": ["Dudváh\\p{L}*"], "en": ["Dudváh"]},
 {"id": "pitvaros", "wiki": "Pitvaros", "skwiki": "Pitvaroš", "sk": ["Pitvaroš\\p{L}*"], "en": ["Pitvaros"]},
]
(D / "terms.json").write_text("[\n" + ",\n".join("  " + json.dumps(t, ensure_ascii=False) for t in terms) + "\n]\n", encoding="utf-8")
print("places", len(places), "| events", len(events), "(+%d)" % len(NEW), "| images", len(images), "| terms", len(terms))
