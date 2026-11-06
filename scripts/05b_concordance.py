"""05b_concordance.py — Inhaltsverzeichnisse auswerten: Hausnummern-Konkordanz und Berufsklassen.

Die Inhaltsverzeichnisse der Vogel-Bände enthalten drei Dinge, die den Rest der
Pipeline stützen:

1. **Nummernbereiche je Seite** (1884): «Haus Nro. 1 — 47 Seite 55» → prüft, dass
   die Gebäudenummern einer Seite des Gebäudeverzeichnisses im erwarteten Bereich liegen.
2. **Strasse → Nummernbereiche → Seite** (1888, 1892): «Rathhausgasse: Haus Nr. 1—5
   Seite 1, „ „ 16—32 „ 3 …» → ordnet jeder Gebäudenummer ihre Strasse zu, unabhängig
   von Zwischentiteln im Verzeichnis, und ist die Grundlage für die Nummernstabilität
   zwischen den Bänden.
3. **Berufsklassen** («Aerzte . . . 71»): das Klassengerüst je Band für `06_occupations.csv`.

    python scripts/05b_concordance.py --run aarau-fraktur-gemini-v1 --reader gemini-3.8-flash

Liest alle Seiten mit section=vorspann und note «Inhalt…» aus 01_pages.csv und
schreibt data/csv/05b_number_ranges.csv (volume, street, no_from, no_to, page_printed)
und data/csv/06_occupation_classes.csv (volume, class, page_printed).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

CSV_DIR = Path("data/csv")
DASH = r"[—–-]"
RANGE_RE = re.compile(rf"(?P<a>\d+\s?[a-z]?)\s*{DASH}\s*(?P<b>\d+\s?[a-z]?)")
PAGE_TAIL = re.compile(r"(?:Seite|S\.|„)\s*(?P<p>\d+)\s*\.?$")
STREET_RE = re.compile(r"^(?P<s>[A-ZÄÖÜ][A-Za-zäöüß' .-]{2,40}?)\s*:\s*$")
CLASS_RE = re.compile(r"^(?P<c>[A-ZÄÖÜ][^.]{2,60}?)\s*(?:\.\s*){2,}\s*(?P<p>\d+)\s*$|^(?P<c2>[A-ZÄÖÜ][^.]{2,60}?)\s+(?P<p2>\d{2,3})\s*$")


def parse_toc(text: str, volume: str) -> tuple[list[dict], list[dict]]:
    ranges, classes = [], []
    street, in_classes = "", False
    for raw in text.split("\n"):
        line = raw.strip().replace("[spalte 2]", "")
        if not line:
            continue
        if re.search(r"Geschäften|Gewerben|Berufsklassen", line):
            in_classes = True
        m = STREET_RE.match(line)
        if m:
            street, in_classes = m.group("s").strip(), False
            continue
        r = RANGE_RE.search(line)
        p = PAGE_TAIL.search(line)
        if r and p and ("Haus" in line or "„" in line or "Nr" in line or street):
            ranges.append({"volume": volume, "street": street, "no_from": r.group("a").replace(" ", ""),
                           "no_to": r.group("b").replace(" ", ""), "page_printed": p.group("p")})
            continue
        if re.match(r"^\d+\s*$", line) or line.startswith("Seite"):
            continue
        c = CLASS_RE.match(line)
        if c and (in_classes or re.search(r"(\.\s){2,}", line)):   # Punktleiste reicht als Kennzeichen
            name = (c.group("c") or c.group("c2") or "").strip(" .")
            page = c.group("p") or c.group("p2")
            if name and not re.match(r"^(Seite|Inhalt|Verzeichni)", name):
                classes.append({"volume": volume, "class": name, "page_printed": page})
    return ranges, classes


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True); ap.add_argument("--reader", required=True)
    args = ap.parse_args()
    meta = {}
    with (CSV_DIR / "01_pages.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            meta[f"{r['volume']}_p{int(r['page']):03d}"] = r
    ranges, classes = [], []
    for jp in sorted((Path("data/atr") / args.run / args.reader).glob("*.json")):
        m = meta.get(jp.stem)
        if not m or m["section"] != "vorspann" or not re.search(r"Inhalt", m["note"], re.I):
            continue
        text = json.loads(jp.read_text(encoding="utf-8")).get("text") or ""
        r, c = parse_toc(text, m["volume"])
        print(f"{jp.stem}: {len(r)} Bereiche, {len(c)} Klassen")
        ranges.extend(r); classes.extend(c)
    for path, rows, fields in ((CSV_DIR / "05b_number_ranges.csv", ranges, ["volume", "street", "no_from", "no_to", "page_printed"]),
                               (CSV_DIR / "06_occupation_classes.csv", classes, ["volume", "class", "page_printed"])):
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
        print(f"{len(rows)} → {path}")


if __name__ == "__main__":
    main()
