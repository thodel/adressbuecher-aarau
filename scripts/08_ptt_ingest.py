"""08_ptt_ingest.py — Aarauer Telefonbuch-Daten aus dem PTT-Bestand (historic.localsearch) einbinden.

    PTT_TSV_DIR=~/Repos/PTT_phonebook_data_tsv/tsv python scripts/08_ptt_ingest.py

Quelle: github.com/thodel/PTT_phonebook_data_tsv (PTT-Archiv, DH Bern, localsearch),
automatisch aus OCR gewonnen, mit den dort beschriebenen Fehlern (Zeichen, Spalten,
Inserate). Drei Chargen: A (bis 1910, Seitenebene: ein Textblock je Seite), B (1911–1937,
Einträge), C (1938–1950, unsegmentiert).

Schreibt nach data/ext/ptt/:
  ptt_a_aarau_pages.tsv     Charge A, Netz Aarau: File, Year, Page, text (1889–1910)
  ptt_b_aarau_entries.tsv   Charge B, Locality = Aarau: alle Spalten (1921–1935)
  ptt_a_aarau_entries.tsv   aus den Seitentexten geschnittene Einträge (Name, Zusatz, Strasse, Nr.)
                            — heuristisch, siehe segment_page(); Qualität je Jahrgang unterschiedlich

Die Seitentexte der Charge A mischen Spalten: oft stehen erst mehrere Namen, dann die
zugehörigen Adressen. Die Segmentierung findet darum zuerst alle «Strasse Nummer»-Stellen
(Strassenvokabular aus 06_streets.csv) und ordnet Namen nur zu, wenn sie direkt vor der
Adresse stehen; sonst bleibt der Name ohne Adresse (address_confidence = none).
"""
from __future__ import annotations

import csv
import os
import re
import sys
from pathlib import Path

csv.field_size_limit(10**9)
SRC = Path(os.environ.get("PTT_TSV_DIR", os.path.expanduser("~/Repos/PTT_phonebook_data_tsv/tsv")))
OUT = Path("data/ext/ptt")
CSV_DIR = Path("data/csv")

A_FIELDS = ["File", "Year", "Page", "text"]


def street_vocab() -> list[str]:
    names = set()
    p = CSV_DIR / "06_streets.csv"
    if p.exists():
        with p.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r["norm_method"] in ("rule", "fuzzy") and int(r["n"]) >= 3:
                    names.add(r["street_norm"])
    names |= {"Bahnhofstraße", "Bahnhofstrasse", "Hintere Bahnhofstr.", "Telli", "Graben", "Weinberg", "Küttigerstraße",
              "Kasinostraße", "Casinostraße", "Laurenzenvorstadt", "Vordere Vorstadt", "Hintere Vorstadt", "Obere Vorstadt",
              "Vor dem Haldenthor", "Jenseits der Aare", "Rathhausgasse", "Rathausgasse", "Zollrain", "Ziegelrain", "Halden",
              "Milchgasse", "Metzgergasse", "Pelzgasse", "Kronengasse", "Kirchgasse", "Igelweid", "Schachen", "Hammer",
              "Bachstraße", "Rain", "Adelbändli", "Golattenmattgasse", "Entfelderstraße", "Gais", "Oberthor", "Schloßplatz",
              "Feerstraße", "Rohrerstraße", "Gönhardweg", "Jurastraße", "Zelglistraße", "Hohlweg"}
    return sorted(names, key=len, reverse=True)


