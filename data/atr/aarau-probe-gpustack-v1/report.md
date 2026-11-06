# ATR batch — aarau-probe-gpustack-v1

- pages: **20**
- started: 2026-11-06T12:08:33+00:00
- wall time: 26.1 min

| model | read | skipped | failed | empty | looped | arguing | cut off | chars/page | s/page | wall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `qwen3.8-27b` | 20 | 0 | 0 | 1 | 0 | 0 | 1 | 2354 | 72.9 | 24.3 min |
| `qwen3-vl-30b-a3b-instruct` | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 2428 | 5.4 | 1.8 min |

**These columns are not quality.** There is no ground truth in this run, and characters per page measures how much a model wrote, not how much of it is right — a model that hallucinates fluently leads this table. Comparing the readings is the point; the numbers only say what each run cost and whether it completed. Measuring accuracy needs transcribed lines and `eval/linebench.py`.

## Readings that were cut off

- `qwen3.8-27b`: 1 of 20 page(s)
  - 1896_p176

These pages hit the model's token ceiling and stop mid-text. The request succeeded and the text is real — there is just less of it than the page has, and it reads like a model that gave up rather than one that was interrupted. Raise the ceiling — `ATR_VLLM_MAX_NEW_TOKENS` on the gateway, `GEMINI_MAX_TOKENS` for an external reader — delete the affected results and re-run: the batch re-reads only what is missing. A reasoning model spends the same ceiling on thinking before it writes a character, so lowering the thinking level buys page as surely as raising the ceiling does (#611) — check the thinking level before buying tokens.

## Pages that came back empty

- `qwen3.8-27b`: 1 of 20 page(s) (5%)
  - 1896_p176

These are successes by every signal this runner has: a 200, no error, both files on disk, and `is_complete` will skip them on every later run. **Look at the images before reading anything into the number.** A blank verso or an envelope flap is genuinely empty, and knowing how many the corpus holds is worth having before extrapolating a cost per page. A *written* page that comes back empty is a defect no other column here would ever show — the segmenter found no lines on it (gateway), or the model answered the page with nothing at all (external reader). The second is a reading the prompt refused, not a page the model could not fetch: compare the same pages under another prompt before concluding anything about the corpus.

## Readings

The texts themselves, so the comparison the table refuses to make can be made by eye. **Read to the end of each one**: a page that hit the token ceiling comes back as an ordinary success and stops mid-sentence, and it is marked here where that happened.

### `qwen3-vl-30b-a3b-instruct`

#### 1884_p022 (2694 characters)

~~~text
18
*Dürr, Karl August, Sohn, Kaufmann, Rathhausgasse 19.
* — =Graden, Hieronimus, Schlosser, Abelbändli 174.
* — =Wüthrich, Gottlieb, Taglöhner, Stadthof 92d.
* — Johann, Schneidermeister, Halben 274.
* — =Siebenmann, Karolina, Registrator's Wittwe, Abelbändli 171.
* — Emil, Sohn, Partik., Abelbändli 171.
* — Gottfried, Schuhmachergehülfe, Halben 271.
* — =Lüscher, Gabriel, Gemisehändler, Rainstraße 825.
* — =Seiler, Hermann, Malermeister, Casinostraße 1130.
* — =Haaf, Schreinermeister, Milchgasse 161.
* — =Haaf, Partik., Ziegelrain 704.
* — =Bürgi, Elisabeth, Wittwe, Ziegelrain 704.
* — =Ackermann, Katharina, Schreiners Wittwe, Milchgasse 161.
* — Lisette, Zettlerin, Halben 279.
Ehner-Furter, Hermann, Schriftsetzer, von Wyden, Pelzgasse 65.
— =Brändli, Elis., Wittwe, Fabrikarb., v. Birkingen (Baden), Isthg. 3.
— Josef, Schriftsetzer, von Birkingen (Baden), Rathausgasse 3.
Eger-Ehner, Theophil, Schneider, von Riehen (Basel), Rainstraße 834.
*Eggen-Sulzer, Ed., Kaufmann, Colonialwaarenhdlg., Laurentzentborg. 119b.
Eggimann-Job, Joh., Wirth, v. Sumiswald (Bern), Bahnhofstraße 1025.
Eglt-Lehmann, Heinrich, Partik., von Wald (Zürich), Zollrain 178.
Eglinger, Mina, Privatin, von Basel, in der Gais 486.
Egloff-Weier, Fr., Postangestellt., v. Wettingen, Speisewirthsch., Schach. 731.
— Georg, Gärtner, von Tägerweilen (Thurg.), vor dem Halbenthör 1009.
— =Allenpach, Maria Magdalena, Wittwe, Partik., von Tägerweilen (Thurgau), vor dem Halbenthör 1109.
*Ehrsam-Landolt, Jakob, Bäckermeister, Zollrain 51.
* — =Wehrli, Alfred, Schneidermeister, Igelweid 631.
* — =Andres, Daniel, Postoffiziant, neues Quartier 975.
* — Jda, Partik., Bachstraße 1040.
* — Emilie, Partik., Bachstraße 1040.
Eichenberger, Maria Anna, Taglöhnerin, von Reinach, Kirchgasse 10.b.
— =Flad, Rudolf, Zimmermann, von Reinach, Milchgasse 154.
— =Fischer, Gottlieb, Schreiner, von Beinwyl, obere Vorstadt 921.
— =Joho, Rudolf, Schuhmacher, von Reinach, Kirchplatz 167b.
Elsasser-Riburg, Gottlieb, Küfermeister, von Unterkulm, Halben 286.
— Ludwig, Postamenter, von Unterkulm, Igelweid 632.
Eng-Käser, Heinrich, Schuhmacher in der Schuhfabrik, von Stüttlingen (Soloth.), Milchgasse 152.
Engel, Karl, Bergolder, von Schwörstadt (Sachsen), Hammer 188.
Engesser-Brunner, Jos., Schneider, v. Durchhausen (Wrtmb.), Rathg. 45.
Erdin-Zumsteg, Siegfr., Taglöhner, v. Ganjingen, hintere Vorstadt 693.
*Eriszmann, Samuel, Friedensrichter und Armenpfleger, Bachstraße 1033.
* — =Zndermayer Abraham, Dekonom, Bachstraße 1033.
— =Sager, Samuel, Güterexpedient, von Gontenschwyl, in der Gais 485.
— =Leutwyler, Samuel, Taglöhner, von Gontenschwyl, in der Gais 485.
— =Hügi, Samuel, Holzpalter, von Schlozrued, Kirchgasse 10.a.
~~~

