"""89_suche.py — Startseite mit Suche über alle Bände und Eintragsseiten (scripts/site_search.py).

    python scripts/89_suche.py --out _site

Nimmt die Tabellen der Kontrollseite (scripts/90_erstblick.py: TABS und load(), mit Telefon, anderen Bänden und
Normdaten) und die Strassenpunkte aus data/geo/streets.geojson. Die Kontrollseite selbst liegt unter korrektur/.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import site_nav  # noqa: E402
import site_search  # noqa: E402

K = importlib.import_module("90_erstblick")

CITY = {
    "key": "aarau", "name": "Aarau", "span": "1833–1913", "lang": "de",
    "title": "Adressbücher der Stadt Aarau",
    "lead": "Einwohner, Häuser und Berufe aus den Adressbüchern und Einwohnerverzeichnissen der Stadt Aarau 1833–1913, "
            "maschinell gelesen und in Felder zerlegt. Gesucht wird über alle Bände.",
    "tagline": "Adressbücher · Einwohner · Häuser · Berufe",
    "repo": K.REPO_URL, "center": [47.3925, 8.0444],
    "korr": "korrektur/?tab={part}&vol={vol}&q={id}",
    "nav": [["karte.html", "Karte: Einzugsgebiet und Wohnorte"]],
    "note": "Quellen: Adressbücher und Verzeichnisse der Stadt Aarau (Kantonsbibliothek Aargau; 1901 und 1913 Deutsche "
            "Nationalbibliothek). Fraktur gelesen mit gemini-3.5-flash, Antiqua mit qwen3.8 (Universität Bern).",
    "page_note": "Seitenbilder sind nicht veröffentlicht (Nachnutzung ungeklärt); «Seite» ist die Seite im PDF.",
    "parts": {"einwohner": "Einwohner", "bewohner": "Bewohner nach Häusern", "gebaeude": "Gebäude", "berufe": "Berufe",
              "register": "Namensregister", "nachtraege": "Nachträge", "hausnummern": "Hausnummern 1900"},
}
SKIP_TABS = {"telefon", "normdaten"}  # keine Adressbuch-Einträge
CORE = {"entry_id", "building_id", "row_id", "volume", "page", "surname", "forename", "alliance_name", "occupation_raw",
        "street_raw", "street_norm", "building_no", "text", "telefon", "other_volume", "authority", "zeitreise",
        "origin_place", "street_place", "owner_text", "origin_norm"}


def streets() -> dict[str, tuple[float, float]]:
    out = {}
    p = Path("data/geo/streets.geojson")
    if p.exists():
        for f in json.loads(p.read_text(encoding="utf-8"))["features"]:
            lon, lat = f["geometry"]["coordinates"]
            for v in [f["properties"]["name"], *f["properties"].get("variants", [])]:
                out[v.strip(" “„\"")] = (lat, lon)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    geo = streets()
    labels = {**site_nav.LABELS["de"], **K.LABELS}
    recs = []
    for key, _label, files, _id, cols in K.TABS:
        if key in SKIP_TABS:
            continue
        for row in K.load(files, list(cols)):
            r = dict(zip(cols if len(cols) == len(row) else cols + [""] * (len(row) - len(cols)), row))
            vol = r.get("volume", "")
            if not vol or not vol[:4].isdigit():
                continue
            street = r.get("street_norm") or r.get("street_raw", "")
            g = geo.get(r.get("street_raw", "").strip(" “„\"")) or geo.get(r.get("street_norm", ""))
            name = r.get("surname", "")
            if not name and r.get("owner_text"):  # Gebäude: Eigentümer als Name
                name = r["owner_text"]
            links, related = site_search.std_links(r)
            recs.append({
                "id": r.get(cols[0], ""), "vol": vol, "year": int(vol[:4]), "part": key,
                "name": name, "forename": r.get("forename", ""), "alliance": r.get("alliance_name", ""),
                "maiden": r.get("maiden_name", ""), "occupation": r.get("occupation_raw", ""),
                "street": street, "no": r.get("building_no") or r.get("building_nos") or r.get("new_no", ""),
                "origin": r.get("origin_norm") or r.get("origin_raw", ""), "title": r.get("title", ""),
                "heading": r.get("heading", ""), "text": r.get("text") or r.get("owner_text", ""),
                "page": r.get("page", ""), "lat": g[0] if g else None, "lon": g[1] if g else None,
                "fields": [(c, r.get(c, "")) for c in cols if c not in CORE],
                "links": links, "related": related,
            })
    site_search.build(args.out, city=CITY, records=recs, labels=labels)


if __name__ == "__main__":
    main()
