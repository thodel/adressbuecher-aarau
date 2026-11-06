# CSV-Schema der Zwischenresultate

Alle Dateien liegen in `data/csv/`, UTF-8, Komma-getrennt, mit Kopfzeile. Jede Zeile
trägt ihre Herkunft; nichts wird überschrieben, was aus einer früheren Stufe stammt. Die
Nummer im Dateinamen ist die Stufe, die die Datei erzeugt.

## 00_volumes.csv — ein Band je Zeile

| Spalte | Inhalt |
|---|---|
| `volume` | Jahr des Bandes (`1884`, `1888`, `1892`, `1896`, `1899`); dient überall als Bandschlüssel |
| `pdf` | Dateiname der Quelle |
| `pages` | Seitenzahl des PDF |
| `sha256` | Prüfsumme des PDF, damit ein Lauf an die Quelle gebunden ist |

Geplante Ergänzung von Hand: `title`, `edition`, `editor`, `publisher`, `place`, `library_shelfmark`
(Kantonsbibliothek Aargau «Cont. 40»), `erara_url`.

## 01_pages.csv — eine Seite je Zeile (Stufe 1, Abschnitte von Hand)

| Spalte | Inhalt |
|---|---|
| `volume`, `page` | Band und PDF-Seite (1-basiert) — der Seitenschlüssel aller folgenden Dateien |
| `image` | Pfad des Seitenbildes relativ zu `data/pages/` |
| `width`, `height` | Pixelmasse des Bildes |
| `source` | `embedded` (byteidentisch aus dem PDF) oder `rendered300:<n>img` (Fallback) |
| `printed_page` | gedruckte Seitenzahl, wie sie auf der Seite steht (römisch möglich); leer, wenn nicht lesbar |
| `section` | `vorspann`, `gebaeude`, `einwohner`, `berufe`, `zeitungen`, `behoerden`, `inserate`, `leer`, `sonst` |
| `typeface` | `fraktur`, `antiqua`, `gemischt` |
| `columns` | Textspalten der Einträge (1 oder 2) |
| `note` | Zwischentitel, Besonderheiten, woran eine Abschnittsgrenze erkannt wurde |

## 02_lines.csv — eine erkannte Zeile je Zeile (Stufe 2, ATR)

| Spalte | Inhalt |
|---|---|
| `volume`, `page`, `line` | Seitenschlüssel und Zeilennummer in Leserichtung (Spalte für Spalte) |
| `column` | Spalte, in der die Zeile steht |
| `x0`, `y0`, `x1`, `y1` | Begrenzung in Bildpixeln (aus dem kraken-Pfad; leer bei VLM-Lesung ohne Geometrie) |
| `indent` | `1`, wenn die Zeile eingerückt ist (Fortsetzungszeile) |
| `text_<reader>` | eine Spalte je Leser, z. B. `text_kraken_german_print`, `text_qwen3vl_german_xix_v2` |
| `text` | die gewählte Lesung |
| `chosen_reader` | welcher Leser gewählt wurde und warum (`single`, `agree`, `vote`, `review`) |
| `run_id` | Name des ATR-Laufs (Verzeichnis unter `data/atr/`) |

## 03_entries_raw.csv — ein Eintrag je Zeile (Stufe 3)

| Spalte | Inhalt |
|---|---|
| `entry_id` | `<volume>-<section>-<page>-<n>`; stabil, solange die Zeilen gleich bleiben |
| `volume`, `page`, `section` | Herkunft |
| `line_from`, `line_to` | erste und letzte Zeile des Eintrags in `02_lines.csv` |
| `text` | der zusammengesetzte Eintragstext, Trennstriche aufgelöst |
| `owner_flag` | `1`, wenn der Eintrag mit `*` (Hausbesitzer) beginnt |
| `dash_prefix` | `1`, wenn der Eintrag mit Gedankenstrich beginnt (Familienname wiederholt) |
| `surname_inherited` | der ergänzte Familienname bei `dash_prefix` |
| `heading` | der zuletzt gesehene Zwischentitel (Strasse im Gebäudeverzeichnis, Berufsklasse im Berufsregister) |

## 04_entries.csv — ein geparster Eintrag je Zeile (Stufe 4)