#### 1884_p040 (2632 characters)

~~~text
36
Morgenthaler. — Müller.

Morgenthaler, Maria, Damenschneiderin, von Strengelbach, Golattenmattgasse 237c.
— Elise, Spetterin, von Madiswyl (Bern), im Hammer 184.
— Mösch-Gäbler, Martin, Kanzleisekretär, von Frick, Bachstraße 1155.
— Kanz, Franz, Kutscher, von Frick, Laurenzenvorstadt 552.
*Mühlberg-Codognari, Fritz, Professör, Rainstraße 878.
— Amsler, Theodor, Postkontrolleur, von Muri, neues Quartier 983.
*Müller-Locher, Wilhelm, Kaufmann, Schloßplatz 195.
* — Haberstich, Friedrich August, Kaufmann, Bahnhofstraße 656.
* — Gamper, Samuel, Spezereihändler, Holzmarkt 665.
* — Woodtke, Jakob, Gemeindeweibel, Rathausgasse 176.
* — Hürner, Eduard, Schirmmacher, Rathausgasse 30.
* — Urech, Küfers Wittwe, Partik., Halben 286.
* — Julius, Partik., Schachen 723.
* — Theodor, Partik., Schachen 723.
* — Gásar, Regt., Schachen 723.
* — Emma, Haushälterin, Schachen 723.
* — von Däniken, Friedrich, Gepäckträger und Dekonom, Schachen 725.
* — Rothplek, Arnold, Baumeister, Pelzgasse 124.
— Suter, Jakob, Lithograph, von Lenzburg, vordere Vorstadt 894.
— Kramer, Joß, Schneidemeister, von Büron (Luzern), Ziegelweid 636.
— Bonäsch, Jakob, Buchbinder, von Unterfultm, hintere Vorstadt 642.
— Eggenschwyler, Johann, Postcommiss, von Muri, Rathausgasse 47.
— Balmer, Alfred, Schriftseker, v. Weinfelden (Thurgau), Milchg. 79.
— Samuel, Maschinenpuzer, von Unterfultm, im Weinberg 335.
— Hofer, Johann, Auffeher von Hirfchthal, Ziegelrain 707b.
— Rauber, Jakob, Taglöhner, von Bözberg, obere Vorstadt 964.
— Berner, Anna Maria, Taglöhnerin von Kulm, Kirchplatz 167a.
— Bildi, Karoline, Wittwe, Partik., von Möttlingen (Württemberg), Halben 285.
— Albertine, Damenschneiderin, von Möttlingen (Württemberg), Halben 285.
— Otto, Commis, von Möttlingen (Württemberg), Halben 285.
— Anna, Fabrikarbeiterin, von Unterfultm, Laurenzenvorstadt 376.
— Häckler, Barbara, Wittwe, Partik., von Kulm, Teil 448.
— Maria, Spetterin, von Bözberg, Ziegelrain 702.
— Maria, Näherin, von Hirfchthal, Rainstraße 875.
— Rintker, Elise, Staatsweibels Wittwe, von Biberstein, vordere Vorstadt 905.
— Elise, Glätterin, von Biberstein, vordere Vorstadt 905.
— Johann, Ingenieur, von Linn, Pelzgasse 129.
— Vogler, Heinrich, Buchbinder, von Unterfultm, im Weinberg 321.
— Eichenberger, Johann, Schreinermeister, von Oberfultm, Halben 290.
— Widmer, Gottlieb, Schuhmacher, von Unterfultm, Milchgasse 143.
— Karl, Reiseprediger, von Binzen (Großh. Baden), h. d. Platz 214.
— Schnider, Susanna, Haushälterin, von Bür, Milchgasse 146.
— Hunn, Verena, Partik., von Unterfultm, Milchgasse 152.
— Maria, Taglöhnerin, von Unterfultm, vor dem Halbenthor 802.
[spalte 2]
~~~

#### 1884_p070 (3282 characters)

