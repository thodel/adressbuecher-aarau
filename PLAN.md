# Adressbücher Aarau 1884–1899 — Projektplan

Stand 06.11.2026. Fünf Bände (Separat-Auszüge aus dem «Handels- und Gewerbe-Adressbuch
für den Kanton Aargau», bearbeitet von Polizeilieutenant G. Vogel, Verlag Sauerländer)
werden zu einem Informationssystem über Personen, Haushalte, Gebäude, Berufe und
Institutionen der Stadt Aarau. Zwischenresultate sind CSV; das Zielmodell ist
CIDOC-CRM 7.1.3 + SDHSS, gebaut mit dem Vokabular-Register und dem Bestandsgraph-Bauer
aus `agentic_historian`.

## 1. Befund: die Quellen

| Band | Seiten | Satz | Abfolge (PDF-Seiten; vollständig in `data/csv/01_pages.csv`) |
|---|---:|---|---|
| 1884 | 100 | Fraktur | Vorspann 1–14 · Einwohner 15–57 · Gebäude 59–72 (2-spaltig) · Strassenliste 73 · Berufe 75–91 · Behörden 92–93 · Inhalt mit Hausnummern-Konkordanz 94–96 |
| 1888 | 192 | Fraktur | Vorspann 1–10 · Gebäude 11–82 · Inserate 83–90 · Einwohner 91–142 · Berufe 143–164 · Behörden 165–166 · Telefon-Abonnenten 167–169 · Strassen/Nachtrag/Inhalt mit Konkordanz 170–175 · Inserate 176–188 |
| 1892 | 200 | Fraktur | Vorspann 1–8 · Gebäude 9–80 · **Inserate-Lage 81–88 mitten im Gebäudeverzeichnis** · Gebäude 89–95 («nach der Nummerierung gebaute Häuser») · Einwohner 96–153 · Berufe 154–174 · Behörden 175–177, 182 · Telefon 178–181 · Strassen/Nachtrag/Inhalt mit Konkordanz 183–188 · Inserate 189–196 |
| 1896 | 290 | Antiqua | Vorspann 1–22 (röm. III–XVI, mit Sachregister, Strassen→Seite) · Gebäude 23–110 · Einwohner 111–166 (**PDF 127–142 wiederholen 111–126**, gedr. S. 89–104 doppelt) · Berufe 167–192 · Zeitungen 193 · Behörden/Anstalten/Vereine 194–210 · illustrierter Anhang 211–262 · Inserate 263–286 |
| 1899 | 248 | Antiqua | Vorspann 1–8 · Gebäude 9–102 · Inserat 103–104 · Einwohner 105–153 (gedr. 1–49) · Berufe 154–196 (gedr. 50–92, Zählung läuft weiter) · Zeitungen 197–198 · Behörden 199–210 · Strassen→Seite 211 · Inserate 212–248 |

Befund Welle 0 (06.11.2026, alle 1 030 Seiten klassifiziert): «Zeitungen» ist in
1884/1888/1892 nur eine Rubrik unter Z im Berufsregister; 1888 und 1892 haben zusätzlich
ein Verzeichnis der Telefon-Abonnenten (Abschnitt `sonst`); 1896 enthält ein Sachregister
und ein Porträt Adolf Freys. Keine fehlenden Seiten; alle Seitenzählungen gehen auf.

Alle PDFs sind reine Bild-PDFs (kein Textlayer, Producer «semantics visual library»,
A4-Seiten, ein Bild pro Seite). Zusammen 1 030 Seiten. Die eingebetteten Scans sind
Graustufen-JPEGs von **1000 px Breite, also ~120 dpi** — für Kleindruck in Fraktur
knapp. Die Seiten werden darum nicht neu gerendert, sondern byteidentisch extrahiert
(`scripts/01_render_pages.py`); ob höher aufgelöste Scans bei der Kantonsbibliothek
Aargau (Stempel «Cont. 40») oder auf e-rara zu haben sind, ist zu klären (Abschnitt 6).

Die Bände sind nicht einheitlich: 1884, 1888, 1892 und 1899 stammen von G. Vogel
(Polizeiwachtmeister, später Polizeilieutenant; 1899 als Separat-Auszug bei der
Polytechnischen Anstalt Bern). **1896 ist ein anderes Werk**: herausgegeben von der
Mittelschweizerischen Geographisch-Kommerziellen Gesellschaft (Zentralstelle für
Adressbücher), Druck Emil Wirz, mit römisch paginiertem Vorspann, einem «Verzeichnis
der Strassen und Plätze» (S. XIV), Gebäude S. 1–88, Einwohner S. 89–128, Berufe
S. 129–155, Behörden/Anstalten/Vereine S. 156–172 und illustriertem Anhang. Sein
Vorwort nennt die Vorgänger: Staubwasser 1869 und 1879, Müller 1877, Vogel 1881, 1884,
1888, 1892 — drei weitere Bände (1869, 1877, 1879, 1881) existieren also und könnten
die Reihe nach vorn verlängern.

Jeder Band hat dieselben Abschnitte (Reihenfolge nach 1899):

1. **Vorwort, Märkte** — Fliesstext, nicht ausgewertet (nur Metadaten).
2. **Verzeichnis der Gebäude und ihrer Bewohner** — nach Strasse/Quartier, je Gebäudenummer
   die Bewohner; «Derselbe», «Dieselbe», «Gemeinde Aarau» als Eigentümer. Die Nummern
   (z. B. «Rain 875», «Halden 284») sind durchlaufende Gebäudenummern, keine Hausnummern
   je Strasse — das ist für die Modellierung des Ortes entscheidend. Die Kopfnote des
   Verzeichnisses (1892, 1899) erklärt die Zeichen: neben jeder Nummer steht der
   Eigentümer; wohnt er selbst im Haus, ist er mit `*` bezeichnet; 1899 kommt ein
   Telefon-Symbol dazu. In 1884 steht dieses Verzeichnis **nach** dem Einwohnerverzeichnis,
   ab 1888 davor; 1899 beginnt jeder Abschnitt mit eigener Seitenzählung.
