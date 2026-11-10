"""06_normalise.py — Normalisierungstabellen für Heimatorte und Strassen (Stufe 6).

    python scripts/06_normalise.py

Liest 04_entries_*.csv und 05_residents_*.csv und schreibt

  data/csv/06_origins.csv   eine Zeile je (origin_raw, origin_canton):
      origin_norm (Ortsname ohne Punkt, Zusatz, Abkürzung), canton_norm, country (CH/DE/FR/IT/AT/…),
      n (Vorkommen), geo_query (Vorschlag für die Geokodierung) + leere Geo-Spalten
  data/csv/06_streets.csv   eine Zeile je street_raw:
      street_norm (Abkürzungen aufgelöst, Artikel vereinheitlicht), n, geo_query + leere Geo-Spalten

Vorhandene Geo-Spalten (lat, lon, …) bleiben erhalten; handgesetzte Werte in den Spalten
`manual_*` haben Vorrang vor den Regeln. Die Regeln sind bewusst konservativ: was sie
nicht kennen, bleibt roh und wird mit `norm_method=raw` markiert.
"""
from __future__ import annotations

import csv
import glob
import re
from collections import Counter
from pathlib import Path

CSV_DIR = Path("data/csv")
ORIGINS = CSV_DIR / "06_origins.csv"
STREETS = CSV_DIR / "06_streets.csv"
ORIGIN_FIELDS = ["origin_raw", "origin_canton", "origin_norm", "canton_norm", "country", "n", "norm_method",
                 "geo_query", "lat", "lon", "osm_type", "osm_id", "display_name", "geo_confidence", "manual_lat", "manual_lon", "note"]
STREET_FIELDS = ["street_raw", "street_norm", "n", "norm_method", "geo_query", "lat", "lon", "osm_type", "osm_id",
                 "display_name", "geo_confidence", "manual_lat", "manual_lon", "note"]

CANTONS = {
    "aargau": ("Aargau", "CH"), "zürich": ("Zürich", "CH"), "zür.": ("Zürich", "CH"), "bern": ("Bern", "CH"),
    "luzern": ("Luzern", "CH"), "luz.": ("Luzern", "CH"), "uri": ("Uri", "CH"), "schwyz": ("Schwyz", "CH"),
    "obwalden": ("Obwalden", "CH"), "nidwalden": ("Nidwalden", "CH"), "unterwalden": ("Unterwalden", "CH"),
    "glarus": ("Glarus", "CH"), "zug": ("Zug", "CH"), "freiburg": ("Freiburg", "CH"), "solothurn": ("Solothurn", "CH"),
    "soloth.": ("Solothurn", "CH"), "sol.": ("Solothurn", "CH"), "basel": ("Basel", "CH"), "baselland": ("Basel-Landschaft", "CH"),
    "baselstadt": ("Basel-Stadt", "CH"), "schaffhausen": ("Schaffhausen", "CH"), "appenzell": ("Appenzell", "CH"),
    "st. gallen": ("St. Gallen", "CH"), "st.gallen": ("St. Gallen", "CH"), "graubünden": ("Graubünden", "CH"),
    "graub.": ("Graubünden", "CH"), "thurgau": ("Thurgau", "CH"), "thurg.": ("Thurgau", "CH"), "tessin": ("Tessin", "CH"),
    "waadt": ("Waadt", "CH"), "wallis": ("Wallis", "CH"), "neuenburg": ("Neuenburg", "CH"), "genf": ("Genf", "CH"),
    "baden": ("Baden", "DE"), "württemberg": ("Württemberg", "DE"), "würtemberg": ("Württemberg", "DE"),
    "würtemb.": ("Württemberg", "DE"), "wrtmb.": ("Württemberg", "DE"), "wrtbg.": ("Württemberg", "DE"),
    "bayern": ("Bayern", "DE"), "baiern": ("Bayern", "DE"), "preußen": ("Preussen", "DE"), "preussen": ("Preussen", "DE"),
    "sachsen": ("Sachsen", "DE"), "hessen": ("Hessen", "DE"), "hannover": ("Hannover", "DE"), "elsaß": ("Elsass", "FR"),
    "elsass": ("Elsass", "FR"), "tyrol": ("Tirol", "AT"), "tirol": ("Tirol", "AT"), "österreich": ("Österreich", "AT"),
    "italien": ("Italien", "IT"), "frankreich": ("Frankreich", "FR"), "england": ("England", "GB"),
    "deutschland": ("Deutschland", "DE"), "holland": ("Niederlande", "NL"), "belgien": ("Belgien", "BE"),
    "russland": ("Russland", "RU"), "amerika": ("Amerika", "US"), "unterwald.": ("Unterwalden", "CH"),
    "wrtmbg.": ("Württemberg", "DE"), "oesterreich": ("Österreich", "AT"), "hanover": ("Hannover", "DE"),
    "schwaben": ("Schwaben", "DE"), "nassau": ("Nassau", "DE"), "pfalz": ("Pfalz", "DE"), "savoyen": ("Savoyen", "FR"),
    "lothringen": ("Lothringen", "FR"), "piemont": ("Piemont", "IT"), "lombardei": ("Lombardei", "IT"), "vorarlberg": ("Vorarlberg", "AT"),
}
GRAND_DUCHY = re.compile(r"^(gr(o)?(ß|ss|s)?h(zgth|zgt|zth|zg|z)?\.?\s*|großh\.?\s*|grossh\.?\s*)", re.I)
COUNTRY_NAME = {"CH": "Schweiz", "DE": "Deutschland", "FR": "Frankreich", "IT": "Italien", "AT": "Österreich",
                "GB": "United Kingdom", "NL": "Niederlande", "BE": "Belgien", "RU": "Russland", "US": "USA"}

