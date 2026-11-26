"""Fälle aus der Stichprobe 1901/1913 (data/review/stichprobe_dnb_1901_1913.csv), scripts/04_parse.py.

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


class DnbFaelle(unittest.TestCase):
    def setUp(self):
        self.p = _parse()

    def test_nummer_direkt_hinter_abkuerzung(self):
        r = self.p.parse_entry("— -Lüthi, Jakob, Kreiscommandant, Auenstein [tel]. Bankstr.1051.", "Joho", origin_dot=True)
        self.assertEqual(r["_addresses"], [("", "Bankstr.", "1051")])
        r = self.p.parse_entry("— Ida, Privatlehrerin, Gollattenmattg.229.", "Hemmeler")
        self.assertEqual(r["_addresses"], [("", "Gollattenmattg.", "229")])

    def test_randfragmente_der_gegenseite(self):
        for t in ("— H", "— Ker Keß Keu", "Kalb, Kalt-L", "*Juraze", "—"):
            self.assertTrue(self.p.is_fragment(t), t)
        for t in ("Kantonsbibliothek, Großratsgebäude.", 'Perusset, A., "', "Meier, Hans, Halden 12"):
            self.assertFalse(self.p.is_fragment(t), t)
        rows = self.p.parse_page("Meier, Hans, Schreiner, Halden 12.\n— M\nLede\n", "1913", 182)
        self.assertEqual([r["surname"] for r in rows], ["Meier"])

    def test_stern_1913_ist_handelsregister(self):
        r = self.p.parse_entry("*Stahel, Jean, Kaufmann, Aarau. Schlossplatz 198.", "", origin_dot=True, star_register=True)
        self.assertEqual(r["citizen_flag"], "")
        self.assertIn("handelsregister", r["residual"])
        r = self.p.parse_entry("*Stahel, Jean, Kaufmann, Schlossplatz 198.", "")
        self.assertEqual(r["citizen_flag"], "1")

    def test_firmenname_mit_ag_nicht_als_allianzname(self):
        r = self.p.parse_entry("*Chocolat Frey A.-G. [tel]. Telli 850.", "", origin_dot=True)
        self.assertEqual((r["surname"], r["alliance_name"]), ("Chocolat Frey A.-G.", ""))
        r = self.p.parse_entry("Erdin-Obrecht, Albin, Kaufmann, Firma Erne und Cie., Bahnhofstraße 610.", "")
        self.assertEqual((r["surname"], r["alliance_name"]), ("Erdin", "Obrecht"))

    def test_doppelstrich_setzt_firma_fort(self):
        firma = {"entry_type": "firma"}
        r = self.p.parse_entry("— — Fabrikgebäude, Bureau [tel]. Laurenzenvorstadt 773.", "Chocolat Frey A.-G.", firma, origin_dot=True)
        self.assertEqual((r["entry_type"], r["origin_raw"]), ("firma", ""))
        r = self.p.parse_entry("—— Rosine, Näherin, hintere Vorstadt 641.", "Hemmeler", {"entry_type": "person"})
        self.assertEqual((r["entry_type"], r["forename"]), ("person", "Rosine"))


if __name__ == "__main__":
    unittest.main()