| Spalte | Inhalt |
|---|---|
| `entry_id` | wie oben |
| `surname`, `alliance_name` | Familienname und Allianzname (`Müller-Hürni` → `Müller`, `Hürni`) |
| `forename` | Vorname(n), Abkürzungen aufgelöst in `forename_expanded` |
| `title` | `Dr.`, `Dr. med.`, `Regt.`, … |
| `civil_status` | `Witwe`, `Wwe.`, `Frau`, `Fräulein`, `geb.` … wie im Text |
| `relation` | `Sohn`, `Tochter`, `geb. <Name>`; Bezug auf den vorangehenden Eintrag bei Gedankenstrich |
| `occupation_raw` | Beruf/Stand wie gedruckt (`Part.` = Partikulier, `Taglöhner`, `Fabrikant`) |
| `origin_raw`, `origin_canton` | Heimatort wie gedruckt und der Kantonszusatz in Klammern |
| `street_raw`, `building_no` | Strasse/Quartier und Gebäudenummer (mit Buchstabenzusatz, `92a`) |
| `address_role` | `wohnung`, `werkstaette`, `geschaeft`, `wohnung+geschaeft`; mehrere Adressen → mehrere Zeilen mit `address_seq` |
| `phone_flag` | `1`, wenn das Telefon-Symbol steht (ab 1899) |
| `parse_method` | `rule` oder `llm` |
| `parse_confidence` | `high`, `medium`, `low`, `review` |
| `residual` | Textrest, den der Parser nicht zuordnen konnte |

## 05_buildings.csv — ein Gebäude je Band je Zeile (Stufe 5)

| Spalte | Inhalt |
|---|---|
| `volume`, `building_no` | Schlüssel |
| `street_raw`, `street_norm` | Strasse/Quartier gemäss Zwischentitel, normiert über `06_streets.csv` |
| `owner_entry_id` | Eintrag des Eigentümers (`Derselbe` aufgelöst) |
| `resident_entry_ids` | Einträge der Bewohner, `;`-getrennt |
| `lat`, `lon`, `osm_way_id`, `geo_method`, `geo_confidence` | Geokodierung (Stufe 10); `geo_method` ∈ `osm-building`, `plan-punkt`, `strassenmitte` |

## 06_occupations.csv, 06_streets.csv, 06_origins.csv — Normalisierungstabellen (handgepflegt)

| Datei | Schlüssel | Spalten |
|---|---|---|
| `06_occupations.csv` | `occupation_raw` | `occupation_norm`, `class` (Berufsklasse aus dem Register des Bandes), `hisco` (optional), `gender_marked` |
| `06_streets.csv` | `street_raw` | `street_norm`, `quarter`, `street_today`, `wikidata`, `osm_id`, `osm_type`, `lat`, `lon`, `note` |
| `06_origins.csv` | `origin_raw` | `origin_norm`, `canton`, `country`, `hls_id`, `wikidata`, `note` |

## 07_persons.csv, 07_groups.csv, 07_roles.csv — bandübergreifende Identität (Stufe 7)

| Datei | Schlüssel | Spalten |
|---|---|---|
| `07_persons.csv` | `person_id` | `name_canonical`, `entry_ids` (`;`-getrennt, je Band höchstens einer), `first_volume`, `last_volume`, `match_score`, `match_rule`, `review` |
| `07_groups.csv` | `group_id` | `name`, `type` (`behoerde`, `verein`, `firma`, `buergergemeinde`, `anstalt`), `volume_ids`, `wikidata` |
| `07_roles.csv` | `person_id, group_id, volume` | `role` (Amt/Funktion), `source_entry_id` |

## 08_mentions.csv — Erwähnungen (Stufe 8)

| Spalte | Inhalt |
|---|---|
| `entry_id` | der erwähnende Eintrag |
| `target_type`, `target_id` | `person`, `building`, `group`, `place` und der jeweilige Schlüssel |
| `role` | `bewohner`, `eigentuemer`, `amtsinhaber`, `heimatort`, `arbeitsort` |

## 09_links_anb.csv — Verknüpfung mit e-periodica (Stufe 9)

| Spalte | Inhalt |
|---|---|
| `target_type`, `target_id` | Person oder Gebäude |
| `pid`, `chunk_id` | e-periodica-Artikel und Passage |
| `journal` | `anb-001` (Aarauer Neujahrsblätter), `arg-001` (Argovia) |
| `year_article`, `year_mention` | Erscheinungsjahr und in der Passage genanntes Jahr |
| `tier` | `strict` (Band 1910–1919) oder `dated` (Jahr im Fenster 1884–1919 in der Passage) |
| `score`, `evidence`, `url` | Matching-Score, gekürzter Beleg, Link |
| `status` | `auto`, `review`, `accepted`, `rejected` |