STREET_RULES = [
    (r"\bstr\.$", "straße"), (r"\bstr\.\s", "straße "), (r"str\.$", "straße"),
    (r"g\.$", "gasse"), (r"gaſſe", "gasse"), (r"=\s*gasse", "gasse"), (r"-\s*gasse", "gasse"),
    (r"^vorst\.?$", "Vorstadt"), (r"\bvorst\.", "Vorstadt"), (r"\bvorstdt\b", "Vorstadt"), (r"\bvst\.", "Vorstadt"),
    (r"^ob\.\s", "obere "), (r"^hinterer?\s+vorstadt$", "hintere Vorstadt"), (r"^jens\.\s*d\.\s*aare$", "jenseits der Aare"), (r"^vord\.\s", "vordere "), (r"^hint\.\s", "hintere "), (r"^v\.\s+vorstadt", "vordere Vorstadt"),
    (r"^h\.\s*d\.\s", "hinter dem "), (r"^hint\.\s*d\.\s", "hinter dem "), (r"^v\.\s*d\.\s", "vor dem "), (r"^vor\s*d\.\s", "vor dem "),
    (r"haldenth\.", "Haldenthor"), (r"haldenthor\.?$", "Haldenthor"), (r"^haldenthor$", "vor dem Haldenthor"),
    (r"^bahnh\.$", "Bahnhof"), (r"hinter dem bahnh\.", "hinter dem Bahnhof"),
    (r"^in\s+d(er|\.)\s+", "in der "), (r"^i\.\s*d\.\s+", "in der "), (r"^im\s+", "im "), (r"^in\s+der\s+telli$", "Telli"),
    (r"^in\s+der\s+gais$", "Gais"), (r"^im\s+hammer$", "Hammer"), (r"^im\s+weinberg$", "Weinberg"), (r"^in\s+der\s+", ""),
    (r"^n\.\s+quartier", "neues Quartier"), (r"^neues quartier$", "neues Quartier"),
    (r"^laurenzenv(or)?st\.?$", "Laurenzenvorstadt"), (r"^laurenzenthorg\.$", "Laurenzenthorgasse"), (r"^laurenzenth\.?g\.?$", "Laurenzenthorgasse"),
    (r"^golatten?m(att)?t?g\.$", "Golattenmattgasse"), (r"^golottenmattgasse$", "Golattenmattgasse"), (r"golattenmatt=?\s*gasse", "Golattenmattgasse"),
    (r"^rath+(aus)?g\.$", "Rathhausgasse"), (r"^rathg\.$", "Rathhausgasse"), (r"^rathhg\.$", "Rathhausgasse"), (r"^rathausgasse$", "Rathhausgasse"),
    (r"^mezgergasse$", "Metzgergasse"), (r"^metzgerg\.$", "Metzgergasse"), (r"^pelzg\.$", "Pelzgasse"), (r"^milchg\.$", "Milchgasse"),
    (r"^kroneng\.$", "Kronengasse"), (r"^kirchg\.$", "Kirchgasse"), (r"^kirchpl(z|\.)\.?$", "Kirchplatz"), (r"^schach\.$", "Schachen"),
    (r"^scheibensch\.$", "Scheibenschachen"), (r"^adelb\.$", "Adelbändli"), (r"^hald\.$", "Halden"), (r"^igelw\.$", "Igelweid"),
    (r"^casinostr", "Kasinostr"), (r"^conradstraße$", "Konradstraße"), (r"^gishübel$", "Gishügel"), (r"^zschokkestr", "Zschokkestr"),
    (r"^gollattenmattgasse$", "Golattenmattgasse"), (r"^gönhards?(f|s)eldweg$", "Gönhardfeldweg"), (r"^ziegelr\.$", "Ziegelrain"),
    (r"^ziegelrein$", "Ziegelrain"), (r"^laurenzenvorstadt$", "Laurenzenvorstadt"), (r"^laurenvorstadt$", "Laurenzenvorstadt"),
    (r"^jens\.\s+der\s+aare$", "jenseits der Aare"), (r"^hinter\s+d\.\s+bahnhof$", "hinter dem Bahnhof"), (r"^gißhügel$", "Gishügel"),
    (r"^bahnhofst\.$", "Bahnhofstraße"), (r"^oberevorstadt$", "obere Vorstadt"), (r"^vorderevorstadt$", "vordere Vorstadt"), (r"^hinterevorstadt$", "hintere Vorstadt"),
    (r"^rain$", "Rain"), (r"^rainstr(aße|\.)$", "Rainstraße"), (r"^bahnhofstr(aße|\.)$", "Bahnhofstraße"),
    (r"^schloßplatz$", "Schlossplatz"), (r"^schloßpl\.$", "Schlossplatz"), (r"^holzmarktpl\.$", "Holzmarktplatz"),
    (r"^jenseits\s+d(er|\.)\s+aare$", "jenseits der Aare"), (r"^hinter dem platz$", "hinter dem Platz"),
]


