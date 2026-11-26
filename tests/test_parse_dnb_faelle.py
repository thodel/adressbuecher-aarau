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

    def test_doppelstrich_setzt_firma_fort(self):                # Issue #3
        firma = {"entry_type": "firma"}
        r = self.p.parse_entry("— — Fabrikgebäude, Bureau [tel]. Laurenzenvorstadt 773.", "Chocolat Frey A.-G.", firma, origin_dot=True)
        self.assertEqual((r["entry_type"], r["forename"], r["occupation_raw"], r["origin_raw"]),
                         ("firma", "", "Fabrikgebäude, Bureau", ""))
        r = self.p.parse_entry("*— — Filiale. Spitalgäßli 1769.", "Konsumverein Aarau", {"entry_type": "institution"}, origin_dot=True)
        self.assertEqual((r["entry_type"], r["forename"]), ("institution", ""))
        for t in ("— — Restaurant zum Bahnhof. Hintere Bahnhofstraße 1034.", "*— — Kosthaus. Scheibenschachen 1671.",
                  "— — Schuhmacher, Schmiedgasse 391.", "*— — & Cie., Lack- und Farbfabrik [tel]. Obere Vorstadt 534."):
            self.assertEqual(self.p.parse_entry(t, "X", {"entry_type": "person"}, origin_dot=True)["forename"], "", t)

    def test_doppelstrich_mit_vorname_bleibt_person(self):       # Issue #3
        r = self.p.parse_entry("— — Oskar, Seidenbandfabrikant, Schmiedgasse 384.", "Frey", {"entry_type": "firma"}, origin_dot=True)
        self.assertEqual((r["entry_type"], r["forename"]), ("person", "Oskar"))
        r = self.p.parse_entry("—— Rosine, Näherin, hintere Vorstadt 641.", "Hemmeler", {"entry_type": "person"})
        self.assertEqual((r["entry_type"], r["forename"]), ("person", "Rosine"))
        r = self.p.parse_entry("— — Anna. Mercerie- und Lingeriegeschäft.", "Dürr", has_address=False)
        self.assertTrue(r["forename"].startswith("Anna"))


class HeimatortOderBeruf1913(unittest.TestCase):
    def setUp(self):
        self.p = _parse()

    def fields(self, t, prev=""):
        r = self.p.parse_entry(t, prev, origin_dot=True)
        return r["forename"], r["occupation_raw"], r["civil_status"], r["origin_raw"], r["_addresses"][0][1]

    def test_ohne_heimatort(self):
        self.assertEqual(self.fields("Stauffer-Wildi, Albert, Bankbeamter. Bahnhofstraße 590."),
                         ("Albert", "Bankbeamter", "", "", "Bahnhofstraße"))
        self.assertEqual(self.fields("Meier, Anna, Privatin. Halden 12."), ("Anna", "", "Privatin", "", "Halden"))
        self.assertEqual(self.fields("Meier, Anna, Witwe, Wäscherin. Halden 12.")[1:4], ("Wäscherin", "Witwe", ""))
        self.assertEqual(self.fields("— -Herzog, Marie. Zelglistraße 1700.", "Urech")[0], "Marie")

    def test_heimatort_bleibt(self):
        self.assertEqual(self.fields("— Elisabeth, Küttigen. Hammer 178.", "Frey")[3], "Küttigen")
        self.assertEqual(self.fields("Klay, Ludwig, Bäriswil (Bern). Zollrain 63.")[3], "Bäriswil")
        self.assertEqual(self.fields("Müller, Hans, Kaufmann, St. Gallen. Westallee 5.")[1:4], ("Kaufmann", "", "St. Gallen"))
        self.assertEqual(self.fields("— Hedwig, Ladentochter. Ober-Erlinsbach. Pelzgasse 106.", "X")[1:4],
                         ("Ladentochter", "", "Ober-Erlinsbach"))
        self.assertEqual(self.fields("Huber, Karl, Schlosser, Darmstadt. Bahnhofstraße 5.")[3], "Darmstadt")

    def test_berufe_gross_geschrieben_und_ohne_endung(self):   # Issue #6
        for t in ("Aeschbach-Urech, Friedrich, Maschinenfabrik und Eisengießerei, Bureau [tel]. Torfeldstraße 942.",
                  "Hagmann-Stolz, Adolf, Schuhhandlung, Filiale. Hint. Vorstadt 357.",
                  "Rennhart-Maier, Martin, Professor. Entfelderstraße 1391.",
                  "Haberstich, Gottlieb, Kupferschmied. Schmiedgasse 389.",
                  "Renold, R., Fabrikants Erbschaft, zum Schloßgarten [tel]. Laurenzenvorstadt 701."):
            self.assertEqual(self.fields(t)[3], "", t)

    def test_orte_mit_berufsendung(self):                      # Issue #6
        for t, o in (("Huber, Karl, Schlosser, Estavayer. Bahnhofstraße 5.", "Estavayer"),
                     ("Huber, Karl, Schlosser, Savognin. Bahnhofstraße 5.", "Savognin"),
                     ("Huber, Karl, Schlosser, Luzern und Schwyz. Bahnhofstraße 5.", "Luzern und Schwyz")):
            self.assertEqual(self.fields(t)[3], o, t)
        self.assertFalse(self.p.looks_like_place("Agent"))


