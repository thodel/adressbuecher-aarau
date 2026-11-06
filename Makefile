PY ?= .venv/bin/python
PDF_DIR ?= $(HOME)/Documents/Adressbuecher_Aarau

.PHONY: venv pages
venv:
	uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt

pages:  ## Seitenbilder extrahieren und 00_volumes.csv / 01_pages.csv anlegen
	$(PY) scripts/01_render_pages.py --pdf-dir "$(PDF_DIR)" --out data/pages --csv data/csv
