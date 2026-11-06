# ATR batch — aarau-antiqua-gemini-retry-v1

- pages: **12**
- started: 2026-11-06T20:47:23+00:00
- wall time: 1.3 min

| model | read | skipped | failed | empty | looped | arguing | cut off | chars/page | s/page | wall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemini-3.8-flash` | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 2224 | 6.7 | 1.3 min |

**These columns are not quality.** There is no ground truth in this run, and characters per page measures how much a model wrote, not how much of it is right — a model that hallucinates fluently leads this table. Comparing the readings is the point; the numbers only say what each run cost and whether it completed. Measuring accuracy needs transcribed lines and `eval/linebench.py`.

## Readings

The texts themselves, so the comparison the table refuses to make can be made by eye. **Read to the end of each one**: a page that hit the token ceiling comes back as an ordinary success and stops mid-sentence, and it is marked here where that happened.

### `gemini-3.8-flash`

#### 1896_p037 (2093 characters)

~~~text
Verzeichnis der Gebäude und ihrer Bewohner. 15

Haus-
Nr.
  161 Dürr-Schmuziger, Isaak, Schreiner.
    Schmuziger, Susette, Part.
    Schmuziger, Verena, Part.
    Märki-Amsler, Jakob, Küfer, von Mandach.

Kirchhof.

  162 Gränicher geb. Richner, Rosa, Witwe, Part.
    Gränicher-Wärtli, Joh. Jak., Schneider, ref. Siegrist. Spezereihdlg.
  163 Vogel-Dubs, Gottfried, Polizeiwachtmeister, von Kölliken.
    Zuber-Müller, Andreas, Part.
    Hess-Wolf, Alexander, Kaufmann, von Zillisheim (Elsass). (Werk-
      stätte und Magazin für Bettwaren).
  164 Wanger-Häusermann, G., Buchbinder.
    Wanger, Rosa.
    Wanger, Julie, Part.
    Kohlmann-Läuchli, Verena, Witwe, Lithographie u. Steindruckerei.
    Läuchli, Adolf, Lithograph, von Remigen.
    Gampp-Spreuer, Philipp, Aufseher, von Hornussen.
  165 a * Wärtli, Friedrich, Buchhalter in Derendingen.
    Fuchs-Sommerhalder, Franz Joseph, Posamenter von Hornussen
    Hübscher-König, Anna, Witwe, Spetterin, von Dottikon.
    Vogt-Keller, Jakob, Schreiner, von Villigen.
    Vogt-Keller, Marie, Hebamme, von Villigen.
  165 b Stierli-Häny, Samuel, Kondukteur d. N. O. B., von Gebenstorf.
  166 Wärtli-Ernst, August, Buchbinder.
    Siebenmann-Sprüngli, Sophie, Witwe, Part.
    Schwalb-Wessler, Adolf, Photograph, von Karlsbad (Böhmen).
  167 a Derselbe.
  167 b Abgetragen.
  168 Gemeinde Aarau, Kirche.
  169 Dieselbe. Pfarrhaus.
    Graf-Fäsi, Ernst, von Winterthur, ref. Pfarrer.

Adelbändli.

  170 Matter-Hagnauer, Jakob, Schneidermeister, von Kölliken, Kleider-
      Fabrikation.
    Matter-Thommen, Maria, Witwe, Wäscherin, von Kölliken.
    Spörri-Käser, Elise, Schneiderin, von Bäretschwyl, (Zürich).
    Wernly, Elisabeth, Näherin, von Thalheim.
  171 Siebenmann-Frey, Ludwig, Schuhmacher, Part.
    Dürr-Siebenmann, Karolina, Registrators Witwe.
    Fischer, Ludwig, Bauamtsarbeiter.
    Gloor Wilhelmine, Taglöhnerin, von Dürrenäsch.
    Gloor, Bertha, Damenschneiderin, von Dürrenäsch.
  172 * Wehrli-Hassler, Friedrich, Pedell.
    Scheibler-Suter, Alfred, Taperierer, von Unter-Entfelden. Möbel-
      magazin und Werkstätte.
~~~

#### 1896_p084 (2539 characters)

~~~text
62            Verzeichnis der Gebäude und ihrer Bewohner.

Haus-
Nr.
1243       Liechti-Steinegger, Paul, Dr. phil., Prof., von Murten (Freiburg).
1252    † Derselbe. Bienenhaus.
    807 †       „    Gartenhaus.
1245    † Dubs-Walther, Karl, Metzger. Scheune.
1218    † Mattenberger-Walther, Jakob, Metzger, von Birr.
1324    † Derselbe. Eiskeller.
1330    †       „    Bienenhaus.
1219    † Kull, Philipp, Spenglers Erbschaft. Gartenhaus und Magazin.
    808    Widmer-Horlacher, Gottfried, Kaminfeger, von Gränichen.
    809    Wernli-Adel, Jakob, Gärtner.
           Riner-Obrist, Johann, Polizeidiener, von Herznach.
           Cadonau-Hunziker, Anton, Kellner, v. Waltensburg (Graubünden).
           Dürr-Hofer, Emil, Gemüsehändler.
    810    Frey-Kumpf, Friedr., Kanzleisekretär u. Musiklehrer, v. Densbüren.
           Frey, Friedr., Sohn, Weinhändler (in Firma Vidiella & Frey), von
             Densbüren.
           Frey, Rosa, Feinwäscherei und Glätterei, von Densbüren.
    811 † Derselbe. Holzhaus.
1201    †       „    Waschhaus.
    812    Abgetragen.
1110    † Siebenmann-Walther, Schneider. Gartenhaus.
    813 † Staat Aargau. Laboratorium.
    814 † Derselbe. Munitionsmagazin.
    815 †       „    Abtritte.
    816 † Rychner, Heinrich, Gewehrfabrikant. Schießstand.
    817 † Derselbe. Scheibenstand.
    818 † Reformirte Kirchgemeinde Aarau. Gartenhaus. (Graf, Pfarrer).

Rain.

    819    Hagenbuch-Gross, Karl, Coiffeur, Chirurg und Leichenbeschauer.
           Spiegelglasversicherungs-Agentur.
           Schatzmann-Bolliger, Elise, Spetterin. von Windisch.
    820    Jörg-Künzli, Peter, Schuhmachermeister. Schuhhandlung.
           Jörg, Emma, Damenschneiderin.
           Keller, Maritz, Schuhmacher, von Wöschnau (Solothurn).
           Gertiser-Andres, Maria, Witwe, Part., von Münchwylen.
           Andres, Emma, Fabrikarbeiterin.
    821    Birkhofer-Hagenbuch, Albertine, Damenschneiderin.
           Andres-Bircher, Heinrich, Buchbinder, Schreibmaterialienhandlung.
           Schürch-Haas, Robert, Buchdrucker, von Rohrbach (Bern).
           Berner, Gottlieb, Dienstmann, von Unterkulm.
    822    Keller, Gottlieb, von Wöschnau (Solothurn).
           Graf-Tröndle, Ottilie, Witwe, v. Worblingen (Großherzogtum Baden).
           Wirtin z. Neuen Bund. Speisewirtschaft.
           Fischer-Widmer, Marie, Witwe, Part.
    823    Wittmer-Schuhmacher, Elise, Witwe, Part., v. Erlinsbach (Soloth.).
           Wittmer, Julius, Lithographieanstalt und Druckerei, von Erlinsbach
             (Solothurn).
~~~

#### 1896_p196 (2712 characters)

~~~text
Die alte Kantonsschule, nach einer alten Lithographie.

Oeffentliche Anstalten.

a. Lehranstalten.

Kantonsschule.
Gründung derselben 1802.
Rektor: Dr. Aug. Tuchschmid.

Professoren und Lehrer.
Dr. Bäbler, für Geschichte sowie einen Teil des
  Deutschen an der Gewerbeschule.
Burgmeier, für Gesang.
Dr. Frey, Stellvertreter des Rektors, für deutsche
  Sprache und Litteratur am Gymnasium u. den
  beiden obern Klassen der Gewerbeschule.
Dr. Fröhlich, für alte Sprachen.
Dr. Ganter, für Mathematik am Gymnasium und
  an der Gewerbeschule.
Dr. Gessner, für alte Sprachen.
Gladbach, für technisches Zeichnen, deskriptive u.
  praktische Geometrie und für Geographie am
  Gymnasium und an der Gewerbeschule.
Hunziker, für Französisch am Gymnasium und
  Gewerbeschule.
Dr. Liechti, für Chemie.
Dr. Mühlberg, für Naturgeschichte.
Rennhart, für Englisch am Gymnasium und an der
  Gewerbeschule, für Italienisch an d. Gewerbe-
  schule.
Rey, Jakob Friedr., für Französisch u. Italienisch.
Roth, Oberst, für theoretischen Militärunterricht.
Dr. Tuchschmid, Rektor, für Mathematik an der
  Gewerbeschule und Physik am Gymnasium u.
  an der Gewerbeschule.
Wäffler, für Turnunterricht.
Wernly, Pfarrer, für Hebräisch.
Widmer, Pfarrer in Gränichen, für Religionsunter-
  richt.
[spalte 2]
Dr. Winteler, für Geschichte am Gymnasium und
  alte Sprachen.
Wolfinger, für Kunstzeichnen.
Zimmermann, für Schreiben und Stenographie.
An der Musikschule.
Rödelberger, Direktor, für Violine und Pianoforte.

Das Kantonsschülerhaus
wurde am 1. Mai 1890 eröffnet. Dasselbe hat den
Zweck, Kantonsschüler, deren Eltern nicht in Aarau
wohnen, aufzunehmen, zu verpflegen und ihnen
während ihrer Studienzeit in Aarau das Elternhaus
zu ersetzen. Es nimmt 38 Schüler auf. Der der-
zeitige Vorsteher ist Dr. H. Ganter.

Töchterinstitut und Lehrerinnen-
Seminar Aarau.
Gründung des Töchterinstituts als einer Privat-
anstalt nach dem Muster der Gossweilerschen Schule
in Zürich durch eine Stiftung der Schultheißin
Hunziker geb. Zollikofer 1786 und Eröffnung den
9. November 1787. Das Töchterinstitut ist die
älteste höhere Lehranstalt unseres Kantons.
Gründung des (staatlichen) Lehrerinnenseminars
1872 im Anschluss an das Töchterinstitut und Er-
öffnung der vereinigten Anstalt anfangs Juni 1873.
Zweck: A. des Töchterinstituts nach der Stif-
tungsurkunde: „Bessere Bildung der Töchter.“ Schon
nach einem Jahre kamen zu den bisherigen wissen-
schaftlichen Fächern noch die französische Sprache
und weibliche Arbeiten hinzu, ersteres, „weil man
hoffte, dadurch die Unkosten, ja vielleicht Sitten-
verderbnis, so die Absendung unserer Töchter nach
der Waadt, Genf oder Colmar veranlasst, wo nicht
ganz, doch zum Teil zu ersparen; letzteres, weil
~~~

#### 1899_p049 (2172 characters)

~~~text
41

Haus-
Nr.
Herzogstrasse.
1439 Wehrli-Märk, Emil, Architekt, v. Höngg (Zür.). „Zur Erika.“
1365 Kummler-Sauerländer, Hermann, Kaufmann [tel].
  — -Frey, Augusta, Witwe, Part.
1366 Kern-von Arand, Heinrich, Fabrikant [tel].
1367 † Derselbe. Wasch- und Holzhaus.
  488 Bally-Schmitter, Adeline, Fabrikants Witwe.
  489 † Dieselbe. Bad- und Waschhaus.

Hinter dem Bahnhof.
  490 † Bally-Arndt, Eugen, Fabrikgebäude. Fabrikat. elast. Gewebe.
  491 † Derselbe. Kesselhaus.
  492 † „ Kosthaus.
  493 † „ Schreiner- und Schlosserwerkstätte.
  494 Wegelin-Schmid, Joh. Rud., Architekt, v. Diesenhofen (Thurg.).
  — -Riesch, Maria, Part., von Diesenhofen.
  Walti-Zimmermann, Rosa, Witwe, Taglöhnerin, v. Dürrenäsch.
  Marti-Hanreiter, Fritz, Bierbrauer.
  Schmid, Frida, Weißnäherin, von Watterdingen (Baden).
  — Anna, „ „ „ „
  — Sophie, „ „ „ „
1072 Gautschi-Maculin, Rud., Speisewirtschaft z. Frohsinn [tel], von
  Reinach.
  Wernli-Hug, Johann, Magaziner, von Thalheim.
  Müller-Hug, Eugen, Wagenkontrolleur, von Affoltern a./A.
  495 Bouvard-Schulthess, Joh., Güterexpedient, von Remetschwyl.
  496 Käser-Plüss, Rudolf, Postkondukteur.
  Buchser-Schmid, Rudolf, Schreiner, von Schöftland.
  497 Brügger-Sommerhalder, Christian, Kontrolleur, von Chur-
  walden (Graubünden).
  Bircher-Kyburz, Anna, Witwe, Part., von Küttigen.
  Mosimann-Walliser, Gottfried, Bahnangestellter, von Signau
  (Bern).
1512 Eckert-Giger, Eduard, Zimmerpolier v. Großräudchen (Preuß.).
  — Elise, Damenschneiderin, von Großräudchen.
  Bopp-Ruh, Gottlieb, Reisender.
  Senn-Winkler, Isidor, Part., Kirchdorf.
  498 † Künzlen & Cie., Eisengießerei und Weichgußfabrik.
  499 † Derselbe. Bureau [tel].
  500 † „ Mechanische Sandmühle.
1078 † „ Eisengießerei.
1302 Rotter-Baumgartner, Johann, Schreinermeister, von Werms-
  dorf (Österreich).
  Bachmann-Kümin, Joseph, Schneider, von Wollerau (Schwyz).
1491 Lüscher-Greninger, Daniel, Gießereibesitzer, von O.-Entfelden.
  501 Fricker-Hiltpold, Verena, Bahnmeisters Witwe, von Veltheim.
  Kielholz, Gottlieb, Adjunkt vom Postdirektor, von Mettau.
  502 Freimaurerloge zur Brudertreue. [tel]
  Niederhauser-Gysin, Theodor, Buchbinder, von Baselaugst.
~~~

#### 1899_p050 (2014 characters)

~~~text
42

Haus-
Nr.
1558 u. 1559 * Kübler-Kuhn, Johann, Bahnhofinspektor.
  Madon-Laufer, Viktor, Lokomotivführer, von Zürich.
  Gossewisch-Maier, Friedr. Aug., Kondukteur, von Schloßrued.
  Landolt-Hartmann, Emilie, Witwe, Part.
1492 Staub-Kübler, Jakob, Bahnangestellter, von Dübendorf (Zch.).
  — -Wehrli, Jakob, Wagenkontrolleur, von Dübendorf (Zch.).
  Forderer-Schwammberger, Alois, Zuschneider, von Ziegel-
    bach (Wtbg.).
  — Mathias, Part., von Ziegelbach.
1293 † Derselbe. Holzschopf.
1477 * Kummler-Sauerländer, Hermann.
  Birchmeier-Kull, August, Maler, von Würenlingen.
  Bolliger-Kielholz, Albert, Bankbuchhalter, von Küttigen.
1472 † Kummler & Cie. Fabrikgebäude.
1478 † Derselbe. Ökonomiegebäude.
1553 † Derselbe. Schuppen.
1539 Bolliger-Gloor, Rudolf, Bankangestellter, von Schmiedrued.
  Hemmeler-Stähli, Emil, Kaufmann.
  Meyer-Fäs, Jean, Postangestellter, von Dintiken.
1357 * Rödelberger-Popp, Franz, Musikdirektor, v. Würzburg (Bayern).
  Künzlen-Kranich, Friedrich, Gießereibesitzer.
1356 Schäfer-Troller, Adolf, Architekt, Südbahnbureau.
1351 Suter-Geissberger, Joseph, Bezirksschullehrer, von Lengnau.
1352 Basler-Furter, Peter, Kantonsgeometer, von Zeihen.
1475 * Doswald-Schenker, Jos. Eduard, von Neuheim (Zug). Speise-
    wirtschaft. Restaurant z. Bahnhof.
503 * Schmuziger-Koller, Daniel, Baumeister, in Zürich.
  Kieser-Dambach, Robert, Bankbeamter.
504 † Derselbe. Holzschopf.
505 † " Magazin.
506 † " Ladenschopf.
507 † " Baracke.
  Müller, Sigmund, Baumeister.
1268 Gerodetti-Habermacher, Virgilius. Marmorsteingeschäft.
    Weinhandlung.
1412 † Derselbe. Marmorsäge.
508 † Tourewani, Peter, Baumeister in Olten. Gartenhaus.
1414 Lüscher-Umiker, Hermann, Mechaniker.
  Bürgi, Werner, Reisender, von St. Gallen.
  Bigler, Ulrich, Dr. phil., Bezirksschullehrer, von Oberthal.
    (Bern).
  Bräm-Huber, Anna, Witwe, Part., von Bülach (Zürich).

Bankstrasse.

509 Kauf, Heinrich, gew. Lokomotivf., von Wellhausen (Thurgau).
  — Alfred, Kassier d. aarg. Kreditanst, v. Wellhausen (Thurg).
~~~

#### 1899_p051 (2009 characters)

~~~text
43

  Haus-
  Nr.
  510  Siebenmann-Siebenmann, Marie, Witwe, Part.
1234 †  Dieselbe. Holzhaus.
1141    Kunz, Johann Jakob, von Wald (Zürich), Part.
        Walder-Kunz, Elise, Witwe, von Benken (Schaffhausen).
        Gessner-Siegfried, August, Dr. phil., Professor, von Zürich.
1251 †  Derselbe. Holz- und Waschhaus.
1146 *  Lüscher-Umiker, Hermann, Mechaniker.
        Schär-Frey, Friedrich, Major, Instr. I. Klasse der Kavallerie,
          von Inkwyl (Bern).

Bahnhofstrasse.

  511 * Aargauische Bank. [tel]
  512 † Dieselbe. Holzhaus.
1360    Zebert-Altorfer, Georg, von Bauma (Zürich). Papeterie. [tel]
        Wirth-Geiger, Joh. Rudolf, Arzt, Part., von Speicher (Appenz.)
1438    Gerber-Walther, Hans, Hôtelier [tel] (Hôtel Terminus).
  513 * Näf & Zschokke. Kreispostgebäude. [tel]
        Brosy-Miville, Rudolf, Kreispostdirektor, v. Mümliswyl (Sol.).
  514 † Dieselben. Postremise.
  515   Schweizerische Nordostbahn. Bahnhofgebäude.
        Kübler-Kuhn, Johann, Bahnhofinspektor.
        Schäfer-Meier, Friedrich, gew. Einnehmer der Nordostbahn.
        Meister-Uttiger, Jakob Emil, Adjunkt des Bahnhofinspektors,
          von Dübendorf (Zürich).
        Kühn-Hofmann, Bernhard, Restaurateur. [tel]
  516 † Schweizerische Nordostbahn. Einsteighalle.
  517 † Dieselbe. Wagenremise.
  518 †   „      Wärterhaus.
  519 †   „      [tel] Güterschopf mit Wohnungen (Güterexpedition,
          Bureau).
        Lindegger-Kyburz, Gottfried, Güterexpedient, v. O.-Entfelden.
        Rippstein-Küng, Joseph, Portier, von Kienberg (Solothurn).
  520 † Dieselbe. Waschhaus und Abtritte.
  521 †   „      Maschinenremise.
  522 †   „      Wasserstationsgebäude.
  523 †   „      Güterschopf (Fruchtschuppen).
  524 †   „      Wagenremise.
  525 †   „      Bahnwärterhäuschen.
  526 †   „      Abtrittgebäude.
  527 †   „      Bahnwärterhäuschen.
  528 †   „              „
  529 †   „              „
  530 †   „              „
  531 †   „              „
  532 †   „              „
  533 †   „              „
~~~

#### 1899_p064 (2189 characters)

~~~text
56

Haus-
Nr.
      Siebenmann-Ackermann, Bernhard, Part.
      Müller-Nünlist, Sigmund, Zimmermeister, von Walterswil
        (Solothurn).
      Renold-Schneider, Maria, Fabrikarbeiterin, von Brunegg.
  674 Kunz-Graf, Ernst, Zuckerbäcker, [tel] von Wald (Zürich).
      Zündt geb. Hagenbuch, Elise Luise, Witwe, Part., von
        Altstätten (St. Gallen).
  675 Studler-Sandmeier, Anna, Witwe, Part.
      Gysi-Studler, Arnold, Mechaniker.
      Hofmann, Arnold, von Aarburg. Manufakturwarenhdlg.
  676 Hagenbuch-Egger, Friedr., Buchbinderei u. Papeterie. [tel]
  677 † Derselbe. Buchbinderwerkstätte.
  678 * Henz-Plüss, Jakob, Kaufmann. [tel]
      — -von Seuter, Hans, Kaufmann.
      Jakob Henz & Cie., Firma. Kolonialwarengeschäft.
  679 Abgetragen; an dessen Platz
1169  Henz-Plüss, Jakob, Kaufmann.
      Jb. Henz & Cie., Firma. Eisenhandlungsgeschäft.
  680 Schäfer-Dennler, Cäsar, Messerschmied.
      Meier-Grossmann, Anna, Witwe, Part., von Rheinfelden.
      Hässig-Hauenstein, Elisabeth, Witwe, Part.
  681 Scherz-Mollet, Karl Niklaus, Wirt, [tel] von Köniz (Bern).
        Gasthof zum Löwen.
      Fisch, Gottlieb, Kaufmann.
  682 Rothpletz-Marti, Friedrichs Erbschaft.
      —, Emil, Verwalter.
      Waldmeier geb. Rothpletz, Bertha, Wwe., Part., v. Hellikon.
      Spychiger-Thomer, Fried., Dek.-Maler, v. Ursenbach (Bern).
  683 Scherz-Mollet, Karl, Gastwirt. Wohnhaus mit † Stal-
        lung, † Waschhaus etc.

Hintere Vorstadt.

  684 * Einwohnergemeinde Aarau. [tel] Elektrische Lichtcentrale.
      Verwalter: Hassler-Schmidt, Friedr. (Bureau).
      Betriebschef: Sprecher-Siegrist, Karl, (Bureau).
  685 † Dieselbe. Holzschopf.
  686 u. 687 † Henz-Plüss, Jakob, Kaufmann, Magazin.
  688 * Derselbe. Wohnhaus.
      Plüss, Anna, Damenschneiderin.
      König-Steininger, Anna, Witwe, Part., von Bottenwyl.
  689 Birmann, Adolf, Müller, von Basel. Mehlhandlung.
      — -Baldenweg, Anna Maria, Witwe, Part., von Basel.
      Gysi-Frey, Friedrich, Schlosser.
  690 * Gemeinde Aarau. Amthaus.
      Bezirksamt [tel] und Staatsanwaltschaft [tel].
      Kantonaler Polizeiposten und Bezirksgefängnisse. [tel]
      Rubli-Schwarz, Joh. Jakob, Gefangenwart, von Effingen.
~~~

#### 1899_p077 (2541 characters)

~~~text
69

Haus-
Nr.
  877 a Wasmer, Jakob, Wagner, von Suhr.
        Hallauer-Lüscher, Anton, Taglöhner, v. Ursendorf (Wtbg.).
        Sommerhalder-König, Louise, Spetterin, v. Gontenschwyl.
        Wehrli-Kähr, Maria. Part.
        Höner-Höner, Anton, Part., von Lachen (Schwyz).
        Egloff, Franz, Postfakteur, von Wettingen.
  877 b Scheibler-Zingg, Fritz, Küfermeister von Unterentfelden.
  878   Keller-Steiner, Karl, Hafer- und Weinhandlung.
        Steiner, Johann, Part.
        Steiner-Lindenmann, Susanne, Witwe, Part.
        Mühlberg-Sutermeister, Fritz, Dr. phil. Professor.
        Von Steiger-Marthaler, William, Techniker, von Bern.
        Steffen-Meier, Anna, Witwe, von Seebach (Zürich).
  879 * Derselbe. Hinterhaus.
        Semmler-Gans, Marg., Schuhhändl., v. Pirmasens (Bayern).
        Volkmer-Mussmann, Barbara, Schuhhändlerin, von Pir-
          masens (Bayern).
1494    Wassmer-Kummler, Emil, Kaufmann, [Zeichen] „Daheim“.
  880   Nägeli-Keller, Joh. Jakob, Schriftsetzer, von Bülach (Zür.)
        Nägeli, Jakob, Tapezierer von Bülach (Zürich).
        Lüscher-Lüscher, Rudolf, Maurer von Moosleerau.
  881 * Armengut der Gemeinde Aarau. Wohnhaus.
        Hässig-Lüscher, Johann, Dienstmann, Antiquar und
          Gemüsehändler.
        Rämisperger-Studler, Verena, Spenglers Witwe, (Taglöhn.)
        Rämisperger, Hermann jünger, Spengler.
  882 † Henz-Gautschi, Emil, Magazin.
  883   Rohr-Hochstrasser, Rudolf, Schmied.
        Wälti-Maurer, Rudolf, Schneider, von Unterkulm.
  884   Bopp-Häusler, Kaspar, Pflästerer. Erbschaft.
        — —, Louise, Witwe, Part.
        Kielholz-Brogli, Franz, Bahnangestellter von Mettau.
        Näf-Eichenberger, Emma, Witwe, Part., v. Meilen (Zürich).
  885 * Rusterholz und Freihofer, Bildhauerei und Grabsteinlager.
        Rusterholz-Schäppi, Alb., Bildhauer, v. Wädenswyl (Zür.)
        Rebmann-Häfliger, Karl Jak., Maler v. Fellbach (Wrtbg.)
        Widmer-Felber, Joh., Fabrikarbeiter, von Gränichen.
        Widmer-Felber, Anna, Weissnäherin, von Gränichen.
        Albiez-Stiner, Gustav, Appreteur, von Säckingen (Baden).
  886 † Dieselben. Magazin.
  887 †      „      Bildhauerei-Atelier.
  888   Berner-Marti, Jakob, Schreinermeister, von Rupperswyl.
        Baumann-Käser, Susanna, Polizeifeldweibels Witwe.
  889   Saxer, Ludwig, Part.
        Saxer, Lisa, Part.
        Dreifuss-Bloch, Karl, Kaufmann, von Endingen. Manu-
          fakturwarenhandlung.
        Wildi-König, Rudolf, von Suhr. General-Agent der Basler
          Lebensversicherungsgesellschaft.
~~~

#### 1899_p087 (2454 characters)

~~~text
79

Haus-
Nr.
  1015  Evangelischer Verein, Kapelle.
1343    Derselbe. Vereinshaus. Klein-Kinderschule.
        Bächli-Holliger, Gottlieb, Schuhmacher, Abwart, von Buchs.
  1016 † Frey-Rüegg & Cie., Fabrik. Seidenbandfabrikation. [tel]
  1017 † Dieselben. Maschinenhaus.
  1018  Dieselben. Wohnhaus mit Holzremise.
        Eichenberger-Fischer, Gottlieb, Schreiner von Beinwyl.
1173 *  Diakonissenstation Aarau.
        Berchten, Susanna, Diakonissin, von St. Stephan (Bern).
        Kunz, Nanette, Näherin, von Mönchaltorf (Zürich).
        Kiener geb. Tschopp, Näherin, von Zezwyl.
        Beyeler, Magdalena, Diakonissin, von Wahlern (Bern).
        Hirt, Luise, von Schmiedrued.
        Fierz, Emma, Männedorf (Zürich).
1208 †  Diakonissenstation Aarau. Waschhaus.
  1019 * Evangelischer Verein.
        Schmuziger-Dietrich, Louis, Pfarrer.
  1020  Hassler-Hunziker, Elise, Witwe, Tapetenhandlung.
        Banga-Lässer, Jean, Kaffeewirtschaft, von Mönchenstein.
          (Kaffeehalle).
        Bär-Hassler, Louis, Sekretär.
        Theodor, Amadeus, Zugführer, von Pizy (Waadt).
  1021 † Dieselbe. Hintergebäude.
        Lässer, Anna, Haushälterin von Wiliberg.
  1022 a Jäger-Hässig, Johann, Maurer, von Aussersihl (Zürich).
        Hunziker-Schürch, Marie, Schriftsetzers Witwe, Part.
        Buhlrein, Friedrich, gewes. Spengler, Part.
  1022 b Wildi-Leuthard, Verena, Witwe, Part., von Veltheim.
        Marfurt, Franz Xaver, Coiffeur, Coiffeurgeschäft.
        Peter, Joh. Ulrich, Mechaniker, Werkführer von Bassers-
          dorf (Zürich).
  1023  Siebenmann-Seiler, Katharina, Witwe, Part.
        Bertschi-Steiner, Gottlieb, Taglöhner von Dürrenäsch.
        Schmuziger-Lang, Elisa, Schreiners Witwe, Taglöhnerin.
        Wullschleger-Blattner, Hch., Stadtarbeiter, Kaffeewirtschaft.
        Wullschleger, Hans, Knecht, von Schloßrued.
  1024  Abgetragen an dessen Platz
1074 *  Spengler-Lienhard, Luise, Witwe, Part.
        Siebenmann-Siebenmann, Arnold, Tapezierer.
        Siebenmann-Blum, Elisa, Witwe, Part.
        Schwanz-Gautschi, Theodor, (Spezereihandlung) von Guten-
          stein (Großherzth. Baden).
        Zuber-Baumann, Andreas, Architekt.
  1025  Eggimann-Joss, Rosina, Witwe, von Sumiswald (Bern) [tel]
          Speisewirtschaft.
        Gross-Daum, Johanna, Hausiererin v. Irmtraut (Preussen).
        Quernheim-Gross, Magdl., Hausiererin, v. Irmtraut (Preus.)
        Felber-Roth, Karl, Schneider, von Unterbötzberg.
~~~

#### 1899_p111 (2332 characters)

~~~text
7

Brunner geb. Lehner, Anna Maria, Part., vor dem Haldenthor 773.
— Oskar, Schriftsetzer, Halden 254.
— geb. Umiker, Elisabeth, Entfelderstraße 970.
— Verena, Hebamme, Halden 287.
Brunnhofer, Albert, Tambourinstruktor, Ziegelrain 715.
— August, Wirt, Zollrain 178.
— Elise, Damenschneiderin, Rain 875.
— Emil, Postangestellter, Schachen 734.
— geb. Gietzentanner, Ursula, Witwe, Halden 247.
— geb. Gietzentanner, Verena, Witwe, Golattenmattgasse 235.
— Lisette, Lehrers, Part., Halden 246.
— geb. Schmidt, Magdalena, Witwe, Halden 253.
Bruns, Dorothea, Fein- und Großwascherei, Schmiedgasse 625.
— Hermann, Schlosser, Schmiedgasse 625.
— Heinrich, Kaufmann, Arbeiterkleiderhalle, vordere Vorstadt 900.
Bühler, Anna, Näherin, Pelzgasse 122.
— Gottlieb, Kupferschmied, Schmiedgasse 632.
— Heinrich, Schmied, Rathausgasse 467.
Bührer geb. Gidemann, Anna, Witwe, Part., Laurenzenthorgasse 349.
Bürgi geb. Burkhardt, Anna, Witwe, obere Vorstadt 935.
— geb. Fricker, Barbara, Witwe, vordere Vorstadt 900.
— geb. Schmid Barbara, Part., Milchgasse 156.
— Werner, Reisender, hinter dem Bahnhofe 1414.
Bürgin geb. Gluck, Maria, Part., vordere Vorstadt 1262.
Bürki, Ida, Gesellschafterin, Bachstraße 1154.
Bucher, Gottlieb, Fabrikarbeiter, Telli 440.
— Johann, Fabrikarbeiter, Telli 440.
— geb. Wirz, Marie, Witwe, Part., Telli 440.
Buchler, Louise, Rain 831.
Buchmann geb. Spycher, Adele, Damenschneiderin, Zollrain 53.
Buchser geb. Bachmann, Maria, Hebamme, Pelzgasse 65.
— Rudolf, Schreiner, hinter dem Bahnhof 496.
— Samuel, Schmied, Pelzgasse 65.
Buffetti, Enrico, Kunstmaler, Gönhardfeldweg 1388.
Buhlrein, Friedrich, Part., Bahnhofstraße 1022.
Burger, Johann, Kriminal-Gerichtsschreiber, Bachstraße 1045.
— Samuel, Wirt, [tel] Schachen 731.
Burgheer, Viktor, Schneider, Graben 1237.
Burkholter, Rudolf, Taglöhner, Halden 276.
Burgmeier, [tel] Joseph, Gesanglehrer und Musikdirektor. Wohnung
  Graben 209. Harmoniumlager, Laurenzenthorgasse 117.
Burkhardt, Ferdinand, Coiffeur, Laurenzenthorgasse 118.
— Ferdinand, Sohn, Coiffeur, Laurenzenthorgasse 118.
— Lina, Coiffeuse, Laurenzenthorgasse 118.
—-Mauch, Pauline, Corsettschneiderin, Ziegelrain 707.
Buser geb. Bräutigam, Rosina, Part., Metzgergasse 56.
— Emil, Güterschaffner, hintere Vorstadt 641.
— Emil, Bäckermeister, [tel] Metzgergasse 57.
— Gottlieb, Kaufmann, Metzgergasse 56.
~~~

#### 1899_p119 (2304 characters)

~~~text
15

Gysi, Hans, Reißzeugfabrikant, Gartenstraße 999.
— Otto, Photograph, vordere Vorstadt 895.
— Otto, Sohn, Photograph, vordere Vorstadt 895.
— Otto Robert, Postcommis, obere Vorstadt 942.
— Rudolf, Maler, obere Vorstadt 940.
— Traugott, Lehrer, jenseits der Aare 1303 b.
Gladbach Philipp, Professor, Kasinostraße 576.
Gloor, Adolf, Dachdecker, Milchgasse 76.
— Arnold, Schreiner, Ziegelrain 707.
— Bertha, Damenschneiderin, Adelbändli 171.
— Elise, Fabrikarbeiterin, Milchgasse 154.
— Ferdinand, Holzspalter, Milchgasse 75.
— Heinrich, Zimmermann, Stadthof 92.
— Heinrich, Bandweber, Scheibenschachen.
— Johann, Zahnmacher, Hammer 183.
— Marie, Vorgängerin, Halden 253.
— geb. Siebenmann, Witwe, Delikatessen-Handlg. Kroneng. 38.
— Wilhelm, Fuhrmann, Schachen 741.
— Wilhelmine, Taglöhnerin, Adelbändli 171.
Gmünder geb. Läuchli, Lina, Glätterin, Pelzgasse 132.
Götz, Friedrich, Schuhfabrikaufseher, Obere Vorstadt 929.
Gonzenbach geb. Gonzenbach, Julie, Witwe, Rain 828.
Gossewisch, Friedrich Aug., Kondukteur, hinter dem Bahnhofe 1558.
Gränicher, Fanny (Firma Hauri und Gränicher), Broderiegeschäft,
  hintere Vorstadt 1236.
— Jakob, Schneider, Kirchhof 162.
— geb. Richner, Rosa, Briefträgers Witwe, Part. Kirchhof 162.
Graf, Arnold Eugen, Coiffeur und Chirurg, Graben 207.
— Ernst, reformierter Pfarrer, Kirchhof 169.
— Hermann, Kaufmann, Jurastraße 1526.
— geb. Hunkeler, Mar., Wwe., Stellenvermittler., ht. Vorstadt 641.
— Jakob, Cementarbeiter, Erlinsbacherstraße 332.
— Johann, Hausknecht, Milchgasse 114.
— Rudolf, Schriftsetzer, Laurenzenvorstadt 1294.
Gröbli, Jakob, Schneider, Rathausgasse 43.
Grolimund, Emma, Lehrerin, vordere Vorstadt 671.
— Sigmund, Buchhandlungsangestellter, vordere Vorstadt 671.
Gross geb. Daum, Johanna, Bahnhofstraße 1025.
— geb. Groß, Luise. Part., Metzgergasse 103.
Grossmann, Otto, Handelsgärtner, Filiale: Graben 219.
Grünhut, Robert, Bahningenieur S. C. B., Schloßplatz 1389.
Grütter, Friedrich, Magaziner, Halden 240.
Gruber, Engelbert, Maurer, Schmiedgasse 635.
Günther, Eugen, Instruktor der Infanterie, Rohrerstraße 1536.
Gugel, Friedrich, Schuhmacher, Rathausgasse 47.
Guggisberg, Emil, Bahnhofstraße, 568 b.
— geb. Hagenbuch, Bertha, Part., Entfelderstraße 967.
Gull, Emil, Kaufmann, Bahnhofstraße 656.
— geb. Wild, Bernardine, Witwe, Bahnhofstraße 656.
~~~

#### 1899_p196 (1325 characters)

~~~text
92

Kaffeewirtschaften.
Baumann, Kaspar, hintere Vorstadt 623.
Banga-Lässer, Joh., Bahnhofstraße 1020.
Guggisberg, Emil, Bahnhofstraße 568.
Keller-Läuchli, Paul, Zollrain 292.
Kunz, Ernst, vordere Vorstadt 674.
Rohr, Hans, Konditor, Graben 205.
Wüthrich, Jakob, Rathausgasse 20.
Wullschleger-Blattner, Bahnhofstraße 1023.

Woll- und Baumwollstoff-Druckerei.
Jenny & Weigel, * Telli 490.

Zahnärzte.
Berner, Hermann, Dr., Graben 618.
Brentano, Max, Entfelderstraße 1075.
Vogt, Adolf, Laurenzenvorstadt 353. (S. Inserat Seite 10.)

Ziegelfabrikanten.
Ernst-Käser, Friedr. Jak., * (Strangfalzziegelei), in der Gais 1353.
Hauri-Siegenthaler, Karl, Rain 866.
Thut-Gidemann, Hermann, * Rain 863.

Zimmermeister.
Eichenberger, Rudolf, Halden 285.
Müller, Sigmund, vordere Vorstadt 673.
Wehrli, Johann, vor dem Haldenthor 770.

Zuckerbäcker.
(Siehe Konditoren.)

Verzeichnis der in der Stadt Aarau erscheinenden
Zeitungen, Zeitschriften und Kalender.
Druck und Verlag der Aktiengesellschaft der Aargauer
Nachrichten, * hintere Vorstadt 662.
Aargauer Nachrichten, 7 mal wöchentlich. Preis Fr. 9 für
  Aarau, franko auswärts Fr. 11.
  Gratisbeilagen: Aarauer Blätter (wöchentl. 8 Seiten stark, illustr.). Taschen-
  fahrtenplan der Eisenbahnen und Posten im Aargau. Gegründet: 1854 durch
  Buchdrucker Martin. Redaktor: Dr. M. Widmann.
~~~
