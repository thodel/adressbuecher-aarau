"""11_authorities.py — Personen der Adressbücher mit Wikidata, HLS und Metagrid verknüpfen.

    python scripts/11_authorities.py fetch      # Kandidaten aus Wikidata (SPARQL, Cache data/ext/wikidata/)
    python scripts/11_authorities.py link       # Abgleich → data/csv/10_authority_links.csv
    python scripts/11_authorities.py metagrid   # Metagrid-Konkordanz für Treffer mit HLS-Nummer

**Kandidaten.** Personen in Wikidata (Mensch, geboren 1790–1881, gestorben 1884 oder später
bzw. ohne Sterbedatum), die entweder einen Aarau-Bezug haben (Geburts-, Sterbe-, Wohn-,
Wirkungs- oder Heimatort Aarau) oder einen HLS-Eintrag (P902). Aus Wikidata kommen Vor- und
Familienname, Lebensdaten, HLS-Nummer, GND, Heimatort (P1321), Geburtsort, Berufe.

**Abgleich je Adressbuch-Eintrag** (Einwohner- und Gebäudeverzeichnis):
- Familienname gleich (normalisiert, Allianzname nicht), erster Vorname gleich oder als
  Initiale/Abkürzung verträglich (Hrch. ~ Heinrich), sonst kein Kandidat.
- Lebensdaten: die Person lebte im Bandjahr und war mindestens 18 (bei «Sohn»/«Tochter»
  mindestens 14); widersprechende Daten schliessen aus.
- Belege: Aarau-Bezug in Wikidata (+3), Heimatort des Eintrags = Heimat- oder Geburtsort in
  Wikidata (+3), Beruf passt (+1), voller Vorname statt Initiale (+1).
- `tier`: **wahrscheinlich** = Name + Lebensdaten + Aarau-Bezug oder Heimatort, und nur ein
  solcher Kandidat; **möglich** = Name + Lebensdaten + nur schwache Belege, oder mehrere
  gleich gute Kandidaten. Nur «wahrscheinlich» wird auf der Kontrollseite verlinkt.

Nachgeschärft nach dem Basler Befund (Präzision 78 % im ersten Durchgang): Mindestalter 21
(Ämter 25); Allianzname als Beleg (+2) bzw. Ausschluss bei Widerspruch; bei mehreren Kandidaten
braucht der beste einen weiteren Beleg (Allianzname, Beruf, Heimatort); je Person, Band und
Verzeichnis nur der beste Eintrag; HLS-Kopfangaben (Heimatort, Aarau erwähnt) als Belege und
Gegenprobe; Urteil der Artikelprüfung über den HLS-MCP aus 32_hls_check.csv (Spalte hls_check).
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

CSV_DIR = Path("data/csv")
EXT = Path("data/ext/wikidata")
OUT = CSV_DIR / "10_authority_links.csv"
UA = "adressbuecher-aarau/0.1 (https://github.com/thodel/adressbuecher-aarau)"
SPARQL = "https://query.wikidata.org/sparql"
AARAU = "Q14274"

WINDOW = "FILTER(YEAR(?b) >= 1790 && YEAR(?b) <= 1881 && (!BOUND(?d) || YEAR(?d) >= 1884))"
ID_QUERIES = {
    "aarau": "SELECT DISTINCT ?p WHERE { VALUES ?rel { wdt:P19 wdt:P20 wdt:P551 wdt:P937 wdt:P1321 } ?p ?rel wd:Q14274 . "
             "?p wdt:P31 wd:Q5; wdt:P569 ?b . OPTIONAL { ?p wdt:P570 ?d } " + WINDOW + " }",
    "hls": "SELECT DISTINCT ?p WHERE { ?p wdt:P902 ?h; wdt:P569 ?b . OPTIONAL { ?p wdt:P570 ?d } " + WINDOW + " }",
}
DETAIL = """SELECT ?p (SAMPLE(?lbl) AS ?label) (SAMPLE(?b) AS ?birth) (SAMPLE(?d) AS ?death) (SAMPLE(?hls) AS ?hls)
  (SAMPLE(?gnd) AS ?gnd) (GROUP_CONCAT(DISTINCT ?gn; separator="|") AS ?given) (GROUP_CONCAT(DISTINCT ?fn; separator="|") AS ?family)
  (GROUP_CONCAT(DISTINCT ?occ; separator="|") AS ?occupations) (GROUP_CONCAT(DISTINCT ?orig; separator="|") AS ?origins)
  (SAMPLE(?bpl) AS ?birthplace) (MAX(?aarau) AS ?aarau_rel) (SAMPLE(?desc) AS ?description)
