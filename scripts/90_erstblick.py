"""90_erstblick.py — Kontrollansicht der Welle-2-Daten als statische Seite (GitHub Pages).

    python scripts/90_erstblick.py --out web/index.html

Liest data/csv/04_entries_*.csv, 04_berufe_*.csv, 05_buildings_*.csv, 05_residents_*.csv
(was vorhanden ist) sowie data/review/flags.csv und bettet alles als JSON in eine Seite
mit Reitern, Volltextfilter, Bandfilter und **Flagging je Zeile** ein:

- Ein Flag (Grund + Notiz) wird im Browser gespeichert (localStorage) und als CSV
  exportiert (Download auf Pages; Zwischenablage, wo der Download gesperrt ist).
  `scripts/91_merge_flags.py` mischt den Export nach `data/review/flags.csv`; die Seite
  zeigt diese Flags beim nächsten Bau als «gemeldet».
- Je Zeile ein Link, der ein vorausgefülltes GitHub-Issue öffnet (Repo-URL unten).

Kein Server, keine externen Daten; die Seitenbilder sind aus Rechtsgründen nicht
enthalten (Herkunft Kantonsbibliothek Aargau, Nachnutzung ungeklärt).
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

CSV_DIR = Path("data/csv")
REVIEW = Path("data/review/flags.csv")
REPO_URL = "https://github.com/thodel/adressbuecher-aarau"

TABS = [
    ("einwohner", "Einwohner", ["04_entries_fraktur.csv", "04_entries_antiqua.csv"], "entry_id",
     ["entry_id", "volume", "page", "citizen_flag", "surname", "alliance_name", "maiden_name", "forename",
      "civil_status", "relation", "occupation_raw", "origin_raw", "origin_canton", "origin_norm", "street_raw", "street_norm",
      "building_no", "origin_place", "street_place", "address_role", "phone_flag", "telefon", "other_volume", "zeitreise", "entry_type", "parse_confidence", "authority", "residual", "text"]),
    ("gebaeude", "Gebäude", ["05_buildings_fraktur.csv", "05_buildings_antiqua.csv"], "building_id",
     ["building_id", "volume", "page", "building_nos", "marker", "street_raw", "owner_text", "building_type",
      "owner_same_as_prev", "phone_flag", "parse_confidence", "note"]),
    ("bewohner", "Bewohner", ["05_residents_fraktur.csv", "05_residents_antiqua.csv"], "entry_id",
     ["entry_id", "volume", "page", "building_no", "surname", "alliance_name", "maiden_name", "forename",
      "civil_status", "relation", "occupation_raw", "origin_raw", "origin_canton", "origin_norm", "street_norm",
      "parse_confidence", "authority", "residual", "text", "origin_place", "street_place"]),
    ("berufe", "Berufe", ["04_berufe_fraktur.csv", "04_berufe_antiqua.csv"], "entry_id",
     ["entry_id", "volume", "page", "heading", "surname", "alliance_name", "forename", "occupation_raw",
      "street_raw", "building_no", "origin_raw", "entry_type", "parse_confidence", "residual", "other_volume", "zeitreise", "text"]),
    ("telefon", "Telefon", ["09_ptt_entries.csv"], "ptt_id",
     ["ptt_id", "ptt_source", "year", "name_raw", "rest", "street_raw", "no", "phone", "numbering",
      "best_tier", "best_volume", "best_ab_name", "best_ab_address", "best_entry_id", "volumes_matched"]),
    ("normdaten", "Normdaten", ["10_authority_links.csv"], "entry_id",
     ["entry_id", "volume", "tier", "surname", "forename", "occupation", "origin", "label", "birth", "death",
      "evidence", "hls_origins", "hls_head", "wd_description", "qid", "hls_id", "n_candidates"]),
]

LABELS = {"telefon": "Telefonbuch", "other_volume": "Andere Bände", "zeitreise": "Karte damals", "entry_id": "ID", "building_id": "ID", "volume": "Band", "page": "PDF-S.", "citizen_flag": "Bürger *",
          "surname": "Name", "alliance_name": "Allianz", "maiden_name": "geb.", "forename": "Vorname",
          "civil_status": "Stand", "relation": "Bezug", "occupation_raw": "Beruf", "origin_raw": "Heimatort",
          "origin_canton": "Kt.", "origin_norm": "Heimatort (norm.)", "street_norm": "Strasse (norm.)", "origin_place": "Ort-Kennung", "street_place": "Strassen-Kennung", "authority": "Normdaten", "tier": "Stufe",
          "occupation": "Beruf", "origin": "Heimatort", "label": "Normdaten-Person", "birth": "geb.", "death": "gest.", "evidence": "Belege",
          "hls_origins": "HLS-Heimatort", "hls_head": "HLS-Kopf", "wd_description": "Wikidata-Beschreibung", "qid": "Wikidata", "hls_id": "HLS", "n_candidates": "Kandidaten", "street_raw": "Strasse", "building_no": "Nr.", "address_role": "Adressrolle",
          "phone_flag": "Tel.", "entry_type": "Typ", "parse_confidence": "Konfidenz", "residual": "Rest/Notiz",
          "text": "ATR-Zeile", "building_nos": "Nr.", "marker": "Marke", "owner_text": "Eigentümer",
          "building_type": "Gebäudeart", "owner_same_as_prev": "Ditto", "note": "Notiz", "heading": "Rubrik", "ptt_id": "ID", "ptt_source": "Quelle",
          "year": "Jahr", "name_raw": "Name (Telefonbuch)", "rest": "Zusatz", "no": "Nr.", "phone": "Telefon",
          "numbering": "Nummern", "best_tier": "Treffer", "best_volume": "Band", "best_ab_name": "Adressbuch-Name",
          "best_ab_address": "Adressbuch-Adresse", "best_entry_id": "Eintrag", "volumes_matched": "Bände"}

REASONS = ["ATR-Lesefehler", "Parser: Feld falsch", "Parser: Eintrag falsch getrennt", "Abschnitt/Rubrik falsch",
           "Quelle: Druckfehler", "Dublette", "Anderes"]


def _geo():
    import sys
    from importlib import import_module
    sys.path.insert(0, str(Path(__file__).parent))
    return import_module("10_geo")


def norm_tables() -> tuple[dict, dict]:
    """(origin_raw, origin_canton) → «Ort» bzw. «Ort, Kanton»; street_raw → street_norm.
    Dieselben Schlüssel wie in data/geo/*.geojson, damit die Karte exakt filtern kann."""
    origins, streets = {}, {}
    p = CSV_DIR / "06_origins.csv"
    if p.exists():
        with p.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r["origin_norm"]:
                    origins[(r["origin_raw"], r["origin_canton"])] = (
                        r["origin_norm"] + (f", {r['canton_norm']}" if r["canton_norm"] else ""),
                        _geo().place_key(r, r["origin_norm"]))
    p = CSV_DIR / "06_streets.csv"
    if p.exists():
        with p.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r["norm_method"] in ("rule", "fuzzy"):
                    streets[r["street_raw"]] = (r["street_norm"], _geo().place_key(r, r["street_norm"]))
    return origins, streets


ORIGINS, STREETS = norm_tables()


def authority_table() -> dict[str, str]:
    """entry_id → «QID|HLS|Label|Lebensdaten|Metagrid-JSON» für Treffer «wahrscheinlich»."""
    out = {}
    p = CSV_DIR / "10_authority_links.csv"
    if p.exists():
        with p.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r["tier"] == "wahrscheinlich":
                    out[r["entry_id"]] = "|".join([r["qid"], r["hls_id"], r["label"], f"{r['birth']}–{r['death']}", r.get("metagrid", "")])
    return out


AUTH = authority_table()


def lv95(lat: float, lon: float) -> tuple[int, int]:
    """WGS84 → LV95 (Näherung von swisstopo, auf ~1 m genau)."""
    p, l = (lat * 3600 - 169028.66) / 10000, (lon * 3600 - 26782.5) / 10000
    e = 2600072.37 + 211455.93 * l - 10938.51 * l * p - 0.36 * l * p * p - 44.54 * l ** 3
    n = 1200147.07 + 308807.95 * p + 3745.25 * l * l + 76.63 * p * p - 194.56 * l * l * p + 119.79 * p ** 3
    return round(e), round(n)


def load_links() -> tuple[dict, dict]:
    """web/telefon.csv (80_telefon.py) und web/baende.csv (81_baende.py) → je entry_id ein Zellwert."""
    phone, other = {}, {}
    if Path("web/telefon.csv").exists():
        for r in csv.DictReader(Path("web/telefon.csv").open(encoding="utf-8")):
            phone[r["entry_id"]] = "|".join(r[k].replace("|", "/") for k in ("how", "ptt_year", "ptt_name", "ptt_street", "ptt_phone", "entity_id", "image"))
    if Path("web/baende.csv").exists():
        by = {}
        for r in csv.DictReader(Path("web/baende.csv").open(encoding="utf-8")):
            by.setdefault(r["entry_id"], []).append(r)
        for k, rs in by.items():
            other[k] = ";;".join("|".join(x[f].replace("|", "/").replace(";;", ";") for f in ("other_volume", "tier", "other_id", "other_text", "evidence"))
                                 for x in sorted(rs, key=lambda x: x["other_volume"]))
    return phone, other


PHONE, OTHER = load_links()


def load_geo() -> dict:
    """gedruckte Strasse → (E, N) aus data/geo/streets.geojson (Punkt je Strasse mit allen Schreibweisen)."""
    out = {}
    p = Path("data/geo/streets.geojson")
    if p.exists():
        for f in json.loads(p.read_text(encoding="utf-8"))["features"]:
            lon, lat = f["geometry"]["coordinates"]
            for v in [f["properties"]["name"], *f["properties"].get("variants", [])]:
                out[v.strip(" “„\"")] = lv95(lat, lon)
    return out


GEO = load_geo()


def zeitreise(r: dict) -> str:
    g = GEO.get(r.get("street_raw", "").strip(" “„\"")) or GEO.get(r.get("street_norm", ""))
    return f"{g[0]},{g[1]},1" if g else "2645400,1249150,0"  # sonst Stadtmitte Aarau


def load(files: list[str], cols: list[str]) -> list[list[str]]:
    rows = []
    for f in files:
        p = CSV_DIR / f
        if not p.exists():
            continue
        with p.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                on, ok = ORIGINS.get((r.get("origin_raw", ""), r.get("origin_canton", "")), ("", "")) if r.get("origin_raw") else ("", "")
                sn, sk = STREETS.get(r.get("street_raw", ""), ("", "")) if r.get("street_raw") else ("", "")
                r["origin_norm"], r["origin_place"], r["street_norm"], r["street_place"] = on, ok, sn, sk
                r["authority"] = AUTH.get(r.get("entry_id", ""), "")
                r["telefon"] = PHONE.get(r.get("entry_id", ""), "")
                r["other_volume"] = OTHER.get(r.get("entry_id", ""), "")
                r["zeitreise"] = zeitreise(r) if "zeitreise" in cols else ""
                row = [r.get(c, "") for c in cols]
                if cols[0] == "entry_id" and r.get("address_seq") and r["address_seq"] not in ("", "1"):
                    row[0] = f"{row[0]}#{r['address_seq']}"
                rows.append(row)
    return rows


def load_flags() -> list[dict]:
    if not REVIEW.exists():
        return []
    with REVIEW.open(encoding="utf-8") as fh:
        return [{"table": r["table"], "id": r["id"], "reason": r["reason"], "note": r["note"],
                 "by": r.get("by", ""), "date": r.get("date", "")}
                for r in csv.DictReader(fh) if r.get("status", "open") != "fixed"]


TEMPLATE = r"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Aarau Adressdaten Kontrolle</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=Source+Code+Pro:wght@400;600&display=swap">
<style>
/* Layout: Werkzeug — Kopf mit Filtern und Flag-Leiste, darunter eine Tabelle, die den Rest füllt. */
:root {
  --bg: #f6f5f1; --paper: #ffffff; --fg: #1d2129; --muted: #5c6370; --line: #d9d7cf;
  --accent: #7a2e2e; --accent-soft: #f1e3e1; --ok: #2f6f4e; --warn: #9a6b11; --bad: #a33a2a; --flag: #fff3c4;
  --font-body: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --font-data: "Source Code Pro", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #15171b; --paper: #1d2026; --fg: #e8e6df; --muted: #a39f94; --line: #353942;
  --accent: #d08a84; --accent-soft: #3a2626; --ok: #7fc39d; --warn: #d9b35a; --bad: #e08a79; --flag: #3b3418; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #15171b; --paper: #1d2026; --fg: #e8e6df; --muted: #a39f94; --line: #353942;
  --accent: #d08a84; --accent-soft: #3a2626; --ok: #7fc39d; --warn: #d9b35a; --bad: #e08a79; --flag: #3b3418; color-scheme: dark }
[hidden] { display: none !important; }
html, body { height: 100%; }
body { background: var(--bg); color: var(--fg); font-family: var(--font-body); font-size: 15px; line-height: 1.4;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 16px; display: flex; flex-direction: column; gap: 10px; box-sizing: border-box; margin: 0; }
header { display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 20px; }
.nav { font-size: 0.9rem; color: var(--muted); }
td a { color: var(--accent); }
.nav a { color: var(--accent); font-weight: 600; text-decoration: none; }
.nav a:hover, .nav a:focus-visible { text-decoration: underline; }
h1 { font-size: 1.3rem; margin: 0; font-weight: 700; letter-spacing: -0.01em; text-wrap: balance; }
.sub { color: var(--muted); font-size: 0.88rem; margin: 0; }
.sub a { color: var(--accent); }
.toolbar { display: flex; flex-wrap: wrap; gap: 8px 12px; align-items: center; }
.tabs { display: flex; gap: 4px; flex-wrap: wrap; }
button { font: inherit; cursor: pointer; }
.tabs button { font-weight: 600; background: transparent; color: var(--muted); border: 1px solid var(--line); border-radius: 999px; padding: 4px 12px; }
.tabs button[aria-selected="true"] { background: var(--accent); border-color: var(--accent); color: #fff; }
button:focus-visible, input:focus-visible, select:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
input[type="search"], select, input[type="text"] { font: inherit; padding: 5px 9px; border: 1px solid var(--line); border-radius: 6px; background: var(--paper); color: var(--fg); min-width: 0; }
input[type="search"] { flex: 1 1 220px; }
.chip { display: inline-flex; gap: 6px; align-items: center; background: var(--accent-soft); border: 1px solid var(--accent); border-radius: 999px; padding: 2px 4px 2px 10px; font-size: 0.88rem; }
.chip button { border: 0; background: transparent; color: var(--accent); font-weight: 700; padding: 0 6px; cursor: pointer; }
.chip .tabhit { text-decoration: underline; font-weight: 600; }
.count { color: var(--muted); font-variant-numeric: tabular-nums; font-size: 0.9rem; }
.flagbar { display: flex; flex-wrap: wrap; gap: 8px 12px; align-items: center; padding: 8px 12px; border: 1px solid var(--line); border-radius: 8px; background: var(--paper); font-size: 0.9rem; }
.flagbar .n { font-weight: 700; color: var(--accent); font-variant-numeric: tabular-nums; }
.btn { border: 1px solid var(--line); background: var(--paper); color: var(--fg); border-radius: 6px; padding: 4px 10px; }
.btn.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
.wrap { flex: 1 1 auto; min-height: 0; overflow: auto; border: 1px solid var(--line); border-radius: 8px; background: var(--paper); }
table { border-collapse: collapse; width: max-content; min-width: 100%; font-size: 13.5px; }
th, td { text-align: left; padding: 4px 8px; border-bottom: 1px solid var(--line); vertical-align: top; white-space: nowrap; max-width: 32ch; overflow: hidden; text-overflow: ellipsis; }
td.wide { white-space: normal; max-width: 48ch; }
th { position: sticky; top: 0; background: var(--paper); font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); z-index: 1; }
td.num, td.id { font-family: var(--font-data); font-variant-numeric: tabular-nums; font-size: 12.5px; }
tr.flagged td { background: var(--flag); }
tr.reported td:first-child::before { content: "✓ "; color: var(--ok); font-weight: 700; }
.pill { display: inline-block; border-radius: 999px; padding: 0 8px; font-size: 0.74rem; font-weight: 600; line-height: 1.5; }
.pill.high { background: color-mix(in srgb, var(--ok) 18%, transparent); color: var(--ok); }
.pill.medium { background: color-mix(in srgb, var(--warn) 18%, transparent); color: var(--warn); }
.pill.review { background: color-mix(in srgb, var(--bad) 18%, transparent); color: var(--bad); }
a.ov { margin-right: 4px; color: var(--muted); }
a.ov.hi { color: var(--accent); font-weight: 600; }
.star { color: var(--accent); font-weight: 700; }
td.act { white-space: nowrap; }
td.act select, td.act input { font-size: 12.5px; padding: 2px 5px; }
td.act input[type="text"] { width: 14ch; }
td.act a { color: var(--muted); font-size: 12px; margin-left: 6px; }
.more { display: block; width: 100%; padding: 8px; background: var(--accent-soft); color: var(--fg); border: 0; }
.legend { color: var(--muted); font-size: 0.84rem; margin: 0; }
.legend b { color: var(--fg); }
#toast { position: fixed; bottom: calc(12px + env(safe-area-inset-bottom, 0px)); right: calc(12px + env(safe-area-inset-right, 0px)); background: var(--fg); color: var(--bg); padding: 8px 14px; border-radius: 8px; font-size: 0.9rem; }
@media (max-width: 600px) { body { font-size: 14px; } th, td { max-width: 22ch; } td.act input[type="text"] { width: 9ch; } }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
<header>
  <nav class="nav"><a href="./">Kontrolle</a> · <a href="karte.html">Karte: Einzugsgebiet und Wohnorte</a> · <a href="https://thodel.github.io/adressbuecher-basel/">Adressbücher Basel</a> · <a href="https://github.com/thodel/adressbuecher-aarau">Repo</a></nav>
  <h1>Adressbücher Aarau: Kontrolle der Datensätze</h1>
  <p class="sub">Stand __DATE__ · Rohdaten aus der ATR-Lesung, regelbasiert geparst, ohne Normalisierung. Fehler hier markieren; die Flags gehen per CSV oder Issue ins Repo.</p>
</header>
<div class="toolbar">
  <div class="tabs" role="tablist" id="tabs"></div>
  <select id="vol" aria-label="Band"><option value="">alle Bände</option></select>
  <select id="conf" aria-label="Konfidenz"><option value="">alle Konfidenzen</option><option value="high">high</option><option value="medium">medium</option><option value="review">review</option></select>
  <label><input type="checkbox" id="onlyflag"> nur markierte</label>
  <span id="colfilter" class="chip" hidden></span>
  <input id="q" type="search" placeholder="Suchen: Name, Beruf, Strasse, Heimatort, ID …" aria-label="Suchen">
  <span class="count" id="count"></span>
</div>
<div class="flagbar">
  <span><span class="n" id="nflags">0</span> Flags in diesem Browser · <span id="nreported">0</span> bereits im Repo gemeldet</span>
  <button class="btn primary" id="dl">Flags als CSV herunterladen</button>
  <button class="btn" id="copy">CSV in die Zwischenablage</button>
  <button class="btn" id="clear">Flags löschen</button>
  <span class="sub">Danach: <code>python scripts/91_merge_flags.py &lt;datei.csv&gt;</code> und committen.</span>
</div>
<p class="legend"><b>Bürger *</b> = Stern im Einwohnerverzeichnis (Bürgerrecht Aarau) · <b>Marke</b> im Gebäudeverzeichnis: * Eigentümer wohnt im Haus, † Nebengebäude · <b>Konfidenz</b>: high = Zeile ging vollständig auf, medium = Hinweis in Rest/Notiz, review = nicht zuordenbar · <b>Telefonbuch</b>: Eintrag mit ☏ → passender Eintrag im PTT-Telefonbuch (Link auf die Person bei Vernetzte Schweiz und aufs Seitenbild) · <b>Andere Bände</b>: dieselbe Person in den anderen Bänden (automatisch; fett = sicher) · <b>Karte damals</b>: historische Karte des Jahres bei swisstopo an der Strasse · <b>✓</b> = Flag schon im Repo · <b>Telefon</b>: Quelle AB = Abonnentenliste im Adressbuch, A = PTT-Telefonbuch 1889–1910 (OCR), G = PTT-Telefonbuch (Gemini, ca. 1898), B = PTT 1921–1935 (neue Hausnummern); Treffer «adresse» = Name + Strasse + Gebäudenummer, «strasse» = Name + Strasse, «name» = Name + Vorname, «nachname» = nur Familienname.</p>
<div class="wrap"><table id="t"><thead></thead><tbody></tbody></table><button class="more" id="more" hidden>weitere Zeilen zeigen</button></div>
<div id="toast" hidden></div>
<script>
const DATA = __DATA__;
const LABELS = __LABELS__;
const REASONS = __REASONS__;
const HOW = {nummer: 'gleiche Telefonnummer und Familienname', sicher: 'Vernetzte Schweiz: sicher', wahrscheinlich: 'Vernetzte Schweiz: wahrscheinlich', möglich: 'Vernetzte Schweiz: möglich (nur Name)', name: 'einzige Person dieses Namens und Vornamens im Telefonbuch'};
const REPORTED = __REPORTED__;
const REPO = "__REPO__";
const PAGE = 300;
const KEY = 'aarau.flags.v1';
const P = new URLSearchParams(location.search);
let tab = P.get('tab') && DATA[P.get('tab')] ? P.get('tab') : ((location.hash.replace('#','') in DATA) ? location.hash.replace('#','') : Object.keys(DATA)[0]);
let colF = P.get('col') || '', valF = P.get('val') || '', labelF = P.get('label') || '';
let shown = PAGE;
let flags = {};
try { flags = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { flags = {}; }
const reported = {}; for (const f of REPORTED) reported[f.table + '|' + f.id] = f;
const $ = id => document.getElementById(id);
const tabsEl = $('tabs'), q = $('q'), vol = $('vol'), conf = $('conf'), onlyflag = $('onlyflag');
const thead = document.querySelector('#t thead'), tbody = document.querySelector('#t tbody'), more = $('more'), count = $('count');
const vols = new Set(); for (const k in DATA) for (const r of DATA[k].rows) vols.add(r[1]);
[...vols].sort().forEach(v => { const o = document.createElement('option'); o.value = v; o.textContent = v; vol.appendChild(o); });
for (const k in DATA) { const b = document.createElement('button'); b.setAttribute('role', 'tab'); b.textContent = `${DATA[k].label} (${DATA[k].rows.length.toLocaleString('de-CH')})`; b.dataset.k = k; b.onclick = () => { tab = k; shown = PAGE; render(); }; tabsEl.appendChild(b); }
function esc(s) { return String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function save() { try { localStorage.setItem(KEY, JSON.stringify(flags)); } catch (e) {} }
function toast(msg) { const t = $('toast'); t.textContent = msg; t.hidden = false; setTimeout(() => { t.hidden = true; }, 2500); }
function issueUrl(k, r) {
  const d = DATA[k], id = r[0];
  const body = `Tabelle: ${d.label}\nID: ${id}\nBand ${r[1]}, PDF-Seite ${r[2]}\n\nATR-Zeile:\n${r[d.cols.indexOf('text')] ?? r[d.cols.indexOf('owner_text')] ?? ''}\n\nProblem:\n`;
  return `${REPO}/issues/new?title=${encodeURIComponent('Flag ' + id)}&labels=${encodeURIComponent('review')}&body=${encodeURIComponent(body)}`;
}
function authLinks(v) {
  if (!v) return '';
  const parts = v.split('|'); const [qid, hls, label, life] = parts; const mg = parts.slice(4).join('|');
  let html = `<a href="https://www.wikidata.org/wiki/${esc(qid)}" target="_blank" rel="noopener" title="${esc(label)} ${esc(life)}">${esc(label || qid)}</a> <small>${esc(life)}</small>`;
  if (hls) html += ` · <a href="https://hls-dhs-dss.ch/de/articles/${esc(hls)}/" target="_blank" rel="noopener">HLS</a>`;
  let links = {}; try { links = mg ? JSON.parse(mg) : {}; } catch (e) { links = {}; }
  const extra = Object.entries(links).filter(([k]) => !/^(HLS|Wikidata|DHS|DSS)$/i.test(k)).slice(0, 6);
  if (extra.length) html += ' · <small>Metagrid: ' + extra.map(([k, u]) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(k)}</a>`).join(', ') + '</small>';
  return html;
}
function cell(k, col, v, r) {
  if (col === 'telefon') {
    if (!v) return r[DATA[k].cols.indexOf('phone_flag')] === '1' ? '<td class="sub">nicht gefunden</td>' : '<td></td>';
    const [how, year, name, st, phone, eid, img] = v.split('|');
    const tip = `Telefonbuch ${year}: ${name}${st ? ', ' + st : ''}${phone ? ', Nr. ' + phone : ''} · Zuordnung: ${HOW[how] || how}`;
    const main = eid ? `<a href="https://thodel.github.io/vernetzte-schweiz/#/e/${esc(eid)}" target="_blank" rel="noopener" title="${esc(tip)}">${esc(year)}${phone ? ' · Nr. ' + esc(phone) : ''}</a>` : `<span title="${esc(tip)}">${esc(year)}</span>`;
    return `<td>${main}${img ? ` · <a href="${esc(img)}" target="_blank" rel="noopener" title="Seite im Telefonbuch (PTT-Archiv)">Bild</a>` : ''} <span class="pill ${how === 'nummer' || how === 'sicher' ? 'high' : 'medium'}" title="${esc(HOW[how] || how)}">${esc(how)}</span></td>`;
  }
  if (col === 'other_volume') {
    if (!v) return '<td></td>';
    return '<td>' + v.split(';;').map(x => { const [ov, tier, oid, otext, ev] = x.split('|');
      return `<a href="?tab=einwohner&vol=${esc(ov)}&q=${encodeURIComponent(oid.split('#')[0])}" title="${esc(otext + ' · ' + tier + ' · ' + ev)}" class="ov ${tier === 'sicher' ? 'hi' : ''}">${esc(ov)}</a>`; }).join(' ') + '</td>';
  }
  if (col === 'zeitreise') {
    if (!v) return '<td></td>';
    const [e, n, prec] = v.split(',');
    const what = prec === '2' ? 'Haus' : prec === '1' ? 'Strasse' : 'Stadt';
    return `<td><a href="https://map.geo.admin.ch/#/map?lang=de&center=${e},${n}&z=${prec === '0' ? 9 : 11}&crosshair=marker&bgLayer=void&layers=ch.swisstopo.zeitreihen@year=${esc(r[1])}" target="_blank" rel="noopener" title="${what} auf der historischen Karte um ${esc(r[1])} (swisstopo Zeitreise; vor 1870 Dufourkarte)">${what} ${esc(r[1])} ↗</a></td>`;
  }
  if (col === 'authority') return `<td class="wide">${authLinks(v)}</td>`;
  if (col === 'qid' && v) return `<td><a href="https://www.wikidata.org/wiki/${esc(v)}" target="_blank" rel="noopener">${esc(v)}</a></td>`;
  if (col === 'hls_id' && v) return `<td><a href="https://hls-dhs-dss.ch/de/articles/${esc(v)}/" target="_blank" rel="noopener">${esc(v)}</a></td>`;
  if (col === 'tier') return `<td><span class="pill ${v === 'wahrscheinlich' ? 'high' : 'medium'}">${esc(v)}</span></td>`;
  if (col === 'parse_confidence') return `<td><span class="pill ${esc(v)}">${esc(v)}</span></td>`;
  if (col === 'citizen_flag' || col === 'phone_flag' || col === 'owner_same_as_prev') return `<td class="num">${v === '1' ? '<span class="star">' + (col === 'citizen_flag' ? '*' : col === 'phone_flag' ? '☏' : '„') + '</span>' : ''}</td>`;
  if (col === 'marker') return `<td class="num star">${esc(v)}</td>`;
  if (col === 'entry_id' || col === 'building_id') return `<td class="id">${esc(v)}</td>`;
  if (['page','building_no','building_nos','volume'].includes(col)) return `<td class="num">${esc(v)}</td>`;
  if (['residual','note','owner_text','occupation_raw','text'].includes(col)) return `<td class="wide">${esc(v)}</td>`;
  return `<td>${esc(v)}</td>`;
}
function actCell(k, r) {
  const key = k + '|' + r[0], f = flags[key] || {};
  const opts = ['<option value="">— Flag —</option>'].concat(REASONS.map(x => `<option value="${esc(x)}" ${f.reason === x ? 'selected' : ''}>${esc(x)}</option>`)).join('');
  return `<td class="act"><select data-key="${esc(key)}" data-f="reason" aria-label="Grund">${opts}</select> <input type="text" data-key="${esc(key)}" data-f="note" placeholder="Notiz" value="${esc(f.note || '')}" aria-label="Notiz"><a href="${issueUrl(k, r)}" target="_blank" rel="noopener">Issue</a></td>`;
}
function render() {
  for (const b of tabsEl.children) b.setAttribute('aria-selected', b.dataset.k === tab);
  const d = DATA[tab], needle = q.value.trim().toLowerCase(), v = vol.value, c = conf.value, ci = d.cols.indexOf('parse_confidence');
  const fi = colF ? d.cols.indexOf(colF) : -1;
  const chip = $('colfilter');
  if (colF && valF) {
    const hits = Object.keys(DATA).map(k => { const j = DATA[k].cols.indexOf(colF); return [k, j < 0 ? 0 : DATA[k].rows.filter(r => r[j] === valF && (!vol.value || r[1] === vol.value)).length]; }).filter(([k, n]) => n > 0);
    const shownLabel = labelF || valF;
    const other = hits.filter(([k]) => k !== tab).map(([k, n]) => `<button type="button" class="tabhit" data-k="${k}">${esc(DATA[k].label)}: ${n}</button>`).join('');
    chip.hidden = false;
    chip.innerHTML = `${esc(labelF ? 'Ort' : (LABELS[colF] || colF))} = <b>${esc(shownLabel)}</b>${other ? ' · Treffer auch in ' + other : ''}<button type="button" id="clearcol" aria-label="Filter entfernen">✕</button>`;
    $('clearcol').onclick = () => { colF = valF = labelF = ''; history.replaceState(null, '', location.pathname); shown = PAGE; render(); };
    for (const b of chip.querySelectorAll('.tabhit')) b.onclick = () => { tab = b.dataset.k; shown = PAGE; render(); };
  }
  else { chip.hidden = true; }
  const rows = d.rows.filter(r => (!v || r[1] === v) && (!c || r[ci] === c) && (!colF || !valF || fi < 0 || r[fi] === valF) && (!onlyflag.checked || flags[tab + '|' + r[0]] || reported[tab + '|' + r[0]]) && (!needle || r.filter((_, i) => d.cols[i] !== 'other_volume').join(' ').toLowerCase().includes(needle)));
  thead.innerHTML = '<tr><th>Flag</th>' + d.cols.map(cc => `<th>${esc(LABELS[cc] || cc)}</th>`).join('') + '</tr>';
  tbody.innerHTML = rows.slice(0, shown).map(r => {
    const key = tab + '|' + r[0];
    const cls = (flags[key] && flags[key].reason ? 'flagged ' : '') + (reported[key] ? 'reported' : '');
    return `<tr class="${cls}" title="${reported[key] ? esc('gemeldet: ' + reported[key].reason + ' ' + reported[key].note) : ''}">${actCell(tab, r)}${r.map((vv, i) => cell(tab, d.cols[i], vv, r)).join('')}</tr>`;
  }).join('');
  more.hidden = rows.length <= shown;
  count.textContent = `${Math.min(shown, rows.length).toLocaleString('de-CH')} von ${rows.length.toLocaleString('de-CH')} Zeilen`;
  $('nflags').textContent = Object.values(flags).filter(f => f.reason).length;
  $('nreported').textContent = REPORTED.length;
  try { localStorage.setItem('aarau.tab', tab); } catch (e) {}
}
tbody.addEventListener('change', e => {
  const el = e.target, key = el.dataset.key; if (!key) return;
  flags[key] = flags[key] || {}; flags[key][el.dataset.f] = el.value;
  if (!flags[key].reason && !flags[key].note) delete flags[key];
  save(); const tr = el.closest('tr'); tr.classList.toggle('flagged', !!(flags[key] && flags[key].reason)); $('nflags').textContent = Object.values(flags).filter(f => f.reason).length;
});
function flagsCsv() {
  const q2 = s => '"' + String(s ?? '').replace(/"/g, '""') + '"';
  const lines = ['table,id,reason,note,by,date'];
  const today = new Date().toISOString().slice(0, 10);
  for (const key in flags) { const f = flags[key]; if (!f.reason) continue; const [t, id] = key.split('|'); lines.push([t, id, f.reason, f.note || '', '', today].map(q2).join(',')); }
  return lines.join('\n') + '\n';
}
$('dl').onclick = () => {
  const blob = new Blob(['﻿' + flagsCsv()], { type: 'text/csv;charset=utf-8' });
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `flags_${new Date().toISOString().slice(0, 10)}.csv`; document.body.appendChild(a); a.click(); a.remove();
  toast('CSV wird heruntergeladen (falls gesperrt: Zwischenablage nutzen)');
};
$('copy').onclick = () => {
  const text = flagsCsv();
  if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(() => toast('CSV kopiert'), () => fallbackCopy(text)); else fallbackCopy(text);
};
function fallbackCopy(text) { const ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); toast('CSV kopiert'); } catch (e) { toast('Kopieren nicht möglich: Text ist markiert'); } ta.remove(); }
$('clear').onclick = () => { if (!Object.keys(flags).length) return; flags = {}; save(); render(); toast('Flags gelöscht'); };
more.onclick = () => { shown += PAGE; render(); };
for (const el of [q, vol, conf, onlyflag]) el.addEventListener(el === q ? 'input' : 'change', () => { shown = PAGE; render(); });
try { const t = localStorage.getItem('aarau.tab'); if (!location.hash && !P.get('tab') && t && DATA[t]) tab = t; } catch (e) {}
if (P.get('vol')) vol.value = P.get('vol');
if (P.get('conf')) conf.value = P.get('conf');
if (P.get('q')) q.value = P.get('q');
render();
</script>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    data = {}
    for key, label, files, _id, cols in TABS:
        rows = load(files, cols)
        if rows:
            data[key] = {"label": label, "cols": cols, "rows": rows}
            print(f"{label}: {len(rows)} Zeilen")
    reported = load_flags()
    html = (TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
            .replace("__LABELS__", json.dumps(LABELS, ensure_ascii=False))
            .replace("__REASONS__", json.dumps(REASONS, ensure_ascii=False))
            .replace("__REPORTED__", json.dumps(reported, ensure_ascii=False))
            .replace("__REPO__", REPO_URL)
            .replace("__DATE__", date.today().strftime("%d.%m.%Y")))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="utf-8")
    print(f"{len(reported)} gemeldete Flags → {args.out} ({args.out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
