"""09b_link_ptt.py — Telefonbuch-Einträge mit den Adressbuch-Einträgen verknüpfen (Agenda 7.1).

    python scripts/09b_link_ptt.py

Vier Telefon-Quellen, je mit eigener Kennung (`ptt_source`):
  AB  die Abonnentenverzeichnisse **in den Adressbüchern selbst** (1888 PDF 167–169,
      1892 PDF 178–181; Abschnitt `sonst` in 01_pages.csv), aus der Gemini-Lesung —
      Form «Name, Zusatz <Tab> Strasse Nr.», mit den alten Gebäudenummern
  A   PTT-Charge A (1889–1910, Seitentexte; `08_ptt_ingest.py`), nur Stellen mit direkt
      vorangehendem Namen — OCR mit Spaltenmischung, Qualität gering
  G   die mit Gemini aus den PTT-Scans gezogene Aarauer Liste (gemini-phonebook-analysis,
      Jahr noch zu bestimmen, alte Gebäudenummern)
  B   PTT-Charge B (1921–1935, Einträge mit Strasse und **neuer** Hausnummer)

Verknüpfung je Telefon-Eintrag und Adressbuch-Band über den Familiennamen (Pflicht),
dann absteigend: Gebäudenummer gleich (nur AB/A/G, altes Nummernsystem) → `adresse`;
Strasse gleich → `strasse`; Vorname/Initiale passt → `name`; Familienname im Band
eindeutig → `nachname`. Firmen (& Cie, A.-G., Bank …) werden gegen das Berufsregister
geprüft. Ausgabe:
  data/csv/09_ptt_entries.csv   ein Telefon-Eintrag je Zeile mit bester Verknüpfung je Band
  data/csv/09_links_ptt.csv     alle Kandidaten mit Tier und Score (für die Prüfung)
"""
from __future__ import annotations

import csv
import glob
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
norm_street = import_module("06_normalise").norm_street

CSV_DIR = Path("data/csv")
EXT = Path("data/ext/ptt")
GEMINI_CSV = EXT / "ptt_g_aarau_entries.csv"
FIRM_RE = re.compile(r"&|\bCie\b|\bCo\.|A\.-G\.|\bAG\b|Bank|Fabrik|Anstalt|Gesellschaft|Verein|Druckerei|Handlung|Brauerei|Hotel|Gebr", re.I)


