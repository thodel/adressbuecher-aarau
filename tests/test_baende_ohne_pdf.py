"""`make pages` (scripts/01_render_pages.py) behält Bände ohne PDF (1901, 1913: TIFF der DNB) samt Abschnitten.

    .venv/bin/python -m unittest discover -s tests -v
"""
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _render():
    spec = importlib.util.spec_from_file_location("render", ROOT / "scripts" / "01_render_pages.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class OhnePdf(unittest.TestCase):
    def test_tiff_baende_bleiben(self):
        r = _render()
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            with (d / "00_volumes.csv").open("w", newline="") as f:
                w = csv.DictWriter(f, ["volume", "pdf", "pages", "sha256"]); w.writeheader()
                w.writerow({"volume": "1899", "pdf": "a.pdf", "pages": "1", "sha256": "x"})
                w.writerow({"volume": "1901", "pdf": "", "pages": "1", "sha256": "y"})
            with (d / "01_pages.csv").open("w", newline="") as f:
                w = csv.DictWriter(f, r.PAGE_FIELDS); w.writeheader()
                w.writerow({"volume": "1899", "page": "1", "section": "alt"})
                w.writerow({"volume": "1901", "page": "93", "section": "einwohner"})
            vols, pages = r.keep_without_pdf(d, [{"volume": "1899", "pdf": "a.pdf", "pages": "1", "sha256": "z"}],
                                             [{"volume": "1899", "page": "1", "section": "neu"}])
            self.assertEqual([v["volume"] for v in vols], ["1899", "1901"])
            self.assertEqual(vols[0]["sha256"], "z")                       # PDF-Band aus dem neuen Lauf
            self.assertEqual({(p["volume"], p["section"]) for p in pages}, {("1899", "neu"), ("1901", "einwohner")})


if __name__ == "__main__":
    unittest.main()
