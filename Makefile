PY ?= .venv/bin/python
PDF_DIR ?= $(HOME)/Documents/Adressbuecher_Aarau

.PHONY: venv pages
venv:
	uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt

pages:  ## Seitenbilder extrahieren und 00_volumes.csv / 01_pages.csv anlegen
	$(PY) scripts/01_render_pages.py --pdf-dir "$(PDF_DIR)" --out data/pages --csv data/csv

RUN ?= aarau-probe-v1
.PHONY: atr-fetch atr-lines
atr-fetch:  ## Ergebnisse eines ATR-Laufs von tei holen (RUN=...)
	$(PY) scripts/02_atr_batch.py fetch --run $(RUN)

atr-lines:  ## 02_lines.csv aus den geholten Läufen bauen (RUN=...)
	$(PY) scripts/02_atr_batch.py lines --run $(RUN)

FULLRUNS = aarau-fraktur-gemini-v1 aarau-antiqua-qwen38-v1 aarau-fraktur-qwen3vl30b-v1 aarau-antiqua-qwen3vl30b-v1
.PHONY: fullrun-fetch fullrun-lines fullrun-parse
fullrun-fetch:  ## alle Volllauf-Ergebnisse von tei holen
	for r in $(FULLRUNS); do $(PY) scripts/02_atr_batch.py fetch --run $$r; done

fullrun-lines:  ## 02_lines.csv aus allen Volllauf-Lesungen
	$(PY) scripts/02_atr_batch.py lines $(foreach r,$(FULLRUNS),--run $(r))

fullrun-parse:  ## Welle 2: Einwohner-Einträge aus Hauptleser je Satzart → 04_entries.csv
	$(PY) scripts/04_parse.py --run aarau-fraktur-gemini-v1 --reader gemini-3.8-flash --section einwohner --out data/csv/04_entries_fraktur.csv
	$(PY) scripts/04_parse.py --run aarau-antiqua-qwen38-v1 --reader qwen3.8-27b --section einwohner --out data/csv/04_entries_antiqua.csv
	$(PY) scripts/04_parse.py --run aarau-fraktur-gemini-v1 --reader gemini-3.8-flash --section berufe --out data/csv/04_berufe_fraktur.csv
	$(PY) scripts/04_parse.py --run aarau-antiqua-qwen38-v1 --reader qwen3.8-27b --section berufe --out data/csv/04_berufe_antiqua.csv
	$(PY) scripts/05_buildings.py --run aarau-fraktur-gemini-v1 --reader gemini-3.8-flash --out-buildings data/csv/05_buildings_fraktur.csv --out-residents data/csv/05_residents_fraktur.csv
	$(PY) scripts/05_buildings.py --run aarau-antiqua-qwen38-v1 --reader qwen3.8-27b --out-buildings data/csv/05_buildings_antiqua.csv --out-residents data/csv/05_residents_antiqua.csv
