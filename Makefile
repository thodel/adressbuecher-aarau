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
