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

Zweite Stichprobe 27.11.2026 (#9): 60 weitere Einwohner-Einträge, je Band 30 (Seed Band × 100 + 9, ohne die ersten 20),
am Seitenbild geprüft (`data/review/stichprobe_dnb_1901_1913_60.csv`). **1901: 27 von 30** (2 Lesung: «Schuhmather»,
«Gipsmeister» statt «Gipsermeister»; 1 Parser: Bureau-Adresse mit der Wohnadresse vermischt). **1913: 23 von 30**
(6 Lesung, meist Orts- und Allianznamen: «Eggwil», «Häggligen», «Ziegelpain», «-Hilfinger» statt «-Hilfiker»,
«Spitalgässlì», «Wartaу» mit kyrillischem у; 1 Lesung und Parser). Mit der ersten Stichprobe: 1901 34 von 40 (85 %),
1913 29 von 39 (74 %). 1913 liegt damit unter der Schwelle von 80 %, die für die Übernahme in Vernetzte Schweiz gilt.

**1913 Einwohner mit Gemini neu gelesen** (27.11.2026, #9): 94 Seiten mit gemini-3.5-flash (antwortet als 3.6-flash),
`scripts/02e_gemini_text.py`, Lauf `aarau-dnb-gemini-1913`, 1,02 $ (0,011 $ je Seite). `02c_compose_run.py --prefer`
setzt diese Seiten vor die qwen-Lesung (`aarau-dnb-final`); 1901 und die übrigen Teile 1913 bleiben qwen. Die sieben
Fehler der Stichproben sind richtig gelesen (Eggiwil, Hägglingen, Ziegelrain, Hilfiker, Schait, Spitalgäßli, Wartau),
keine kyrillischen Zeichen mehr, Zeilen ohne den Gedankenstrich vor einem Vornamen 19 → 1. Neue Stichprobe 30
Einträge (Seed 191313, `data/review/stichprobe_dnb_1913_gemini.csv`): **26 von 30** (2 Lesung: «Bureauist» statt
«Bureaulist», fehlender Gedankenstrich vor «Martha»; 2 Parser: «Schwarz & Cie.» als geerbter Familienname, «Bureau»
ohne Feld). Offen: «Meyer-Schait, Jakob, Dintikon [tel]. Spezereihandlung …» – Heimatort im Beruf.

**Flags vom 06.11.2026 nachgeprüft** (27.11.2026): Die 48 Flags 1884 («Eintrag falsch getrennt», Kopfzeilen als
Einträge) sind seit dem Parser-Fix vom 06.11. behoben. Beim Nachprüfen fanden sich verwandte Muster in allen Bänden,
jetzt in `scripts/04_parse.py` behoben (Tests: `tests/test_parse_flags_1884.py`):

- **Gedankenstrich falsch gelesen**: «--», «–», «- » oder ein verlorener Strich («*-Säuberli» statt «*— -Säuberli»,
  1913) am Zeilenanfang; der Rest landete im Familiennamen und wurde an alle Folgeeinträge vererbt. Seitenzahlen
  «- 120 -» galten als Einträge. Familiennamen, die mit einem Strich beginnen: vorher 83 Adresszeilen, jetzt 0.
- **Ganze Einträge verworfen**, weil der Parser den Anfang nicht erkannte: Namen mit Partikel («Helm-von Arx»,
  «Von Steiger», «Da Col»), mehrwortige Körperschaften («Aargauische Bank»), fehlendes Komma nach dem Familiennamen
  («Frymann Gottfried»). Im Einwohnerverzeichnis 76 von 86 Zeilen mit Adresse zurückgeholt, im Berufsregister rund
  150; die Folgeeinträge erbten vorher den falschen Familiennamen («Heller» statt «Helm»). Weiter verworfen bleiben
  Wortreste vom Umbruch, Unterzeilen einer Körperschaft («Präsident: …») und «+Jäggi» (Stern als «+» gelesen).
- **Allianzname ohne «=»** («— Leutwyler, Samuel», Lesefehler) wird jetzt aufgelöst statt nur vermerkt: Allianzname
  Leutwyler, Vorname Samuel, Konfidenz «medium» (33 Einträge).

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