# Schreibvarianten desselben Orts (Lesung oder Druck), auf die im Band häufigere Form gebracht
ORIGIN_VARIANTS = {
    "Üken": "Ueken",          # 1899 «Üken», sonst «Ueken»; heute Herznach-Ueken AG (Nominatim fand Uken in Japan)
}


def norm_origin(raw: str, canton_raw: str) -> tuple[str, str, str, str]:
    """→ (origin_norm, canton_norm, country, method)"""
    s = raw.strip()
    s = re.split(r"\.\s+[A-ZÄÖÜ(]", s + " ")[0].strip()      # «Densbüren. Generalagentur …» → «Densbüren»
    s = re.sub(r"\s*[.,;:]+$", "", s).strip()
    s = re.sub(r"\s+", " ", s)
    method = "rule"
    canton_norm, country = "", ""
    c = canton_raw.strip().strip(".,").strip()
    m = re.match(r"^(?P<o>[^()]+?)\s*\((?P<c>[^)]+)\)\.?$", s)      # «Affoltern (Bern)» noch im Ortsnamen
    if m:
        s = m.group("o").strip()
        c = c or m.group("c").strip().strip(".,")
    s = re.sub(r"\s+(b\.|bei)\s+.*$", "", s)                       # «Buch bei Weinfelden» → «Buch»
    s = ORIGIN_VARIANTS.get(s, s)
    c2 = GRAND_DUCHY.sub("", c).strip()
    key = c2.lower().strip()
    if key in CANTONS:
        canton_norm, country = CANTONS[key]
    elif key + "." in CANTONS:
        canton_norm, country = CANTONS[key + "."]
    elif c:
        canton_norm, country, method = c2, "", "canton-unknown"
    # Ort selbst nennt ein Land/Kanton: «Basel», «Zürich», «Solothurn»
    if not canton_norm and s.lower() in CANTONS and CANTONS[s.lower()][1] == "CH":
        canton_norm, country = CANTONS[s.lower()]
    if not country:
        country = "CH"                       # Standardannahme: Schweizer Heimatort
    if not s:
        method = "empty"
    return s, canton_norm, country, method


def norm_street(raw: str) -> tuple[str, str]:
    s = raw.strip().strip(",;").strip()
    s = re.sub(r"\s+", " ", s)
    if not s or "„" in s or re.search(r"^(von|v\.)\s+(?!d\.)", s) or s.endswith("-") or s.endswith(" und"):
        return s, "raw"
    # Parserreste: «von Zürich Graben» → letztes Wort, wenn davor ein Heimatort steht
    low = s.lower()
    low = low.replace("strasse", "straße").replace("laurentzen", "laurenzen").replace(" thor", "thor")
    low = re.sub(r"=\s*", "", low)                      # «Vor= Stadt» → «vorstadt» (Trennstrich)
    for pat, rep in STREET_RULES:
        new = re.sub(pat, rep, low, flags=re.I)
        if new != low:
            low = new
    # Gross-/Kleinschreibung: Artikel klein, Namen gross
    words = low.split(" ")
    out = []
    for i, w in enumerate(words):
        if w in ("der", "dem", "in", "im", "vor", "hinter", "jenseits", "obere", "vordere", "hintere", "neues", "d.", "beim", "bei"):
            out.append(w)
        else:
            out.append(w[:1].upper() + w[1:])
    n = " ".join(out)
    n = n.replace("Straße", "straße").replace("Strasse", "strasse")
    return n, "rule"


