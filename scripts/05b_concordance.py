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
        p = PAGE_TAIL.search(line)
        if p and ("Haus" in line or "„" in line or "Nr" in line or street):
            spec = line[:p.start()]
            spec = re.sub(r"^(Haus\s*Nr\.?|„|\"|Nr\.?|\s)+", "", spec).strip(" .,")
            found = False
            for item in re.split(r"\s*(?:,|\bu\.|\bund\b)\s*", spec):
                item = item.strip()
                r = RANGE_RE.search(item)
                if r:
                    a, b = r.group("a"), r.group("b")
                elif re.fullmatch(r"\d+\s?[a-z]?", item):
                    a = b = item
                else:
                    continue
                found = True
                ranges.append({"volume": volume, "street": street, "no_from": a.replace(" ", ""),
                               "no_to": b.replace(" ", ""), "page_printed": p.group("p")})
            if found:
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


def _n(s: str) -> int:
    return int(re.sub(r"\D", "", s) or 0)


def flag_ranges(ranges: list[dict]) -> None:
    """Lesefehler sichtbar machen: Bereich rückwärts, unplausibel lang (> 80 Nummern) oder
    überschneidet sich mit dem Bereich einer anderen Strasse desselben Bandes."""
    for r in ranges:
        r["note"] = ""
        a, b = _n(r["no_from"]), _n(r["no_to"])
        if b < a:
            r["note"] = "rückwärts"
        elif b - a > 80:
            r["note"] = f"unplausibel lang ({b - a + 1})"
    by_vol: dict[str, list[dict]] = {}
    for r in ranges:
        if r["street"]:
            by_vol.setdefault(r["volume"], []).append(r)
    for rows in by_vol.values():
        for i, r in enumerate(rows):
            a, b = _n(r["no_from"]), _n(r["no_to"])
            for s in rows[i + 1:]:
                if s["street"] == r["street"]:
                    continue
                c, d = _n(s["no_from"]), _n(s["no_to"])
                if max(a, c) <= min(b, d):
                    for x in (r, s):
                        other = s["street"] if x is r else r["street"]
                        if other not in x["note"]:
                            x["note"] = (x["note"] + "; " if x["note"] else "") + f"überschneidet {other}"
    n = sum(1 for r in ranges if r["note"])
    if n:
        print(f"{n} Bereiche mit Hinweis (Lesefehler prüfen)")


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
    flag_ranges(ranges)
    for path, rows, fields in ((CSV_DIR / "05b_number_ranges.csv", ranges, ["volume", "street", "no_from", "no_to", "page_printed", "note"]),
                               (CSV_DIR / "06_occupation_classes.csv", classes, ["volume", "class", "page_printed"])):
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
        print(f"{len(rows)} → {path}")


if __name__ == "__main__":
    main()