3. **Alphabetisches Verzeichnis der Einwohner** — der Kern. Ein Eintrag:
   `Name[-Allianzname], Vorname, [Zivilstand/Witwe/Sohn/Tochter], Beruf, [von Heimatort (Kanton)], Strasse Gebäudenummer.`
   Gedankenstrich = Wiederholung des Familiennamens der vorangehenden Zeile; Stern =
   Hausbesitzer; Abkürzungen («Part.», «Wwe.», «Hrch.», «v.»). Mehrere Adressen pro Eintrag
   kommen vor («Wohnung …; Werkstätte …»).
4. **Geschäfts- und Gewerbetreibende nach Berufsklassen** — Berufsregister, zweispaltig,
   mit eigenem Stichwortverzeichnis (S. 91 von 1884).
5. **Zeitungen, Zeitschriften, Kalender.**
6. **Behörden, Beamte, Vereine, Anstalten, Gesellschaften** — Ämter mit Inhabern
   (Rollen in Gruppen, mit Jahr).
7. **Inseratenanhang** — Firmenanzeigen; optional (Firmen, Gründungsjahre, Adressen).

Eigenschaften, die die Verarbeitung bestimmen: gedruckt, aber Fraktur in den frühen
Bänden; feste Zeilenstruktur mit Einzug für Fortsetzungszeilen; hohe Dichte an
Abkürzungen; dieselben Personen in bis zu fünf Bänden — die Zeitreihe ist der Mehrwert.

## 2. Befund: was `agentic_historian` liefert

Geprüft am 06.11.2026 gegen `~/Repos/agentic_historian` (main) und den laufenden
MCP-ATR-Server auf tei (`server_status`: ok, Gateway `130.92.59.240:8200`, 64 Modelle).

| Baustein | Wo | Nutzen hier |
|---|---|---|
| Batch-ATR über das Gateway | `atr_batch.py`, MCP `start_batch`/`job_status`/`job_log` | jede Seite mit mehreren Modellen lesen, wiederaufnehmbar, mit Bericht |
| Druckmodelle auf dem Gateway | `kraken-german_print`, `kraken-austrian_fraktur`, `kraken-catmus_print_large`, `kraken-catmus_gothic_print` | Zeilengeometrie (PAGE XML) + Text für Fraktur und Antiqua |
| VLM-Leser | `qwen3vl-german-xix-v2`, `qwen3.5-4b-german-xix-v2` (Gateway); Gemini via `via="external"` mit versioniertem Prompt | Seitentext ohne Segmentierung; robust bei Spalten und Abkürzungen |
| Vergleich zweier Lesungen | `compare_readings`, `page_quality` | Abweichung je Seite, abgeschnittene Seiten erkennen |
| Ground-Truth-Bewertung | `score_ground_truth`, `gt_score.py` | CER auf handkorrigierten Seiten |
| Entitäten + Verknüpfung | `agents/entity_agent.py`, `utils/mcp_client.py`, `search_agent.py` | HLS/HBLS/Wikidata-Verknüpfung für Amtsträger und bekannte Personen (optional) |
| e-periodica-MCP | `eperiodica` (`search_semantic` mit Jahresfilter und NER-Entitäten, `search_articles`, `get_article`) | Aarauer Neujahrsblätter `anb-001` (1910–2023) und Argovia `arg-001` (ab 1860) für die Verknüpfung in Abschnitt 4a |
| Vokabular-Register | `knowledge_hub/ontology/registry.py` (CIDOC 7.1.3 + SDHSS aus OntoMe-Schnappschüssen) | die erlaubten Begriffe; alles, was wir brauchen, ist schon drin (E21, E53, E74, E41, E42, C5, C12, C13, C3, C9, P74, P67, P152) |
| Graph-Bauer | `knowledge_hub/bestandsgraph.py` (`Build`, `Dataset`) | stabile URIs, Provenienz je Knoten, keine Blank Nodes |
| Prüfung | `knowledge_hub/ontology/validate.py`, `shapes.ttl` | CRM-RDFS-Prüfung + SHACL als CI-Tor |
| Betrieb | `deploy/qlever/`, `docs/KG_BESTANDSGRAPH_PLAN.md` | QLever auf idhefix, `/sparql/` über tei |
| Veröffentlichung | `utils/publish_github.py`, `output_site/` | ein Commit je Dokument im Outputs-Repo (optional) |

Was es **nicht** gibt und hier entsteht: eine Eintrags-Segmentierung für Verzeichnisse,
ein Parser für die Eintragsgrammatik, eine Normalisierung von Berufen/Strassen/Heimatorten,
eine Personenidentifikation über Bände hinweg, und das Adressbuch-spezifische Mapping.
Der NER-Prompt von Agent C ist auf spätmittelalterliche Verwaltungsschriften geeicht und
wird nicht für die Einträge verwendet; die Einträge sind regelhaft genug für einen Parser
mit LLM-Nachbesserung bei Resten.

### Befund Welle 1 — ATR-Probe (06.11.2026, 20 Seiten, `data/csv/probe_pages.csv`)

