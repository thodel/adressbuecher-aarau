"""05_buildings.py — Gebäudeverzeichnis parsen: Gebäude, Eigentümer, Bewohner (Stufe 5).

Grammatik der Bände (Gemini-Lesung im GT-Format):

    Rathausgasse.                         ← Strassentitel (keine Ziffer, endet mit . oder :)
    356. Hunziker, Emil Guido, Rentier.   ← Gebäudenummer [* oder †] Eigentümer[, Gebäudeart]
      Käser-Kähr, Ulrich, Kutscher, von Melchnau (Bern).   ← eingerückt: Bewohner
    357.† Derselbe. Remise.               ← Ditto-Eigentümer (Derselbe/Dieselbe/Dieselben/„), Gebäudeart
    365. u. 366.† Dieselbe. Scheune.      ← mehrere Nummern
    119a Rohr-Häfig, Emma, Wittwe, …      ← 1884: zweispaltig, ohne Punkt nach der Nummer

`*` = der Eigentümer wohnt selbst im Haus; `†` = Nebengebäude (Scheune, Remise, …).
1892/1899 setzen vor der Bewohnerzeile «—» für den wiederholten Familiennamen des
Eigentümers; das übernimmt `04_parse.parse_entry` mit dem Eigentümernamen als Vorgabe.

    python scripts/05_buildings.py --run aarau-probe-gemini-v1 --reader gemini-3.8-flash
    python scripts/05_buildings.py --text data/gt/1884_p070.txt --volume 1884 --page 70

Schreibt data/csv/05_buildings.csv (ein Gebäude je Zeile) und data/csv/05_residents.csv
(eine Person je Zeile, geparst wie ein Einwohnereintrag, mit `building_no`).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
_p = import_module("04_parse")
parse_entry, prenormalise, FIELDS = _p.parse_entry, _p.prenormalise, _p.FIELDS

CSV_DIR = Path("data/csv")
B_FIELDS = ["building_id", "volume", "page", "line", "building_no", "building_nos", "marker",
            "street_raw", "owner_text", "owner_same_as_prev", "owner_surname", "owner_entry",
            "building_type", "phone_flag", "parse_confidence", "note"]

NUM_RE = re.compile(r"^\s*(?P<nos>\d+\s?[a-z]?(?:\s*(?:\.|,)?\s*(?:u\.|und|-|–)\s*\d+\s?[a-z]?)*)\s*\.?\s*(?P<mark>[*†+]|\(\*\))?\s*(?P<rest>.*)$")
DITTO_RE = re.compile(r"^(Derselbe|Dieselbe|Dieselben|Dieselb\.|„|\"|''|Ders\.|Dies\.)\s*[.,]?\s*(?P<type>.*)$")
STREET_RE = re.compile(r"^[A-ZÄÖÜ][^\d,]{2,60}[.:]?$")
STREET_SUFFIX = re.compile(r"(strasse|straße|gasse|gässchen|gäßchen|gässli|garten|vorstadt|platz|weg|rain|halden|hof|graben|thor|tor|aare|bahnhof|quartier|telli|gais|hammer|schachen|weinberg|igelweid|adelbändli|binsenhof|goldern|roggenhausen|oberholz|waltersburg|wöschnau|gishügel|kirchhof|stadthof|scheibenschachen|zelgli|promenade|allee|matte|holz|feld|halde|bühl|berg)\.?:?$", re.I)


AFTER_NUMBERING = "(nach der Nummerierung gebaut)"
PAREN_STREET = re.compile(r"\((?P<st>((vor|hinter|jenseits|in|im|an|bei|Vor|Hinter|Jenseits|In|Im|An|Bei|v\.|h\.)\s*)?((dem|der|den|d\.)\s+)?((obere|vordere|hintere|neues|Obere|Vordere|Hintere|Neues)\s+)?[A-ZÄÖÜ][^()\d,]{2,40}?)\.?(,[^()]*)?\)?(?=\s|$|\))")


def street_from_parens(text: str) -> str:
    for m in PAREN_STREET.finditer(text or ""):
        cand = m.group("st").strip().rstrip(".")
        c2 = cand.replace("ß", "ss")
        if is_street_heading(c2[:1].upper() + c2[1:]) or re.search(r"(str|g|bg|gässchen|gässli|vorst|garten)\.?$", c2):
            return cand
    return ""


def known_streets() -> set[str]:
    out = set()
    p = Path("data/csv/05b_number_ranges.csv")
    if p.exists():
        with p.open(encoding="utf-8") as fh:
            out |= {r["street"].lower() for r in csv.DictReader(fh) if r["street"]}
    return out


KNOWN_STREETS = known_streets()


def is_street_heading(s: str) -> bool:
    t = s.strip().rstrip(".:").strip()
    if not t or "," in t or re.search(r"\d", t) or len(t.split()) > 5 or t[:1].islower():
        return False
    return t.lower() in KNOWN_STREETS or bool(STREET_SUFFIX.search(t))


LOOKS_ENTRY = re.compile(r"^(\*\s*)?((Dr|Frau|Fräulein|Wwe|Witwe)\.?\s+)?[A-ZÄÖÜ][\w'.-]+(\s*-\s*[\w'.-]+)?(\s+(geb\.|&|u\.|und|von|de|à)\s+[\w'.-]+)*\s*,|^[A-ZÄÖÜ][\w-]+\s+(Gebr\.|&|u\.)")
HEADER_RE = re.compile(r"^(Haus[-=]?|Nr\.|—\s*\d+\s*—|\d+)\s*$")
TYPE_WORDS = ("Scheune", "Remise", "Waschhaus", "Holzhaus", "Holzschopf", "Schopf", "Magazin",
              "Fabrik", "Werkstätte", "Stall", "Gartenhaus", "Sommerhaus", "Eiskeller", "Keller",
              "Schuppen", "gebäude", "Hintergebäude", "Trinkhalle", "Brunnenhaus", "Bureau",
              "Comptoir", "Kapelle", "Turnhaus", "Pfarrhaus", "Kirche", "Schulhaus", "Spritzenhaus",
              "Badanstalt", "Lagerhaus", "Erbschaft", "häuschen", "Rebhaus", "Wagenschopf",
              "Wohngebäude", "Wohnhaus", "Oekonomiegebäude", "Abgetragen")


def split_type(owner: str) -> tuple[str, str]:
    """'Gemeinde Aarau, Brunnenhaus.' → ('Gemeinde Aarau', 'Brunnenhaus')"""
    parts = [p.strip(" .") for p in owner.split(",")]
    if len(parts) >= 2 and any(w.lower() in parts[-1].lower() for w in TYPE_WORDS) and not re.search(r"\bvon\b", parts[-1]):
        return ", ".join(parts[:-1]), parts[-1]
    m = re.match(r"^(?P<o>.+?)\.\s+(?P<t>[A-ZÄÖÜ][\w-]+(?:gebäude|haus|schopf|keller|halle|stall)?)\.?$", owner)
    if m and any(w.lower() in m.group("t").lower() for w in TYPE_WORDS):
        return m.group("o"), m.group("t")
    return owner.strip(" ."), ""


def parse_building_page(text: str, volume: str, page: int, street: str = "", prev_owner: dict | None = None):
    buildings, residents = [], []
    cur = prev_owner or None          # Bewohner am Seitenanfang gehören zum letzten Gebäude der Vorseite
    prev = prev_owner or {}
    for i, raw in enumerate(prenormalise(text).split("\n"), start=1):
        line = raw.rstrip()
        s = line.strip()
        if not s or s == "[spalte 2]" or HEADER_RE.match(s) or re.match(r"^(\d+\s+)?Verzeichniss? der Gebäude", s):
            continue
        if re.match(r"^Nach der Num\w*ung gebaute Häuser", s):
            street = AFTER_NUMBERING            # ab hier steht die Strasse in Klammern beim Gebäude
            continue
        s = re.sub(r"^Nr\.\s+(?=[A-ZÄÖÜ])", "", s)
        m = NUM_RE.match(s) if not line.startswith("  ") or re.match(r"^\s{0,8}\d", line) else None
        if m and re.match(r"^(Verzeichnis|Alphabetisches|Gebäude|Haus)", m.group("rest") or ""):
            continue                                   # Kolumnentitel mit Seitenzahl
        if m and m.group("nos") and (m.group("rest") or m.group("mark")):
            nos = re.sub(r"\s+", " ", m.group("nos")).strip()
            first = re.match(r"\d+\s?[a-z]?", nos).group(0).replace(" ", "")
            rest = m.group("rest").strip()
            phone = "1" if "[tel]" in rest else ""
            rest = rest.replace("[tel]", "").strip()
            d = DITTO_RE.match(rest)
            if d:
                owner_text, same, btype = prev.get("owner_text", ""), "1", d.group("type").strip(" .")
                surname, oentry = prev.get("owner_surname", ""), prev.get("owner_entry", "")
                conf = "high" if owner_text else "review"
            else:
                owner_text, btype = split_type(rest)
                same = ""
                e = parse_entry(owner_text, prev.get("owner_surname", ""))
                surname = e["surname"]
                oentry = json.dumps({k: e[k] for k in ("surname", "alliance_name", "forename", "occupation_raw", "origin_raw", "civil_status") if e.get(k)}, ensure_ascii=False)
                conf = "high" if surname else "medium"
            cur = {"building_id": f"{volume}-B-{first}", "volume": volume, "page": str(page), "line": i,
                   "building_no": first, "building_nos": nos, "marker": (m.group("mark") or "").strip("()"),
                   "street_raw": street, "owner_text": owner_text, "owner_same_as_prev": same,
                   "owner_surname": surname, "owner_entry": oentry, "building_type": btype,
                   "phone_flag": phone, "parse_confidence": conf, "note": ""}
            buildings.append(cur)
            prev = cur
        elif cur is not None and volume == "1884" and line.startswith("  "):
            # 1884 (zweispaltig, ohne Bewohnerzeilen): Einzug = Fortsetzung des Eigentümers
            joined = (cur["owner_text"][:-1] + s) if cur["owner_text"].endswith("-") and s[:1].islower() \
                else (cur["owner_text"] + ("" if cur["owner_text"].endswith("-") else " ") + s)
            cur["owner_text"], cur["building_type"] = split_type(joined.strip())
            e = parse_entry(cur["owner_text"], "")
            cur["owner_surname"] = e["surname"]
            cur["owner_entry"] = json.dumps({k: e[k] for k in ("surname", "alliance_name", "forename", "occupation_raw", "origin_raw", "civil_status") if e.get(k)}, ensure_ascii=False)
        elif cur is not None and (line.startswith("  ") or s.startswith("—") or LOOKS_ENTRY.match(s) or s[:1].islower()
                                  or not is_street_heading(s)):
            # 1899 rückt Bewohner nicht ein: «Name, …» ohne Hausnummer ist ein Bewohner
            starts_entry = bool(LOOKS_ENTRY.match(s) or s.startswith("—"))
            has_resident = bool(residents) and residents[-1]["building_id"] == cur["building_id"]
            if not starts_entry and not has_resident:
                # Fortsetzung der Eigentümerzeile («… Quincaillerie-» / «waaren- und Uhrenhandlung.»)
                joined = (cur["owner_text"][:-1] + s) if cur["owner_text"].endswith("-") and s[:1].islower() \
                    else (cur["owner_text"] + ("" if cur["owner_text"].endswith("-") else " ") + s)
                cur["owner_text"], btype = split_type(joined.strip())
                cur["building_type"] = btype or cur["building_type"]
                e = parse_entry(cur["owner_text"], prev.get("owner_surname", "") if cur is not prev else "")
                cur["owner_surname"] = e["surname"] or cur["owner_surname"]
                cur["owner_entry"] = json.dumps({k: e[k] for k in ("surname", "alliance_name", "forename", "occupation_raw", "origin_raw", "civil_status") if e.get(k)}, ensure_ascii=False)
                continue
            if has_resident and (line.startswith("    ") or not starts_entry):
                # tiefer eingerückt: Fortsetzung der letzten Bewohnerzeile
                r = residents[-1]
                r["text"] = (r["text"][:-1] + s) if r["text"].endswith("-") and s[:1].islower() else (r["text"] + " " + s)
                keep = ("entry_id", "volume", "page", "section", "line_from", "text")
                parsed = {k: v for k, v in parse_entry(r["text"], cur["owner_surname"], has_address=False).items() if k in FIELDS and k not in keep}
                residents[-1] = {**r, **parsed, "line_to": i, "building_id": cur["building_id"],
                                 "building_no": cur["building_no"], "street_raw": street}
                continue
            e = parse_entry(s, cur["owner_surname"], has_address=False)
            e = {k: v for k, v in e.items() if k != "_addresses"}
            e.update({"entry_id": f"{volume}-gebaeude-{page:03d}-L{i:03d}", "volume": volume,
                      "page": str(page), "section": "gebaeude", "line_from": i, "line_to": i,
                      "building_id": cur["building_id"], "building_no": cur["building_no"], "street_raw": street})
            residents.append(e)
        elif is_street_heading(s) and not s.startswith("—"):
            street = s.rstrip(".:").strip()
        else:
            if cur is not None:
                cur["note"] = (cur["note"] + " | " if cur["note"] else "") + f"unzugeordnet Z{i}: {s[:60]}"
    return buildings, residents, street, prev


def check_ranges(buildings: list[dict]) -> None:
    """Gebäudenummer gegen den Seitenbereich des Inhaltsverzeichnisses (05b) prüfen."""
    rng_path = CSV_DIR / "05b_number_ranges.csv"
    if not rng_path.exists():
        return
    printed = {}
    with (CSV_DIR / "01_pages.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["printed_page"].isdigit():
                printed[(r["volume"], r["page"])] = r["printed_page"]
    ranges = {}
    with rng_path.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if not r["street"]:
                ranges.setdefault((r["volume"], r["page_printed"]), []).append((int(re.sub(r"\D", "", r["no_from"])), int(re.sub(r"\D", "", r["no_to"]))))
    flagged = 0
    for b in buildings:
        key = (b["volume"], printed.get((b["volume"], b["page"]), ""))
        if key not in ranges:
            continue
        n = int(re.sub(r"\D", "", b["building_no"]) or 0)
        lo = min(a for a, _ in ranges[key]); hi = max(z for _, z in ranges[key])
        if not (lo - 40 <= n <= hi + 40):      # «nach der Nummerierung gebaute Häuser» dürfen abweichen
            b["note"] = (b["note"] + " | " if b["note"] else "") + f"Nummer ausserhalb Seitenbereich {lo}-{hi}"
            if b["parse_confidence"] == "high":
                b["parse_confidence"] = "medium"
            flagged += 1
    if flagged:
        print(f"{flagged} Gebäudenummern ausserhalb des Seitenbereichs laut Inhaltsverzeichnis")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--text", type=Path); ap.add_argument("--volume"); ap.add_argument("--page", type=int)
    ap.add_argument("--run"); ap.add_argument("--reader")
    ap.add_argument("--out-buildings", type=Path, default=CSV_DIR / "05_buildings.csv")
    ap.add_argument("--out-residents", type=Path, default=CSV_DIR / "05_residents.csv")
    args = ap.parse_args()

    pages = []
    if args.text:
        pages.append((args.volume, args.page, args.text.read_text(encoding="utf-8")))
    else:
        meta = {}
        with (CSV_DIR / "01_pages.csv").open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                meta[f"{r['volume']}_p{int(r['page']):03d}"] = r
        for jp in sorted((Path("data/atr") / args.run / args.reader).glob("*.json")):
            m = meta.get(jp.stem)
            if m and m["section"] == "gebaeude":
                pages.append((m["volume"], int(m["page"]), json.loads(jp.read_text(encoding="utf-8")).get("text") or ""))

    all_b, all_r = [], []
    street, prev, last = "", None, (None, None)
    for vol, page, text in pages:
        if vol != last[0]:                        # Strasse/Eigentümer innerhalb des Verzeichnisses mitführen (auch über Inserate-Lagen)
            street, prev = "", None            # Strasse/Eigentümer nur über direkte Folgeseiten mitführen
        b, r, street, prev = parse_building_page(text, vol, page, street, prev)
        all_b.extend(b); all_r.extend(r)
        last = (vol, page)
    # «nach der Nummerierung gebaute Häuser»: Strasse aus der Klammer beim Eigentümer oder beim ersten Bewohner
    res_by_b: dict[str, list[dict]] = {}
    for r in all_r:
        res_by_b.setdefault(r["building_id"], []).append(r)
    fixed = 0
    last_st = ""
    for b in all_b:
        if b["street_raw"] == AFTER_NUMBERING:
            st = street_from_parens(b["owner_text"] + " " + b["building_type"]) or next((street_from_parens(r["text"]) for r in res_by_b.get(b["building_id"], []) if street_from_parens(r["text"])), "")
            txt = b["owner_text"] + " " + b["building_type"]
            how = "Strasse aus Klammer"
            if not st and (re.search(r'(["„“]|\bid\b)\s*\.?\s*$', b["owner_text"]) or re.search(r'(^\s*(["„“]|id\b))|(\bid\.?\s*$)', b["building_type"]) or b["owner_same_as_prev"]):
                st, how = last_st, "Strasse vom vorigen Gebäude (Ditto)"
            b["street_raw"] = st
            last_st = st or last_st
            b["note"] = (b["note"] + " | " if b["note"] else "") + (f"nach der Nummerierung gebaut; {how}" if st else "nach der Nummerierung gebaut; Strasse fehlt")
            fixed += 1 if st else 0
            for r in res_by_b.get(b["building_id"], []):
                r["street_raw"] = st
    if any(b["note"].startswith("nach der Nummerierung") or "nach der Nummerierung" in b["note"] for b in all_b):
        n_after = sum(1 for b in all_b if "nach der Nummerierung" in b["note"])
        print(f"nach der Nummerierung gebaut: {n_after} Gebäude, Strasse aus Klammer: {fixed}")
    check_ranges(all_b)
    for path, rows, fields in ((args.out_buildings, all_b, B_FIELDS),
                               (args.out_residents, all_r, ["building_id", "building_no"] + FIELDS)):
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            w.writeheader(); w.writerows(rows)
    conf = {}
    for b in all_b:
        conf[b["parse_confidence"]] = conf.get(b["parse_confidence"], 0) + 1
    print(f"{len(all_b)} Gebäude ({conf}), {len(all_r)} Bewohner → {args.out_buildings}, {args.out_residents}")


if __name__ == "__main__":
    main()