def read_existing(path: Path, key_cols: list[str]) -> dict[tuple, dict]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        return {tuple(r[k] for k in key_cols): r for r in csv.DictReader(fh)}


def main() -> None:
    rows = []
    for f in sorted(glob.glob(str(CSV_DIR / "04_entries_*.csv")) + glob.glob(str(CSV_DIR / "05_residents_*.csv"))):
        with open(f, encoding="utf-8") as fh:
            rows.extend(csv.DictReader(fh))

    # ── Heimatorte ────────────────────────────────────────────────────────
    cnt = Counter((r["origin_raw"], r.get("origin_canton", "")) for r in rows if r.get("origin_raw"))
    old = read_existing(ORIGINS, ["origin_raw", "origin_canton"])
    out = []
    for (raw, canton), n in sorted(cnt.items(), key=lambda x: (-x[1], x[0])):
        o, cn, country, method = norm_origin(raw, canton)
        q = o + (f", {cn}" if cn else "") + f", {COUNTRY_NAME.get(country, country)}"
        rec = {k: "" for k in ORIGIN_FIELDS}
        prev = old.get((raw, canton), {})
        if prev and (prev.get("origin_norm"), prev.get("canton_norm")) != (o, cn):
            # Normform geändert → alte Geokodierung gilt nicht mehr (manuelle Koordinaten bleiben)
            prev = {k: v for k, v in prev.items() if k not in ("lat", "lon", "osm_type", "osm_id", "display_name", "geo_confidence")}
        rec.update(prev)
        rec.update({"origin_raw": raw, "origin_canton": canton, "origin_norm": o, "canton_norm": cn, "country": country,
                    "n": str(n), "norm_method": method, "geo_query": q})
        out.append(rec)
    with ORIGINS.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ORIGIN_FIELDS); w.writeheader(); w.writerows(out)
    print(f"{len(out)} Heimatorte (roh) → {ORIGINS}; normierte Orte: {len({(r['origin_norm'], r['canton_norm'], r['country']) for r in out})}")

    # ── Strassen ──────────────────────────────────────────────────────────
    cnt = Counter(r["street_raw"] for r in rows if r.get("street_raw"))
    old = read_existing(STREETS, ["street_raw"])
    out = []
    # Lesefehler unscharf an häufige Strassennamen angleichen («Ziegelnrain» → «Ziegelrain»)
    base = Counter()
    for raw, n in cnt.items():
        sn, m = norm_street(raw)
        if m == "rule":
            base[sn] += n
    known = [k for k, v in base.items() if v >= 15]
    import difflib
    for raw, n in sorted(cnt.items(), key=lambda x: (-x[1], x[0])):
        sn, method = norm_street(raw)
        if method == "rule":
            # an einen deutlich häufigeren, ähnlichen Namen angleichen (Lesefehler sind seltener als die richtige Form)
            bigger = [k for k in known if k != sn and base[k] >= 3 * base.get(sn, 0)]
            close = difflib.get_close_matches(sn, bigger, n=1, cutoff=0.86)
            if close:
                sn, method = close[0], "fuzzy"
        rec = {k: "" for k in STREET_FIELDS}
        rec.update(old.get((raw,), {}))
        rec.update({"street_raw": raw, "street_norm": sn, "n": str(n), "norm_method": method,
                    "geo_query": f"{sn}, Aarau, Schweiz" if method in ("rule", "fuzzy") else ""})
        out.append(rec)
    with STREETS.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=STREET_FIELDS); w.writeheader(); w.writerows(out)
    norms = Counter(r["street_norm"] for r in out if r["norm_method"] in ("rule", "fuzzy"))
    covered = sum(int(r["n"]) for r in out if r["norm_method"] in ("rule", "fuzzy"))
    print(f"{len(out)} Strassen (roh) → {STREETS}; normiert: {len(norms)} Namen, {covered} von {sum(cnt.values())} Zeilen")


if __name__ == "__main__":
    main()