**Gemini 3.8 Flash** (extern, Prompt `prompts/adressbuch_atr.md`, Runner-Digest
`@48d0eac8`, Datei-SHA-256 `20f4eeb6…`, `reasoning=low`, Lauf `aarau-probe-gemini-v1`): 20/20 Seiten gelesen, keine
abgeschnitten, kein Leerlauf, 2 502 Zeichen und 10,9 s je Seite, 3,6 min für die
Probe. Zweispaltige Seiten (Gebäude 1884, Berufsregister) werden mit `[spalte 2]`
korrekt getrennt; der Kolumnentitel bleibt; handschriftliche Randnotizen werden als
`[handschriftlich: …]` ausgesondert statt in den Text zu rutschen; durchscheinende
Buchstaben der Nachbarseite (1899) werden ignoriert. Fehlerbild auf den gesichteten
Seiten: einzelne Ziffern (893/693), ein systematischer Fraktur-Lesefehler
**«Oekonom» → «Dekonom»** (O/D), vereinzelt verdoppelte Buchstaben («Elsassser»);
die Doppelstrich-Trennung ⸗ wird als `=` wiedergegeben. Struktur (Stern, Gedankenstrich,
Einzug der Fortsetzungszeilen) ist für den Parser direkt brauchbar.

**GPUStack** (`aarau-probe-gpustack-v1`, über den externen Leser mit
`GEMINI_BASE_URL=https://gpustack.unibe.ch/v1`, gleicher Prompt, Reasoning auf
Modell-Default, von tei per CLI gestartet, weil der MCP-Server keine Basis-URL-Wahl hat):
`qwen3.8-27b` 20/20 gelesen, 72,9 s je Seite, eine Seite leer und am Token-Deckel
abgebrochen (1896 S. 176, zweispaltiges Berufsregister: 164 s Nachdenken, kein Text —
das Reasoning-Problem aus `docs/BATCH_ATR.md`; ohne Denkabschaltung im externen Leser
bleibt das ein Risiko). `qwen3-vl-30b-a3b-instruct` 20/20, **5,4 s je Seite**, keine
Abbrüche.

**Gateway** (`aarau-probe-v1`): kraken ~50 s je Seite inklusive Segmentierung; Details
unten. Erste Lesung `kraken-german_print` auf 1884 S. 18: Wörter weitgehend richtig,
langes s und ⸗ erhalten, aber Stern/Gedankenstrich am Zeilenanfang teils verstümmelt,
eine Randnotiz als Textzeile («Keiaiait»), und auf zweispaltigen Seiten werden die
Spalten zeilenweise vermischt.

**Ground Truth** (`data/gt/`, 4 Seiten, `provenance.csv`): 1884 S. 18 (Fraktur,
Einwohner), 1884 S. 80 (Fraktur, Berufsregister zweispaltig), 1896 S. 99 (Antiqua,
Einwohner zweispaltig), 1899 S. 16 (Antiqua, Einwohner). Entstanden aus der
Gemini-Lesung, jede Abweichung zu kraken am Bildausschnitt entschieden
(`scripts/gt_diff.py`), dann die Seite gegen das Bild gelesen — **von Claude, nicht von
einer Person**, und von Gemini ausgehend: Gemini kommt dadurch zu gut weg, die anderen
Zahlen sind belastbar. Eine menschliche Zweitkorrektur dieser vier Seiten ist der
günstigste Weg, die Verzerrung zu messen.

Zeichenfehlerrate (CER, Levenshtein auf dem normalisierten Seitentext: ſ→s, ⸗/=→-,
Randnotizen entfernt), je GT-Seite:

| Leser | 1884 S. 18 Fraktur | 1884 S. 80 Fraktur 2-sp. | 1896 S. 99 Antiqua 2-sp. | 1899 S. 16 Antiqua | s/Seite |
|---|---:|---:|---:|---:|---:|
| `gemini-3.8-flash` (extern, Prompt-Digest `@48d0eac8`) | 0,007* | 0,004* | 0,000* | 0,000* | 10,9 |
| `qwen3.8-27b` (GPUStack) | 0,044 | 0,057 | 0,010 | 0,001 | 72,9 |
| `qwen3-vl-30b-a3b-instruct` (GPUStack) | 0,032 | 0,046 | 0,031 | 0,011 | 5,4 |
| `kraken-german_print` (Gateway) | 0,033 | 0,073 | 0,432 | 0,020 | ~50 |
| `kraken-austrian_fraktur` (Gateway) | 0,057 | 0,098 | 0,476 | 0,034 | ~50 |
| `kraken-catmus_print_large` (Gateway) | 0,260 | 0,291 | — | — | ~50 |
| `qwen3vl-german-xix-v2` (Gateway) | — | — | — | — | — |

\* GT geht von dieser Lesung aus, Zahl nach unten verzerrt.

Lesart: Auf **Antiqua** sind Gemini und qwen3.8 praktisch fehlerfrei, qwen3-vl-30b bei
1–3 %. Auf **Fraktur** liegt Gemini unter 1 %, kraken-german_print bei 3 % (einspaltig)
und 7 % (zweispaltig), die Qwen-Modelle bei 3–6 %; kraken-catmus ist hier unbrauchbar.
**Zweispaltige Seiten** brechen den kraken-Pfad (43–48 % auf Antiqua, weil die
Segmentierung die Spalten zeilenweise verbindet); alle Seitenleser lösen die Spalten mit
`[spalte 2]` korrekt auf. Systematische Fehler: Gemini liest Fraktur-«Oe» als «De»
(Oekonom → Dekonom), qwen3.8 modernisiert gegen den Prompt (Wittwe → Witwe, Partik. →
Part.), kraken verstümmelt Stern und Gedankenstrich am Zeilenanfang.

**Entscheid für Welle 1 (Vorschlag):** Hauptleser Gemini 3.8 Flash für alle 1 030
Seiten (~3 h, Kosten je Seite) mit `qwen3-vl-30b-a3b-instruct` als zweiter, kostenloser
Lesung für den Abgleich (~1,5 h); `kraken-german_print` nur für einspaltige Seiten als
dritte Stimme und für Zeilengeometrie, wo sie gebraucht wird. qwen3.8 nur, wenn das
Nachdenken abschaltbar wird. Vor dem Volllauf: Prompt um die Oe/De-Falle ergänzen und
die vier GT-Seiten von einer Person gegenlesen lassen.