WHERE {
  VALUES ?p { %s }
  OPTIONAL { ?p wdt:P569 ?b } OPTIONAL { ?p wdt:P570 ?d }
  OPTIONAL { ?p rdfs:label ?lbl FILTER(LANG(?lbl) = "de") }
  OPTIONAL { ?p schema:description ?desc FILTER(LANG(?desc) = "de") }
  OPTIONAL { ?p wdt:P902 ?hls } OPTIONAL { ?p wdt:P227 ?gnd }
  OPTIONAL { ?p wdt:P735 ?g . ?g rdfs:label ?gn FILTER(LANG(?gn) IN ("de","mul","en")) }
  OPTIONAL { ?p wdt:P734 ?f . ?f rdfs:label ?fn FILTER(LANG(?fn) IN ("de","mul","en")) }
  OPTIONAL { ?p wdt:P106 ?o . ?o rdfs:label ?occ FILTER(LANG(?occ) = "de") }
  OPTIONAL { ?p wdt:P1321 ?op . ?op rdfs:label ?orig FILTER(LANG(?orig) = "de") }
  OPTIONAL { ?p wdt:P19 ?bp . ?bp rdfs:label ?bpl FILTER(LANG(?bpl) = "de") }
  OPTIONAL { VALUES ?rel { wdt:P19 wdt:P20 wdt:P551 wdt:P937 wdt:P1321 } ?p ?rel wd:Q14274 . BIND(1 AS ?aarau) }
} GROUP BY ?p"""


def sparql(q: str) -> list[dict]:
    data = urllib.parse.urlencode({"query": q}).encode()
    req = urllib.request.Request(SPARQL, data=data, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        res = json.loads(r.read().decode("utf-8"))
    return [{k: v["value"] for k, v in b.items()} for b in res["results"]["bindings"]]


def fetch() -> None:
    EXT.mkdir(parents=True, exist_ok=True)
    for name, q in ID_QUERIES.items():
        out_p = EXT / f"candidates_{name}.json"
        if out_p.exists():
            print(f"{name}: vorhanden ({out_p})"); continue
        ids = sorted({r["p"].rsplit("/", 1)[-1] for r in sparql(q)})
        print(f"{name}: {len(ids)} Kennungen")
        rows = []
        for i in range(0, len(ids), 250):
            batch = " ".join(f"wd:{x}" for x in ids[i:i + 250])
            for attempt in range(3):
                try:
                    rows.extend(sparql(DETAIL % batch)); break
                except Exception as exc:  # noqa: BLE001
                    print(f"   ! Paket {i}: {exc}; neuer Versuch"); time.sleep(10)
            time.sleep(1.5)
            print(f"   {min(i + 250, len(ids))}/{len(ids)}", end="\r")
        out_p.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
        print(f"\n{name}: {len(rows)} Personen mit Angaben → {out_p}")


# ── Namen ────────────────────────────────────────────────────────────────

ABBR = {"hrch": "heinrich", "hch": "heinrich", "joh": "johann", "jb": "jakob", "jak": "jakob", "fr": "friedrich",
        "friedr": "friedrich", "gottl": "gottlieb", "gottfr": "gottfried", "rud": "rudolf", "sam": "samuel",
        "wilh": "wilhelm", "ed": "eduard", "alb": "albert", "jos": "josef", "ferd": "ferdinand", "herm": "hermann",
        "theod": "theodor", "carl": "karl", "ulr": "ulrich", "chr": "christian", "christ": "christian",
        "sl": "samuel", "abr": "abraham", "phil": "philipp", "aug": "august", "alfr": "alfred", "em": "emil",
        "gust": "gustav", "ad": "adolf", "conr": "konrad", "konr": "konrad", "max": "max", "jul": "julius"}


def nk(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = s.replace("ss", "s").replace("th", "t").replace("ck", "k").replace("y", "i").replace("ph", "f").replace("c", "k")
    return re.sub(r"[^a-z]", "", s)


def first_forename(s: str) -> tuple[str, bool]:
    """→ (Schlüssel, ist_voll); «Hrch.» → heinrich (voll=False), «J.» → j (Initiale)"""
    tok = (s or "").replace(",", " ").split()
    if not tok:
        return "", False
    t = tok[0].rstrip(".")
    low = t.lower()
    if low in ABBR:
        return nk(ABBR[low]), False
    full = not tok[0].endswith(".") and len(t) > 2
    return nk(t), full


def forename_ok(entry_fk: str, entry_full: bool, cand_given: list[str]) -> tuple[bool, bool]:
    """→ (passt, voll)"""
    for g in cand_given:
        gk = nk(g.split()[0]) if g else ""
        if not gk or not entry_fk:
            continue
        if entry_fk == gk:
            return True, True
        if not entry_full and (gk.startswith(entry_fk) or entry_fk.startswith(gk[:3])) and len(entry_fk) >= 1:
            return True, False
    return False, False


def cand_names(c: dict) -> tuple[list[str], list[str]]:
    given = [g for g in c.get("given", "").split("|") if g]
    family = [f for f in c.get("family", "").split("|") if f]
    lbl = c.get("label", "")
    if lbl and " " in lbl:
        parts = lbl.split()
        if not given:
            given = [parts[0]]
        family = family or [parts[-1]]
        family.append(parts[-1])
    return given, family


def year(s: str) -> int | None:
    m = re.match(r"^-?(\d{4})", s or "")
    return int(m.group(1)) if m else None


def load_candidates() -> list[dict]:
    seen, out = set(), []
    for f in sorted(EXT.glob("candidates_*.json")):
        for c in json.loads(f.read_text(encoding="utf-8")):
            q = c["p"].rsplit("/", 1)[-1]
            if q in seen:
                continue
            seen.add(q)
            c["qid"] = q
            c["by"], c["dy"] = year(c.get("birth", "")), year(c.get("death", ""))
            c["given_l"], c["family_l"] = cand_names(c)
            out.append(c)
    return out


def load_entries() -> list[dict]:
    rows = []
    for f in sorted(glob.glob(str(CSV_DIR / "04_entries_*.csv")) + glob.glob(str(CSV_DIR / "05_residents_*.csv"))):
        kind = "einwohner" if "04_entries" in f else "bewohner"
        with open(f, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("entry_type") == "firma" or not r.get("surname"):
                    continue
                if r.get("address_seq") not in (None, "", "1"):
                    continue
                r["_kind"] = kind
                rows.append(r)
    origins = {}
    p = CSV_DIR / "06_origins.csv"
    if p.exists():
        with p.open(encoding="utf-8") as fh:
            for o in csv.DictReader(fh):
                origins[(o["origin_raw"], o["origin_canton"])] = o["origin_norm"]
    for r in rows:
        r["_origin"] = origins.get((r.get("origin_raw", ""), r.get("origin_canton", "")), "")
    return rows


MANUAL = re.compile(r"taglöhner|knecht|schuster|schuhmacher|dienstmann|postcommis|arbeiter|wärter|haushälterin|magd|"
                    r"fabrikarb|näherin|glätterin|wäscherin|spetterin|ausläufer|handlanger|maurer|zimmermann|schneider|"
                    r"gehülfe|geselle|lehrling|kutscher|fuhrmann|heizer|portier|weibel|abwart|wirth\b|wirt\b|metzger", re.I)
ELITE = re.compile(r"politiker|professor|hochschul|ingenieur|architekt|unternehmer|industrieller|jurist|richter|arzt|"
                   r"mediziner|botaniker|zoologe|chemiker|physiker|historiker|offizier|general|oberst|schriftsteller|"
                   r"bankier|diplomat|theolog|philolog|nationalrat|ständerat|regierungsrat|fabrikant|landschaftsmaler|kunstmaler|bildhauer|komponist", re.I)
FEMALE = re.compile(r"witwe|wittwe|wwe\b|frau\b|fräulein|frl\.|tochter", re.I)


def is_female(r: dict) -> bool:
    occ = (r.get("occupation_raw") or "").split(",")[0].strip()
    return bool(FEMALE.search(" ".join([r.get("civil_status", ""), r.get("relation", "")])) or r.get("maiden_name")
                or re.search(r"(in|erin|innen)$", occ) and not re.search(r"(Kaufmann|Medizin)$", occ))


SENIOR = re.compile(r"oberricht|regierungsr|professor|direktor|pfarrer|fürsprech|notar|arzt|oberst|richter|präsident|rektor|staatsarchiv|ständerat|nationalrat|stadtammann|gemeindeammann", re.I)


def second_forename_conflict(entry_forename: str, cand_given: list[str], label: str) -> bool:
    """Beide nennen einen zweiten Vornamen, und er ist verschieden («Johann Jakob» / «Johann Ludwig»)."""
    et = [t for t in re.split(r"[\s,]+", entry_forename or "") if t and not t.endswith(".")]
    lt = [t for t in (label or "").split()[:-1]]
    if len(et) < 2 or len(lt) < 2:
        return False
    return nk(et[1]) != nk(lt[1]) and nk(et[1]) not in [nk(g) for g in cand_given]


def load_hls(hls_id: str) -> dict:
    p = Path("data/ext/hls") / f"{hls_id}.json"
    return json.loads(p.read_text(encoding="utf-8")) if hls_id and p.exists() else {}


def occ_match(entry_occ: str, cand_occ: str) -> bool:
    e = nk(entry_occ)
    for o in cand_occ.split("|"):
        ok = nk(o)
        if len(ok) >= 5 and (ok[:6] in e or (len(e) >= 5 and e[:6] in ok)):
            return True
    return False


def link() -> None:
    cands = load_candidates()
    by_fam: dict[str, list[dict]] = defaultdict(list)
    for c in cands:
        for f in set(nk(x) for x in c["family_l"]):
            if f:
                by_fam[f].append(c)
    rows = load_entries()
    out = []
    verdicts: dict = {}
    if (CSV_DIR / "32_hls_check.csv").exists():
        with (CSV_DIR / "32_hls_check.csv").open(encoding="utf-8") as fh:
            for v in csv.DictReader(fh):
                verdicts[(v["hls_article"], v.get("entry_id", ""))] = v

    def verdict_for(hls: str, entry_id: str) -> str:
        if not hls:
            return ""
        v = verdicts.get((hls, entry_id)) or verdicts.get((hls, ""))
        return v["verdict"] if v else ""
    for r in rows:
        fam = nk(r["surname"])
        pool = by_fam.get(fam, [])
        if not pool:
            continue
        fk, full = first_forename(r.get("forename", ""))
        if not fk:
            continue
        vol = int(r["volume"])
        min_age = 14 if r.get("relation") in ("Sohn", "Tochter") else 21
        scored = []
        for c in pool:
            ok, full_match = forename_ok(fk, full, c["given_l"])
            if not ok:
                continue
            if c["by"] is None or c["by"] > vol - min_age or (c["dy"] is not None and c["dy"] < vol):
                continue
            if second_forename_conflict(r.get("forename", ""), c["given_l"], c.get("label", "")):
                continue
            vd = verdict_for(c.get("hls", ""), r["entry_id"])
            if vd == "falsch":
                continue                       # am HLS-Artikel widerlegt
            confirmed = vd == "bestätigt"
            if not confirmed and SENIOR.search(r.get("occupation_raw", "") or "") and vol - c["by"] < 25:
                continue                       # Amt passt nicht zum Alter
            cand_occ = " ".join([c.get("occupations", ""), c.get("description", "")])
            if not confirmed and MANUAL.search(r.get("occupation_raw", "") or "") and ELITE.search(cand_occ):
                continue                       # Stand widerspricht (Taglöhner ↔ Professor, Politiker, Industrieller)
            if not confirmed and ELITE.search(cand_occ) and vol - c["by"] < 26 and not re.search(r"student|sohn", (r.get("occupation_raw", "") + r.get("relation", "")), re.I):
                continue                       # späterer Akademiker war im Bandjahr noch in Ausbildung → Vater/Namensvetter
            if not confirmed and is_female(r) and not FEMALE.search(c.get("description", "")) and not re.search(r"(a|e|ine|ette)$", (c["given_l"] or [""])[0]):
                continue                       # Eintrag einer Frau, Kandidat ein Mann
            ev, score = (["HLS-Artikel bestätigt"], 5) if confirmed else ([], 0)
            # Allianzname gegen den Doppelnamen im Wikidata-Label («Emma Coradi-Stahl»): Beleg oder Ausschluss
            al = nk(r.get("alliance_name", ""))
            lab = c.get("label", "")
            lab_all = nk(lab.split()[-1].split("-", 1)[1]) if lab and "-" in lab.split()[-1] else ""
            if al and lab_all:
                if al == lab_all:
                    ev.append("Allianzname"); score += 2
                else:
                    continue
            hf = load_hls(c.get("hls", ""))
            if hf.get("aarau_mentions", 0) > 0 and c.get("aarau_rel") != "1":
                ev.append("HLS nennt Aarau"); score += 1     # oft nur «Kantonsschule Aarau» → schwach
            # «Auw und Turgi», «Suhr u. Winterthur»: jeder genannte Ort zählt
            e_places = [nk(x) for x in re.split(r"\s+(?:und|u\.)\s+", r["_origin"]) if x.strip()] if r["_origin"] else []
            hls_places = [nk(x) for x in hf.get("origins", [])]
            if set(e_places) & set(hls_places):
                ev.append("HLS-Heimatort"); score += 3
            # Gegenprobe: Heimatort im Adressbuch widerspricht allen Heimatorten der Normdaten. Nur
            # Heimatorte (HLS, P1321), nicht der Geburtsort; nicht bei am Artikel bestätigten Personen,
            # denn das Bürgerrecht wechselte (Kurz 1888 «von Schwamendingen», später Aarau).
            known_places = [x for x in hls_places + [nk(x) for x in c.get("origins", "").split("|") if x] if x]
            if not confirmed and e_places and known_places and not set(e_places) & set(known_places) \
                    and nk("Aarau") not in known_places:
                continue
            # nur der Geburtsort ist bekannt und weicht ab: kein Ausschluss, aber kein «wahrscheinlich»
            bp_only = nk(re.sub(r"^Bezirk\s+", "", c.get("birthplace", "")))
            if (not confirmed and e_places and not known_places and bp_only and bp_only not in e_places
                    and bp_only != nk("Aarau")):
                ev.append("Geburtsort weicht ab")
            if c.get("aarau_rel") == "1":
                ev.append("Aarau-Bezug"); score += 3
            bp = nk(re.sub(r"^Bezirk\s+", "", c.get("birthplace", "")))
            if e_places and (set(e_places) & {nk(x) for x in c.get("origins", "").split("|") if x} or bp in e_places):
                ev.append("Heimatort"); score += 3
            if r.get("occupation_raw") and c.get("occupations") and occ_match(r["occupation_raw"], c["occupations"]):
                ev.append("Beruf"); score += 1
            if full_match:
                score += 1
            scored.append((score, ev, c, full_match or full))
        if not scored:
            continue
        scored.sort(key=lambda x: -x[0])
        best = scored[0]
        def is_strong(sc):
            e = set(sc[1])
            if "HLS-Artikel bestätigt" in e:
                return True
            if "Geburtsort weicht ab" in e:
                return False
            # Aarau-Bezug in Wikidata; oder Heimatort zusammen mit Beruf bzw. Allianzname
            return "Aarau-Bezug" in e or (({"Heimatort", "HLS-Heimatort"} & e) and ({"Beruf", "Allianzname"} & e))
        strong = [s for s in scored if is_strong(s)]
        extra = {"Allianzname", "Beruf", "Heimatort", "HLS-Heimatort"} & set(best[1])
        if (strong and len([s for s in strong if s[0] == strong[0][0]]) == 1 and best is strong[0]
                and (len(scored) == 1 or extra or "HLS-Artikel bestätigt" in best[1]) and (best[3] or "HLS-Artikel bestätigt" in best[1])):          # best[3]: voller Vorname, nicht nur Initiale
            tier = "wahrscheinlich"           # mehrere Kandidaten: nur mit weiterem Beleg (Namensvettern)
        else:
            tier = "möglich"
        c = best[2]
        out.append({"entry_id": r["entry_id"], "kind": r["_kind"], "volume": r["volume"], "surname": r["surname"],
                    "forename": r.get("forename", ""), "occupation": r.get("occupation_raw", ""), "origin": r["_origin"],
                    "qid": c["qid"], "label": c.get("label", ""), "birth": c["by"] or "", "death": c["dy"] or "",
                    "hls_id": c.get("hls", ""), "gnd": c.get("gnd", ""), "wd_description": c.get("description", ""),
                    "wd_occupations": c.get("occupations", "")[:120], "evidence": "+".join(best[1]) or "nur Name+Daten",
                    "score": best[0], "n_candidates": len(scored), "tier": tier,
                    "hls_origins": "; ".join(load_hls(c.get("hls", "")).get("origins", [])),
                    "hls_head": load_hls(c.get("hls", "")).get("head", "")})
    # je Person, Band und Verzeichnis nur der beste Eintrag «wahrscheinlich» (Väter/Söhne, Handwerker gleichen Namens)
    groups: dict = defaultdict(list)
    for o in out:
        if o["tier"] == "wahrscheinlich":
            groups[(o["qid"], o["volume"], o["kind"])].append(o)
    for grp in groups.values():
        if len(grp) > 1:
            grp.sort(key=lambda o: -int(o["score"]))
            for o in grp[1:]:
                o["tier"] = "möglich"; o["evidence"] += " (Namensvetter im Band)"
    # Urteil der Artikelprüfung über den HLS-MCP (32_hls_check.csv): falsch → verworfen, zweifelhaft → möglich
    chk = {}
    if (CSV_DIR / "32_hls_check.csv").exists():
        with (CSV_DIR / "32_hls_check.csv").open(encoding="utf-8") as fh:
            chk = {(r["hls_article"], r.get("entry_id", "")): r for r in csv.DictReader(fh)}
            chk.update({(k[0], ""): v for k, v in list(chk.items())})
    for o in out:
        h = o["hls_id"]
        v = (chk.get((h, o["entry_id"])) or chk.get((h, "")) or {}) if h else {}
        o["hls_check"] = (v.get("verdict", "") + ": " + v.get("note", "")) if v else ("ungeprüft" if h else "")
        if o["tier"] == "wahrscheinlich" and v.get("verdict") == "falsch":
            o["tier"] = "verworfen"
        elif o["tier"] == "wahrscheinlich" and v.get("verdict") == "zweifelhaft":
            o["tier"] = "möglich"
        elif o["tier"] == "wahrscheinlich" and h and not v:
            o["tier"] = "möglich"; o["evidence"] += " (HLS-Artikel noch nicht geprüft)"
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()) if out else ["entry_id"])
        w.writeheader(); w.writerows(out)
    c = Counter(x["tier"] for x in out)
    persons = len({x["qid"] for x in out if x["tier"] == "wahrscheinlich"})
    print(f"{len(rows)} Personen-Einträge geprüft, {len(cands)} Wikidata-Kandidaten → {len(out)} Treffer {dict(c)}; "
          f"{persons} verschiedene Personen «wahrscheinlich» → {OUT}")


HLS_DIR = Path("data/ext/hls")


def hls_facts(hls_id: str) -> dict | None:
    """Kopfangaben eines HLS-Artikels: Lebensdaten mit Orten, Heimatort(e), Aarau erwähnt.
    Gespeichert werden nur diese Angaben, nicht der Artikeltext."""
    HLS_DIR.mkdir(parents=True, exist_ok=True)
    p = HLS_DIR / f"{hls_id}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    url = f"https://hls-dhs-dss.ch/de/articles/{hls_id}/"
    import subprocess
    res = subprocess.run(["curl", "-sL", "-m", "30", "-A", UA, "-w", "\n%{http_code}", url], capture_output=True, text=True)
    html, _, code = res.stdout.rpartition("\n")
    time.sleep(float(__import__("os").environ.get("HLS_PAUSE", "1.5")))
    if code.strip() != "200":
        print(f"  ! HLS {hls_id}: HTTP {code.strip()}")
        return None
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    m = re.search(r"Autorin/Autor:[^0-9]{0,80}?(?P<head>(\d{1,2}\.\d{1,2}\.)?\d{4}[^.]{0,200}?,\s*(\d{1,2}\.\d{1,2}\.)?\d{4}[^.]{0,200}?)\.", text)
    head = m.group("head") if m else ""
    o = re.search(r"\bvon (?P<o>[A-ZÄÖÜ][\w-]+(?: \([^)]*\))?(?:(?:,| und) [A-ZÄÖÜ][\w-]+(?: \([^)]*\))?)*)\.", text[m.start():m.start() + 600] if m else "")
    origins = [x.strip() for x in re.split(r",| und ", o.group("o"))] if o else []
    body = text[m.start():] if m else text
    facts = {"hls_id": hls_id, "head": head[:200], "origins": [re.sub(r"\s*\(.*\)", "", x) for x in origins],
             "aarau_mentions": len(re.findall(r"\bAarau\b", body[:6000])), "url": url}
    p.write_text(json.dumps(facts, ensure_ascii=False), encoding="utf-8")
    return facts


def hlscheck() -> None:
    with OUT.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    ids = sorted({r["hls_id"] for r in rows if r["hls_id"]})
    done = 0
    for h in ids:
        if hls_facts(h) is not None:
            done += 1
    print(f"HLS-Kopfangaben für {done}/{len(ids)} Artikel in {HLS_DIR}")


def metagrid() -> None:
    with OUT.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    cache_p = EXT / "metagrid_cache.json"
    cache = json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.exists() else {}
    ids = sorted({r["hls_id"] for r in rows if r["tier"] == "wahrscheinlich" and r["hls_id"]})
    for h in ids:
        if h in cache:
            continue
        url = f"https://api.metagrid.ch/widget/hls-dhs-dss/person/{int(h)}.json?lang=de&include=true"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30) as r:
                data = json.loads(r.read().decode("utf-8"))
            links = {k: v["url"] for d in data for k, v in d.items()} if isinstance(data, list) else {}
        except Exception as exc:  # noqa: BLE001
            print(f"  ! {h}: {exc}"); links = None
        if links is not None:
            cache[h] = links
        time.sleep(0.5)
    cache_p.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
    for r in rows:
        r["metagrid"] = json.dumps(cache.get(r["hls_id"], {}), ensure_ascii=False) if r["hls_id"] else ""
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"Metagrid: {len(ids)} HLS-Nummern, {sum(1 for h in ids if cache.get(h))} mit Konkordanz")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["fetch", "link", "hlscheck", "metagrid"])
    a = ap.parse_args()
    {"fetch": fetch, "link": link, "hlscheck": hlscheck, "metagrid": metagrid}[a.cmd]()


if __name__ == "__main__":
    main()
