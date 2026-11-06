"""10_geo.py — Geokodierung über Nominatim (OpenStreetMap) und GeoJSON für die Karte (Stufe 10).

    python scripts/10_geo.py geocode [--only origins|streets] [--limit N]
    python scripts/10_geo.py geojson

`geocode` füllt lat/lon/osm_* in 06_origins.csv und 06_streets.csv. Jede Anfrage wird in
data/geo/nominatim_cache.json abgelegt (Schlüssel = Anfragetext), sodass ein zweiter Lauf
nur neue Namen kostet. Nominatim-Regeln: höchstens eine Anfrage je Sekunde, eigener
User-Agent, keine Massenabfragen — darum 1,1 s Pause und Cache.

Strategie Heimatorte: Kanton bekannt → «Ort, Kanton, Land» (countrycodes=Land);
Schweiz ohne Kanton → zuerst «Ort, Aargau» (die meisten Heimatorte liegen im Kanton),
dann «Ort, Schweiz». `geo_confidence` sagt, welche Stufe traf: canton / aargau-assumed /
country / none. Strassen: «Strasse, Aarau, Schweiz», nur Treffer innerhalb der Stadt.

`geojson` schreibt data/geo/origins.geojson (Punkt je Heimatort mit Zähler je Band) und
data/geo/streets.geojson (Punkt je Strasse mit Zähler je Band) aus den CSV.
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import re
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

CSV_DIR = Path("data/csv")
GEO_DIR = Path("data/geo")
CACHE = GEO_DIR / "nominatim_cache.json"
UA = "adressbuecher-aarau/0.1 (+https://github.com/thodel/adressbuecher-aarau)"
BASE = "https://nominatim.openstreetmap.org/search"
AARAU_BOX = (7.98, 47.36, 8.12, 47.42)   # lon_min, lat_min, lon_max, lat_max (grosszügig)


def load_cache() -> dict:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def save_cache(c: dict) -> None:
    GEO_DIR.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(c, ensure_ascii=False, indent=0), encoding="utf-8")


def query(cache: dict, q: str, countrycodes: str = "", viewbox: tuple | None = None) -> list:
    key = f"{q}|{countrycodes}|{viewbox or ''}"
    if key in cache:
        return cache[key]
    params = {"q": q, "format": "jsonv2", "limit": 3, "addressdetails": 1, "accept-language": "de"}
    if countrycodes:
        params["countrycodes"] = countrycodes
    if viewbox:
        params["viewbox"] = ",".join(str(x) for x in viewbox); params["bounded"] = 1
    req = urllib.request.Request(BASE + "?" + urllib.parse.urlencode(params), headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"   ! {q}: {exc}")
        data = None
    time.sleep(1.1)
    if data is not None:
        cache[key] = data
        save_cache(cache)
    return data or []


STATE_ALIASES = {"Basel": ("Basel-Stadt", "Basel-Landschaft"), "Appenzell": ("Appenzell Ausserrhoden", "Appenzell Innerrhoden"),
                 "Unterwalden": ("Obwalden", "Nidwalden"), "Freiburg": ("Freiburg", "Fribourg"), "Waadt": ("Waadt", "Vaud"),
                 "Wallis": ("Wallis", "Valais"), "Genf": ("Genf", "Genève"), "Neuenburg": ("Neuenburg", "Neuchâtel"),
                 "Tessin": ("Tessin", "Ticino"), "Graubünden": ("Graubünden", "Grischun", "Grigioni")}


def pick(results: list, canton: str = "") -> dict | None:
    """Nur Siedlungen und Verwaltungseinheiten (keine Läden, Strassen, Haltestellen);
    bei bekanntem Kanton nur Treffer in diesem Kanton (address.state)."""
    ok = []
    for r in results:
        if (r.get("category") or r.get("class")) not in ("place", "boundary"):
            continue
        if canton:
            state = (r.get("address") or {}).get("state", "")
            wanted = STATE_ALIASES.get(canton, (canton,))
            if not any(w in state for w in wanted):
                continue
        ok.append(r)
    return ok[0] if ok else None


ORIGIN_SPECIAL = {"Zezwyl": "Zetzwil", "Ryken": "Riken", "Rued": "Schlossrued", "Oberendingen": "Endingen",
                  "Unterendingen": "Endingen", "Bözberg": "Bözberg", "Hallwyl": "Seengen", "Schloßrued": "Schlossrued",
                  "Schmidrued": "Schmiedrued", "Unterkulm": "Unterkulm", "Hirschthal": "Hirschthal", "Möriken": "Möriken-Wildegg"}


def modern_origin(o: str) -> list[str]:
    """Varianten in heutiger Schreibung, in Reihenfolge der Plausibilität."""
    out = [o]
    if o in ORIGIN_SPECIAL:
        out.append(ORIGIN_SPECIAL[o])
    v = re.sub(r"wyl$", "wil", o)
    v = v.replace("ß", "ss").replace("Schloß", "Schloss")
    if v != o:
        out.append(v)
    v2 = re.sub(r"y", "i", v)
    if v2 != v and v2 not in out:
        out.append(v2)
    return out


def geocode_origins(cache: dict, limit: int | None) -> None:
    path = CSV_DIR / "06_origins.csv"
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh)); fields = list(rows[0].keys())
    done = 0
    for r in rows:
        if r["lat"] or r["manual_lat"] or r["norm_method"] == "empty" or not r["origin_norm"]:
            continue
        if limit and done >= limit:
            break
        o, cn, cc = r["origin_norm"], r["canton_norm"], r["country"].lower()
        hit, conf = None, "none"
        for var in modern_origin(o):
            if cn and cc == "ch":
                hit = pick(query(cache, f"{var}, {cn}", "ch"), cn); conf = "canton" if hit else conf
            if not hit and cc == "ch" and not cn:
                hit = pick(query(cache, f"{var}, Aargau", "ch"), "Aargau"); conf = "aargau-assumed" if hit else conf
                if not hit:
                    hit = pick(query(cache, var, "ch")); conf = "country" if hit else conf
            if not hit and cc != "ch":
                q = f"{var}, {cn}" if cn else var
                hit = pick(query(cache, q, cc)); conf = "country" if hit else conf
            if not hit and len(o) > 3:
                hit = pick(query(cache, f"{var}, {cn}" if cn else var)); conf = "world" if hit else conf
            if hit:
                if var != o:
                    conf += "/modern"
                break
        done += 1
        if hit:
            r.update({"lat": hit["lat"], "lon": hit["lon"], "osm_type": hit.get("osm_type", ""), "osm_id": str(hit.get("osm_id", "")),
                      "display_name": hit.get("display_name", "")[:120], "geo_confidence": conf})
        else:
            r["geo_confidence"] = "none"
        print(f"{done:4d} {o!r:30} {cn!r:14} → {conf:15} {r['display_name'][:60]}")
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
    c = Counter(r["geo_confidence"] or "offen" for r in rows)
    print("Heimatorte:", dict(c))


MANUAL_STREETS = GEO_DIR / "manual_streets.csv"   # street_norm, query, lat, lon, note


def modern_query(n: str) -> str:
    """historische Schreibung → heutige OSM-Schreibung für die Anfrage"""
    q = n.replace("straße", "strasse").replace("Straße", "Strasse")
    q = re.sub(r"thor", "tor", q).replace("Rathhaus", "Rathaus").replace("Casino", "Kasino")
    return q


def load_manual_streets() -> dict[str, dict]:
    if not MANUAL_STREETS.exists():
        return {}
    with MANUAL_STREETS.open(encoding="utf-8") as fh:
        return {r["street_norm"]: r for r in csv.DictReader(fh)}


def in_aarau(hit: dict) -> bool:
    a = hit.get("address", {})
    return any(a.get(k) == "Aarau" for k in ("town", "city", "municipality", "village", "suburb", "city_district"))


def geocode_streets(cache: dict, limit: int | None) -> None:
    path = CSV_DIR / "06_streets.csv"
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh)); fields = list(rows[0].keys())
    manual = load_manual_streets()
    by_norm: dict[str, dict] = {}
    done = 0
    for r in rows:
        if r["norm_method"] != "rule":
            continue
        n = r["street_norm"]
        m = manual.get(n)
        if m and m.get("lat"):
            r.update({"lat": m["lat"], "lon": m["lon"], "geo_confidence": "manual", "display_name": m.get("note", ""), "osm_type": "", "osm_id": ""})
            continue
        if r["lat"] and r["geo_confidence"] == "osm-aarau":
            continue
        if n in by_norm:
            r.update(by_norm[n]); continue
        if limit and done >= limit:
            break
        q = (m.get("query") if m and m.get("query") else modern_query(n))
        res = [x for x in query(cache, f"{q}, Aarau", "ch", AARAU_BOX) if in_aarau(x)]
        pref = ("residential", "pedestrian", "living_street", "tertiary", "secondary", "primary", "unclassified",
                "neighbourhood", "quarter", "suburb", "square", "footway", "service", "locality", "park")
        hit = next((x for x in res if x.get("type") in pref), None) or (res[0] if res else None)
        done += 1
        upd = {"lat": hit["lat"], "lon": hit["lon"], "osm_type": hit.get("osm_type", ""), "osm_id": str(hit.get("osm_id", "")),
               "display_name": hit.get("display_name", "")[:120], "geo_confidence": "osm-aarau"} if hit else \
              {"lat": "", "lon": "", "osm_type": "", "osm_id": "", "display_name": "", "geo_confidence": "none"}
        r.update(upd); by_norm[n] = upd
        print(f"{done:4d} {n!r:32} → {upd.get('geo_confidence')} {upd.get('display_name', '')[:60]}")
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print("Strassen:", dict(Counter(r["geo_confidence"] or "offen" for r in rows)))


def place_key(r: dict, fallback: str) -> str:
    """Schlüssel des Ortes, an dem ein Heimatort/eine Strasse auf der Karte liegt:
    OSM-Objekt, sonst handgesetzte Koordinate, sonst die normierte Schreibung.
    Verschiedene Schreibungen desselben Ortes («Paris» / «Paris (Frankreich)») fallen
    so auf einen Punkt; die Kontrollseite filtert über denselben Schlüssel."""
    if r.get("manual_lat"):
        return f"manual/{r['manual_lat']},{r['manual_lon']}"
    if r.get("osm_id"):
        return f"{r.get('osm_type', '')}/{r['osm_id']}"
    if r.get("lat"):
        return f"pt/{r['lat']},{r['lon']}"
    return f"name/{fallback}"


def load_rows() -> list[dict]:
    rows = []
    for f in sorted(glob.glob(str(CSV_DIR / "04_entries_*.csv")) + glob.glob(str(CSV_DIR / "05_residents_*.csv"))):
        kind = "einwohner" if "04_entries" in f else "bewohner"
        with open(f, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                r["_kind"] = kind
                rows.append(r)
    return rows


def _feature(a: dict, extra: dict) -> dict:
    name, _ = a["names"].most_common(1)[0]
    props = {"key": a["key"], "name": name, "variants": [n for n, _ in a["names"].most_common(6)],
             "counts": a["counts"], "total": sum(a["counts"].values()), "by_kind": a["by_kind"],
             "top_occupations": [k for k, _ in a["occupations"].most_common(5)]}
    props.update(extra)
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [a["lon"], a["lat"]]}, "properties": props}


def geojson() -> None:
    rows = load_rows()
    vols = sorted({r["volume"] for r in rows})
    GEO_DIR.mkdir(parents=True, exist_ok=True)

    def new_agg(key: str, lat: str, lon: str) -> dict:
        return {"key": key, "lat": float(lat), "lon": float(lon), "names": Counter(), "cantons": Counter(),
                "countries": Counter(), "confidence": Counter(), "counts": {v: 0 for v in vols},
                "by_kind": {"einwohner": {v: 0 for v in vols}, "bewohner": {v: 0 for v in vols}}, "occupations": Counter(), "citizens": {v: 0 for v in vols}}

    # Heimatorte
    with (CSV_DIR / "06_origins.csv").open(encoding="utf-8") as fh:
        orig = {(r["origin_raw"], r["origin_canton"]): r for r in csv.DictReader(fh)}
    agg: dict[str, dict] = {}
    unlocated = Counter()
    for r in rows:
        if not r.get("origin_raw"):
            continue
        o = orig.get((r["origin_raw"], r.get("origin_canton", "")))
        if not o:
            continue
        lat, lon = o["manual_lat"] or o["lat"], o["manual_lon"] or o["lon"]
        if not lat:
            unlocated[r["volume"]] += 1; continue
        k = place_key(o, o["origin_norm"])
        a = agg.setdefault(k, new_agg(k, lat, lon))
        a["names"][o["origin_norm"]] += 1
        if o["canton_norm"]:
            a["cantons"][o["canton_norm"]] += 1
        a["countries"][o["country"]] += 1
        a["confidence"][o["geo_confidence"] or "manual"] += 1
        a["counts"][r["volume"]] += 1
        a["by_kind"][r["_kind"]][r["volume"]] += 1
        if r.get("occupation_raw"):
            a["occupations"][r["occupation_raw"].split(",")[0].strip()] += 1
    feats = []
    for a in agg.values():
        canton = a["cantons"].most_common(1)[0][0] if a["cantons"] else ""
        country = "FR" if canton in ("Frankreich", "Elsass") else (a["countries"].most_common(1)[0][0] if a["countries"] else "")
        if canton and country == "CH" and any(c != "CH" for c in a["countries"]):
            country = next(c for c, _ in a["countries"].most_common() if c != "CH")
        feats.append(_feature(a, {"canton": canton, "country": country, "confidence": a["confidence"].most_common(1)[0][0]}))
    located = {v: sum(a["counts"][v] for a in agg.values()) for v in vols}
    out = {"type": "FeatureCollection", "features": feats,
           "meta": {"volumes": vols, "located": located, "unlocated": dict(unlocated)}}
    (GEO_DIR / "origins.geojson").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"origins.geojson: {len(feats)} Orte; verortet je Band {located}; nicht verortet {dict(unlocated)}")

    # Strassen
    with (CSV_DIR / "06_streets.csv").open(encoding="utf-8") as fh:
        streets = {r["street_raw"]: r for r in csv.DictReader(fh)}
    agg2: dict[str, dict] = {}
    unloc2 = Counter()
    for r in rows:
        if not r.get("street_raw"):
            continue
        s = streets.get(r["street_raw"])
        if not s or not (s["manual_lat"] or s["lat"]):
            unloc2[r["volume"]] += 1; continue
        k = place_key(s, s["street_norm"])
        a = agg2.setdefault(k, new_agg(k, s["manual_lat"] or s["lat"], s["manual_lon"] or s["lon"]))
        a["names"][s["street_norm"]] += 1
        a["counts"][r["volume"]] += 1
        a["by_kind"][r["_kind"]][r["volume"]] += 1
        if r.get("citizen_flag") == "1":
            a["citizens"][r["volume"]] += 1
        if r.get("occupation_raw"):
            a["occupations"][r["occupation_raw"].split(",")[0].strip()] += 1
    feats = [_feature(a, {"citizens": a["citizens"]}) for a in agg2.values()]
    located = {v: sum(a["counts"][v] for a in agg2.values()) for v in vols}
    out = {"type": "FeatureCollection", "features": feats, "meta": {"volumes": vols, "located": located, "unlocated": dict(unloc2)}}
    (GEO_DIR / "streets.geojson").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"streets.geojson: {len(feats)} Strassen; verortet je Band {located}; nicht verortet {dict(unloc2)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("geocode"); g.add_argument("--only", choices=["origins", "streets"]); g.add_argument("--limit", type=int)
    sub.add_parser("geojson")
    args = ap.parse_args()
    if args.cmd == "geocode":
        cache = load_cache()
        if args.only in (None, "streets"):
            geocode_streets(cache, args.limit)
        if args.only in (None, "origins"):
            geocode_origins(cache, args.limit)
    else:
        geojson()


if __name__ == "__main__":
    main()