**Welle 2, erster Stand:** `scripts/04_parse.py` (regelbasiert) löst auf den zehn
Einwohner-Probeseiten der Gemini-Lesung 426 Adresszeilen auf, 407 «high», 14 «medium»
(Firmen, Ditto-«id.» von 1888, unsichere Allianznamen), 5 «review» (Seitenanfang ohne
vorangehenden Familiennamen, da die Probeseiten nicht aufeinander folgen). Erkannte
Konventionen: Stern = Hausbesitzer, Gedankenstrich = geerbter Familienname, «-Name» nach
Gedankenstrich = Allianzname, «geb.» = Geburtsname, Doppeladressen mit «;», «[tel]»,
«id. id.» in 1888 für Heimatort und Adresse der Vorzeile.

## 3. Architektur der Pipeline

```
PDF ──01──▶ Seitenbilder ──02──▶ ATR (2 Leser) ──03──▶ Abschnitte & Zeilen
                                                        │
      ┌─────────────────────────────────────────────────┘
      ▼
04 Einträge (roh) ──05──▶ Einträge (geparst) ──06──▶ Normalisierung
                                                        │
      ┌─────────────────────────────────────────────────┘
      ▼
07 Identität (Personen, Gebäude, Firmen über Bände) ──08──▶ CIDOC/SDHSS Turtle ──09──▶ QLever + MCP
```

Jede Stufe liest CSV und schreibt CSV, ist für sich lauffähig und wiederholbar; ein
Lauf der ganzen Kette ist `make all`. Jede Zeile jeder CSV trägt ihre Herkunft
(Band, Seite, Zeile, ATR-Lauf, Prompt-Digest beziehungsweise Modell-Id), damit der
Graph später sagen kann, woher ein Tripel stammt.

### CSV-Zwischenresultate (`data/csv/`)

| Datei | Schlüssel | Spalten (Kern) |
|---|---|---|
| `00_volumes.csv` | `volume` (1884 …) | Titel, Ausgabe, Bearbeiter, Verlag, Seitenzahl, PDF-Hash |
| `01_pages.csv` | `volume, page` | Bilddatei, Buchseite (gedruckt), Abschnitt (einwohner/gebaeude/berufe/behoerden/zeitungen/inserate/sonst), Spalten, Satz (fraktur/antiqua) |
| `02_lines.csv` | `volume, page, line` | Text je Leser (`text_kraken`, `text_vlm`), gewählter Text, Einzug (Fortsetzung ja/nein), Geometrie |
| `03_entries_raw.csv` | `entry_id` | Abschnitt, zusammengesetzter Eintragstext, Zeilen von–bis, Stern (Hausbesitzer) |
| `04_entries.csv` | `entry_id` | `surname, alliance_name, forename, title, civil_status, relation (Witwe/Sohn/Tochter von), occupation_raw, origin_raw, origin_canton, street_raw, building_no, address_role (Wohnung/Werkstätte/Geschäft), owner_flag, parse_confidence, parse_method (rule/llm)` |
| `05_buildings.csv` | `volume, building_no` | Strasse/Quartier (roh und normiert), Eigentümer-Eintrag, Bewohner-Einträge, `lat`, `lon`, `osm_way_id`, `geo_method`, `geo_confidence` (Abschnitt 4b) |
| `06_occupations.csv` | `occupation_raw` | normierte Berufsbezeichnung, Berufsklasse (aus dem Register des Bandes), HISCO-Code (optional) |
| `06_streets.csv` | `street_raw` | normierte Strasse, Quartier, heutiger Name (wo bekannt), Wikidata/GeoNames, `osm_id`, `osm_type`, `lat`, `lon` (Nominatim, Abschnitt 4b) |
| `06_origins.csv` | `origin_raw` | Heimatort normiert, Kanton, HLS-/Wikidata-Id |
| `07_persons.csv` | `person_id` | kanonischer Name, Einträge je Band (`entry_ids`), erstes/letztes Jahr, Matching-Score, Matching-Regel |
| `07_groups.csv` | `group_id` | Behörden, Vereine, Firmen, Gemeinden (Bürgerorte); Typ |
| `07_roles.csv` | `person_id, group_id, volume` | Amt/Funktion, Quelle (Behördenverzeichnis) |
| `08_mentions.csv` | `entry_id, target_id` | Eintrag → Person/Gebäude/Gruppe/Ort; Rolle der Erwähnung |
| `09_links_anb.csv` | `target_id, chunk_id` | Verknüpfung Person/Gebäude ↔ Passage der Aarauer Neujahrsblätter (Abschnitt 4a); Stufe, Score, Beleg, Status |

Die Dateien 00–05 sind je Band eindeutig (eine Zeile pro Vorkommen), 06 sind
Normalisierungstabellen (handgepflegt, versioniert), 07–08 sind bandübergreifend.

### Mapping auf CIDOC-CRM 7.1.3 + SDHSS (Entwurf, `docs/mapping.md`)

Alle Begriffe aus `registry.py`; nichts Eigenes, solange SDHSS es hat.