def key(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = s.replace("ss", "s").replace("ck", "k").replace("th", "t").replace("y", "i")
    return re.sub(r"[^a-z]", "", s)


def split_name(name: str) -> tuple[str, str]:
    """«Gamper-Andres» → (gamper, andres); «Frey & Co.» → (frei, '')"""
    n = re.sub(r"^\d+\s*", "", name).strip(" .,")
    n = re.split(r"\s*[,(]", n)[0]
    if "-" in n and not FIRM_RE.search(n):
        a, b = n.split("-", 1)
        return key(a), key(b)
    return key(n.split()[0] if n else ""), ""


def street_no(s: str) -> tuple[str, str]:
    """«Bahnhofstrasse 39» → (Bahnhofstraße, 39) über die Strassennormalisierung"""
    s = (s or "").strip()
    m = re.match(r"^(?P<st>.+?)\s*(?P<no>\d{1,4}\s?[a-z]?)?\.?$", s)
    if not m:
        return "", ""
    st, no = m.group("st").strip(" ,."), (m.group("no") or "").replace(" ", "")
    st = st.replace("strasse", "straße").replace("Strasse", "Straße")
    sn, method = norm_street(st)
    return (sn if method == "rule" else st), no


# ── Quellen ───────────────────────────────────────────────────────────────

def load_in_book() -> list[dict]:
    """Telephon-Abonnenten in den Adressbüchern (Gemini-Lesung, Abschnitt sonst)."""
    meta = {}
    with (CSV_DIR / "01_pages.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            meta[f"{r['volume']}_p{int(r['page']):03d}"] = r
    out = []
    for jp in sorted(Path("data/atr/aarau-fraktur-gemini-v1/gemini-3.8-flash").glob("*.json")):
        m = meta.get(jp.stem)
        if not m or m["section"] != "sonst" or "Telephon" not in m["note"]:
            continue
        text = json.loads(jp.read_text(encoding="utf-8")).get("text") or ""
        prev_name = ""
        n = 0
        for line in text.split("\n"):
            line = line.replace("[tel]", "").strip()
            parts = re.split(r"\t+|\s{3,}", line)
            if len(parts) < 2:
                continue
            name, addr = parts[0].strip(" ,"), parts[-1].strip(" .")
            if name.startswith("„") or name in ("", "\""):
                name = prev_name
            else:
                prev_name = name
            if not re.search(r"\d", addr) and not addr:
                continue
            n += 1
            st, no = street_no(addr)
            out.append({"ptt_source": "AB", "ptt_id": f"AB-{m['volume']}-{int(m['page']):03d}-{n:03d}", "year": m["volume"],
                        "name_raw": name, "rest": "", "street_raw": addr, "street_norm": st, "no": no, "phone": "",
                        "numbering": "alt"})
    return out


def load_a() -> list[dict]:
    p = EXT / "ptt_a_aarau_entries.tsv"
    if not p.exists():
        return []
    out = []
    with p.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["address_confidence"] != "adjacent" or not r["name"] or len(r["name"]) > 40 or re.search(r"\d", r["name"]):
                continue
            sn, _ = norm_street(r["street"].replace("strasse", "straße"))
            out.append({"ptt_source": "A", "ptt_id": r["ptt_id"], "year": r["year"], "name_raw": r["name"], "rest": r["rest"],
                        "street_raw": f"{r['street']} {r['no']}".strip(), "street_norm": sn, "no": re.sub(r"[^0-9a-z]", "", r["no"].lower()), "phone": "", "numbering": "alt"})
    return out


def load_g() -> list[dict]:
    if not GEMINI_CSV.exists():
        return []
    out = []
    with GEMINI_CSV.open(encoding="utf-8") as fh:
        for i, r in enumerate(csv.DictReader(fh), start=1):
            name = (r.get("nachname") or r.get("nachname_oder_firmenname") or "").strip()
            if not name or r.get("ort") not in ("Aarau", ""):
                continue
            addr = (r.get("strasse") or "").strip()
            st, no = street_no(addr) if addr else ("", "")
            out.append({"ptt_source": "G", "ptt_id": f"G-{i:03d}", "year": "ca. 1898", "name_raw": name, "rest": ", ".join(x for x in (r.get("vorname", ""), r.get("weitere_angabe", "")) if x),
                        "street_raw": addr, "street_norm": st, "no": no, "phone": r.get("telefonnummer", ""), "numbering": "alt"})
    return out


def load_b() -> list[dict]:
    p = EXT / "ptt_b_aarau_entries.tsv"
    if not p.exists():
        return []
    out = []
    with p.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            st, no = street_no(r["Street"])
            out.append({"ptt_source": "B", "ptt_id": r["ptt_id"], "year": r["Year"], "name_raw": r["EntityName1"], "rest": ", ".join(x for x in (r["EntityName2"], r["Supplement"]) if x),
                        "street_raw": r["Street"], "street_norm": st, "no": no, "phone": r["PhoneNumber"], "numbering": "neu"})
    return out


# ── Adressbuch-Index ─────────────────────────────────────────────────────

def load_entries() -> dict[str, list[dict]]:
    by_vol: dict[str, list[dict]] = defaultdict(list)
    for f in sorted(glob.glob(str(CSV_DIR / "04_entries_*.csv")) + glob.glob(str(CSV_DIR / "04_berufe_*.csv"))):
        with open(f, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if not r.get("surname"):
                    continue
                sn, _ = norm_street(r.get("street_raw", ""))
                r["_sk"] = key(r["surname"]); r["_ak"] = key(r.get("alliance_name", "")); r["_fk"] = key(r.get("forename", ""))
                r["_st"] = sn; r["_no"] = re.sub(r"[^0-9a-z]", "", (r.get("building_no") or "").lower())
                r["_kind"] = "berufe" if "berufe" in f else "einwohner"
                by_vol[r["volume"]].append(r)
    return by_vol


def match(p: dict, rows: list[dict], index: dict[str, list[dict]]) -> tuple[dict | None, str, int]:
    sk, ak = split_name(p["name_raw"])
    if not sk:
        return None, "", 0
    cands = index.get(sk, [])
    if not cands:
        return None, "", 0
    fk = key((p["rest"].split(",")[0] if p["rest"] else "").split()[0] if p["rest"].strip() else "")
    best, tier, score = None, "", 0
    for c in cands:
        s = 1
        t = "nachname"
        if ak and c["_ak"] == ak:
            s += 2
        if p["numbering"] == "alt" and p["no"] and c["_no"] and p["no"] == c["_no"] and p["street_norm"] and c["_st"] == p["street_norm"]:
            s += 6; t = "adresse"
        elif p["street_norm"] and c["_st"] and c["_st"] == p["street_norm"]:
            s += 3; t = "strasse"
        if fk and c["_fk"] and (c["_fk"] == fk or c["_fk"][:1] == fk[:1]):
            s += 1
            if t == "nachname":
                t = "name"
        if s > score:
            best, tier, score = c, t, s
    if tier == "nachname" and len({c["entry_id"].rsplit("#", 1)[0] for c in cands}) > 1:
        return best, "nachname-mehrdeutig", score
    return best, tier, score


def main() -> None:
    ptt = load_in_book() + load_a() + load_g() + load_b()
    by_vol = load_entries()
    index = {v: defaultdict(list) for v in by_vol}
    for v, rows in by_vol.items():
        for r in rows:
            index[v][r["_sk"]].append(r)
    vols = sorted(by_vol)
    links, out = [], []
    for p in ptt:
        best_overall = None
        for v in vols:
            c, tier, score = match(p, by_vol[v], index[v])
            if c:
                links.append({"ptt_source": p["ptt_source"], "ptt_id": p["ptt_id"], "ptt_year": p["year"], "volume": v,
                              "entry_id": c["entry_id"], "kind": c["_kind"], "tier": tier, "score": score,
                              "ab_name": f"{c['surname']}{'-' + c['alliance_name'] if c.get('alliance_name') else ''}, {c.get('forename', '')}",
                              "ab_street": c.get("street_raw", ""), "ab_no": c.get("building_no", "")})
                if best_overall is None or score > best_overall["score"]:
                    best_overall = links[-1]
        row = dict(p)
        row.update({"best_volume": best_overall["volume"] if best_overall else "", "best_entry_id": best_overall["entry_id"] if best_overall else "",
                    "best_tier": best_overall["tier"] if best_overall else "kein", "best_score": best_overall["score"] if best_overall else 0,
                    "best_ab_name": best_overall["ab_name"] if best_overall else "", "best_ab_address": (best_overall["ab_street"] + " " + best_overall["ab_no"]).strip() if best_overall else "",
                    "volumes_matched": ";".join(l["volume"] for l in links if l["ptt_id"] == p["ptt_id"] and l["tier"] in ("adresse", "strasse", "name"))})
        out.append(row)
    fields = ["ptt_source", "ptt_id", "year", "name_raw", "rest", "street_raw", "street_norm", "no", "phone", "numbering",
              "best_volume", "best_entry_id", "best_tier", "best_score", "best_ab_name", "best_ab_address", "volumes_matched"]
    with (CSV_DIR / "09_ptt_entries.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(out)
    with (CSV_DIR / "09_links_ptt.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(links[0].keys()) if links else ["ptt_id"]); w.writeheader(); w.writerows(links)
    print(f"{len(out)} Telefon-Einträge, {len(links)} Kandidaten → 09_ptt_entries.csv, 09_links_ptt.csv")
    for src in ("AB", "A", "G", "B"):
        rows = [r for r in out if r["ptt_source"] == src]
        if rows:
            c = Counter(r["best_tier"] for r in rows)
            print(f"  {src:2} n={len(rows):5d}  " + "  ".join(f"{k}:{v}" for k, v in sorted(c.items(), key=lambda x: -x[1])))


if __name__ == "__main__":
    main()
