"""Die Bände stehen im Auswahlmenü der Seite nach Jahr geordnet, und nur Bände stehen dort.

Bis 25.11.2026 sammelte die Seite die zweite Spalte jedes Reiters und sortierte sie als Zeichenkette: im Menü
standen Seitenzahlen der Hausnummern 1900 und Telefonquellen (A, AB, B, G), «10» vor «1833», 1900 fehlte.

    python3 -m unittest discover -s tests -v
"""
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _seite():
    spec = importlib.util.spec_from_file_location("erstblick", ROOT / "scripts" / "90_erstblick.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class VolumeOrder(unittest.TestCase):
    def test_nach_jahr_nicht_als_zeichenkette(self):
        data = {"a": {"cols": ["id", "volume", "page"], "rows": [["x", "1899", "10"], ["y", "1833", "7"], ["z", "1900", "3"]]},
                "telefon": {"cols": ["ptt_id", "ptt_source", "year"], "rows": [["t", "AB", "1910"]]}}
        self.assertEqual(_seite().volume_order(data), ["1833", "1899", "1900"])


class GebauteSeite(unittest.TestCase):
    def test_menue_im_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "index.html"
            subprocess.run([sys.executable, "scripts/90_erstblick.py", "--out", str(out)], cwd=ROOT, check=True,
                           capture_output=True)
            m = re.search(r"const VOLS = (\[[^\]]*\]);", out.read_text(encoding="utf-8"))
        self.assertIsNotNone(m, "Bandliste fehlt in der Seite")
        vols = json.loads(m.group(1))
        self.assertTrue(all(re.fullmatch(r"1[89]\d\d", v) for v in vols), vols)
        self.assertEqual(vols, sorted(vols, key=int))
        self.assertIn("1833", vols)
        self.assertIn("1900", vols)


class Staedteleiste(unittest.TestCase):
    """scripts/site_nav.py (in allen adressbuecher-* gleich): mehrere Bestände einer Stadt nach Anfangsjahr."""

    def test_bestaende_einer_stadt_nach_jahr(self):
        import re as _re
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
        import site_nav
        stadt: dict = {}
        for _key, name, _url in site_nav.CITIES:
            ort, jahre = name.rsplit(" ", 1)
            stadt.setdefault(ort, []).append(int(_re.match(r"\d{4}", jahre).group(0)))
        for ort, anfang in stadt.items():
            self.assertEqual(anfang, sorted(anfang), ort)


if __name__ == "__main__":
    unittest.main()