| Gegenstand | Klasse | Kanten |
|---|---|---|
| Band | `E31_Document` | `P4` → `E52` (Jahr), `P2` → E55 «Adressbuch», `owl:sameAs` e-rara/Bibliothek, wenn vorhanden |
| Eintrag | `E31_Document` als Teil (`P148_has_component` vom Band) | `P67_refers_to` → Person, Gebäude, Gruppe; `P3_has_note` = Rohtext; Seite/Zeile als `E42` |
| Person | `E21_Person` | `P1` → `E41` (Name, Namensvariante je Band, `P190`), `P152_has_parent` (Sohn/Tochter von), Witwe → `sdh-slc:C9` Relationship mit `sdh-slc:P20` had partner |
| Beruf | `sdh-slc:C12` Actor's Social Role (Vokabular) + `sdh-slc:C13` Embodiment je Person und Band | `P4` → E52 (Bandjahr als Zeitpunkt der Beobachtung) |
| Wohnsitz | `P74_has_current_or_former_residence` → Gebäude; je Band als `E13_Attribute_Assignment` mit Zeit (damit Umzüge datierbar sind) | |
| Gebäude | `E53_Place` mit `E42` (Gebäudenummer) | `P89_falls_within` → Strasse (`E53`) → Aarau (`E53`, Wikidata) |
| Hausbesitz | Stern = `E13` «besitzt» (Rollentyp E55), nicht als Rechtsakt modelliert | |
| Heimatort / Bürgerrecht | `sdh-slc:C5` Membership (Typ «Bürgerrecht») → `E74_Group` (Bürgergemeinde) mit `P74`-Ort | |
| Behörde, Verein, Firma | `E74_Group` + `crm-sup:C9` Gruppentyp | Amt = `sdh-slc:C13` innerhalb der Gruppe, mit Bandjahr |
| Herkunft jedes Knotens | `prov:wasDerivedFrom` → Datensatz (Band + ATR-Lauf + Pipeline-Commit) | |

Offene Modellfragen für `docs/mapping.md`: (a) ob ein Eintrag E31 oder `E33_Linguistic
Object` ist; (b) Beobachtung je Band als E13 oder als SDHSS-Zeitspanne an C13/P74;
(c) wie «Derselbe» im Gebäudeverzeichnis (Eigentümer = Bewohner) ohne Doppelung
ausgedrückt wird. Entscheid vor Stufe 08, nach Rücksprache mit dem Bestandsgraph-Mapping.

## 4. Schritte und Abnahme

| Welle | Schritt | Inhalt | Abnahme |
|---|---|---|---|
| 0 | Setup ✅ 06.11.2026 | Repo-Struktur, `requirements.txt`, `Makefile`, Seitenbilder byteidentisch extrahiert (`data/pages/`, nicht im Git), `00_volumes.csv` mit SHA-256, `01_pages.csv` mit Abschnitt, Seitenzahl, Satz und Spalten für alle 1 030 Seiten | erfüllt; Grenzseiten je auf der Einzelseite bestätigt |
| 0 | Ground Truth | 20 Seiten (4 je Band, aus Einwohner- und Gebäudeverzeichnis) handkorrigiert; 200 Einträge daraus als Soll für den Parser | `data/gt/` liegt vor |
| 1 | ATR Probe (läuft seit 06.11.2026) | Alle 1 030 Seiten liegen auf tei unter `data/nextcloud/adressbuecher-aarau/<jahr>/`, dazu `probe/` mit 20 geschichteten Seiten (`data/csv/probe_pages.csv`: je Band 2× Einwohner, 1× Gebäude, 1× Berufe). Lauf `aarau-probe-v1` mit `kraken-german_print`, `kraken-austrian_fraktur`, `kraken-catmus_print_large`, `qwen3vl-german-xix-v2`; Gemini extern (`reasoning=low`, Prompt versioniert) als zweite Probe | `compare_readings` je Satzart; dann GT-Korrektur von 4 Seiten und `score_ground_truth`: CER je Leser; Entscheid je Band |
| 1 | ATR voll | alle Seiten mit den zwei besten Lesern; `compare_readings`; Seiten mit hoher Abweichung in Review-Liste | `02_lines.csv` vollständig; Bericht je Band |
| 2 | Einträge | Zeilen → Einträge (Einzug, Gedankenstrich, Stern), Abschnittslogik; Parser für die Eintragsgrammatik (Regeln + Abkürzungstabelle), LLM-Nachparse für Reste mit `parse_method=llm` | ≥ 95 % der GT-Einträge feldgenau; Rest in `review/` |
| 2 | Gebäude | Gebäudeverzeichnis → `05_buildings.csv`; Abgleich Einwohner ↔ Gebäude innerhalb des Bandes | jede Einwohneradresse findet ihr Gebäude oder steht in der Fehlliste |
| 3 | Normalisierung | Berufe (Register des Bandes als Klassengerüst, HISCO optional), Strassen (Aarauer Strassenverzeichnis, heutige Namen), Heimatorte (HLS/Wikidata über MCP) | Tabellen 06 handgeprüft; Deckung ≥ 98 % |
| 3 | Identität | Personen über Bände: blocking auf Nachname+Vorname, Scoring mit Beruf, Heimatort, Adresse, Allianzname, Witwen-Übergang; Gebäude über Bände (Nummer stabil? prüfen); Firmen/Behörden | `07_*.csv`; Stichprobe 100 Paare manuell bewertet, Precision ≥ 0,95 |
| 4 | Graph | `scripts/08_export_rdf.py` mit `bestandsgraph.Build`; `validate.py` + SHACL in CI; Zählungen = CSV | Turtle je Band + gesamt; Prüfung grün; Tripelzahl im Manifest |
| 4 | Betrieb | QLever-Index nach dem Muster `deploy/qlever/`; Fragen in `docs/queries.md` (Wer wohnte wann wo; Berufswandel; Haushalte je Gebäude; Ämterkumulation) | `/sparql/` beantwortet die vier Fragen |
| 5 | Informationssystem | MCP-Server nach dem Muster `kf_mcp` (search_persons, get_person, get_building, entries_by_year, search_fulltext) + Einbindung in den Swiss History Bot; einfache Weboberfläche (Person → Zeitstrahl der Adressen) | Server registriert in `mcp_registry.py`; Bot findet Aarauer Personen |
| 5 | Neujahrsblätter | Verknüpfung von Personen und Gebäuden/Strassen mit den Aarauer Neujahrsblättern über den e-periodica-MCP (Abschnitt 4a) | `09_links_anb.csv`; Stichprobe 100 Kandidaten bewertet, Precision ≥ 0,9 |
| 5 | Geovisualisierung | Strassen über Nominatim, Gebäude über georeferenzierten Stadtplan auf OSM-Gebäude; GeoJSON je Band; Leaflet-Karte mit Zeitschieber (Abschnitt 4b) | ≥ 95 % der Einträge mindestens auf Strassenmitte; 50 Gebäude handgeprüft; Karte läuft statisch aus `web/` |

