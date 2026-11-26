"""Ab 1913 steht der Heimatort ohne «von» vor einem Punkt, die Adresse dahinter (scripts/04_parse.py).

    .venv/bin/python -m unittest discover -s tests -v
"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _parse():
    spec = importlib.util.spec_from_file_location("parse", ROOT / "scripts" / "04_parse.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class HeimatortVorPunkt(unittest.TestCase):
    def setUp(self):
        self.p = _parse()

    def test_kanton_in_klammern_und_abkuerzung_in_der_strasse(self):
        r = self.p.parse_entry("Custer-Roth, Emil, Fabrikant, Rheineck (St. Gallen). Westallee Neugut 1552.", "", origin_dot=True)
        self.assertEqual((r["origin_raw"], r["origin_canton"], r["occupation_raw"]), ("Rheineck", "St. Gallen", "Fabrikant"))
        self.assertEqual(r["_addresses"], [("", "Westallee Neugut", "1552")])
        r = self.p.parse_entry("— -Pfister, Fried., Brunnenmeister, U.-Entfelden. Hint. Zelgli 1849.", "Dätwyler", origin_dot=True)
        self.assertEqual((r["origin_raw"], r["_addresses"][0][1]), ("U.-Entfelden", "Hint. Zelgli"))

    def test_telefon_vor_dem_punkt(self):
        r = self.p.parse_entry("Däster-Freiermuth, Gottfried, Malermeister, Murgenthal [tel]. Spitalgäßli 1710.", "", origin_dot=True)
        self.assertEqual((r["phone_flag"], r["origin_raw"], r["_addresses"][0][1]), ("1", "Murgenthal", "Spitalgäßli"))

    def test_firma_ohne_komma_am_letzten_punkt(self):
        r = self.p.parse_entry("*Custer & Cie. Fabrikation von Kellereiartikeln u. Champagner [tel]. Bahnhofstraße 626.", "", origin_dot=True)
        self.assertEqual(r["_addresses"], [("", "Bahnhofstraße", "626")])
        self.assertEqual(r["origin_raw"], "")

    def test_aeltere_baende_unveraendert(self):
        r = self.p.parse_entry("Meier, Hans, Schreiner, Hint. Zelgli 18.", "")
        self.assertEqual((r["origin_raw"], r["_addresses"][0][1]), ("", "Hint. Zelgli"))


if __name__ == "__main__":
    unittest.main()
