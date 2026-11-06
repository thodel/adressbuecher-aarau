"""92_karte.py — Kartenseite: Einzugsgebiet (Heimatorte) und Wohnorte (Strassen) auf OpenStreetMap.

    python scripts/92_karte.py --out web/karte.html

Bettet data/geo/origins.geojson und data/geo/streets.geojson ein. Leaflet kommt von
cdnjs (feste Version), die Kacheln von OpenStreetMap (Attribution Pflicht; für hohe
Last wäre ein eigener Kachelanbieter nötig, Abschnitt 6 des Plans).
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

GEO_DIR = Path("data/geo")

TEMPLATE = r"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Aarau Einzugsgebiet und Wohnorte</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap">
<style>
/* Layout: Karte füllt die Fläche; links ein schmales Bedienfeld mit Modus, Band und Zähleiste. */
:root {
  --bg: #f6f5f1; --paper: #ffffff; --fg: #1d2129; --muted: #5c6370; --line: #d9d7cf;
  --accent: #7a2e2e; --accent-2: #2f5f8f; --font-body: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #15171b; --paper: #1d2026; --fg: #e8e6df; --muted: #a39f94; --line: #353942; --accent: #d08a84; --accent-2: #7fb0dc; color-scheme: dark } }
:root[data-theme="dark"] { --bg: #15171b; --paper: #1d2026; --fg: #e8e6df; --muted: #a39f94; --line: #353942; --accent: #d08a84; --accent-2: #7fb0dc; color-scheme: dark }
html, body { height: 100%; margin: 0; }
body { background: var(--bg); color: var(--fg); font-family: var(--font-body); font-size: 15px; line-height: 1.4; display: flex; flex-direction: column;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 12px; box-sizing: border-box; gap: 10px; }
header { display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 18px; }
.nav { font-size: 0.9rem; color: var(--muted); }
.nav a { color: var(--accent); font-weight: 600; text-decoration: none; }
.nav a:hover, .nav a:focus-visible { text-decoration: underline; }
h1 { font-size: 1.25rem; margin: 0; font-weight: 700; }
.sub { color: var(--muted); font-size: 0.88rem; margin: 0; }
.sub a { color: var(--accent); }
.main { flex: 1 1 auto; min-height: 0; display: flex; gap: 12px; }
.panel { flex: 0 0 270px; display: flex; flex-direction: column; gap: 10px; min-width: 0; overflow: auto; }
.card { background: var(--paper); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px; }
.card h2 { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); margin: 0 0 6px; }
.seg { display: flex; gap: 4px; flex-wrap: wrap; }
.seg button { font: inherit; font-weight: 600; border: 1px solid var(--line); background: transparent; color: var(--muted); border-radius: 999px; padding: 3px 11px; cursor: pointer; }
.seg button[aria-pressed="true"] { background: var(--accent); border-color: var(--accent); color: #fff; }
.seg button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.stat { display: flex; justify-content: space-between; font-variant-numeric: tabular-nums; font-size: 0.92rem; padding: 2px 0; border-bottom: 1px dashed var(--line); }
.stat:last-child { border: 0; }
.bar { height: 6px; background: var(--accent); border-radius: 3px; }
#map { flex: 1 1 auto; min-width: 0; border: 1px solid var(--line); border-radius: 8px; background: var(--paper); }
.leaflet-popup-content { font-family: var(--font-body); font-size: 13.5px; }
.leaflet-popup-content b { color: var(--accent); }
.leaflet-popup-content a { color: #7a2e2e; font-weight: 600; }
#top a { color: var(--fg); text-decoration: none; border-bottom: 1px dotted var(--muted); }
#top a:hover, #top a:focus-visible { color: var(--accent); }
.legend { font-size: 0.85rem; color: var(--muted); }
@media (max-width: 760px) { .main { flex-direction: column; } .panel { flex: 0 0 auto; max-height: 40%; } }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
/* Leaflet 1.9.4 Kern-Styles (inline, da Stylesheets nur von Google Fonts geladen werden dürfen) */
.leaflet-pane,.leaflet-tile,.leaflet-marker-icon,.leaflet-marker-shadow,.leaflet-tile-container,.leaflet-pane>svg,.leaflet-pane>canvas,.leaflet-zoom-box,.leaflet-image-layer,.leaflet-layer{position:absolute;left:0;top:0}.leaflet-container{overflow:hidden}.leaflet-tile,.leaflet-marker-icon,.leaflet-marker-shadow{-webkit-user-select:none;-moz-user-select:none;user-select:none;-webkit-user-drag:none}.leaflet-tile::selection{background:transparent}.leaflet-safari .leaflet-tile{image-rendering:-webkit-optimize-contrast}.leaflet-safari .leaflet-tile-container{width:1600px;height:1600px;-webkit-transform-origin:0 0}.leaflet-marker-icon,.leaflet-marker-shadow{display:block}.leaflet-container .leaflet-overlay-pane svg{max-width:none!important;max-height:none!important}.leaflet-container .leaflet-marker-pane img,.leaflet-container .leaflet-shadow-pane img,.leaflet-container .leaflet-tile-pane img,.leaflet-container img.leaflet-image-layer,.leaflet-container .leaflet-tile{max-width:none!important;max-height:none!important;width:auto;padding:0}.leaflet-container img.leaflet-tile{mix-blend-mode:plus-lighter}.leaflet-container.leaflet-touch-zoom{-ms-touch-action:pan-x pan-y;touch-action:pan-x pan-y}.leaflet-container.leaflet-touch-drag{-ms-touch-action:pinch-zoom;touch-action:none;touch-action:pinch-zoom}.leaflet-container.leaflet-touch-drag.leaflet-touch-zoom{-ms-touch-action:none;touch-action:none}.leaflet-container{-webkit-tap-highlight-color:transparent}.leaflet-container a{-webkit-tap-highlight-color:rgba(51,181,229,.4)}.leaflet-tile{filter:inherit;visibility:hidden}.leaflet-tile-loaded{visibility:inherit}.leaflet-zoom-box{width:0;height:0;-moz-box-sizing:border-box;box-sizing:border-box;z-index:800}.leaflet-overlay-pane svg{-moz-user-select:none}.leaflet-pane{z-index:400}.leaflet-tile-pane{z-index:200}.leaflet-overlay-pane{z-index:400}.leaflet-shadow-pane{z-index:500}.leaflet-marker-pane{z-index:600}.leaflet-tooltip-pane{z-index:650}.leaflet-popup-pane{z-index:700}.leaflet-map-pane canvas{z-index:100}.leaflet-map-pane svg{z-index:200}.leaflet-vml-shape{width:1px;height:1px}.lvml{behavior:url(#default#VML);display:inline-block;position:absolute}.leaflet-control{position:relative;z-index:800;pointer-events:visiblePainted;pointer-events:auto}.leaflet-top,.leaflet-bottom{position:absolute;z-index:1000;pointer-events:none}.leaflet-top{top:0}.leaflet-right{right:0}.leaflet-bottom{bottom:0}.leaflet-left{left:0}.leaflet-control{float:left;clear:both}.leaflet-right .leaflet-control{float:right}.leaflet-top .leaflet-control{margin-top:10px}.leaflet-bottom .leaflet-control{margin-bottom:10px}.leaflet-left .leaflet-control{margin-left:10px}.leaflet-right .leaflet-control{margin-right:10px}.leaflet-fade-anim .leaflet-popup{opacity:0;-webkit-transition:opacity .2s linear;-moz-transition:opacity .2s linear;transition:opacity .2s linear}.leaflet-fade-anim .leaflet-map-pane .leaflet-popup{opacity:1}.leaflet-zoom-animated{-webkit-transform-origin:0 0;-ms-transform-origin:0 0;transform-origin:0 0}svg.leaflet-zoom-animated{will-change:transform}.leaflet-zoom-anim .leaflet-zoom-animated{-webkit-transition:-webkit-transform .25s cubic-bezier(0,0,.25,1);-moz-transition:-moz-transform .25s cubic-bezier(0,0,.25,1);transition:transform .25s cubic-bezier(0,0,.25,1)}.leaflet-zoom-anim .leaflet-tile,.leaflet-pan-anim .leaflet-tile{-webkit-transition:none;-moz-transition:none;transition:none}.leaflet-zoom-anim .leaflet-zoom-hide{visibility:hidden}.leaflet-interactive{cursor:pointer}.leaflet-grab{cursor:-webkit-grab;cursor:-moz-grab;cursor:grab}.leaflet-crosshair,.leaflet-crosshair .leaflet-interactive{cursor:crosshair}.leaflet-popup-pane,.leaflet-control{cursor:auto}.leaflet-dragging .leaflet-grab,.leaflet-dragging .leaflet-grab .leaflet-interactive,.leaflet-dragging .leaflet-marker-draggable{cursor:move;cursor:-webkit-grabbing;cursor:-moz-grabbing;cursor:grabbing}.leaflet-marker-icon,.leaflet-marker-shadow,.leaflet-image-layer,.leaflet-pane>svg path,.leaflet-tile-container{pointer-events:none}.leaflet-marker-icon.leaflet-interactive,.leaflet-image-layer.leaflet-interactive,.leaflet-pane>svg path.leaflet-interactive,svg.leaflet-image-layer.leaflet-interactive path{pointer-events:visiblePainted;pointer-events:auto}.leaflet-container{background:#ddd;outline-offset:1px}.leaflet-container a{color:#0078a8}.leaflet-zoom-box{border:2px dotted #38f;background:rgba(255,255,255,.5)}.leaflet-container{font-family:"Helvetica Neue",Arial,Helvetica,sans-serif;font-size:12px;font-size:.75rem;line-height:1.5}.leaflet-bar{box-shadow:0 1px 5px rgba(0,0,0,.65);border-radius:4px}.leaflet-bar a{background-color:#fff;border-bottom:1px solid #ccc;width:26px;height:26px;line-height:26px;display:block;text-align:center;text-decoration:none;color:#000}.leaflet-bar a,.leaflet-control-layers-toggle{background-position:50% 50%;background-repeat:no-repeat;display:block}.leaflet-bar a:hover,.leaflet-bar a:focus{background-color:#f4f4f4}.leaflet-bar a:first-child{border-top-left-radius:4px;border-top-right-radius:4px}.leaflet-bar a:last-child{border-bottom-left-radius:4px;border-bottom-right-radius:4px;border-bottom:none}.leaflet-bar a.leaflet-disabled{cursor:default;background-color:#f4f4f4;color:#bbb}.leaflet-touch .leaflet-bar a{width:30px;height:30px;line-height:30px}.leaflet-touch .leaflet-bar a:first-child{border-top-left-radius:2px;border-top-right-radius:2px}.leaflet-touch .leaflet-bar a:last-child{border-bottom-left-radius:2px;border-bottom-right-radius:2px}.leaflet-control-zoom-in,.leaflet-control-zoom-out{font:bold 18px 'Lucida Console',Monaco,monospace;text-indent:1px}.leaflet-touch .leaflet-control-zoom-in,.leaflet-touch .leaflet-control-zoom-out{font-size:22px}.leaflet-control-layers{box-shadow:0 1px 5px rgba(0,0,0,.4);background:#fff;border-radius:5px}.leaflet-control-layers-toggle{width:36px;height:36px}.leaflet-control-layers .leaflet-control-layers-list,.leaflet-control-layers-expanded .leaflet-control-layers-toggle{display:none}.leaflet-control-layers-expanded .leaflet-control-layers-list{display:block;position:relative}.leaflet-control-layers-expanded{padding:6px 10px 6px 6px;color:#333;background:#fff}.leaflet-control-layers-scrollbar{overflow-y:scroll;overflow-x:hidden;padding-right:5px}.leaflet-control-layers-selector{margin-top:2px;position:relative;top:1px}.leaflet-control-layers label{display:block;font-size:13px;font-size:1.08333em}.leaflet-control-layers-separator{height:0;border-top:1px solid #ddd;margin:5px -10px 5px -6px}.leaflet-default-icon-path{background-image:url(data:image/png;base64,)}.leaflet-container .leaflet-control-attribution{background:#fff;background:rgba(255,255,255,.8);margin:0}.leaflet-control-attribution,.leaflet-control-scale-line{padding:0 5px;color:#333;line-height:1.4}.leaflet-control-attribution a{text-decoration:none}.leaflet-control-attribution a:hover,.leaflet-control-attribution a:focus{text-decoration:underline}.leaflet-attribution-flag{display:inline!important;vertical-align:baseline!important;width:1em;height:.6669em}.leaflet-left .leaflet-control-scale{margin-left:5px}.leaflet-bottom .leaflet-control-scale{margin-bottom:5px}.leaflet-control-scale-line{border:2px solid #777;border-top:none;line-height:1.1;padding:2px 5px 1px;white-space:nowrap;-moz-box-sizing:border-box;box-sizing:border-box;background:rgba(255,255,255,.8)}.leaflet-control-scale-line:not(:first-child){border-top:2px solid #777;border-bottom:none;margin-top:-2px}.leaflet-control-scale-line:not(:first-child):not(:last-child){border-bottom:2px solid #777}.leaflet-touch .leaflet-control-attribution,.leaflet-touch .leaflet-control-layers,.leaflet-touch .leaflet-bar{box-shadow:none}.leaflet-touch .leaflet-control-layers,.leaflet-touch .leaflet-bar{border:2px solid rgba(0,0,0,.2);background-clip:padding-box}.leaflet-popup{position:absolute;text-align:center;margin-bottom:20px}.leaflet-popup-content-wrapper{padding:1px;text-align:left;border-radius:12px}.leaflet-popup-content{margin:13px 24px 13px 20px;line-height:1.3;font-size:13px;font-size:1.08333em;min-height:1px}.leaflet-popup-content p{margin:17px 0;margin:1.3em 0}.leaflet-popup-tip-container{width:40px;height:20px;position:absolute;left:50%;margin-top:-1px;margin-left:-20px;overflow:hidden;pointer-events:none}.leaflet-popup-tip{width:17px;height:17px;padding:1px;margin:-10px auto 0;pointer-events:auto;-webkit-transform:rotate(45deg);-moz-transform:rotate(45deg);-ms-transform:rotate(45deg);transform:rotate(45deg)}.leaflet-popup-content-wrapper,.leaflet-popup-tip{background:#fff;color:#333;box-shadow:0 3px 14px rgba(0,0,0,.4)}.leaflet-container a.leaflet-popup-close-button{position:absolute;top:0;right:0;border:none;text-align:center;width:24px;height:24px;font:16px/24px Tahoma,Verdana,sans-serif;color:#757575;text-decoration:none;background:transparent}.leaflet-container a.leaflet-popup-close-button:hover,.leaflet-container a.leaflet-popup-close-button:focus{color:#585858}.leaflet-popup-scrolled{overflow:auto}.leaflet-oldie .leaflet-popup-content-wrapper{-ms-zoom:1}.leaflet-oldie .leaflet-popup-tip{width:24px;margin:0 auto}.leaflet-oldie .leaflet-control-zoom,.leaflet-oldie .leaflet-control-layers,.leaflet-oldie .leaflet-popup-content-wrapper,.leaflet-oldie .leaflet-popup-tip{border:1px solid #999}.leaflet-div-icon{background:#fff;border:1px solid #666}.leaflet-tooltip{position:absolute;padding:6px;background-color:#fff;border:1px solid #fff;border-radius:3px;color:#222;white-space:nowrap;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;pointer-events:none;box-shadow:0 1px 3px rgba(0,0,0,.4)}.leaflet-tooltip.leaflet-interactive{cursor:pointer;pointer-events:auto}.leaflet-tooltip-top:before,.leaflet-tooltip-bottom:before,.leaflet-tooltip-left:before,.leaflet-tooltip-right:before{position:absolute;pointer-events:none;border:6px solid transparent;background:transparent;content:""}.leaflet-tooltip-bottom{margin-top:6px}.leaflet-tooltip-top{margin-top:-6px}.leaflet-tooltip-bottom:before,.leaflet-tooltip-top:before{left:50%;margin-left:-6px}.leaflet-tooltip-top:before{bottom:0;margin-bottom:-12px;border-top-color:#fff}.leaflet-tooltip-bottom:before{top:0;margin-top:-12px;margin-left:-6px;border-bottom-color:#fff}.leaflet-tooltip-left{margin-left:-6px}.leaflet-tooltip-right{margin-left:6px}.leaflet-tooltip-left:before,.leaflet-tooltip-right:before{top:50%;margin-top:-6px}.leaflet-tooltip-left:before{right:0;margin-right:-12px;border-left-color:#fff}.leaflet-tooltip-right:before{left:0;margin-left:-12px;border-right-color:#fff}@media print{.leaflet-control{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.leaflet-control-zoom-in, .leaflet-control-zoom-out { color: #000 !important; }
</style>
<header>
  <nav class="nav"><a href="./">Kontrolle</a> · <a href="karte.html">Karte: Einzugsgebiet und Wohnorte</a> · <a href="https://thodel.github.io/adressbuecher-basel/">Adressbücher Basel</a> · <a href="https://github.com/thodel/adressbuecher-aarau">Repo</a></nav>
  <h1>Adressbücher Aarau: Einzugsgebiet und Wohnorte</h1>
  <p class="sub">Stand __DATE__ · Heimatorte und Strassen über OpenStreetMap (Nominatim) verortet, Strassen auf Strassenmitte, Gebäude noch nicht</p>
</header>
<div class="main">
  <div class="panel">
    <div class="card"><h2>Ansicht</h2><div class="seg" id="mode"><button data-m="origins" aria-pressed="true">Einzugsgebiet</button><button data-m="streets" aria-pressed="false">Wohnorte</button></div></div>
    <div class="card"><h2>Band</h2><div class="seg" id="vol"></div></div>
    <div class="card"><h2>Verortet</h2><div id="stats"></div></div>
    <div class="card" id="topcard"><h2 id="toptitle">Grösste Orte</h2><div id="top"></div></div>
    <p class="legend">Kreisfläche ∝ Zahl der Einträge. Klick auf einen Kreis oder einen Namen in der Liste führt zu den zugehörigen Einträgen. Heimatort = Bürgerort («von …») im Einwohner- und Gebäudeverzeichnis; ein Ort ohne Kantonsangabe wurde zuerst im Aargau gesucht (Konfidenz «aargau-assumed»).</p>
  </div>
  <div id="map" role="application" aria-label="Karte"></div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script>
const ORIGINS = __ORIGINS__;
const STREETS = __STREETS__;
let mode = location.hash === '#streets' ? 'streets' : 'origins';
let vol = 'alle';
const map = L.map('map', { preferCanvas: true });
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>-Mitwirkende' }).addTo(map);
let layer = L.layerGroup().addTo(map);
const $ = id => document.getElementById(id);
const vols = ORIGINS.meta.volumes;
$('vol').innerHTML = ['alle'].concat(vols).map(v => `<button data-v="${v}" aria-pressed="${v === vol}">${v}</button>`).join('');
function data() { return mode === 'origins' ? ORIGINS : STREETS; }
function count(f) { const c = f.properties.counts; return vol === 'alle' ? f.properties.total : (c[vol] || 0); }
function fmt(n) { return n.toLocaleString('de-CH'); }
// Link auf die Kontrollseite, gefiltert auf diesen Ort bzw. diese Strasse (und den gewählten Band)
function keyOf(p) { return mode === 'origins' ? p.name + (p.canton ? ', ' + p.canton : '') : p.name; }
function entriesUrl(p, t) {
  const u = new URLSearchParams({ tab: t, col: mode === 'origins' ? 'origin_norm' : 'street_norm', val: keyOf(p) });
  if (vol !== 'alle') u.set('vol', vol);
  return './?' + u.toString();
}
function links(p) {
  return `<br><a href="${entriesUrl(p, 'einwohner')}">Einträge im Einwohnerverzeichnis</a> · <a href="${entriesUrl(p, 'bewohner')}">Bewohner (Gebäudeverzeichnis)</a>`;
}
function render() {
  for (const b of $('mode').children) b.setAttribute('aria-pressed', b.dataset.m === mode);
  for (const b of $('vol').children) b.setAttribute('aria-pressed', b.dataset.v === vol);
  const d = data(), feats = d.features.filter(f => count(f) > 0);
  layer.clearLayers();
  const maxN = Math.max(1, ...feats.map(count));
  const scale = mode === 'origins' ? 22 : 30;
  feats.sort((a, b) => count(b) - count(a));
  for (const f of feats) {
    const n = count(f), [lon, lat] = f.geometry.coordinates, p = f.properties;
    const r = 3 + scale * Math.sqrt(n / maxN);
    const isHome = mode === 'origins' && p.name === 'Aarau';
    const c = L.circleMarker([lat, lon], { radius: r, color: mode === 'origins' ? '#7a2e2e' : '#2f5f8f', weight: 1, fillOpacity: isHome ? 0.15 : 0.45 });
    const per = vols.map(v => `${v}: ${fmt(p.counts[v] || 0)}`).join(' · ');
    c.bindPopup(`<b>${p.name}</b>${p.canton ? ', ' + p.canton : ''}${p.country && p.country !== 'CH' ? ' (' + p.country + ')' : ''}<br>${fmt(n)} Einträge${vol === 'alle' ? '' : ' in ' + vol}<br><small>${per}</small>${p.top_occupations && p.top_occupations.length ? '<br><small>Berufe: ' + p.top_occupations.join(', ') + '</small>' : ''}${p.confidence ? '<br><small>Verortung: ' + p.confidence + '</small>' : ''}${links(p)}`);
    c.bindTooltip(`${p.name} (${fmt(n)})`);
    c.addTo(layer);
  }
  const loc = vol === 'alle' ? Object.values(d.meta.located).reduce((a, b) => a + b, 0) : (d.meta.located[vol] || 0);
  const un = vol === 'alle' ? Object.values(d.meta.unlocated).reduce((a, b) => a + b, 0) : (d.meta.unlocated[vol] || 0);
  const pct = loc + un ? Math.round(100 * loc / (loc + un)) : 0;
  $('stats').innerHTML = `<div class="stat"><span>${mode === 'origins' ? 'Heimatorte' : 'Strassen'} auf der Karte</span><span>${fmt(feats.length)}</span></div><div class="stat"><span>Einträge verortet</span><span>${fmt(loc)} von ${fmt(loc + un)} (${pct} %)</span></div><div class="bar" style="width:${pct}%"></div>`;
  $('toptitle').textContent = mode === 'origins' ? 'Grösste Heimatorte' : 'Strassen mit den meisten Einträgen';
  $('top').innerHTML = feats.slice(0, 12).map(f => `<div class="stat"><span><a href="${entriesUrl(f.properties, 'einwohner')}">${f.properties.name}</a>${f.properties.canton && f.properties.canton !== 'Aargau' ? ' <small>(' + f.properties.canton + ')</small>' : ''}</span><span>${fmt(count(f))}</span></div>`).join('');
  if (feats.length) {
    // Ausschnitt: Mitteleuropa (Ausreisser in Übersee bleiben auf der Karte, bestimmen aber den Ausschnitt nicht)
    const near = feats.filter(f => f.geometry.coordinates[0] > 4 && f.geometry.coordinates[0] < 13 && f.geometry.coordinates[1] > 44 && f.geometry.coordinates[1] < 52);
    const pts = (near.length ? near : feats).slice(0, mode === 'origins' ? 120 : feats.length).map(f => [f.geometry.coordinates[1], f.geometry.coordinates[0]]);
    map.fitBounds(L.latLngBounds(pts).pad(0.15), { maxZoom: mode === 'origins' ? 9 : 16 });
  } else { map.setView([47.392, 8.045], 14); }
}
$('mode').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; mode = b.dataset.m; render(); });
$('vol').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; vol = b.dataset.v; render(); });
render();
</script>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    o = json.loads((GEO_DIR / "origins.geojson").read_text(encoding="utf-8"))
    s = json.loads((GEO_DIR / "streets.geojson").read_text(encoding="utf-8"))
    html = (TEMPLATE.replace("__ORIGINS__", json.dumps(o, ensure_ascii=False, separators=(",", ":")))
            .replace("__STREETS__", json.dumps(s, ensure_ascii=False, separators=(",", ":")))
            .replace("__DATE__", date.today().strftime("%d.%m.%Y")))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="utf-8")
    print(f"→ {args.out} ({args.out.stat().st_size / 1e6:.2f} MB; {len(o['features'])} Orte, {len(s['features'])} Strassen)")


if __name__ == "__main__":
    main()