Wellen 1–2 sind sequenziell; 3a (Normalisierung) und 3b (Identität) laufen parallel;
4 wartet auf 3. Die GT aus Welle 0 ist die Messlatte für alles danach.

### 4a. Verknüpfung mit den Aarauer Neujahrsblättern (e-periodica)

Befund (06.11.2026, `eperiodica.corpus_stats`): die Aarauer Neujahrsblätter sind als
Lauf `anb-001` im MCP, 1 208 Artikel, 1910–2023, Volltext als Vision-OCR. Die
semantische Suche liefert je Treffer eine ~1000-Zeichen-Passage; wo der LLM-NER-Lauf
den Artikel verarbeitet hat, trägt jede Passage `entities` (Personen, Organisationen,
Orte mit Offsets). Das ist der Hebel für Skalierung: nicht Volltext lesen, sondern den
Entitätsindex der Zeitschrift gegen `07_persons.csv` und `06_streets.csv` abgleichen.

Nebenbefund: die *Argovia* (`arg-001`, ab 1860) führt in der «Vereinschronik» jährlich
Mitgliederlisten mit Name, Beruf und «in Aarau» — dieselbe Form wie ein Adressbuch-
eintrag, und für 1884–1899 direkt als zweite Quelle für die Personenidentität (Welle 3)
nutzbar. Wird im selben Schritt mitgeführt.

**Zeitfenster.** Verknüpft wird nur, was in das Fenster Adressbuchjahre + 20 Jahre
fällt, also **1884–1919**. Zwei Stufen:

1. *Streng:* Neujahrsblätter-Bände 1910–1919 (das einzige Überlappungsjahrzehnt). Eine
   dort genannte Person oder Adresse wird als zeitgenössisch behandelt.
2. *Datiert:* spätere Bände nur, wenn die Passage selbst ein Jahr im Fenster trägt
   (Nachrufe, «Aarau um 1900», Hausgeschichten mit Baujahr). Das Jahr kommt aus der
   Passage (Regex auf vierstellige Jahreszahlen ± NER-Datum), nicht aus dem Erscheinungsjahr.
   Passagen ohne datierbaren Bezug werden **nicht** verknüpft, auch wenn der Name passt.

**Verfahren (`scripts/09_link_anb.py`).**

| Schritt | Inhalt |
|---|---|
| Kandidaten | je Person aus `07_persons.csv`: `search_semantic` mit Name + Beruf + Strasse, `year_from/year_to` auf das Fenster; zusätzlich `search_articles` mit dem exakten Namen; je Strasse/Gebäude analog (`Rathausgasse 30`, Gebäudenummer, Quartier) |
| Filter | Passage muss im Fenster liegen (Stufe 1 oder 2); `entities` muss den Namen als PERSON beziehungsweise den Ort als PLACE enthalten, wo `entities` vorhanden ist; sonst Stringabgleich (rapidfuzz, Nachname exakt, Vorname tolerant, Allianzname als Bonus) |
| Scoring | Name (Pflicht) + Beruf in der Passage + Strasse/Gebäude in der Passage + Jahr im Fenster; Schwelle für «automatisch», darunter «Review» |
| Ausgabe | `09_links_anb.csv`: `person_id | building_id, pid (e-periodica), chunk_id, year_article, year_mention, tier (strict/dated), score, evidence (Passage gekürzt), url, status (auto/review/rejected)` |
| Graph | Artikel = `E31_Document` mit `owl:sameAs` e-periodica-URL und `P4` Erscheinungsjahr; Erwähnung = `P67_refers_to` vom Artikel zur Person/zum Ort, als `E13_Attribute_Assignment` mit Score und Verfahren als Provenienz, damit automatische und geprüfte Links unterscheidbar bleiben |

Was das nicht ist: keine Übernahme des Zeitschriftentexts in den Graphen (In Copyright;
nur Passagen-Id, Jahr, URL und ein kurzer Beleg), keine Verknüpfung über den Namen
allein. Skalierung: die Kandidatensuche ist je Person ein bis zwei MCP-Aufrufe; bei
~5 000 Personen über fünf Bände eine Nacht, Ergebnisse gecacht nach `chunk_id`.
Dasselbe Verfahren gilt später unverändert für die *Argovia* und weitere Läufe des MCP.

### 4b. Geovisualisierung auf OpenStreetMap

Die Karte ist Teil des Informationssystems (Welle 5) und setzt auf OpenStreetMap:
OSM-Daten für Geokodierung und Grundkarte, Leaflet als Kartenbibliothek, GeoJSON als
Austauschformat. Keine proprietären Kartendienste.