class BerufVorPunkt(unittest.TestCase):                            # Issue #5
    def setUp(self):
        self.p = _parse()

    def test_beruf_nicht_in_der_strasse(self):
        r = self.p.parse_entry("Villiger, Anton, Geschäftsführer d. Aarg. Nachrichten. Bahnhofstraße 658.", "")
        self.assertEqual((r["occupation_raw"], r["_addresses"]), ("Geschäftsführer d. Aarg. Nachrichten",
                                                                  [("", "Bahnhofstraße", "658")]))
        r = self.p.parse_entry("Lenzi, Hans, Lebens- und Unfallversicherung. Auswanderung. Zollrain 12.", "")
        self.assertEqual(r["_addresses"][0][1], "Zollrain")

    def test_von_ort_vor_punkt_ist_heimatort(self):
        r = self.p.parse_entry("Huber, Jakob, Obsthändler, von Fahrwangen. Golattenmattgasse 229.", "")
        self.assertEqual((r["occupation_raw"], r["origin_raw"], r["_addresses"][0][1]),
                         ("Obsthändler", "Fahrwangen", "Golattenmattgasse"))

    def test_kuerzel_und_nummern_trennen_nicht(self):
        for t, street in (("Meier, Hans, Hafner, vord. Vorst. 12.", "vord. Vorst."),
                          ("Meier, Hans, Architect, Bureau Bahnhofstr. 1020, Wohnung Bachstraße 5.", None),
                          ("Meier, Hans, Oberarzt an der Krankenanstalt. Nr. 1186.", None)):
            r = self.p.parse_entry(t, "")
            self.assertNotIn("beruf vor punkt", r["residual"], t)
            if street:
                self.assertEqual(r["_addresses"][0][1], street)


class Legende(unittest.TestCase):                                  # Issue #4
    def setUp(self):
        self.p = _parse()

    def test_legende_ist_kein_eintrag(self):
        rows = self.p.parse_page("Alphabetisches Verzeichnis\n* = Im Handelsregister eingetragen. [tel] = Telephon.\n"
                                 "Meier, Hans, Schreiner, Halden 12.\n", "1913", 137)
        self.assertEqual([r["surname"] for r in rows], ["Meier"])

    def test_rubriken_nach_der_legende(self):
        text = ("Die\nGeschäfts- und Gewerbetreibenden\nin alphabetischer Folge der Berufsklassen.\n"
                "* = Im Handelsregister eingetragen.\nAdvokaten.\n(Siehe Fürsprecher.)\nÄrzte.\n"
                "Frey, Konrad, Dr. med., Laurenzenvorstadt 706.\nAgenturen.\nDolder, J.,* Bahnhofstrasse 610.\n")
        rows = self.p.parse_page(text, "1901", 148, section="berufe")
        self.assertEqual([(r["surname"], r["heading"]) for r in rows], [("Frey", "Ärzte"), ("Dolder", "Agenturen")])

    def test_agent_zeile_bleibt_keine_rubrik(self):
        self.assertFalse(self.p.is_heading("Generalagentur der Basler Lebensversicherungen"))
        self.assertTrue(self.p.is_heading("Agenturen."))


