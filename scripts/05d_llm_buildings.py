"""05d_llm_buildings.py — frühe Bände (1833–1881, Hausnumerierung 1900) aus den LLM-Lesungen in CSV.

    python scripts/05d_llm_buildings.py --run gemini-frueh-v1 --run-1900 qwen-1900hn-v1

Liest data/atr/<run>/<band>_p<nnn>.jsonl (scripts/02d_llm_pages.py: ein JSON-Objekt je Druckzeile mit
house_no, marker, surname, forename, occupation, origin, heading, text) und schreibt:

- data/csv/05_buildings_frueh.csv  ein Gebäude je Zeile (Spalten wie 05_buildings_*.csv)
- data/csv/05_residents_frueh.csv  eine Person/Gebäudezeile je Zeile (Spalten wie 05_residents_*.csv)
- data/csv/05_register_frueh.csv   alphabetische Namensregister am Bandende (Name, Beruf, Hausnummer)
- data/csv/05_nachtraege_frueh.csv Veränderungen, Nachträge und Berichtigungen (Umzüge, neue Bewohner)
- data/csv/05_hausnumerierung_1900.csv  neue Nummer, Eigentümer, Gebäude, alte Nummer
- Abschnitt je Seite in data/csv/01_pages.csv (nur leere Felder werden gefüllt; Handangaben bleiben)

Regeln:
- Abschnitt einer Seite: «gebaeude», wenn mindestens die Hälfte der Einträge eine Hausnummer hat und der
  Text nicht mit der Nummer endet; «register», wenn die meisten Texte auf eine Nummer enden («Gehret,
  Forstinspektor 405.»); «inserate» bei langen Texten (Schnitt über 250 Zeichen); «nachtrag», wenn der
  Median der Hausnummern einer Gebäudeseite weit unter der bisher höchsten liegt (Veränderungen am Bandende); einzelne
  Einträge unter «Berichtigungen/Aenderungen/Veränderungen» gehen ebenfalls in die Nachträge; «leer» ohne
  Einträge; sonst «sonst» (Behörden, Vorspann, Tarife).
- Ein Gebäude beginnt, wo sich die Hausnummer ändert; der erste Eintrag ist der Eigentümer bzw. die erste
  Partei, die folgenden sind Bewohner. Zeilen ohne Nummer oben auf einer Seite gehören zum letzten Gebäude
  der Vorseite (Fortsetzung).
- Eine Klammer über mehrere Nummern hat das Modell teils je Nummer ausgeschrieben: aufeinanderfolgende
  Gebäude mit gleichem Text (ohne Nummer) und fortlaufenden Nummern werden zu einem Gebäude zusammengezogen
  (building_nos = alle Nummern, note = «Klammer zusammengeführt»).
- Randstreifen der Nachbarseite, die das Modell trotz Anweisung mitliest («1 C»), fallen weg; das lange s (ſ),
  das Gemini in einigen Seiten als Zeichen ausgibt, wird zu s.
- «Derselbe/Dieselbe/Dieselben/dto.» als Eigentümer → owner_same_as_prev = 1.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

CSV_DIR = Path("data/csv")
ATR = Path("data/atr")
B_FIELDS = ["building_id", "volume", "page", "line", "building_no", "building_nos", "marker",
            "street_raw", "owner_text", "owner_same_as_prev", "owner_surname", "owner_entry",
            "building_type", "phone_flag", "parse_confidence", "note"]
R_FIELDS = ["building_id", "building_no", "entry_id", "volume", "page", "section", "line_from", "line_to",
            "entry_type", "citizen_flag", "dash_prefix", "surname", "surname_inherited", "alliance_name",
            "maiden_name", "forename", "title", "civil_status", "relation", "occupation_raw", "origin_raw",
            "origin_canton", "address_seq", "address_role", "street_raw", "building_no", "phone_flag", "heading",
            "parse_method", "parse_confidence", "residual", "text"]
REG_FIELDS = ["entry_id", "volume", "page", "line", "surname", "forename", "civil_status", "occupation_raw",
              "building_no", "text"]
HN_FIELDS = ["row_id", "volume", "page", "line", "new_no", "surname", "alliance_name", "forename", "civil_status",
             "occupation_raw", "building_type", "old_no", "heading", "parse_confidence", "text"]
DITTO = re.compile(r"^(derselbe|dieselbe|dieselben|dasselbe|gleicher|dto\.?|„|\")$", re.I)
LEAD_NO = re.compile(r"^\s*(?:[*†]?\s*\d+[a-z]?\s*[.,]?\s*(?:[*†]\s*)?(?:(?:u\.|und|&|—|-)\s*)?)+")
TRAIL_NO = re.compile(r"\d+[a-z]?\.?\s*$")
FIRM = re.compile(r"\b(Gebr\.|Gebrüder|Comp\.|Cie\.|& Co|Gesellschaft|Fabrik|Bank|Gemeinde|Stadt Aarau|Staat|Centralbahn|Verein)\b")
NUM = re.compile(r"\d+")


HEADERS: dict[tuple[str, int], str] = {}
MED: dict[tuple[str, int], int | None] = {}  # (Band, Seite) → Median der Hausnummern  # (Band, Seite) → Kopfzeilen und Zwischentitel der Seite


def load(run: str) -> list[tuple[str, int, list[dict]]]:
    pages = []
    for f in sorted((ATR / run).glob("*.jsonl")):
        vol, p = f.stem.split("_p")
        rows = [json.loads(ln) for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()]
        HEADERS[(vol, int(p))] = " / ".join(r.get("text", "") for r in rows if r.get("type") in ("pageheader", "heading"))
        rows = [{k: (v.replace("ſ", "s").strip() if isinstance(v, str) else v) for k, v in r.items()} for r in rows
                if r.get("type") in ("entry", "row")]
        pages.append((vol, int(p), [r for r in rows if not fragment(r)]))
    return pages


def fragment(r: dict) -> bool:
    """Randstreifen der Nachbarseite («1 C», «2 s»): keine Namensfelder, Resttext höchstens 3 Zeichen."""
    if any(r.get(k) for k in ("surname", "forename", "occupation", "origin", "new_no", "old_no", "building")):
        return False
    return len(body(r).strip("*† .")) <= 3


def body(r: dict) -> str:
    """Eintragstext ohne vorangestellte Hausnummer(n) und Marken."""
    t = (r.get("text") or "").strip()
    return LEAD_NO.sub("", t).strip() or t


CHANGES = re.compile(r"Veränder|Berichtig|Aenderung|Änderung", re.I)


def section_of(entries: list[dict]) -> str:
    if not entries:
        return "leer"
    texts = [(r.get("text") or "").strip() for r in entries]
    if sum(len(t) for t in texts) / len(texts) > 250:
        return "inserate"
    trail = sum(1 for t in texts if TRAIL_NO.search(t) and not re.match(r"^[*†]?\s*\d", t))
    if trail >= 0.6 * len(entries):
        return "register"
    with_no = sum(1 for r in entries if NUM.search(str(r.get("house_no") or "")))
    return "gebaeude" if with_no >= 0.5 * len(entries) else "sonst"


def text_of(r: dict) -> str:
    if r.get("text"):
        return r["text"].strip()
    parts = [r.get("surname", ""), r.get("forename", ""), r.get("civil_status", ""), r.get("occupation", "")]
    t = ", ".join(p for p in parts if p)
    if r.get("origin"):
        t += f", von {r['origin']}"
    return t + "."


def numbers(h: str) -> list[int]:
    ns = [int(x) for x in NUM.findall(h or "")]
    if len(ns) == 2 and re.search(r"[–-]", h or "") and 0 < ns[1] - ns[0] < 30:
        return list(range(ns[0], ns[1] + 1))
    return ns


def resident(r: dict, vol: str, page: int, idx: int, b: dict, section: str) -> dict:
    rec = {k: "" for k in R_FIELDS}
    occ = (r.get("occupation") or "").strip()
    rec.update({
        "building_id": b["building_id"], "building_no": b["building_no"],
        "entry_id": f"{vol}-{section}-{page:03d}-E{idx:03d}", "volume": vol, "page": str(page), "section": section,
        "line_from": str(idx), "line_to": str(idx),
        "entry_type": "firma" if FIRM.search(text_of(r)) else "person",
        "surname": (r.get("surname") or "").strip(), "alliance_name": (r.get("alliance_name") or "").strip(),
        "forename": (r.get("forename") or "").strip(), "title": (r.get("title") or "").strip(),
        "civil_status": (r.get("civil_status") or "").strip(), "occupation_raw": occ,
        "origin_raw": (r.get("origin") or "").strip(), "street_raw": b["street_raw"],
        "heading": (r.get("heading") or "").strip(), "parse_method": "llm", "parse_confidence": "medium",
        "text": text_of(r)})
    m = re.search(r"geb\.\s*([^,]+)", rec["civil_status"] + " " + rec["text"])
    if m:
        rec["maiden_name"] = m.group(1).strip(" .")
    return rec


def buildings(pages, vol_filter=None):
    bld, res, reg, sections, nach = [], [], [], {}, []
    last = {}  # Band → letztes Gebäude (für Fortsetzungszeilen)
    top = {}   # Band → höchste Hausnummer des Hauptverzeichnisses
    for vol, page, entries in pages:
        sec = section_of(entries)
        if sec == "gebaeude":
            ns = sorted(n for r in entries for n in numbers(str(r.get("house_no") or ""))[:1])
            first = ns[len(ns) // 2] if ns else None  # Median: eine verlesene erste Nummer («73» statt 273) kippt nichts
            MED[(vol, page)] = first
            if CHANGES.search(HEADERS.get((vol, page), "")) and not any(
                    r.get("heading") and not CHANGES.search(r["heading"]) for r in entries):
                sec = "nachtrag"  # ganze Seite unter «Nachtrag & Berichtigungen»
            elif first is not None and first < top.get(vol, 0) - 50:
                sec = "nachtrag"  # Neubeginn der Nummern: Veränderungen/Nachträge am Bandende
        sections[(vol, page)] = sec
        if sec == "nachtrag" or sec == "gebaeude":
            keep = []
            for i, r in enumerate(entries, 1):
                if sec == "nachtrag" or CHANGES.search(r.get("heading") or ""):
                    nach.append({"entry_id": f"{vol}-nachtrag-{page:03d}-E{i:03d}", "volume": vol, "page": str(page),
                                 "line": str(i), "surname": r.get("surname", ""), "forename": r.get("forename", ""),
                                 "civil_status": r.get("civil_status", ""), "occupation_raw": r.get("occupation", ""),
                                 "building_no": str(r.get("house_no") or ""), "text": text_of(r)})
                else:
                    keep.append(r)
            if sec == "nachtrag":
                continue
            entries = keep
            if first is not None:  # laufender Stand = Median der Seiten (Ausreisser wie 1118 mitten in 1881 zählen nicht)
                top[vol] = max(top.get(vol, 0), first)
        if sec == "register":
            for i, r in enumerate(entries, 1):
                t = text_of(r)
                no = (r.get("house_no") or "") or (TRAIL_NO.search(t).group(0).strip(" .") if TRAIL_NO.search(t) else "")
                reg.append({"entry_id": f"{vol}-register-{page:03d}-E{i:03d}", "volume": vol, "page": str(page),
                            "line": str(i), "surname": r.get("surname", ""), "forename": r.get("forename", ""),
                            "civil_status": r.get("civil_status", ""), "occupation_raw": r.get("occupation", ""),
                            "building_no": no, "text": t})
            continue
        if sec != "gebaeude":
            continue
        cur = None
        for i, r in enumerate(entries, 1):
            h = str(r.get("house_no") or "").strip()
            street = (r.get("heading") or "").strip().rstrip(".:")
            if not h:
                cur = cur or last.get(vol)
                if cur is None:
                    continue
            elif cur is None or h != cur["building_no"] or cur["volume"] != vol:
                owner = text_of(r)
                sur = (r.get("surname") or "").strip()
                cur = {k: "" for k in B_FIELDS}
                cur.update({"building_id": f"{vol}-B-{len([b for b in bld if b['volume'] == vol]) + 1}",
                            "volume": vol, "page": str(page), "line": str(i), "building_no": h,
                            "building_nos": ",".join(map(str, numbers(h))) or h,
                            "marker": (r.get("marker") or "").strip(), "street_raw": street,
                            "owner_text": body({"text": owner}), "owner_surname": sur,
                            "owner_same_as_prev": "1" if DITTO.match(sur) else "",
                            "owner_entry": json.dumps({k: r.get(k) for k in ("surname", "alliance_name", "forename",
                                                                            "civil_status", "occupation", "origin")
                                                       if r.get(k)}, ensure_ascii=False),
                            "parse_confidence": "medium"})
                med, ns = MED.get((vol, page)), numbers(h)
                if med and ns and ns[0] < med - 100:
                    cur["note"] = f"Nummer unplausibel (Seitenmedian {med})"
                if DITTO.match(sur):
                    cur["building_type"] = (r.get("occupation") or r.get("forename") or "").strip()
                bld.append(cur)
                last[vol] = cur
            res.append(resident(r, vol, page, i, cur, "gebaeude"))
    return bld, res, reg, sections, nach


def merge_brackets(bld: list[dict], res: list[dict]) -> int:
    """Je Nummer ausgeschriebene Klammer-Einträge zu einem Gebäude zusammenziehen."""
    by_id = {}
    for r in res:
        by_id.setdefault(r["building_id"], []).append(r)
    keep, merged = [], 0
    for b in bld:
        p = keep[-1] if keep else None
        same = (p and p["volume"] == b["volume"] and p["owner_text"] == b["owner_text"]
                and len(by_id.get(b["building_id"], [])) == 1 and len(by_id.get(p["building_id"], [])) == 1)
        if same:
            pn, bn = numbers(p["building_nos"]), numbers(b["building_nos"])
            same = bool(pn and bn and bn[0] == pn[-1] + 1)
        if same:
            p["building_nos"] = ",".join(map(str, numbers(p["building_nos"]) + numbers(b["building_nos"])))
            p["building_no"] = f"{numbers(p['building_nos'])[0]}–{numbers(p['building_nos'])[-1]}"
            p["note"] = "Klammer zusammengeführt"
            for r in by_id.get(b["building_id"], []):
                r["_drop"] = True
            for r in by_id.get(p["building_id"], []):
                r["building_no"] = p["building_no"]
            merged += 1
            continue
        keep.append(b)
    bld[:] = keep
    res[:] = [r for r in res if not r.get("_drop")]
    return merged


def hausnumerierung(run: str) -> tuple[list[dict], dict]:
    rows, sections = [], {}
    prev = {}
    for vol, page, entries in load(run):
        sections[(vol, page)] = "gebaeude" if entries else "leer"
        for i, r in enumerate(entries, 1):
            sur = (r.get("surname") or "").strip()
            rec = {"row_id": f"{vol}-hn-{page:03d}-E{i:03d}", "volume": vol, "page": str(page), "line": str(i),
                   "new_no": str(r.get("new_no") or "").strip(), "surname": sur,
                   "alliance_name": (r.get("alliance_name") or "").strip(),
                   "forename": (r.get("forename") or "").strip(), "civil_status": (r.get("civil_status") or "").strip(),
                   "occupation_raw": (r.get("occupation") or "").strip(),
                   "building_type": (r.get("building") or "").strip(), "old_no": str(r.get("old_no") or "").strip(),
                   "heading": (r.get("heading") or "").strip(), "parse_confidence": "medium",
                   "text": (r.get("text") or "").strip()}
            rows.append(rec)
            prev = rec
    return rows, sections


def write(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"{path}: {len(rows)} Zeilen")


def update_pages(sections: dict) -> None:
    p = CSV_DIR / "01_pages.csv"
    with p.open(newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        fields, rows = rd.fieldnames, list(rd)
    n = 0
    for r in rows:
        s = sections.get((r["volume"], int(r["page"])))
        if s and not r["section"]:
            r["section"] = s
            r["typeface"] = r["typeface"] or ("antiqua" if r["volume"] == "1900" else "fraktur")
            n += 1
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"{p}: {n} Abschnitte ergänzt")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", default="gemini-frueh-v1")
    ap.add_argument("--run-1900", default="qwen-1900hn-v1")
    a = ap.parse_args()
    bld, res, reg, sections, nach = buildings(load(a.run))
    merged = merge_brackets(bld, res)
    print(f"Klammern zusammengeführt: {merged}")
    write(CSV_DIR / "05_buildings_frueh.csv", B_FIELDS, bld)
    write(CSV_DIR / "05_residents_frueh.csv", R_FIELDS, res)
    write(CSV_DIR / "05_register_frueh.csv", REG_FIELDS, reg)
    write(CSV_DIR / "05_nachtraege_frueh.csv", REG_FIELDS, nach)
    hn, sec_hn = hausnumerierung(a.run_1900)
    write(CSV_DIR / "05_hausnumerierung_1900.csv", HN_FIELDS, hn)
    update_pages({**sections, **sec_hn})


if __name__ == "__main__":
    main()