**Vorbilder** (gesichtet 06.11.2026): [Basler Liegenschaften 1400–1700 interaktiv](https://dhbern.github.io/basler-liegenschaften-interaktiv)
(DH Bern, Leaflet, Löffelscher Stadtplan 1862 als WMS-Grundkarte, Polygone von 1615 als
Layer, Jahresschieber, Einfärbung nach Beruf/Zunft/Gewerbe/Wert, Klick auf Liegenschaft
→ Besitzerzeitstrahl mit «gesichert»/«unsicher» und Fade-out für interpolierte Jahre,
Einleitungsdialog zur Datengrundlage) und [eos_persons](https://thodel.github.io/eos_persons/)
(`~/Repos/eos_persons`: `map.html` Dossier-Karte mit Farbwahl nach Personenzahl, Belegzahl,
Periode, Quelle und Jahresbereich; `movements.html` Personenbewegungen in zwei Modi —
Personensuche mit farbigen Trajektorien und rollenkodierten Markern ▲ ● ▼, Heatmap mit
gleitendem 30-Jahre-Fenster oder kumulativ, Abspielen; alles statisch aus `movements.csv`
über PapaParse, Situationsplan 1862 als WMS, Leaflet.heat). Was davon übernommen wird:

| Element | Vorbild | Hier |
|---|---|---|
| Statische Seite, Daten aus CSV/GeoJSON, kein Server | beide | gleich; `web/` liest `data/geo/*.geojson` |
| Historischer Plan als Grundkarte, moderne Karte als Alternative | Löffel 1862 / Situationsplan 1862 (WMS BS) | georeferenzierter Aarauer Plan oder Siegfriedkarte (swisstopo-WMTS) als Overlay; OSM als Grundkarte |
| Jahresschieber mit Abspielen | beide | fünf diskrete Bände statt Jahresfenster; Fenster = Band |
| Einfärbung nach Berufsklasse, gruppiert | Basel (Zunft/Gewerbe) | Berufsklassen aus dem Register der Bände (`06_occupations.csv`) |
| Klick → Zeitstrahl mit Sicherheitsgrad | Basel (gesichert/unsicher, Fade-out) | je Gebäude: Bewohner und Eigentümer je Band; Personenidentität mit Matching-Score als «gesichert/unsicher» |
| Personensuche mit Trajektorien, Rollenmarker | eos movements | Umzugslinien aus `trajectories.geojson`; Marker ▲ erster Band, ● dazwischen, ▼ letzter Band |
| Heatmap mit Fenster | eos movements | Dichte je Band, Filter nach Beruf/Heimatort |
| Einleitung zur Datengrundlage | Basel | Pflicht: ATR-Fehler, Identitätsunsicherheit, Geokodierungsstufe erklären |

Lehre aus eos_persons: die Carto-Grundkarte verlangt inzwischen einen API-Schlüssel und
zeigt sonst Wasserzeichen. Der Kachelanbieter wird darum zu Beginn festgelegt und nicht
aus einem Beispiel übernommen (Abschnitt 6, Punkt 7).

**Geokodierung in zwei Ebenen.** Die Adressbücher nennen Strasse oder Quartier und eine
durchlaufende Gebäudenummer, keine heutige Hausnummer. Darum:

| Ebene | Quelle | Verfahren | Genauigkeit |
|---|---|---|---|
| Strasse / Quartier | OSM über Nominatim (`06_streets.csv` bekommt `osm_id`, `osm_type`, Mittelpunkt `lat/lon`, Linie als GeoJSON) | Strassenname normiert → Nominatim mit `city=Aarau`; umbenannte oder verschwundene Strassen (Haldenthor, Telli, Im Hammer) von Hand auf heutige OSM-Objekte oder ein gezeichnetes Polygon gelegt | Strassenmitte |
| Gebäude | historischer Stadtplan / Siegfriedkarte (swisstopo, Blatt Aarau 1880er) oder Gebäudeversicherungs-Nummernplan, georeferenziert in QGIS; Nummern von Hand oder halbautomatisch auf heutige OSM-Gebäude (`building=*`) gelegt | je Gebäudenummer ein Punkt oder Polygon, `05_buildings.csv` bekommt `lat/lon`, `osm_way_id`, `geo_method` (osm-building / plan-punkt / strassenmitte), `geo_confidence` | Gebäude, wo der Plan es hergibt; sonst Rückfall auf die Strasse |

Die Ebene ist pro Zeile vermerkt, damit die Karte Punkte mit Gebäudegenauigkeit und
Punkte auf Strassenmitte unterscheidbar zeichnet. Prüfung der Gebäudeebene an 50
Gebäuden, die heute noch stehen (Rathaus, Kirchgasse, Laurenzenvorstadt).

**Datenprodukte (`data/geo/`).** `streets.geojson`, `buildings.geojson` und je Band
`residents_<jahr>.geojson` (ein Feature je Eintrag mit Person, Beruf, Gebäude,
Hausbesitz, `entry_id`). Dazu `trajectories.geojson`: je Person mit mehr als einem Band
eine Linie durch ihre Wohnorte in Jahresfolge. Alles aus den CSV erzeugt
(`scripts/10_geo.py`), reproduzierbar.

**Karte (`web/`).** Statische Seite mit Leaflet, OSM-Kacheln (eigener Kachelanbieter oder
ein Anbieter, dessen Nutzungsbedingungen den Betrieb erlauben; die Standard-Kacheln von
osm.org sind für eine öffentliche Anwendung nicht vorgesehen) und OSM-Attribution.
Funktionen in der Reihenfolge ihres Nutzens:

1. Zeitschieber über die fünf Bände; Punkte je Gebäude, Grösse = Anzahl Bewohner.
2. Filter nach Beruf (normiert), Heimatort, Hausbesitz; Farbe nach Berufsklasse.
3. Person anklicken → Zeitstrahl ihrer Adressen und Linie der Umzüge.
4. Gebäude anklicken → Bewohner je Band, Eigentümer, Neujahrsblätter-Belege (4a).
5. Overlay der georeferenzierten Siegfriedkarte (swisstopo-WMTS, offen lizenziert) zum
   Vergleich mit dem heutigen OSM-Stand.

**Im Graphen.** Strasse und Gebäude sind schon `E53_Place`; die Koordinate kommt als
`geo:lat/long` und `P168_place_is_defined_by` (WKT) dazu, das OSM-Objekt als
`owl:sameAs` auf `https://www.openstreetmap.org/way/<id>` — beides Begriffe aus dem
Register. Die Karte liest also entweder die GeoJSON-Dateien oder später direkt den
SPARQL-Endpunkt; beides liefert dieselben Punkte.

## 5. Repo-Struktur

```
adressbuecher-aarau/
  PLAN.md               dieser Plan
  README.md
  Makefile              render → atr → entries → normalise → link → rdf
  pyproject.toml        Abhängigkeiten: pymupdf, pandas, rapidfuzz, rdflib, pyshacl; agentic_historian als Pfadabhängigkeit
  scripts/
    01_render_pages.py  PDF → PNG (300 dpi), 01_pages.csv-Gerüst
    02_atr_batch.py     Seiten hochladen, start_batch, Ergebnisse → 02_lines.csv
    03_entries.py       Zeilen → Einträge
    04_parse.py         Eintragsgrammatik → 04_entries.csv
    05_buildings.py
    06_normalise.py
    07_link.py
    08_export_rdf.py
    09_link_anb.py      e-periodica-MCP: Neujahrsblätter (und Argovia) ↔ Personen/Gebäude
    10_geo.py           Nominatim-Geokodierung, Gebäudepunkte, GeoJSON je Band
  web/                  Leaflet-Karte (OSM-Kacheln, Zeitschieber), statisch
  prompts/              versionierte ATR- und Parse-Prompts
  data/
    pdf/                nicht im Git (Hash in 00_volumes.csv)
    pages/              nicht im Git
    atr/                ATR-Rohausgaben je Lauf (Text ja, Bilder nein)
    csv/                die Zwischenresultate (im Git)
    geo/                GeoJSON: Strassen, Gebäude, Bewohner je Band, Umzugslinien
    gt/                 Ground Truth (im Git)
    rdf/                Turtle + Manifest
  docs/
    schema.md           Spaltenbeschreibung aller CSV
    mapping.md          CIDOC/SDHSS-Mapping mit Begründung
    queries.md          SPARQL-Fragen
  tests/
```

## 6. Entscheidungen, die noch ausstehen

1. **Wo liegen die Seitenbilder für das ATR?** Nextcloud-Share (`dav:`) oder
   `/mnt/wbkolleg_dh_1/tei/datasets/adressbuecher-aarau` (`datasets:`). Letzteres ist
   dauerhaft und vermeidet den Share-Walk; Vorschlag: datasets.
2. **ATR-Leser je Satzart** — wird in Welle 1 gemessen, nicht geraten. Erwartung: kraken
   `german_print`/`austrian_fraktur` für Zeilen und Geometrie, VLM als zweite Lesung.
3. **Veröffentlichung** — eigenes Repo (dieses) mit CSV und Turtle, oder zusätzlich ein
   Commit je Seite in `agentic-historian-outputs`. Vorschlag: nur hier, bis der Graph steht.
4. **Lizenz der Digitalisate** — Herkunft der PDFs (Kantonsbibliothek Aargau, Stempel
   sichtbar) und Nachnutzungsbedingungen klären, bevor Bilder irgendwo veröffentlicht werden.
5. **Gebäudenummern** — ob die durchlaufenden Nummern zwischen 1884 und 1899 stabil
   bleiben (Vorwort der Bände lesen); davon hängt die Gebäude-Identität in Welle 3 ab
   und die Gebäudeebene der Geokodierung in 4b.
6. **Zuordnung der Gebäudenummern zu Orten — offen.** Geklärt ist nach Welle 0, was
   die Nummern sind: eine **stadtweit fortlaufende Gebäudenummerierung** («Verzeichniß
   der Wohn- und Oekonomiegebäude im Stadtbezirk Aarau in fortlaufender Nro.»). Die
   Inhaltsverzeichnisse von 1884 (PDF 94), 1888 (PDF 172–173) und 1892 (PDF 185–186)
   enthalten eine **Konkordanz Strasse → Nummernbereiche → Seite** (z. B. Rathausgasse
   Nr. 1–5, 16–32, 42–49, 176; Zollrain 50–54, 87–91, 177–181, 292–293; Laurenzenvorstadt
   353–385, 390–430, 544–552, 585–612); Neubauten erhielten die nächste freie Nummer,
   darum liegen die Bereiche einer Strasse verstreut, und die späten Nummern (1178–1230)
   stehen unter «nach der Nummerierung gebaute Häuser». Das 1896er «Verzeichnis der
   Strassen und Plätze» (S. XIV) und 1899 (PDF 211) verweisen nur Strasse → Seite.
   Die Konkordanz gibt also jeder Nummer ihre Strasse und ist eine erste Prüfung der
   Nummernstabilität zwischen den Bänden (Welle 2). **Offen bleibt die Lage im Raum:**
   welcher Plan die Nummern trägt (Kandidaten: Brandversicherungs-/Nummernplan im
   Stadtarchiv Aarau, Katasterplan, Gebäudeversicherung Aargau) und ob er digital und
   nachnutzbar vorliegt. Ohne Plan bleibt die Karte auf Strassenmitte. Entscheid steht aus.
7. **Kachelanbieter** für die öffentliche Karte (eigener Server, swisstopo-Grundkarte
   als Alternative zu OSM-Kacheln, oder ein OSM-Kachelanbieter mit passenden Bedingungen).
8. **Auflösung der Scans** — ~120 dpi. Höher aufgelöste Digitalisate anfragen
   (Kantonsbibliothek Aargau, e-rara) oder mit dem Vorhandenen messen, ob die CER reicht.
