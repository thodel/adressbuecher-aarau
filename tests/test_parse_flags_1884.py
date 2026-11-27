"""Fälle aus den Flags vom 06.11.2026 (1884, data/review/flags.csv) und verwandte Muster in allen Bänden,
scripts/04_parse.py.

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


LEX = {"Hrch", "Ida", "Elise", "Fanny", "Emil", "August", "Emma", "Karl", "Gottfried", "William", "Samuel",
       "Heinrich", "Jakob", "Aarau", "Bureau"}


class Flags1884(unittest.TestCase):
    def setUp(self):
        self.p = _parse()

    def rows(self, text, prev=""):
        return self.p.parse_page(text, "1884", 31, prev_surname=prev, forenames=LEX)

    def test_doppelstrich_ist_gedankenstrich(self):
        rows = self.rows("Döhnel, August, Schuhmacher, Golattenmattgasse 239.\n"
                         "  -- Emma, Spetterin, von Badenweiler (Grßhzth. Baden), Halden 267.\n"
                         "Dubs-Schärli, Jakob, Müller, im Hammer 182.\n"
                         "  --  -Walther, Karl, Metzger u. Speisewirth, v. Küttigen, Rathhausg. 32.\n"
                         "*- -Rüegg & Cie., Seidenbandfabrikation, Bahnhofstraße 566.")
        self.assertEqual([(r["surname"], r["alliance_name"], r["forename"]) for r in rows],
                         [("Döhnel", "", "August"), ("Döhnel", "", "Emma"), ("Dubs", "Schärli", "Jakob"),
                          ("Dubs", "Walther", "Karl"), ("Dubs", "Rüegg & Cie.", "Seidenbandfabrikation")])

    def test_seitenzahl_mit_halbgeviertstrich_bleibt_kopf(self):
        self.assertEqual(self.rows("Meier, Hans, Schreiner, Halden 12.\n– 135 –"), self.rows("Meier, Hans, Schreiner, Halden 12."))

    def test_seitenzahl_mit_bindestrich_ist_kein_eintrag(self):
        rows = self.p.parse_page("Meier, Hans, Schreiner, Halden 12.\n- 136 -\n\nKath. Vereinshaus, Kasinostraße 654.\n-- 201 --",
                                 "1913", 178, forenames=LEX)
        self.assertEqual([r["surname"] for r in rows], ["Meier", "Kath. Vereinshaus"])

    def test_verlorener_gedankenstrich_vor_allianzname(self):
        rows = self.rows("Wehrli, Emil, Gärtner, Halden 1.\n*-Säuberli, Emil, Bäckermeister, Rathausgasse 30.\n"
                         "— -Schwarz, Emil, Briefträger, Stritengäßchen 1213.\n- Wilhelm, Schreiner, Halden 2.")
        self.assertEqual([(r["surname"], r["alliance_name"], r["forename"], r["citizen_flag"]) for r in rows],
                         [("Wehrli", "", "Emil", ""), ("Wehrli", "Säuberli", "Emil", "1"), ("Wehrli", "Schwarz", "Emil", ""),
                          ("Wehrli", "", "Wilhelm", "")])

    def test_trennstrich_am_zeilenende_bleibt_wort(self):
        t = self.p.prenormalise("Einwohnergemeinde Aarau. Bezirksschulgebäude u. Lehrerinnen-\n  -Seminar.")
        self.assertNotIn("—", t)

    def test_name_mit_von_ist_eintragsanfang(self):
        rows = self.rows("  — Ida, Damenschneiderin, von Erlinsbach, Schachen 737.\n"
                         "Helm-von Arx, Elise, Wittwe, Wollenwaarenhdlg., von Oerlikon (Zürich),\n"
                         "    Zollrain 52.\n"
                         "  — Fanny, Modistin, von Oerlikon (Zürich), Zollrain 52.", prev="Heller")
        self.assertEqual([(r["surname"], r["alliance_name"], r["forename"], r["street_raw"], r["building_no"]) for r in rows],
                         [("Heller", "", "Ida", "Schachen", "737"), ("Helm", "von Arx", "Elise", "Zollrain", "52"),
                          ("Helm", "", "Fanny", "Zollrain", "52")])

    def test_partikel_am_anfang(self):
        for text, name in (("Von Steiger, William, Techniker, Rain 878.", "Von Steiger"),
                           ("Von der Crone, Heinrich, Schriftsetzer, Hintere Vorstadt 360.", "Von der Crone"),
                           ("Da Col, Simon, Cementarbeiter, Halden 290.", "Da Col")):
            rows = self.rows("Meier, Hans, Schreiner, Halden 12.\n" + text)
            self.assertEqual(rows[-1]["surname"], name, text)

    def test_ganze_zeile_mit_adresse_wird_nicht_verworfen(self):
        rows = self.rows("Meier, Hans, Schreiner, Halden 12.\nAargauische Bank, [tel] Bahnhofstraße 511.")
        self.assertEqual(rows[-1]["surname"], "Aargauische Bank")
        self.assertEqual(rows[-1]["entry_type"], "institution")

    def test_unterzeile_einer_koerperschaft_bleibt_weg(self):
        rows = self.rows("Meier, Hans, Schreiner, Halden 12.\nSchützengesellschaft Aarau. Präsident: Rud. Hegnauer, Hammer 194.")
        self.assertEqual(len(rows), 1)

    def test_komma_nach_familienname_fehlt(self):
        r = self.rows("Frymann Gottfried, Part., Hammer 188.")[0]
        self.assertEqual((r["surname"], r["forename"], r["civil_status"]), ("Frymann", "Gottfried", "Part."))
        for text, name in (("Konsumverein Aarau, Bahnhofstraße 1.", "Konsumverein Aarau"),
                           ("Lagerhaus Aarau, Bahnhof 832.", "Lagerhaus Aarau")):
            self.assertEqual(self.rows(text)[0]["surname"], name, text)

    def test_allianzname_ohne_bindestrich(self):
        rows = self.rows("*Erismann, Samuel, Friedensrichter, Bachstraße 1033.\n"
                         "  — Leutwyler, Samuel, Taglöhner, von Gontenschwyl, in der Gais 485.")
        r = rows[-1]
        self.assertEqual((r["surname"], r["alliance_name"], r["forename"], r["occupation_raw"]),
                         ("Erismann", "Leutwyler", "Samuel", "Taglöhner"))
        self.assertEqual(r["parse_confidence"], "medium")

    def test_kein_allianzname_bei_amt_oder_klammer(self):
        rows = self.rows("Aarg. Forstverwaltung, Bahnhofstraße 1.\n  — Oberforstamt, Bureau, Bahnhofstraße 1.")
        self.assertEqual(rows[-1]["alliance_name"], "")
        rows = self.rows("Meier, Hans, Schreiner, Halden 12.\n  — (Merz), Maria, Damenschneiderin, Halden 12.")
        self.assertEqual(rows[-1]["alliance_name"], "")


if __name__ == "__main__":
    unittest.main()
