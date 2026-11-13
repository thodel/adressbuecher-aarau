"""80_telefon.py — Einträge mit Telefonzeichen mit dem Telefonbuch der PTT verbinden.

    python scripts/80_telefon.py --vs ~/Repos/vernetzte-schweiz [--commit <sha>]

Für jeden Eintrag mit `phone_flag = 1` (☎ bzw. Nummer im Adressbuch) sucht das Skript den passenden
Eintrag im PTT-Telefonbuch und schreibt ihn nach web/telefon.csv:

1. **nummer** — die im Adressbuch gedruckte Nummer (aus data/qwen/<Band>/entries.csv, Feld `phone`)
   steht im Telefonbuch derselben Gemeinde, höchstens 5 Jahre entfernt, und der Familienname passt.
2. sonst die Verknüpfung von «Vernetzte Schweiz» (links/ptt_ab.csv) mit ihrer Stufe
   **sicher / wahrscheinlich / möglich**; bei mehreren die beste Stufe, dann das nächste Jahr.
3. sonst **name**: im Telefonbuch der Gemeinde (höchstens 5 Jahre entfernt) steht genau eine Person mit diesem
   Familiennamen und passendem Vornamen (gleich oder Abkürzung).

Gelesen wird aus vernetzte-schweiz am angegebenen Commit (Standard: HEAD), nicht aus dem Arbeitsstand;
der Commit steht in web/telefon_source.txt. Dazu je Treffer die Einheit (Seite «#/e/<id>» von Vernetzte
Schweiz) und, für Telefonbücher bis 1910, das Seitenbild auf dem IIIF-Server des PTT-Archivs.

Die Daten in data/csv und data/qwen bleiben unverändert.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import re
import subprocess
import unicodedata
from collections import defaultdict
from pathlib import Path
import importlib
import sys

sys.path.insert(0, str(Path(__file__).parent))
forename_score = importlib.import_module("81_baende").forename_score

CITY = Path.cwd().name.removeprefix("adressbuecher-")  # baden, bern, …
CITY_LABEL = CITY.capitalize()  # Gemeinde, wo die CSV keine Spalte municipality haben (Aarau, Basel)
CSV_DIR = Path("data/csv")
QWEN = Path("data/qwen")
OUT = Path("web/telefon.csv")
TIER = {"nummer": 0, "sicher": 1, "wahrscheinlich": 2, "möglich": 3, "name": 4}
IIIF = "https://iiif.ptt-archiv.ch/iiif/3/{ref}_{img:04d}.jp2/full/max/0/default.jpg"


def git_show(vs: Path, commit: str, path: str) -> bytes:
    return subprocess.run(["git", "-C", str(vs), "show", f"{commit}:{path}"], check=True, capture_output=True).stdout


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.replace("ß", "ss")).encode("ascii", "ignore").decode().lower()
    first = re.split(r"[-,\s]+", s.strip())[0] if s.strip() else ""
    return re.sub(r"[^a-z]", "", first)


def same_name(a: str, b: str) -> bool:
    a, b = fold(a), fold(b)
    return bool(a and b) and (a == b or (len(a) >= 4 and len(b) >= 4 and a[:4] == b[:4]))


def qwen_numbers() -> dict[tuple[str, int, int], str]:
    """(Band, Seite, Nr. auf der Seite) → gedruckte Telefonnummer, wenn eine dasteht (nicht nur ☎)."""
    out = {}
    if not QWEN.exists():  # Aarau, Basel: keine qwen-Lesung, also keine gedruckten Nummern
        return out
    for d in QWEN.iterdir():
        p = d / "entries.csv"
        if not p.exists():
            continue
        with p.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                num = re.sub(r"\D", "", r.get("phone", ""))
                if num and num != "1" and re.fullmatch(r"\s*\d[\d\s]*\s*", r.get("phone", "")):
                    out[(d.name, int(r["page"]), int(r["seq"]))] = num
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--vs", type=Path, required=True, help="Checkout von thodel/vernetzte-schweiz")
    ap.add_argument("--commit", default="HEAD")
    args = ap.parse_args()
    commit = subprocess.run(["git", "-C", str(args.vs), "rev-parse", args.commit], check=True,
                            capture_output=True, text=True).stdout.strip()

    entries = []
    for f in sorted(p.name for p in CSV_DIR.glob("04_*.csv") if "probe" not in p.name):  # Einwohner, Berufe, ggf. Gemeinden
        with (CSV_DIR / f).open(encoding="utf-8") as fh:
            entries += [r for r in csv.DictReader(fh) if r.get("phone_flag") == "1"]
    for r in entries:
        r["municipality"] = r.get("municipality") or CITY_LABEL
    nums = qwen_numbers()
    munis = {r["municipality"] for r in entries if r["municipality"]}

    ptt = {}
    by_number = defaultdict(list)  # (Gemeinde, Nummer) → PTT-Einträge
    by_name = defaultdict(list)  # (Gemeinde, Familienname gefaltet) → PTT-Einträge
    with gzip.open(io.BytesIO(git_show(args.vs, commit, "data/norm/ptt_entries.csv.gz")), "rt", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["municipality_1914"] in munis:
                ptt[r["id"]] = r
                if r["phone_norm"]:
                    by_number[(r["municipality_1914"], r["phone_norm"])].append(r)
                if r["entity_type"] == "person":
                    by_name[(r["municipality_1914"], fold(r["surname"] or r["name1"]))].append(r)
    links = defaultdict(list)
    for r in csv.DictReader(io.StringIO(git_show(args.vs, commit, "links/ptt_ab.csv").decode("utf-8"))):
        if r["city"] == CITY:
            links[r["ab_id"].split(":", 1)[1]].append(r)
    entity = {}
    with gzip.open(io.BytesIO(git_show(args.vs, commit, "links/entities.csv.gz")), "rt", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            entity[r["record_id"]] = r["entity_id"]
    if not ptt:  # Gemeinden ausserhalb des Telefonbuchs: die Links tragen trotzdem Namen und Jahr
        print("Hinweis: keine PTT-Einträge für", sorted(munis))

    rows, stats = [], defaultdict(int)
    for e in entries:
        vol, page, seq = e["volume"], int(e["page"]), int(e["line_from"])
        num = nums.get((vol, page, seq), "")
        best = None
        if num:
            cands = [p for p in by_number.get((e["municipality"], num), [])
                     if abs(int(p["year"]) - int(vol)) <= 5 and same_name(e["surname"], p["surname"] or p["name1"])]
            if cands:
                p = min(cands, key=lambda p: abs(int(p["year"]) - int(vol)))
                best = ("nummer", p)
        if not best and links.get(e["entry_id"]):
            l = min(links[e["entry_id"]], key=lambda l: (TIER[l["tier"]], int(l["year_gap"])))
            best = (l["tier"], ptt.get(l["ptt_id"], {"id": l["ptt_id"], "year": l["ptt_year"], "name1": l["ptt_name"],
                                                     "name2": "", "street": l["ptt_address"], "phone": "",
                                                     "refcode": "", "image": "", "batch": ""}))
        if not best and e["entry_type"] == "person":
            # 3. Name: genau eine Person dieses Namens mit passendem Vornamen im Telefonbuch der Gemeinde (±5 Jahre)
            cands = [p for p in by_name.get((e["municipality"], fold(e["surname"])), [])
                     if abs(int(p["year"]) - int(vol)) <= 5
                     and (forename_score(e["forename"], p["forename"] or p["name2"]) or 0) >= 2]
            people = {(fold(p["surname"] or p["name1"]), fold(p["forename"] or p["name2"])[:3]) for p in cands}
            if cands and len(people) == 1:
                best = ("name", min(cands, key=lambda p: abs(int(p["year"]) - int(vol))))
        if not best:
            stats["ohne"] += 1
            continue
        how, p = best
        stats[how] += 1
        img = re.search(r"(\d+)$", p.get("image", "") or "")
        image = IIIF.format(ref=p["refcode"], img=int(img.group(1))) if img and p.get("batch") == "A" and p.get("refcode") else ""
        rows.append({"entry_id": e["entry_id"], "how": how, "ptt_year": p["year"],
                     "ptt_name": ", ".join(x for x in (p.get("name1", ""), p.get("name2", "")) if x),
                     "ptt_street": p.get("street", ""), "ptt_phone": p.get("phone", ""), "ab_phone": num,
                     "ptt_id": p["id"], "entity_id": entity.get(p["id"], ""), "image": image})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (OUT.parent / "telefon_source.txt").write_text(
        f"web/telefon.csv aus thodel/vernetzte-schweiz @ {commit}\n"
        "(data/norm/ptt_entries.csv.gz, links/ptt_ab.csv, links/entities.csv.gz) mit scripts/80_telefon.py\n",
        encoding="utf-8")
    print(f"{len(entries)} Einträge mit Telefon: " + ", ".join(f"{k} {v}" for k, v in sorted(stats.items())) + f" → {OUT}")


if __name__ == "__main__":
    main()
