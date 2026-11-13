# adressbuecher-aarau

Auswertung der Adressbücher der Stadt Aarau 1884, 1888, 1892, 1896 und 1899
(Separat-Auszüge aus dem Handels- und Gewerbe-Adressbuch für den Kanton Aargau).

Ziel ist ein Informationssystem über Personen, Haushalte, Gebäude, Berufe und
Institutionen Aaraus im späten 19. Jahrhundert, modelliert in CIDOC-CRM 7.1.3 + SDHSS.
Zwischenresultate sind CSV. Das Tooling (ATR, Vokabular-Register, Graph-Bauer, Prüfung,
QLever, MCP) kommt aus [agentic_historian](https://github.com/thodel/agentic_historian).

Der Plan mit Befund, Pipeline, CSV-Schema, Mapping und Abnahmekriterien steht in
[PLAN.md](PLAN.md).

Visualisierungen:

- Kontrollseite der Datensätze mit Flagging und Telefonbuch-Abgleich: https://thodel.github.io/adressbuecher-aarau/
- Karte Einzugsgebiet und Wohnorte: https://thodel.github.io/adressbuecher-aarau/karte.html
- Schwesterprojekt Basel 1841/1850/1862: https://thodel.github.io/adressbuecher-basel/ ([Repo](https://github.com/thodel/adressbuecher-basel))

## Betrieb

- ATR läuft über den Server `tei` (SSH-Alias in `~/.ssh/config`, oder `TEI_SSH=user@host`); die
  Läufe werden über den MCP-ATR-Server von agentic_historian gestartet (siehe PLAN.md, Welle 1).
- `make fullrun-fetch fullrun-parse erstblick` holt fertige Läufe, parst alle Abschnitte und baut
  die Kontrollseite `web/index.html`; GitHub Pages baut dieselbe Seite bei jedem Push.
- Flags von der Kontrollseite: CSV exportieren, `make flags-merge FILE=…`, committen.
- Verknüpfungen in `web/`, mit den Skripten erzeugt und eingecheckt (der Pages-Bau braucht kein Netz):
  - `telefon.csv` (`scripts/80_telefon.py --vs ~/Repos/vernetzte-schweiz`): Einträge mit ☏ → PTT-Telefonbuch
    (Verknüpfung von Vernetzte Schweiz, sonst einzige Person mit Name und Vorname), mit Link auf die Person und das
    Seitenbild; Commit in `telefon_source.txt`. Spalte «Telefonbuch» im Reiter Einwohner.
  - `baende.csv` (`scripts/81_baende.py`): dieselbe Person in den anderen Bänden (Spalte «Andere Bände»).
- Spalte «Karte damals»: historische Karte des Jahres bei swisstopo (Zeitreise) an der Strasse (data/geo/streets.geojson).