def segment_page(text: str, vocab: list[str]) -> list[dict]:
    """Einträge aus einem Seitentext der Charge A: Name[, Zusatz] [Strasse Nr]."""
    t = re.sub(r"\s+", " ", text).replace(" . . .", "").replace(" . .", "")
    t = re.sub(r"(\s\.){2,}", " ", t)
    alt = "|".join(re.escape(v) for v in vocab)
    addr_re = re.compile(rf"(?P<street>{alt})\s*(?P<no>\d{{1,4}}\s?[a-z]?)?", re.I)
    # Kandidaten für Namen: «Nachname, Rest» vor der nächsten Adresse
    entries = []
    pos = 0
    for m in addr_re.finditer(t):
        before = t[pos:m.start()].strip(" .,;:")
        # letzter Name-Block vor der Adresse: beginnt mit Grossbuchstabe, enthält Komma
        cand = re.split(r"(?<=\d)\s+(?=[A-ZÄÖÜ])|(?<=[a-z]\.)\s{2,}(?=[A-ZÄÖÜ])", before)
        name_block = cand[-1].strip(" .,;:") if cand else ""
        if name_block and re.match(r"^[A-ZÄÖÜ][\w'&.-]+", name_block) and len(name_block) < 120:
            parts = [p.strip() for p in name_block.split(",")]
            entries.append({"name": parts[0], "rest": ", ".join(parts[1:]), "street": m.group("street"),
                            "no": (m.group("no") or "").replace(" ", ""), "address_confidence": "adjacent"})
        else:
            entries.append({"name": "", "rest": name_block[:80], "street": m.group("street"),
                            "no": (m.group("no") or "").replace(" ", ""), "address_confidence": "unassigned"})
        pos = m.end()
    return entries


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if not SRC.exists():
        sys.exit(f"PTT-TSV nicht gefunden: {SRC} (PTT_TSV_DIR setzen)")
    # Charge A: Seiten des Netzes Aarau
    pages = []
    with (SRC / "a1.tsv").open(encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if (row.get("Network") or "").strip() == "Aarau" or "_Aarau_" in (row.get("File") or ""):
                pages.append({"File": row["File"], "Year": row["Year"], "Page": row["Page"], "text": (row.get("AggregatedContent") or "").strip()})
    pages.sort(key=lambda r: (int(r["Year"]), int(r["Page"]) if r["Page"].isdigit() else 0))
    with (OUT / "ptt_a_aarau_pages.tsv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=A_FIELDS, delimiter="\t"); w.writeheader(); w.writerows(pages)
    print(f"Charge A: {len(pages)} Seiten, Jahre {sorted({r['Year'] for r in pages})}")

    vocab = street_vocab()
    ents = []
    for p in pages:
        for i, e in enumerate(segment_page(p["text"], vocab), start=1):
            ents.append({"ptt_id": f"A-{p['Year']}-{int(p['Page']):03d}-{i:03d}", "year": p["Year"], "page": p["Page"], **e})
    with (OUT / "ptt_a_aarau_entries.tsv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["ptt_id", "year", "page", "name", "rest", "street", "no", "address_confidence"], delimiter="\t")
        w.writeheader(); w.writerows(ents)
    named = sum(1 for e in ents if e["name"])
    print(f"Charge A segmentiert: {len(ents)} Adressstellen, davon {named} mit direkt vorangehendem Namen")

    # Charge B: Einträge mit Locality Aarau
    rows = []
    for f in sorted(SRC.glob("b*.tsv")):
        with f.open(encoding="utf-8", errors="replace") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                if (row.get("Locality") or "").strip().lower() == "aarau":
                    rows.append({k: (row.get(k) or "").strip() for k in ("EntityName1", "EntityName2", "Supplement", "Street", "Locality", "PhoneNumber", "Year", "Page", "File")})
    rows.sort(key=lambda r: (int(r["Year"]), r["EntityName1"]))
    for i, r in enumerate(rows, start=1):
        r["ptt_id"] = f"B-{r['Year']}-{i:05d}"
    with (OUT / "ptt_b_aarau_entries.tsv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["ptt_id", "EntityName1", "EntityName2", "Supplement", "Street", "Locality", "PhoneNumber", "Year", "Page", "File"], delimiter="\t")
        w.writeheader(); w.writerows(rows)
    years = {}
    for r in rows:
        years[r["Year"]] = years.get(r["Year"], 0) + 1
    print(f"Charge B: {len(rows)} Einträge Aarau, je Jahr {dict(sorted(years.items()))}")


if __name__ == "__main__":
    main()