class Institutionen(unittest.TestCase):
    def setUp(self):
        self.p = _parse()

    def test_institution_bleibt_ganz(self):
        r = self.p.parse_entry("Kredit-Anstalt, Aargauische, [tel] Laurenzenvorstadt 700.", "")
        self.assertEqual((r["entry_type"], r["surname"], r["alliance_name"], r["forename"], r["occupation_raw"]),
                         ("institution", "Kredit-Anstalt", "", "", "Aargauische"))
        r = self.p.parse_entry("Lehrerinnen-Seminar, Laurenzenvorstadt 802.", "")
        self.assertEqual((r["entry_type"], r["surname"], r["alliance_name"]), ("institution", "Lehrerinnen-Seminar", ""))
        r = self.p.parse_entry("Kreiskommando, Laurenzenvorstadt 714.", "")
        self.assertEqual(r["entry_type"], "institution")

    def test_geschaeft_und_aktiengesellschaft(self):
        r = self.p.parse_entry("Eisen- und Quincailleriehandlung, Kronengasse 41.", "")
        self.assertEqual((r["entry_type"], r["surname"]), ("firma", "Eisen- und Quincailleriehandlung"))
        r = self.p.parse_entry("Conradin Zschokke A. G. Technisches Bureau, Laurenzenvorstadt 9.", "")
        self.assertEqual(r["entry_type"], "firma")

    def test_namen_bleiben_personen(self):
        for t, s, a in (("Neuburger-Imhof, Albert, Apotheker, Graben 215.", "Neuburger", "Imhof"),
                        ("Wyler-Guggenheim, Raphael, Kaufmann, Graben 7.", "Wyler", "Guggenheim"),
                        ("Kurz-Korkhaus, Elsbeth, Witwe, Laurenzenvorstadt 710.", "Kurz", "Korkhaus")):
            r = self.p.parse_entry(t, "")
            self.assertEqual((r["entry_type"], r["surname"], r["alliance_name"]), ("person", s, a), t)
        r = self.p.parse_entry("Muster-Bank, Emil, Lithograph, Gais 487.", "", forenames={"Emil"})
        self.assertEqual((r["entry_type"], r["alliance_name"]), ("person", "Bank"))

    def test_umbrochene_zeile_gehoert_zum_vorigen_eintrag(self):
        text = ("Pfau, Joh. Jakob, Direktor der aarg.\nKreditanstalt, Laurentenvorst. 1340.\n"
                "— Joh. Jakob, Bankangestellter, Laurenzenvorst. 100.\n"
                "Vallentin, Emil, Gießer, Milchgasse 137.\nVersicherungsamt, Bahnhofstraße 606.\n")
        rows = self.p.parse_page(text, "1896", 140)
        self.assertEqual([(r["surname"], r["forename"]) for r in rows],
                         [("Pfau", "Joh. Jakob"), ("Pfau", "Joh. Jakob"), ("Vallentin", "Emil"), ("Versicherungsamt", "")])
        self.assertEqual(rows[0]["occupation_raw"], "Direktor der aarg. Kreditanstalt")

    def test_rollenwort_nur_als_ganzes_wort(self):
        r = self.p.parse_entry("Lenzin, Joseph, Bureauangestellter, Pelzgasse 92.", "")
        self.assertEqual((r["occupation_raw"], r["_addresses"]), ("Bureauangestellter", [("", "Pelzgasse", "92")]))
        r = self.p.parse_entry("Meier, Hans, Schreiner, Wohnung Zollrain 181; Werkstätte Hammer 12.", "")
        self.assertEqual([a[0] for a in r["_addresses"]], ["wohnung", "werkstätte"])


if __name__ == "__main__":
    unittest.main()