~~~text
66
977 Stigeler-Schaub, Jos., Zeughaus-
Direktor, von Reffingen.
978 Ernst-Pfisterer, Bierbrauers Wwe.,
Giseller.
979 Thut-Laufer, Rud., Regt., von
Oberentfelden.
980 Derselbe, Scheune.
981 Mayer-Richner, Raap., Professör,
von Baden.
982 Derselbe, Holzhaus.
983 Bed-Braun, Friedr., Sattler.
984 Gemeinde Aarau, Brunnenhaus.
985 Rieding, H., Zimmermstr., Schopf.
986 Abgetragen (an dessen Stelle
Nr. 1171 (Bierfeller).
987 Gemeinde Aarau, Brunnenhaus.
988 Hagnauer-Wildberger, Barbara,
Wittwe, Partit.
989 Diefelbe.
990 Rothplek, Julius, Maler.
991 Derselbe, Holzhaus.
992 Schäfer, Jda, Partit.
993 Behrlt-Herzog, Rud., Geschäfts-
führer, von Rüttigen.
994 Derselbe, Gartenhaus.
995 Zschoppe-Sauerländer, Guido,
Buchhändler.
996 Fischer-Schmidlin, Bertha, Part.
997 Diefelbe, Holzschopf.
998 Gift-Büchli, Emil, Mechaniker.
999*Schröder, Wilh., Fabrikant, von
Grefeld, in Zürich.
1000 Derselbe, Wasch- und Holzhaus.
Goldern.
1001 Siebenmann-Steiner, Jb., Dekon.
1002 u. 3 Derselbe, Deconomiegebäude.
Winfenhof.
1004 Künifer, Friedrich, Bierbrauer,
Fazremife.
1005 Künifer, Abrah. u. Jb., Dekonom.
1006 u. 7 Diefelben, Scheune.
1008 Diefelben, Holzschopf.
1009 Diefelb., Werkstätte u. Waschhaus.
1010 Künifer, Friedr.
1011 Derselbe, Holzhaus.
1012 Derselbe, Trinthalie.
Bahnhofstraße.
1013 Lüscher-Zahler, Rud., Notar,
Notariats-Bureau.
1014 Derselbe, Waschhaus.
1015 Evangelische Kapelle.
1016 Frei-Feer, Bertha, Fabrikants
Wittwe, Fabrik.
1017 Diefelbe, Maschinenhaus.
1018 Diefelbe.
1019 Evangelischer Verein.
1020 Häfeler-Hunziker, K., Kaufmann.
1021 Derselbe, Hintergebäude.
1022a Jäger-Hägig, Joh., Maurer, von
Ueferfihl (Zürich).
1022b Wildi-Leuthard, B., Schneiders
Wittwe, von Beltlheim.
1023 Siebenmann-Seiler, Katharina,
Benedikts Wittwe.
1024 Abgetragen (an dessen Stelle 1074).
1025 Spengler-Lienhard, F., Mezger.
Bachstraße.
1026*Gemeinde Aarau.
1027*Diefelbe, Mühllecheune.
1028 Schmidt-Siebenmann, A., Sattler.
1029 Derselbe, Werkstätte.
1030 Gemeinde Aarau, Schuppen.
1031 Senn-Zubler, Johann, Küfer,
von Hottwyl.
1032 Siebenmann-Brunnhofer, Otto,
Schloffer.
1033 Grismann, Sl., Friedensrichter
und Armenpfleger.
1034 Derselbe, Scheune.
1035 Imhof-Ammann, Ernkt, Fabrikt.
1036 u. 37 Andres-Bircher, F., Gafner,
Gafnerci und Holzhaus.
1038 Brunner, Gottfried, Partit.
1039*Schmuziger-Kern, K., Baummtr.
1040 Häfeler-Oberlin, Albert, Postad-
juncts Erben.
1041 Herzog, Th., Dekonom, Scheune.
1042 Derselbe, Remife.
1043*Herzog, Th., Fakob und Anna.
1044 u. 45 Diefelb., Deconomiegebäude.
1046 Herzog, Hans, General, Scheune.
1047 Derselbe, Eidg. Artillerie-Bureau.
1048*Herzog, Theodor und Mitthaftc.
1049 u. 50*Diefelben, Fabrikgebäude.
1051 Wyfer-Müller, Alf., Seidenfärcer.
1052 Derselbe.
1053 Herzog, Theodor und Mitthaftc,
Holzhaus.
1054 Reiner-Scheuermann, Elife,
Fabrikants Wittwe.
1055 Wyfer-Müller, Alf., Seidenfärcer.
1056 Derselbe, Färcerei.
1057 u. 58 Derselbe, Färcberei.
1059 Frei-Volley, Edwin, Kaufmann.
1060 Derselbe, Scheune.
1061 Brad.
1062 Frei-Volley, Edwin, Kaufmann.
1063*Schäfer-Troller, Adolf, Architekt,
(in der Gais).
1864* Derselbe, Holzschopf (in der Gais).
1865 Derselbe, Barafe
1066*Minifer-Groß, Friedr., Bierbrauer
(Mezzergaffe).
1067 Dehler-Frei, August, Rebhäuschen
(Weinberg).
1068 Burkhard, Ferd., Coiffeur, Reb-
häuschen (Weinberg).
~~~

#### 1884_p084 (3477 characters)

~~~text
80
Müll-Verkäufer.
Im Stadtbezirk.
Andres-Bircher, Maria, Milchgasse 148.
Baumann, Kaspar, Casinostraße 660.
Berchtold, St., vor dem Haldenthor 773.
Bircher, Andreas, im Tannergut 302.
Birrmann, A., Müller, hint. Vorst. 684.
Brach, Abraham, Deconom, Bachstr. 1061.
Brunnerhofer, Magdalena, Halden 253.
Dubs, Jakob, Müller, im Hammer 182.
Erlsmann, A., Deconom, Bachstr. 1033.
Etter, Reinhard, Laurenzenvorstadt 361.
Fehlmann, J., Decon., Roggenhausen.
Fischer, Th., Bierbrauer, Zollrain 179.
Gantner, M., Deconom, Schloßpl. 197.
Gautschi, R., Deconom, in der Telli 460.
Güyer, A., Fabrikant, in der Telli 456.
Herzog, Th., Deconom, Bachstraße 1045.
Keller, J., Deconom, neues Quart. 1145.
Keller, W., Deconom, Rainstraße 850.
Maurer, Philipp, Milchgasse 73.
Müller, Fr., Deconom, Schachen 725.
Rinifer, Herm., neues Quartier 1195.
Rinifer, Abraham, Binjenhof 1005.
Rüetschi, G., Sohn, Abelbändli 81.
Schär, Friedrich, Holzmarktplaz 663.
Siebenmann, J., Decon., Goldern 1001.
Steiner, E., Decon., Laurenzenvorst. 547.
Waltherr-Schakmann, Gottl., Deconom,
Rainstraße 856.
Waltherr-Matter, Jakob, Deconom,
Schachen 739.
Weber, Wilhelm, im Weinberg 337.
Widli, St., Schreiner, Ziegelrain 716.
Wullschleger, H., Deconom, Ziegler. 741.
Außerhalb des Stadtbezirks.
Eng, Jakob, in Stützlingen.
Rohr, Wittwe, " Buchs.
Roth, Jakob, " Röhr.
Hächler, Johann, " " 
Richner, Johann, " " 
Richner, Gottlieb, " " 
Ruef, Friedrich, " " 
Büthrich, Martin, " " 
Berttschi, Johann, " Sühr.
Dietiker, Adolf, " " 
Schmid, Johannes, " " 
Steiner, Gottlieb, " " 
Haberlisch, Gottfr., " Oberentfelden.
Waltherr, Rudolf, " " 
Burger, Gottlieb, " Unterentfelden.
Gerber, Jakob, " " 
Wernli, Louise, " " 
Zimmerli, Maria, " " 
Peyer, Frau, " der Wöschau.
Holliger, Jakob, " Holziken.
Wyß, Christian, " " 
Pfister, Kaspar, " Rupperswyl.
Ryfer, Johann, " Liebegg.
Mineralwasser, künstl. Fabrikation
D. H. Euster, Bahnhofstraße 651.
Modewaaren.
Gottschall, Amalie, Pelzgasse 67.
Häfner, Emma, Wittwe, Rathausg. 23.
Helm, Fanny, Zollrain 52.
Kirchner-Vonwiller, Stda, Kroneng. 42.
Suter, Stda, vordere Vorstadt 666.
Theodor-Hagnauer, Marie, Kroneng. 37.
Widmer, Karoline, vord. Vorstadt 893.
Modistinnen.
Aeschbach, Marie, Mezgergasse 100.
Bryner, Anna, Halden 284.
Gottschall, Amalie, Pelzgasse 67.
Gottschall, Marie, Pelzgasse 67.
Häfner, Emma, Wittwe, Rathausg. 23.
Häfner, Julie, Abelbändli 172.
Helm, Fanny, Zollrain 52.
Kirchner-Vonwiller, Stda, Kroneng. 42.
Lütscher, Charlotte, Halden 279.
Schmidt, Jenny, Rathausgasse 44.
Schmuziger, Mina, Casinostraße 584.
Sennbauer-Gossewitsch, Amalie, Kirch-
plaz 164.
Suter, Stda, vordere Vorstadt 666.
Widmer, Karoline, vord. Vorstadt 893.
Widmer, Marie, vordere Vorstadt 893.
Neubehandlungen.
Bühler, Jakob (Wiener-Neubel), obere
Vorstadt 925.
Camifasca, Franz, Rathausgasse 4.
Gewerbehalle Aarau, Ziegelrain 754.
Strub, Leonhard, Milchgasse 71.
Musikalienhandlungen.
Braut, Charlotte, Holzmarktplaz 661.
Hirsbrunner, Jakob, Halden 255.
Widmer, F. S., Casinostraße 573.
Mühlenbaugeschäft.
Märki u. Haller, Bachstraße 933.
Müller.
Birrmann, Albert (obere Mühle), hintere
Vorstadt 684.
Dubs, Jakob (untere Mühle), im
Hammer 182.
Ziegler-Enkli, Lina, Wittwe (mittlere
Mühle), Stadthof 95.
Räherinnen.
Blaser, Elisabeth, Pelzgasse 68.
Brunnerhofer, Elise, Rainstraße 875.
Fischer, Emilie, Laurenzenvorstadt 548.
Frieden, Agatha, Stadthof 92.
Gantner, Elise, Kirchgasse 8a.
Häuptli, Barbara, Halden 290.
Hediger, Lisette, Ziegelrain 709.
Seller, Anna, Schachen 737.
~~~

#### 1888_p039 (2192 characters)

~~~text
Haus-
Nr.
356. Hunziker, Emil Guido, Rentier.
Räfer-Rühr, Ulrich, Kutscher, von Melchnau (Bern).
357.+ Derfelbe. Remife.
358.+ Derfelbe. Waschhaus.
359.+ Derfelbe. Sommerhaus.
360.* Studer=Schram, Theodors, Arzts Erbschaft.
Kurz und Stierli, Advokatur= und Notariatsbüreau (Inhaber C. Kurz,
Fürsprch und Notar und G. L. Stierli, Fürsprch).
Lüscher-Wülser, Lisette, Part., von Aarburg.
Mürtz, Jda, Drs., Part.
Kurz, Erwin, Fürsprch, von Schwamendingen (Zürich).
Wehrli, Karl Emil, Architekt, von Hönng (Zürich).
Rettiger-Bertschinger, Arnold, Procurist, von Liestal.
361.* Diefelbe.
Etter-Hägi, Reinhard, Milchverkäufer, von Langridentbach (Thurgau).
Wirz-Widmer, Adolf, Postkondukteur, von Menziken.
362.* Diefelbe.
Wernli-Reinhard, Kaspar, Weichenwärter, von Thalheim.
Schmid, Rosa, Damenschneiderin, von Gipf.
363.* Diefelbe.
Frey-Häuptli, Gottlieb, Eisenbahnkondukteur, von Biberstein.
364.* Wydler-Frey, Med. Drs. Erbschaft.
Wydler, Mathilde, Partif.
Frey-Hagnauer, Konrad, Dr. Med., praktischer Arzt.
365. u. 366. + Diefelbe. Scheune.
367.* Schmitter-Schmidlin, Friedrich, Fabrikants Erbschaft.
Tanner, Erwin, Fürsprch, (Advokaturbureau).
Zehnder-Siebenmann, Traugott, Part., von Birrmenstorf.
368. 369. 370. + Diefelbe. Deconomiegebäude.
371. Hunziker-Fleiner, Hermann, Privatier.
Fahrländer-Hunziker, Karl, Dr. Jur. Regierungsrath, von Laufenburg.
372.+ Derfelbe. Holzhaus und Remife.
373.+ Hunziker-Züst, Guido, Rentier. Comptoir und Magazin.
374. u. 375. Derfelbe. Wohngebäude.
376.* Hunziker-Springer's Erbschaft.
Ruef-Zweifel, Wilhelm, Schlosser, von Rekingen.
Meyer-Hägeli, Alois, Taglöhner, von Büron (Luzern).
Fischer-Roth, Ludwig, Straßenwärter.
Dill-Frei, Joh. Fr. Christoph, Schuster, von Basel.
Zimmerli-Stenz, Eduard, Cementmüller, von Ofringen.
Suter-Arber, Rudolf, Pofamenter, von Gränichen.
Weber-Suter, Joh., Gärtner, von Oberflachs.
Brunnerhofer-Bolliger, Lisette, Fabrikarbeiterin.
Steiner-Haller, Heinrich, Taglöhner, von Rein.
Häufemann-Ruef, Adolf, Taglöhner, von Egliswyl.
Leu-Karrer, Jakob, Taglöhner, von Schlokrued.
Blattner-Hemmeler, Jakob, Maler, von Rüttigen.
Blattner, August, Gerichtskanzlist, von Rüttigen.
Müller-Suter, Jakob, Pofamenter, von Gränichen.
~~~

#### 1888_p092 (2231 characters)

~~~text
74
Andres — Baldeschwylер.

Andres-Baumann, Salome, Wittwe, Milchgasse 140.
X Andres-Bircher, Friedrich, Hafner, obere Vorstadt 916.
Andres-Bircher, Heinrich, Buchbinder, Cajinofstrasse 1176.
Andres-Bircher, Maria, Metzgerei und Milchverkauf, Milchgasse 140.
Andres-Eichelberger, Otto, Hafner, Milchgasse 78.
Andres, Emma, Fabrikarbeiterin, vordere Vorstadt 676.
X Andres, Gottlieb, Fondsverwalter, jenseits der Nare 299 b.
X Andres-Schmid, Jakob, Schreiner, jenseits der Nare 299 a.
Andres-Heinzmann, Maria, Becks Wittwe, jenseits der Nare 299.
Andres, Jakob, Bahngestellter, Halden 256.
Andres-Weier, Samuel, Schlosser, Milchgasse 147.
Andres, Mina, Auffeherin, vordere Vorstadt 676.
Andres, Otto, Sohn, Metzger, Milchgasse 140.
Andres-Ramfeier, Rosina, Gipser's Wittwe, Ziegelrain 709.
X Andres-Weber, Friedrich, Buchhalter, Ziegelrain 709.
Andres-Walter, Verena, Metzgers Wittwe, Halden 256.
X Angst-Häffig, Gottlieb, Negt. von Eglifan, Bibel-Depot und Niederlage technischer und chemischer Produkte, hinter dem Blag 214.
Angst-Kirchhofer, Jakob, Gipser von Wyl (Zürich), Halden 254.
Appenzeller-Weier, Marie, Weißnäherin von Höngg (Zürich), Golatten-mattgasse 233.
Apper, Emil, Tapezierer v. Wollishofen (Zürich), Logis vord. Vorstadt 669, Werkstätte vordere Vorstadt 675.

Bachmann, Elise, Fabrikarbeiterin von Bottenwyl, Schachen 726.
Bachmann, Marie, Fabrikarbeiterin von Bottenwyl, Schachen 726.
Bachmann-Müller, Rudolf, Maurer von Bottenwyl, Halden 280 b.
Bachmann-Rickart, Bernhard, Schneider von Bottenwyl, v. d. Halden-thor 779.
Bachmann-Kinifer, Johann, Küfer, Milchgasse 159.
Bachmann-Vogelsang, Zuzanna, Wittwe von Bottenwyl, Schachen 726.
X Bäbler, Johann Jakob, Dr. Professor von Matt (Glarus), Bach- strasse 1101.
Bächli-Holliger, Gottlieb, Schuhmacher von Buchs, Pelzgasse 125.
Bächli, Jakob, Gasarbeiter von Buchs, Milchgasse 153.
Bächli, Joseph, Staatsweibel von Würenlingen, Halden 253.
Bär, Rudolf, Schreiner, obere Vorstadt 964.
Bär, Louis, Commis id. id.
X Bär, Marie, Arbeitslehrerin id. id.
Bär-Frei, Johanna, Wittwe, Part., obere Vorstadt 964.
Bäuerlin-Siebenmann, Rosa, Wittwe, Auffeherin der Gewerbehalle, von Baden, Schachen 737.
Baldeschwylер, Mathilde, Part. von Laufenburg, Laurenzenvorstadt 403.
~~~

#### 1888_p127 (2326 characters)

~~~text
Rothwyler–Saxer.
109
Rothwyler-Hupfer, Anton, Büchsenmacher von Dürrheim (Großh. Baden), Hammer 190.
Ruch-Schäffli, Alfred, Schuhmacher von Mittlödi (Starus) Milchgasse 151.
Ruef-Joho, Johann, Taglöhner, von Rekingen, Halden 249.
Ruef-Zweifel, Wilhelm, Schlosser, Neitingen, Laurenzenvorstadt 376.
Ruefli, Johann, Taglöhner, von Seengen, Igelweid 637.
Rüedi-Wärtli, Johann, Staatsweibel von Sulz, Milchgasse 79.
Rüegg-Stephani, Barbara, Postkondutteurs Wittwe von Balmen (Zürich), Milchgasse 145.
Rüegger-Gysling, Otto, Malermeister von Wyl (Zürich), Zieglerain 746.
Rüegger-Holliger, Maria, Wittwe, Taglöhnerin von Niederwyl, vor dem Haldenthor 1083.
Rüetschi-Bopp, Hermann, Techniker und Glockengießer, Rainstraße 843.
Rüetschi-Christen, Jakob, Glockengießer, obere Vorstadt 929.
Rüetschi, Gottlieb, Bäcker und Wirth von Zuhrt, Felzgasse 131.
Rüetschi-Henberger, Ludwig, Kanzleisekretär, Rain 825.
Rüetschi-Mattli, Gottfried, Obergerichtsweibel, Adelbändli 81.
Rüetschi-Nüppleri, Friedrich, Buchhalter, Casinostraße 571.
Rüetschi-Nüppleri, Sophie, Part., Wittwe, hintere Vorstadt 694.
Rüetschi-Wenger, Gottfried, Milchverkäufer, Spezereihandlung und Salzverkauf, Adelbändli 81.
Rüetschi-Schilling, Anna, Fabrikarbeiterin von Schlieren (Zürich), Laurenzenvorstadt 1114.
Rumpf, Bertha, Part. von Basel, vordere Vorstadt 893.
Rusterholz-Schäppi, Albert, Bildhauer von Wädenswil, Rain 885.
Sager-Klauenbösch, Jakob, Pofamenter von Gränichen, obere Vorstadt 937.
Sager-Wildi, Jakob, Taglöhner von Gränichen, obere Vorstadt 947.
Salm, Marie, Damenschneiderin von Veltheim, Milchgasse 144.
Salm, Barbara, Haushälterin id. id. id.
Sandmeier, Melchior, Part. von Seengen, in der Telli 440.
Sandmeier-Rohr, Susette, Wittwe, Part., obere Vorstadt 955.
Sandmeier, Gottlieb, Buchbinder, id. id. id.
Sandmeier, Marie, Ladentochter, id. id. id.
Sandmeier, Marie, Damenschneiderin id. id. id.
Sandmeier, Margaretha, Damenschneiderin id. id. id.
Sandmeier-Dbrecht, Dachdeckergefelle, Zieglerain 708.
Sauerländer-Benz, Elise, Wittwe, Part., Laurenzenvorstadt 394.
Sauerländer-Euster, Emma, Part., Laurenzenvorstadt 418.
Sauerländer-Frey, Remigius, Buchdruckereibesitzer, Laurenzenvorstadt 418.
Saxer, Elise, Part., vordere Vorstadt 889.
Saxer-Pfleger, Ludwig, Kaufmann, vordere Vorstadt 889.
Saxer-Truog, Anna, Wittwe, Haushälterin, Rain 872.
~~~

#### 1888_p163 (3147 characters)

~~~text
Wirthschaften.
Gasthöfe.
Krone: Mathys, Rudolf, Kronengasse 39.
Löwen: Müller, Heinrich, vordere Vorstadt 681.
Ochsen: Wettler, Adolf, Laurenzenthor-gasse 115.
Rößli: Kübn Bernhard, Mezgergasse 112.
Wildenmann: Kohr, Samuel, vordere Vorstadt 667.
Kreuz: Maurer, Emil, jenseits der Aare 298.
Kurhaus: Wächter, Hans, zum Alpen-zeiger 317.
Herberge: Günselen, Louise, obere Vorstadt 912.

Speisewirthschaften.
Anmann, Johann, Schachen 734.
Baumann, Heinrich, 3. Freihof, Laurenzen-vorstadt 390.
Bertshinger-Kiniker, Anna, zur Cantine, Laurenzenvorstadt 590.
Brunnhöfer-Meder, August, Zollrain 178.
Dubs, Carl, Rathausgasse 32.
Dürr, Gabriel, Graben 1237.
Eggimann, Johann, Bahnhofstrasse 1025.
Egloff, Franz, Schachen 731.
Fischer-Eglinger, Rud., in der Gais 486.
Fischer, Thomas, „zur Kettenbrücke“, Zollrain 179.
Gautschi, Rudolf, zum Frohsinn, hinter dem Bahnhof 1072.
Hässiger-Hilfiker, Otto, Pelzgasse 136.
Hässig-Sienhard, Hermann, Rathaus-gasse 46.
Hässig-Sigle, Julius, zum „rothen Haus“, Bahnhofstrasse 1160.
Holzach-Siebenmann, Dietrich, Bahnhof-strasse 563.
Holzach-Schmidt, Friedrich, Ziegelrain 700.
Keller, Gottlieb, zum neuen Bund, Rain 822.
Kiefer-Lepraz, Fanny, Zollrain 87.
Kühn, Bernhard, Bahnhofrestauration, Bahnhofstrasse 515.
Randegger, Conrad, zur bairischen Halle, obere Vorstadt 926.
Renold-Hinden, Daniel, Schachen 733.
Riniker, Friedrich, Binsenhof 1010.
Rohr, Johann, Holzmarkt 662.
Rohr-Gloor, Adolf, Pelzgasse 127.
Siebenmann, Otto, Mezgerasse 60.
Siebenmann, Bernhard, vordere Vorstadt 673.
Stahel-Ernst, Johann, Graben 1161.
Strübin-Frey, August, Casinostraße 570.
Bogt-Siegrist, Samuel, Graben 222.
Weber-Segnauer, Hermann, Bahnhofstrasse 568.
Wirth, Emma, zum Affenfakten, vordere Vorstadt 672 und hintere Vorstadt 692.
Woodtli, J. Diethelm, Salben 277.

Vintenwirthschaften.
Brand, Jakob, vordere Vorstadt 669.
Brütschlin-Bosshard, Babette, Schachen 727.
Graf-Tröndle, Ludwig, Rathausgasse 18.
Geß, Wilhelm, Pelzgasse 66.
Lauchli-Bürgi, Anna, Wittwe, Rathausgasse 25.
Meister, Georg, Graben 216.
Richter, Johann, Bahnhofstrasse 541.
Miniker, Friedrich, Bierbrauer, Mezgergasse 102.
Rohner, Emil, Zollrain 51.
Rüetschi, Gottlieb, Pelzgasse 131.
Schmidt, Hans, Bierhalle, 3. Zunftstube, Pelzgasse 129.
Siebenmann, Friedrich, Bierbrauer, im Weinberg 321.
Siebenmann-Rohr, Rudolf, Bierbrauer, Graben 620.
Steger, Melchior, Rain 832.
Bibiella, Manuel, Spanische Weinhalle, Kirchgasse 7.
Bonary, Carolina, Zollrain 52.
Widmer, Rudolf, obere Vorstadt 927.
Wüthrich-Lüdi, Samuel, zum Storchen, Laurenzenthorngasse 117.

Sommerwirthschaften.
Kühn, Bernhard, zum Rößli (Köstligarten), Schachen.
Fehlmann, Johann Jakob, in Roggen-haufen.

Kaffee-wirthschaften.
Baumann, Kaspar, Casinostraße 660.
Brunner, Elise, Zgelweid 634.
Keller-Lauchli, Paul, Zollrain 292.
Widmer, Samuel, Bahnhofstrasse 1023.

Woll- u. Baumwollhoff-Druckereien.
Jenny u. Weigel, Tell 449.

Zeitungen.
Druck und Verlag der Attiengesellschaft des Aargauer Tagblattes, Oberthor 223: Aargauer Tagblatt, 6 Mal wöchentlich. Preis Fr. 9 für Aarau, franco auswärts Fr. 10.
Aargauer Volksfreund, 3 Mal wöchentlich. Preis für Aarau und auswärts Fr. 6.
[spalte 2]
~~~

#### 1892_p037 (1428 characters)

~~~text
Haus-
Nr.
337. Weber-Weber, Wilhelm, Milchverkäufer, von Menziten.
338. Wehrlí-Graf, Jakob, Handlanger, von Rüttigen.
339. * Zimmermann, Maria, Wittwe, Erbschaft.
Heuberger-Siebenmann, Gottlieb, Sekretär.
Döbeli-Binder Samuel, Bezirksschullehrer, von Seon.
1247. † Siebenmann-Hagnauer, Friedrich, Bierbrauer. Wagenshopf und
Giskeller.
Weinberg.
340. † Frey-Frey, R., Stadtrath. Rebhäuschen.
341. † Kern-Rychner, Emil. Rebhäuschen.
Jenjeits der Aare.
342. Bauhofer-Keller, Anna Kaufmanns Wittwe.
Bauhofer, Maria, Lehrerin in Erlinsbach.
Tuchschmid, August, Dr. Professor, von Thundorf (Thurgau).
Müller, Rosa, Haushälterin, von Unterkulm.
Hunziker-Müller, Marie Anna, Schuhmachers Wittwe, von Unter-Kulm.
343. † Diefelbe. Holzschopf.
344. † Gemeinde Aarau. Holzmagazin.
345. † Diefelbe. Werthaus.
1280. † Gemeinde Aarau. Spritzenhaus.
346. Müller-Rothpletz, Arnold, Architekt und Baumeister.
347. † Abgetragen.
348. † Gemeinde Aarau. Badanstalt.
† Diefelbe. Schuppen für Kriegsfuhrwerke.
1104.
Laurenzentorgasse.
349. Häfker-Wanger, Emil, Negot., Kolonialwaarenhandlung.
Erné-Leblanc, Eduard, Kaufmann, von Leuggern.
350. † Derfelbe. Holzschopf.
351. Aktiengesellschaft der Creditanstalt.
Graben.
352. * Dreysuf-Götschel, Adolf, Kaufmann, von Endingen, in Basel.
Dreisuf, Max Emil, Sohn, Kaufmann, von Endingen. Französische
Waarenhalle. Ellenwaarenhandlung und Damenkonfektion.
Frey-Hagnauer, Konrad, Dr. Med., praktischer Arzt.
~~~

#### 1892_p112 (2481 characters)

~~~text
96
Gautschi — Gloor.
Gautschi-Leuenberger, Rudolf, Defonom von Reinach, Tell 460.
Gautschi-Maculin, Rudolf, Wirt zum „Frohsinn“, von Reinach, hinter dem Bahnhof 1172.
Gautschi-Notb, Rudolf, Sohn, Defonom von Reinach, Tell 460.
XGautschi-Siebenmann, Samuel, Kantons-Ingenieur, hintere Vorstadt 646.
Geizmann, Xaver, Sekretär von Hägglingen, Pelzgasse 130.
Geyer-Schleich, Josepfi, Schneider von Benfeld (Elfa), Rathausgasse 45.
Gerber-Haßler, Louise Elisabeth, Wittwe, Part., vordere Vorstadt 670.
XGerber-Seiler, Gustav, March. Tailleur. Kleider- und Tuchhandlung, vordere Vorstadt 670.
Gerber, Robert, Commis, vordere Vorstadt 670.
Gerodetti-Habermacher, Virgilus, Hutmacher und Handlung von Marmorsteinen von Sagliano (Italien), hinter dem Bahnhof 1268.
Gertifer-Andrez, Maria, Wittwe, Part. von Wünchwylen, Rain 820.
XGefner, August, Dr. Professor von Zürich, Bachstraße 1101.
Giesch-Caviezcl, Adolf, Kaufmann von Chur, hintere Vorstadt 638.
Giezentanner, Elisabeth, Part. von Kappel (St. Gallen), Golattenmattgasse 235.
Giger-Märki, Jakob, Schreiner von Gontenschwy, Halden 286.
Giger-Wildi, Rosina, Malers Wittwe, Part. von Kirchheim (Württemberg), obere Vorstadt 937:
Ging-Hug, August, Schmied, Stadthof 92 e, Werkstätte Casinofstraße 572.
Ging, Johann Jakob, Part., Casinofstraße 571.
Ging-Ryser, Wilhelm, Wagner, Wittgasse 77, Werkstätte Casinofstraße 572.
Ginsberg-Ammann, Elisabeth, Wittwe, Part., Bahnhofstraße 1026.
XGifi- von Arz, Viktor, Kaufmann, Tuchhandlung von Niedergösgen (Solothurn), Holzmarkt 664.
XGifi-Bächli, Adolf, Tapezierer von Buchs, Pelzgasse 126.
Gifi-Wernli, Samuel, Schreinermeister von Möriken, Stadthof 92 b.
Gifiger-Feer, Johann, Gärtner v. Rienberg (Solothurn), Casinoftr. 580.
XGyfi-Ammann, Traugott, Lehrer, jenseits der Aare 1303 b.
Gyfi, Anna, Buchhalterin, vordere Vorstadt 895.
Gyfi-Anderegg, Emil, Maler, obere Vorstadt 942.
XGyfi-Büchle, Emil, Part., Gartenstraße 978.
Gyfi-Fischer, Friedrich, Schlosser, hintere Vorstadt 645.
Gyfi, Hans, Sohn, Mechaniker, vordere Vorstadt 895.
Gyfi, Lisette, Modelltechers, Part., Kirchgasse 10.
Gyfi, Otto, Sohn, Photograph, vordere Vorstadt 895.
Gyfi, Otto Robert, Postcommis, obere Vorstadt 942.
XGyfi-Siebenmann, Otto, Photograph, vordere Vorstadt 895.
XGyfi-Studler, Arnold, Mechaniker, vordere Vorstadt 675.
Gladdach-Renold, Professor von Dppenheim (Hessen), Casinofstraße 576.
Gloor, Bertha, Damenschneiderin von Dürrenäsch, Adelbändli 171.
Gloor, Elise, Fabrikarbeiterin, von Seon, Halden 260.
~~~

#### 1892_p117 (2236 characters)

~~~text
Helm – Herzog.
101
Helm-von Arx, Elise, Wittwe von Derlikon (Zürich), Zoltrain 52.
Hemmeler-Biedermann, August, Kaufmann, Meggergasse 55.
Hemmeler, Emil, Sohn, Kaufmann, Meggergasse 58.
Hemmeler-Zech, Gottlieb, Zimmermeister, vor dem Paldenthor 767.
Hemmeler-Frey, Friedrich, Kaufmann, alt Stadtrath, h. Vorst. 638.
Hemmeler-Pasler, August, Kaufmann, Quincallerie- und Kinderspiel- wahren, Meggergasse 55.
Hemmeler, Ida, Privatlehrerin, Solattenmattgasse 229.
Hemmeler, Marie, Gürtlers, Ladentöchter, Zoltrain 177.
Hemmeler-Pfister, Friedrich, Postcommiss, Casinostraße 1130.
Hemmeler, Rosa, Gürtlers, Ladentöchter, Rathausgasse 47.
Hemmeler, Rosina, Part., Milchgasse 145.
Hemmeler-Roth, Wilhelm, Sekretär, obere Vorstadt 921.
Hemmeler-Scheidler, Berena, Haftners Wittwe, Geschirr- und Glas- warenhandlung, obere Vorstadt 944.
Hemmeler-Schmidt, Wilhelm, Haftnermeister, Geschirrhandl., ob. Vorst. 919.
Hemmeler-Stahl, Jakob, Uhrenmacher, Rathausgasse 23.
Hemmeler-Stahl, Ida (Firma Ritter-Stahl), Quincalleriewarenhand- lung, Rathausgasse 21.
Hemmeler-Türler, Emil, Kaufmann, Mercerie-, Garn- und Ellenwaren- handlung, Meggergasse 58.
Hengherr-Hiltbrunner, August, Lehrer von Affoltern bei Höngg (Zürich), Feerstraße 1308.
Henz-Gautschi, Emil, Kaufmann, Eisenwarenhandlung, vordere Vor- stadt 903.
Henz-Mürf, Julius, Kaufmann, vordere Vorstadt 1169.
Henz-Plüf, Jakob, Kaufmann, vordere Vorstadt 1169.
Henz-Siebenmann, Adele, Haftners Wittwe, Hintere Vorstadt 688.
Henz-von Seuter, Hans, Kaufmann, vordere Vorstadt 678.
Hering-Leuenberger, Johann, Lehrer von Kriisforf, Wohnung Zoltrain 181, Bettwaren- und Möbelhandlung, Meggergasse 105.
Hermann, Elisabeth, Spetterin von Rohrbach (Bern), Solattenmatt- gasse 231 b.
Hertfelder-Bür, Marie, Wittwe, Part., Kirchgasse 13.
Herzig-Hauri, Friedrich, March. Tailleur von Wynau (Bern), hintere Vorstadt 644.
Herzig-Weber, Friedrich, Dachdecker- und Kaminfeger von Obersteckholz (Bern), Adelbändli 173.
Herzog-Dietter, Konrad, Schneider vom Homburg (Thurgau), Halden 252.
Herzog-Hagnauer, Heinrich, Lehrer von Reffingen, hinter dem Bahn- hof 1268.
Herzog, Hans, Dr. phil., Staatsarchivar, Bachstraße 1047.
Herzog, Jakob, Part., Bachstraße 1045.
Herzog-von Jenner, Lina, Wittwe, Bachstraße 1045.
~~~

#### 1899_p045 (1712 characters)

~~~text
37
Haus-
Nr.
451 † Dieselben. Fabrikgebäude.
452 † " Färberei.
453 † " Druckerei.
1085 † " Farbgebäude.
1158 † " Fabrikgebäude.
1565 † " Magazingebäude.
454 * Krippendorf-Müller, Herm., Prof. Dr. phil., in Dresden.
Rothpletz-Bürgi, Maria, Pfarrers Witwe.
— Heinrich, Förster.
Hassler-Weisser, Arnold, Commis.
455 * Derselbe.
Küng-Furrer, Anton, Sekretär, von Birri.
1133 † Imhof-Aman, Ernst (Fabrikationsgebäude).
456 Guyer-Gunkel, Oskar, Kaufmann ⚭. Halbleinfabrikation.
457 † Derselbe. Fabrikationsgebäude.
458 † " Scheune.
459 † " Tuchwalke.
460 Gautschi-Roth, Rudolf und Gautschi, Friedr., Ökonom, von
Reinach.
— -Wernli, Rudolf, Ökonom, von Reinach.
— -Roth, Rudolf, Sohn, Ökonom, von Reinach.
— Friedrich. Sohn, Ökonom, von Reinach.
1159 † Dieselben. Stall.
461 † Baumann, Gebr., Weinhandlung (Weinkeller).
1209 † Dieselben. Eiskeller.
462 † Staat Aargau. Turnhaus.

Rohrerstrasse.
1479 * Baumann, Gebr., Weinhändler, Speisewirtschaft zum „Jura“.
Leube-Kienberger, Adele, von Frick, ⚭ Wirtin zum Café
„Jura“.
Zogg-Moos, Osw. Martin, Kaufmann, von Wallenstadt.
1536 Valli-Eggspühler, August, ⚭ Übernehmer von Erdarbeiten,
von Modgliano, Italien.
Günther-Sollefer, Eugen, Instruktor der Infanterie, von Rhein-
felden.
Leu-Zimmermann, Jakob, Kanzlist, von Birrenlauf.
1507 † Derselbe. Magazin.
1560 Kaspar-Häuptli, Eduard, Ferger, von ZezwyI.
Wernli-Häuptli, Julius, Lagerhaus-Kassier, von Thalheim.
— * Käser-Plüss, Rudolf, Postkondukteur.
1362 † Jura-Cementfabriken, Schuppen für die Seilbahn.
Fischer & Schmuziger. Bureau. ⚭
Angerer, Joseph, Schneidermeister, von Stilfs (Tirol).
463 * Spirgi-Hochstrasser, Elise, Witwes (Erbschaft).
464 † Lagerhäuser der Centralschweiz. Petroleum-Keller (Alkohol-
dépôt).
~~~

### `qwen3.8-27b`

#### 1896_p176 (0 characters — stopped at the token ceiling)

~~~text
(empty)
~~~

*27 page(s) omitted here for length — all of them are in `/home/dh/agentic_historian/agentic_historian/data/vlm_test/aarau-probe-gpustack-v1`.*
