# adressbuecher-aarau

Auswertung der Adressbücher der Stadt Aarau 1884, 1888, 1892, 1896, 1899, 1901 und 1913
(Separat-Auszüge aus dem Handels- und Gewerbe-Adressbuch für den Kanton Aargau).

Dazu die früheren, nach Häusern geordneten Verzeichnisse 1833 (Häuserbesitzer), 1859, 1867, 1877, 1879, 1881
(«Verzeichniss sämmtlicher Einwohner, Wohn- und Oekonomie-Gebäude»), der Adress-Kalender 1869 (alle Fraktur,
gelesen mit gemini-3.5-flash) und das Verzeichnis der neuen Hausnumerierung 1900 (Antiqua, gelesen mit qwen3.8).
Stichprobe vor dem Lauf (16 Seiten, blind am Seitenbild): Fraktur Gemini 95 %, qwen3.8 61 % voll korrekte
Einträge; 1900 beide 97 %. `make frueh-read frueh-parse` → `data/csv/05_buildings_frueh.csv`,
`05_residents_frueh.csv`, `05_register_frueh.csv` (Namensregister), `05_nachtraege_frueh.csv`,
`05_hausnumerierung_1900.csv`; ohne Nachkorrektur.

Dazu 1901 (Jg. 10) und 1913 aus der Deutschen Nationalbibliothek (TIFF, kein PDF; Seitenbilder nicht im Repo),
gelesen mit qwen3.8-27b (Lauf `aarau-antiqua-qwen38-1901-1913`, 438 Seiten, keine Ausfälle) →
`04_entries_dnb.csv`, `04_berufe_dnb.csv`, `05_buildings_dnb.csv`, `05_residents_dnb.csv`. Seite = Bildnummer der
DNB-Datei. Ab 1913 steht der Heimatort ohne «von» vor einem Punkt («…, Bottenwil. Asylstraße 1147.»), und «*» heisst
«im Handelsregister eingetragen» (Hinweis `handelsregister`, kein Bürger-Stern). Die Gemeinden des Bezirks im Band 1913
(S. 277–297) sind nicht eingebunden. Stichprobe 20 Einwohner-Einträge am Seitenbild
(`data/review/stichprobe_dnb_1901_1913.csv`): 13 von 19 voll korrekt, ein Randfragment der Gegenseite (inzwischen
verworfen); Fehler: 4 Parser (Institutionen mit Bindestrich wie in allen Bänden, Firmen-Folgezeile, Berufswort als
Heimatort), 2 Lesung («Wehrlí», «Überlingen» statt «Ueberlingen»). Die Institutionen sind seither in allen Bänden
behoben: Körperschaften (Ämter, Anstalten, Kassen, Vereine …) haben `entry_type` «institution», Geschäftsnamen
(«…handlung», «…fabrik») «firma», beide mit ganzem Namen statt Name und Allianzname; umbrochene Zeilen wie
«Direktor der aarg. | Kreditanstalt, …» gehören zum vorigen Eintrag, und «Bureau», «Laden», «Magazin» gelten als
Adressrolle nur als ganzes Wort (nicht in «Bureauangestellte», «Ladentochter», «Magaziner»).
1913 steht vor dem Punkt nicht immer ein Heimatort: Stand und Beruf («Privatin.», «Bankbeamter.») und der Vorname
bei Einträgen ohne Beruf («Wehrli-Säuberli, Emil [tel]. Rathausgasse 30.») bleiben in ihren Feldern; als Ort gilt,
was in Klammern steht, als Heimatort der älteren Bände vorkommt oder keine Berufsendung hat (`looks_like_place`).
Bekannte Lücke: einzelne Orte auf -er/-in (Estavayer, Savognin) fallen in den Beruf.

Ziel ist ein Informationssystem über Personen, Haushalte, Gebäude, Berufe und
Institutionen Aaraus im späten 19. Jahrhundert, modelliert in CIDOC-CRM 7.1.3 + SDHSS.
Zwischenresultate sind CSV. Das Tooling (ATR, Vokabular-Register, Graph-Bauer, Prüfung,
QLever, MCP) kommt aus [agentic_historian](https://github.com/thodel/agentic_historian).

Der Plan mit Befund, Pipeline, CSV-Schema, Mapping und Abnahmekriterien steht in
[PLAN.md](PLAN.md).

Visualisierungen:

- Suche über alle Bände (Liste, Karte, Facetten, Zeitstrahl) mit Seite je Eintrag: https://thodel.github.io/adressbuecher-aarau/
  (`scripts/89_suche.py` mit dem gemeinsamen `scripts/site_search.py`; `make suche` baut alles nach `_site/`)
- Korrekturmodus (Kontrollseite der Datensätze mit Flagging und Telefonbuch-Abgleich): https://thodel.github.io/adressbuecher-aarau/korrektur/
- Karte Einzugsgebiet und Wohnorte: https://thodel.github.io/adressbuecher-aarau/karte.html
- Schwesterprojekt Basel 1841/1850/1862: https://thodel.github.io/adressbuecher-basel/ ([Repo](https://github.com/thodel/adressbuecher-basel))

## Betrieb

- ATR läuft über den Server `tei` (SSH-Alias in `~/.ssh/config`, oder `TEI_SSH=user@host`); die
  Läufe werden über den MCP-ATR-Server von agentic_historian gestartet (siehe PLAN.md, Welle 1).
- `make fullrun-fetch fullrun-parse erstblick` holt fertige Läufe, parst alle Abschnitte und baut
  die Kontrollseite `web/index.html`; GitHub Pages baut sie bei jedem Push unter `korrektur/`, die Startseite ist die Suche.
- Flags von der Kontrollseite: CSV exportieren, `make flags-merge FILE=…`, committen.
- Verknüpfungen in `web/`, mit den Skripten erzeugt und eingecheckt (der Pages-Bau braucht kein Netz):
  - `telefon.csv` (`scripts/80_telefon.py --vs ~/Repos/vernetzte-schweiz`): Einträge mit ☏ → PTT-Telefonbuch
    (Verknüpfung von Vernetzte Schweiz, sonst einzige Person mit Name und Vorname), mit Link auf die Person und das
    Seitenbild; Commit in `telefon_source.txt`. Spalte «Telefonbuch» im Reiter Einwohner.
  - `baende.csv` (`scripts/81_baende.py`): dieselbe Person in den anderen Bänden (Spalte «Andere Bände»).
- Spalte «Karte damals»: historische Karte des Jahres bei swisstopo (Zeitreise) an der Strasse (data/geo/streets.geojson).
