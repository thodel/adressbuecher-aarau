# Telefonbuch-Daten (PTT) für Aarau

Externe Bestände, hier nur der Aarauer Ausschnitt; Erzeugung mit `scripts/08_ptt_ingest.py`.

| Datei | Quelle | Inhalt |
|---|---|---|
| `ptt_a_aarau_pages.tsv` | [thodel/PTT_phonebook_data_tsv](https://github.com/thodel/PTT_phonebook_data_tsv), Charge A (`a1.tsv`), Netz Aarau | 657 Seitentexte der Telefonbücher 1889, 1892–1896, 1898–1900, 1902, 1904, 1910 (OCR, Spalten gemischt) |
| `ptt_a_aarau_entries.tsv` | daraus geschnitten | «Strasse Nummer»-Stellen mit dem direkt davorstehenden Namen (heuristisch) |
| `ptt_b_aarau_entries.tsv` | dieselbe Quelle, Charge B (`b*.tsv`), Locality = Aarau | 17 331 Einträge 1921–1935 mit Strasse und **neuer** Hausnummer, Telefonnummer |
| `ptt_g_aarau_entries.csv` | [thodel/gemini-phonebook-analysis](https://github.com/thodel/gemini-phonebook-analysis), `telefonbuch_pttarchiv_aarau` | 355 mit Gemini aus den MFK-Scans gezogene Einträge (Netz Aarau; Jahr noch zu bestimmen, Gebäudenummern alt) |

Herkunft der Rohdaten: PTT-Archiv, Digital Humanities Universität Bern und localsearch
(historic.localsearch.ch); automatisch OCR-gelesen, mit den im Quell-Repo beschriebenen
Fehlern (Zeichen, Spaltenzuordnung, Inserate). Die Daten sind laut Projektleitung frei nutzbar
(öffentliche Datenbank historic.localsearch.ch).

Verknüpfung mit den Adressbüchern: `scripts/09b_link_ptt.py` → `data/csv/09_ptt_entries.csv`.
