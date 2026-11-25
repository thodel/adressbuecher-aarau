"""«Problem melden» füllt Band, Seite und Zeile aus den Spalten des Reiters, nicht aus fester Stelle.

Bis 25.11.2026 las issueBody() Band und PDF-Seite an Stelle 2 und 3 jeder Zeile: im Telefon-Reiter stand dort
«Band AB, PDF-Seite 1888» (Quelle und Jahr), in den Normdaten die Stufe als Seite.

Braucht node; ohne node werden die Tests übersprungen.

    python3 -m unittest discover -s tests -v
"""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")


def body(data: dict, tab: str, row: list) -> str:
    src = (ROOT / "scripts" / "90_erstblick.py").read_text(encoding="utf-8")
    m = re.search(r"function issueBody\(k, r\) \{.*?\n\}\n", src, re.S)
    assert m, "issueBody fehlt in scripts/90_erstblick.py"
    js = f"const DATA = {json.dumps(data)};\n{m.group(0)}\nprocess.stdout.write(issueBody({json.dumps(tab)}, {json.dumps(row)}));"
    return subprocess.run([NODE, "-e", js], capture_output=True, text=True, check=True).stdout


@unittest.skipUnless(NODE, "node fehlt")
class IssueBody(unittest.TestCase):
    def test_telefon_nennt_quelle_und_jahr_statt_band(self):
        data = {"telefon": {"label": "Telefon", "cols": ["ptt_id", "ptt_source", "year", "name_raw", "rest", "street_raw"]}}
        b = body(data, "telefon", ["AB-1888-167-001", "AB", "1888", "Aargauische Bank", "", "Bahnhofstraße 511"])
        self.assertIn("Telefonbuch AB 1888", b)
        self.assertNotIn("Band AB", b)
        self.assertNotIn("PDF-Seite", b)
        self.assertIn("Aargauische Bank, Bahnhofstraße 511", b)

    def test_normdaten_ohne_seite(self):
        data = {"normdaten": {"label": "Normdaten", "cols": ["entry_id", "volume", "tier", "surname", "label"]}}
        b = body(data, "normdaten", ["1896-einwohner-111-L032", "1896", "verworfen", "Aeschbach", "Friedrich Aeschbach"])
        self.assertIn("Band 1896", b)
        self.assertNotIn("PDF-Seite verworfen", b)
        self.assertIn("Normdaten-Person:\nFriedrich Aeschbach\n", b)
        self.assertNotIn("ATR-Zeile", b)

    def test_einwohner_band_und_seite(self):
        data = {"einwohner": {"label": "Einwohner", "cols": ["entry_id", "volume", "page", "surname", "text"]}}
        b = body(data, "einwohner", ["1884-einwohner-015-L006", "1884", "15", "Abt", "Abt, Jakob, Schreiner"])
        self.assertIn("Band 1884, PDF-Seite 15", b)
        self.assertIn("Abt, Jakob, Schreiner", b)


if __name__ == "__main__":
    unittest.main()
