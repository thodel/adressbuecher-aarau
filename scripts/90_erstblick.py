"""90_erstblick.py — eine durchsuchbare HTML-Seite aus den Welle-2-CSV bauen.

    python scripts/90_erstblick.py --out <pfad>/erstblick.html

Liest data/csv/04_entries_*.csv, 04_berufe_*.csv, 05_buildings_*.csv, 05_residents_*.csv
(was davon vorhanden ist) und bettet die Zeilen als JSON in eine statische Seite mit
Reitern, Volltextfilter und Bandfilter ein. Kein Server, keine externen Daten.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

CSV_DIR = Path("data/csv")

TABS = [
    ("einwohner", "Einwohner", ["04_entries_fraktur.csv", "04_entries_antiqua.csv"],
     ["volume", "page", "citizen_flag", "surname", "alliance_name", "maiden_name", "forename", "civil_status",
      "relation", "occupation_raw", "origin_raw", "origin_canton", "street_raw", "building_no", "address_role",
      "phone_flag", "entry_type", "parse_confidence", "residual"]),
    ("gebaeude", "Gebäude", ["05_buildings_fraktur.csv", "05_buildings_antiqua.csv"],
     ["volume", "page", "building_nos", "marker", "street_raw", "owner_text", "building_type",
      "owner_same_as_prev", "phone_flag", "parse_confidence", "note"]),
    ("bewohner", "Bewohner", ["05_residents_fraktur.csv", "05_residents_antiqua.csv"],
     ["volume", "page", "building_no", "surname", "alliance_name", "maiden_name", "forename", "civil_status",
      "relation", "occupation_raw", "origin_raw", "origin_canton", "parse_confidence", "residual"]),
    ("berufe", "Berufe", ["04_berufe_fraktur.csv", "04_berufe_antiqua.csv"],
     ["volume", "page", "heading", "surname", "alliance_name", "forename", "occupation_raw", "street_raw",
      "building_no", "origin_raw", "entry_type", "parse_confidence"]),
]

LABELS = {"volume": "Band", "page": "PDF-S.", "citizen_flag": "Bürger *", "surname": "Name",
          "alliance_name": "Allianz", "maiden_name": "geb.", "forename": "Vorname", "civil_status": "Stand",
          "relation": "Bezug", "occupation_raw": "Beruf", "origin_raw": "Heimatort", "origin_canton": "Kt.",
          "street_raw": "Strasse", "building_no": "Nr.", "address_role": "Adressrolle", "phone_flag": "Tel.",
          "entry_type": "Typ", "parse_confidence": "Konfidenz", "residual": "Rest/Notiz", "building_nos": "Nr.",
          "marker": "Marke", "owner_text": "Eigentümer", "building_type": "Gebäudeart",
          "owner_same_as_prev": "Ditto", "note": "Notiz", "heading": "Rubrik"}


def load(files: list[str], cols: list[str]) -> list[list[str]]:
    rows = []
    for f in files:
        p = CSV_DIR / f
        if not p.exists():
            continue
        with p.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                rows.append([r.get(c, "") for c in cols])
    return rows


TEMPLATE = r"""<title>Aarau Adressdaten Erstblick</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=Source+Code+Pro:wght@400;600&display=swap">
<style>
/* Layout: ein Werkzeug, nicht ein Text — Kopfzeile mit Filtern, darunter eine Tabelle, die den Rest füllt. */
:root {
  --bg: #f6f5f1; --paper: #ffffff; --fg: #1d2129; --muted: #5c6370; --line: #d9d7cf;
  --accent: #7a2e2e; --accent-soft: #f1e3e1; --ok: #2f6f4e; --warn: #9a6b11; --bad: #a33a2a;
  --font-body: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --font-data: "Source Code Pro", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #15171b; --paper: #1d2026; --fg: #e8e6df; --muted: #a39f94; --line: #353942;
  --accent: #d08a84; --accent-soft: #3a2626; --ok: #7fc39d; --warn: #d9b35a; --bad: #e08a79; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #15171b; --paper: #1d2026; --fg: #e8e6df; --muted: #a39f94; --line: #353942;
  --accent: #d08a84; --accent-soft: #3a2626; --ok: #7fc39d; --warn: #d9b35a; --bad: #e08a79; color-scheme: dark }
html, body { height: 100%; }
body { background: var(--bg); color: var(--fg); font-family: var(--font-body); font-size: 15px; line-height: 1.4;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 16px; display: flex; flex-direction: column; gap: 12px; box-sizing: border-box; }
header { display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px 20px; }
h1 { font-size: 1.35rem; margin: 0; font-weight: 700; letter-spacing: -0.01em; text-wrap: balance; }
.sub { color: var(--muted); font-size: 0.9rem; margin: 0; }
.toolbar { display: flex; flex-wrap: wrap; gap: 8px 14px; align-items: center; }
.tabs { display: flex; gap: 4px; flex-wrap: wrap; }
.tabs button { font: inherit; font-weight: 600; background: transparent; color: var(--muted); border: 1px solid var(--line);
  border-radius: 999px; padding: 4px 12px; cursor: pointer; }
.tabs button[aria-selected="true"] { background: var(--accent); border-color: var(--accent); color: #fff; }
.tabs button:focus-visible, input:focus-visible, select:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
input[type="search"], select { font: inherit; padding: 5px 10px; border: 1px solid var(--line); border-radius: 6px;
  background: var(--paper); color: var(--fg); min-width: 0; }
input[type="search"] { flex: 1 1 220px; }
.count { color: var(--muted); font-variant-numeric: tabular-nums; font-size: 0.9rem; }
.wrap { flex: 1 1 auto; min-height: 0; overflow: auto; border: 1px solid var(--line); border-radius: 8px; background: var(--paper); }
table { border-collapse: collapse; width: max-content; min-width: 100%; font-size: 13.5px; }
th, td { text-align: left; padding: 5px 9px; border-bottom: 1px solid var(--line); vertical-align: top; white-space: nowrap; max-width: 34ch; overflow: hidden; text-overflow: ellipsis; }
td.wide { white-space: normal; max-width: 46ch; }
th { position: sticky; top: 0; background: var(--paper); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); z-index: 1; }
td.num { font-family: var(--font-data); font-variant-numeric: tabular-nums; }
.pill { display: inline-block; border-radius: 999px; padding: 0 8px; font-size: 0.75rem; font-weight: 600; line-height: 1.5; }
.pill.high { background: color-mix(in srgb, var(--ok) 18%, transparent); color: var(--ok); }
.pill.medium { background: color-mix(in srgb, var(--warn) 18%, transparent); color: var(--warn); }
.pill.review { background: color-mix(in srgb, var(--bad) 18%, transparent); color: var(--bad); }
.star { color: var(--accent); font-weight: 700; }
.more { display: block; width: 100%; font: inherit; padding: 8px; background: var(--accent-soft); color: var(--fg); border: 0; cursor: pointer; }
.legend { color: var(--muted); font-size: 0.85rem; }
.legend b { color: var(--fg); }
@media (max-width: 600px) { body { font-size: 14px; } th, td { max-width: 24ch; } }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
<header>
  <h1>Adressbücher Aarau: erster Blick auf die Daten</h1>
  <p class="sub">Stand __DATE__ · Rohdaten aus der Gemini-Lesung, regelbasiert geparst, noch ohne Normalisierung und ohne menschliche Korrektur.</p>
</header>
<div class="toolbar">
  <div class="tabs" role="tablist" id="tabs"></div>
  <select id="vol" aria-label="Band"><option value="">alle Bände</option></select>
  <input id="q" type="search" placeholder="Suchen: Name, Beruf, Strasse, Heimatort …" aria-label="Suchen">
  <span class="count" id="count"></span>
</div>
<p class="legend"><b>Bürger *</b> = Stern im Einwohnerverzeichnis (Bürgerrecht Aarau) · <b>Marke</b> im Gebäudeverzeichnis: * Eigentümer wohnt im Haus, † Nebengebäude · <b>Konfidenz</b>: high = Zeile ging vollständig auf, medium = Hinweis in Rest/Notiz, review = nicht zuordenbar.</p>
<div class="wrap"><table id="t"><thead></thead><tbody></tbody></table><button class="more" id="more" hidden>weitere Zeilen zeigen</button></div>
<script>
const DATA = __DATA__;
const LABELS = __LABELS__;
const PAGE = 400;
let tab = location.hash.replace('#','') in DATA ? location.hash.replace('#','') : Object.keys(DATA)[0];
let shown = PAGE;
const tabsEl = document.getElementById('tabs'), q = document.getElementById('q'), vol = document.getElementById('vol');
const thead = document.querySelector('#t thead'), tbody = document.querySelector('#t tbody'), more = document.getElementById('more'), count = document.getElementById('count');
const vols = new Set(); for (const k in DATA) for (const r of DATA[k].rows) vols.add(r[0]);
[...vols].sort().forEach(v => { const o = document.createElement('option'); o.value = v; o.textContent = v; vol.appendChild(o); });
for (const k in DATA) { const b = document.createElement('button'); b.role = 'tab'; b.textContent = `${DATA[k].label} (${DATA[k].rows.length.toLocaleString('de-CH')})`; b.dataset.k = k; b.onclick = () => { tab = k; shown = PAGE; render(); }; tabsEl.appendChild(b); }
function esc(s) { return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function cell(col, v) {
  if (col === 'parse_confidence') return `<td><span class="pill ${esc(v)}">${esc(v)}</span></td>`;
  if (col === 'citizen_flag' || col === 'phone_flag' || col === 'owner_same_as_prev') return `<td class="num">${v === '1' ? '<span class="star">' + (col === 'citizen_flag' ? '*' : col === 'phone_flag' ? '☏' : '„') + '</span>' : ''}</td>`;
  if (col === 'marker') return `<td class="num star">${esc(v)}</td>`;
  if (['page','building_no','building_nos','volume'].includes(col)) return `<td class="num">${esc(v)}</td>`;
  if (['residual','note','owner_text','occupation_raw'].includes(col)) return `<td class="wide">${esc(v)}</td>`;
  return `<td>${esc(v)}</td>`;
}
function render() {
  for (const b of tabsEl.children) b.setAttribute('aria-selected', b.dataset.k === tab);
  const d = DATA[tab], needle = q.value.trim().toLowerCase(), v = vol.value;
  const rows = d.rows.filter(r => (!v || r[0] === v) && (!needle || r.join(' ').toLowerCase().includes(needle)));
  thead.innerHTML = '<tr>' + d.cols.map(c => `<th>${esc(LABELS[c] || c)}</th>`).join('') + '</tr>';
  tbody.innerHTML = rows.slice(0, shown).map(r => '<tr>' + r.map((v, i) => cell(d.cols[i], v)).join('') + '</tr>').join('');
  more.hidden = rows.length <= shown;
  count.textContent = `${Math.min(shown, rows.length).toLocaleString('de-CH')} von ${rows.length.toLocaleString('de-CH')} Zeilen`;
  try { localStorage.setItem('erstblick.tab', tab); } catch (e) {}
}
more.onclick = () => { shown += PAGE; render(); };
q.addEventListener('input', () => { shown = PAGE; render(); });
vol.addEventListener('change', () => { shown = PAGE; render(); });
try { const t = localStorage.getItem('erstblick.tab'); if (!location.hash && t && DATA[t]) tab = t; } catch (e) {}
render();
</script>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    data = {}
    for key, label, files, cols in TABS:
        rows = load(files, cols)
        if rows:
            data[key] = {"label": label, "cols": cols, "rows": rows}
            print(f"{label}: {len(rows)} Zeilen")
    html = (TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
            .replace("__LABELS__", json.dumps(LABELS, ensure_ascii=False))
            .replace("__DATE__", date.today().strftime("%d.%m.%Y")))
    args.out.write_text(html, encoding="utf-8")
    print(f"→ {args.out} ({args.out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
