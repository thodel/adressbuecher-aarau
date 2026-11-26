"""07_gemeinden.py — Namen der Schweizer Gemeinden (heutige und ehemalige) aus Wikidata.

    python scripts/07_gemeinden.py            # → data/ext/ch_gemeinden.csv

Für den Parser (`04_parse.looks_like_place`): ab 1913 steht vor dem Punkt Heimatort oder Beruf, und ein
Ortsname mit Berufsendung («Estavayer», «Savognin») soll Ort bleiben. Gemeinden der Schweiz (Q70208) und
ehemalige Gemeinden (Q685309), je Bezeichnung und Alias auf Deutsch, Französisch und Italienisch.
Eingecheckt, damit der Parser kein Netz braucht.
"""
from __future__ import annotations

import csv
import json
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path("data/ext/ch_gemeinden.csv")
QUERY = """
SELECT ?item ?name ?kind WHERE {
  VALUES (?cls ?kind) { (wd:Q70208 "gemeinde") (wd:Q685309 "ehemalig") }
  ?item wdt:P31 ?cls .
  { ?item rdfs:label ?name } UNION { ?item skos:altLabel ?name }
  FILTER(LANG(?name) IN ("de", "fr", "it"))
}"""


def main() -> None:
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": QUERY, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": "adressbuecher-aarau/1.0 (research script)"})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read())
    rows = {(b["item"]["value"].rsplit("/", 1)[1], b["name"]["value"], b["kind"]["value"])
            for b in data["results"]["bindings"]}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["qid", "name", "kind"])
        w.writerows(sorted(rows, key=lambda r: (r[1], r[0])))
    print(f"{OUT}: {len(rows)} Namen, {len({r[0] for r in rows})} Gemeinden")


if __name__ == "__main__":
    main()
