# Kalibracja SWWF na obserwacjach IMGW — 2026-10-12 14:15
hindcast: /home/runner/work/SWWF/SWWF/hindcast_v2 (96 przebiegów 00Z z 30 członkami, okien na przebieg: [13]); obs: imgw_dobowe_2020-11-01_2026-03-31_mc-1-2-3-11-12.csv.gz (52851 stacjodni)
Próba jest dobrana pod zdarzenia i dni spokojne (nie klimatologiczna) — FAR i odsetki zdarzeń z sekcji 1-5 dotyczą próby mieszanej; sekcja 6 rozdziela doby bez zdarzenia i ze zdarzeniem.

## 0. Kontrola okna doby IMGW (k=0)
- opad SMDB: start  0 UTC: r=0.820 | start  6 UTC: r=0.863 | start 12 UTC: r=0.801 | start 18 UTC: r=0.651  (najwyższe r = okno zgodne z IMGW)
- TMIN: start  0 UTC: r=0.885 | start  6 UTC: r=0.828 | start 12 UTC: r=0.817 | start 18 UTC: r=0.794  (najwyższe r = okno zgodne z IMGW)

## 1. Opad dobowy (okno 06->06 UTC)
### wyprzedzenie k=0: n=5249 stacjodni, mokrych (>=1 mm) 1338
- średnia obs 1.29 mm, GEFS 1.66 mm; korelacja sqrt = 0.863
- dni mokre: GEFS/obs = 1.08; obs > max zespołu: 6.7% dni mokrych
- P(opad>=1 mm): P=0: n=2532, zaszło 1% | P=0-20%: n=536, zaszło 7% | P=20-40%: n=311, zaszło 15% | P=40-60%: n=267, zaszło 26% | P=60-80%: n=274, zaszło 46% | P=80-100%: n=1329, zaszło 78%
- P(opad>=5 mm): P=0: n=3867, zaszło 0% | P=0-20%: n=552, zaszło 7% | P=20-40%: n=233, zaszło 16% | P=40-60%: n=165, zaszło 33% | P=60-80%: n=144, zaszło 43% | P=80-100%: n=288, zaszło 77%
- P(opad>=10 mm): P=0: n=4642, zaszło 0% | P=0-20%: n=297, zaszło 5% | P=20-40%: n=122, zaszło 25% | P=40-60%: n=61, zaszło 48% | P=60-80%: n=62, zaszło 61% | P=80-100%: n=65, zaszło 80%
### wyprzedzenie k=1: n=5304 stacjodni, mokrych (>=1 mm) 1496
- średnia obs 1.43 mm, GEFS 1.69 mm; korelacja sqrt = 0.820
- dni mokre: GEFS/obs = 0.94; obs > max zespołu: 6.8% dni mokrych
- P(opad>=1 mm): P=0: n=1890, zaszło 1% | P=0-20%: n=856, zaszło 6% | P=20-40%: n=479, zaszło 21% | P=40-60%: n=441, zaszło 36% | P=60-80%: n=456, zaszło 53% | P=80-100%: n=1182, zaszło 78%
- P(opad>=5 mm): P=0: n=3463, zaszło 0% | P=0-20%: n=899, zaszło 7% | P=20-40%: n=376, zaszło 21% | P=40-60%: n=203, zaszło 37% | P=60-80%: n=176, zaszło 56% | P=80-100%: n=187, zaszło 78%
- P(opad>=10 mm): P=0: n=4424, zaszło 0% | P=0-20%: n=591, zaszło 6% | P=20-40%: n=138, zaszło 29% | P=40-60%: n=69, zaszło 39% | P=60-80%: n=53, zaszło 75% | P=80-100%: n=29, zaszło 83%
### wyprzedzenie k=2: n=5303 stacjodni, mokrych (>=1 mm) 1438
- średnia obs 1.37 mm, GEFS 1.57 mm; korelacja sqrt = 0.710
- dni mokre: GEFS/obs = 0.77; obs > max zespołu: 9.9% dni mokrych
- P(opad>=1 mm): P=0: n=1427, zaszło 1% | P=0-20%: n=1101, zaszło 6% | P=20-40%: n=659, zaszło 20% | P=40-60%: n=617, zaszło 37% | P=60-80%: n=591, zaszło 55% | P=80-100%: n=908, zaszło 74%
- P(opad>=5 mm): P=0: n=3015, zaszło 1% | P=0-20%: n=1294, zaszło 7% | P=20-40%: n=557, zaszło 23% | P=40-60%: n=236, zaszło 41% | P=60-80%: n=138, zaszło 55% | P=80-100%: n=63, zaszło 65%
- P(opad>=10 mm): P=0: n=4205, zaszło 1% | P=0-20%: n=874, zaszło 6% | P=20-40%: n=135, zaszło 33% | P=40-60%: n=74, zaszło 50% | P=60-80%: n=13, zaszło 69% | P=80-100%: n=2, zaszło 50%

## 2. Śnieg — metody rozpoznawania fazy opadu (okno 06->06 UTC)
Zdarzenie obserwowane: opad rodzaju S (śnieg) o sumie >= X mm. Prognoza: P(opad zamarznięty >= X mm) wg metody. Kolumna 'deszcz->śnieg' = odsetek dni z obserwowanym DESZCZEM >=3 mm, w których metoda daje P(śnieg>=3 mm) >= 30% (fałszywy śnieg).
### wyprzedzenie k=0: n=5249; obs śnieg >=1 mm: 607, >=3 mm: 315, >=5 mm: 194; deszcz >=3 mm: 330
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A dawna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.37 | 0.63 | 0.23 | 0.63 | 0.49 | 2% |
| D obecna (produkcja): T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.66 | 0.63 | 0.31 | 0.83 | 0.53 | 13% |
| G: CPOFP (gdy ważny), inaczej D | 0.41 | 0.63 | 0.24 | 0.71 | 0.51 | 4% |
| W0: mokry termometr, zimniejsza z 2 próbek (1@0C->0@2C) | 0.59 | 0.64 | 0.29 | 0.82 | 0.53 | 8% |
| W1: mokry termometr (1@0.5C->0@2.5C) | 0.69 | 0.62 | 0.32 | 0.88 | 0.54 | 13% |
| W2: mokry termometr (1@1C->0@3C) | 0.74 | 0.64 | 0.32 | 0.92 | 0.56 | 22% |
- wiarygodność P(śnieg>=3 mm), metoda 'D' (produkcyjna): P=0: n=4253, zaszło 1% | P=0-20%: n=359, zaszło 11% | P=20-40%: n=146, zaszło 21% | P=40-60%: n=109, zaszło 21% | P=60-80%: n=136, zaszło 35% | P=80-100%: n=246, zaszło 50%
### wyprzedzenie k=1: n=5304; obs śnieg >=1 mm: 650, >=3 mm: 336, >=5 mm: 191; deszcz >=3 mm: 402
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A dawna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.30 | 0.67 | 0.19 | 0.60 | 0.52 | 3% |
| D obecna (produkcja): T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.54 | 0.64 | 0.28 | 0.77 | 0.54 | 8% |
| G: CPOFP (gdy ważny), inaczej D | 0.32 | 0.66 | 0.20 | 0.68 | 0.52 | 3% |
| W0: mokry termometr, zimniejsza z 2 próbek (1@0C->0@2C) | 0.46 | 0.67 | 0.24 | 0.79 | 0.54 | 8% |
| W1: mokry termometr (1@0.5C->0@2.5C) | 0.57 | 0.64 | 0.28 | 0.85 | 0.55 | 10% |
| W2: mokry termometr (1@1C->0@3C) | 0.68 | 0.64 | 0.31 | 0.89 | 0.56 | 14% |
- wiarygodność P(śnieg>=3 mm), metoda 'D' (produkcyjna): P=0: n=4036, zaszło 1% | P=0-20%: n=643, zaszło 12% | P=20-40%: n=229, zaszło 24% | P=40-60%: n=137, zaszło 33% | P=60-80%: n=128, zaszło 39% | P=80-100%: n=131, zaszło 45%
### wyprzedzenie k=2: n=5303; obs śnieg >=1 mm: 612, >=3 mm: 308, >=5 mm: 176; deszcz >=3 mm: 419
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A dawna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.31 | 0.66 | 0.19 | 0.64 | 0.56 | 2% |
| D obecna (produkcja): T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.47 | 0.71 | 0.22 | 0.75 | 0.59 | 7% |
| G: CPOFP (gdy ważny), inaczej D | 0.32 | 0.67 | 0.19 | 0.69 | 0.56 | 3% |
| W0: mokry termometr, zimniejsza z 2 próbek (1@0C->0@2C) | 0.44 | 0.71 | 0.21 | 0.76 | 0.59 | 6% |
| W1: mokry termometr (1@0.5C->0@2.5C) | 0.52 | 0.70 | 0.24 | 0.81 | 0.60 | 8% |
| W2: mokry termometr (1@1C->0@3C) | 0.59 | 0.70 | 0.25 | 0.85 | 0.61 | 11% |
- wiarygodność P(śnieg>=3 mm), metoda 'D' (produkcyjna): P=0: n=3718, zaszło 1% | P=0-20%: n=913, zaszło 11% | P=20-40%: n=304, zaszło 17% | P=40-60%: n=187, zaszło 26% | P=60-80%: n=120, zaszło 42% | P=80-100%: n=61, zaszło 43%

## 3. Mróz — temperatura powietrza vs odczuwalna (okno doby kalendarzowej 00-24 UTC; obserwacja = TMIN powietrza)
Uwaga: IMGW mierzy tylko temperaturę powietrza, więc odczuwalnej NIE da się zweryfikować wprost; poniżej sprawdzamy, jak daleko od powietrza jest każda wersja i czy 'odczuwalna' nie robi fałszywych alarmów względem realnego mrozu.
### wyprzedzenie k=0: n=5237
- prognoza min. T powietrza: błąd średni +1.31 C, MAE 2.09 C; w mroźnych dniach (obs <= -10 C): błąd +3.67 C
- odczuwalna z PORYWÓW (dawna wersja hazardu; produkcja używa T powietrza): chłodniejsza od powietrza średnio o 5.9 C
- odczuwalna z wiatru ŚREDNIEGO: chłodniejsza od powietrza średnio o 4.3 C
- próg -5 C (obs zdarzeń 1135), powietrze: P>=30%: traf. 816, fałsz. 101, przegap. 319 (POD 0.72, FAR 0.11, CSI 0.66)
- próg -10 C (obs zdarzeń 472), powietrze: P>=30%: traf. 209, fałsz. 42, przegap. 263 (POD 0.44, FAR 0.17, CSI 0.41)
- próg -15 C (obs zdarzeń 108), powietrze: P>=30%: traf. 50, fałsz. 9, przegap. 58 (POD 0.46, FAR 0.15, CSI 0.43)
- próg -20 C (obs zdarzeń 23), powietrze: P>=30%: traf. 3, fałsz. 0, przegap. 20 (POD 0.13, FAR 0.00, CSI 0.13)
### wyprzedzenie k=1: n=5290
- prognoza min. T powietrza: błąd średni +1.36 C, MAE 2.14 C; w mroźnych dniach (obs <= -10 C): błąd +3.62 C
- odczuwalna z PORYWÓW (dawna wersja hazardu; produkcja używa T powietrza): chłodniejsza od powietrza średnio o 5.8 C
- odczuwalna z wiatru ŚREDNIEGO: chłodniejsza od powietrza średnio o 4.1 C
- próg -5 C (obs zdarzeń 1159), powietrze: P>=30%: traf. 847, fałsz. 94, przegap. 312 (POD 0.73, FAR 0.10, CSI 0.68)
- próg -10 C (obs zdarzeń 484), powietrze: P>=30%: traf. 217, fałsz. 63, przegap. 267 (POD 0.45, FAR 0.23, CSI 0.40)
- próg -15 C (obs zdarzeń 100), powietrze: P>=30%: traf. 44, fałsz. 23, przegap. 56 (POD 0.44, FAR 0.34, CSI 0.36)
- próg -20 C (obs zdarzeń 17), powietrze: P>=30%: traf. 2, fałsz. 0, przegap. 15 (POD 0.12, FAR 0.00, CSI 0.12)
### wyprzedzenie k=2: n=5292
- prognoza min. T powietrza: błąd średni +1.03 C, MAE 2.03 C; w mroźnych dniach (obs <= -10 C): błąd +3.69 C
- odczuwalna z PORYWÓW (dawna wersja hazardu; produkcja używa T powietrza): chłodniejsza od powietrza średnio o 5.7 C
- odczuwalna z wiatru ŚREDNIEGO: chłodniejsza od powietrza średnio o 4.1 C
- próg -5 C (obs zdarzeń 1036), powietrze: P>=30%: traf. 736, fałsz. 91, przegap. 300 (POD 0.71, FAR 0.11, CSI 0.65)
- próg -10 C (obs zdarzeń 427), powietrze: P>=30%: traf. 218, fałsz. 85, przegap. 209 (POD 0.51, FAR 0.28, CSI 0.43)
- próg -15 C (obs zdarzeń 98), powietrze: P>=30%: traf. 36, fałsz. 15, przegap. 62 (POD 0.37, FAR 0.29, CSI 0.32)
- próg -20 C (obs zdarzeń 13), powietrze: P>=30%: traf. 3, fałsz. 0, przegap. 10 (POD 0.23, FAR 0.00, CSI 0.23)

## 4. Gołoledź — opad w warunkach marznących (CFRZR >= 0.5) vs obserwowane godziny gołoledzi (GOLO)
- k=0, obs GOLO>=1 h: 18 zdarzeń z 665; prognoza P(opad marznący >= 0.1 mm): P>=10%: traf. 5, fałsz. 16, przegap. 13 (POD 0.28, FAR 0.76, CSI 0.15) | P>=30%: traf. 3, fałsz. 7, przegap. 15 (POD 0.17, FAR 0.70, CSI 0.12)
- k=0, obs GOLO>=1 h: 18 zdarzeń z 665; prognoza P(opad marznący >= 1.0 mm): P>=10%: traf. 4, fałsz. 6, przegap. 14 (POD 0.22, FAR 0.60, CSI 0.17) | P>=30%: traf. 3, fałsz. 2, przegap. 15 (POD 0.17, FAR 0.40, CSI 0.15)
- k=1, obs GOLO>=1 h: 26 zdarzeń z 672; prognoza P(opad marznący >= 0.1 mm): P>=10%: traf. 8, fałsz. 20, przegap. 18 (POD 0.31, FAR 0.71, CSI 0.17) | P>=30%: traf. 3, fałsz. 9, przegap. 23 (POD 0.12, FAR 0.75, CSI 0.09)
- k=1, obs GOLO>=1 h: 26 zdarzeń z 672; prognoza P(opad marznący >= 1.0 mm): P>=10%: traf. 4, fałsz. 8, przegap. 22 (POD 0.15, FAR 0.67, CSI 0.12) | P>=30%: traf. 3, fałsz. 4, przegap. 23 (POD 0.12, FAR 0.57, CSI 0.10)
- k=2, obs GOLO>=1 h: 45 zdarzeń z 672; prognoza P(opad marznący >= 0.1 mm): P>=10%: traf. 15, fałsz. 27, przegap. 30 (POD 0.33, FAR 0.64, CSI 0.21) | P>=30%: traf. 9, fałsz. 9, przegap. 36 (POD 0.20, FAR 0.50, CSI 0.17)
- k=2, obs GOLO>=1 h: 45 zdarzeń z 672; prognoza P(opad marznący >= 1.0 mm): P>=10%: traf. 11, fałsz. 15, przegap. 34 (POD 0.24, FAR 0.58, CSI 0.18) | P>=30%: traf. 2, fałsz. 0, przegap. 43 (POD 0.04, FAR 0.00, CSI 0.04)

## 5. Zamieć (gwałtowny wiatr + widzialność) — UWAGA: to NIE jest produkcyjny hazard Snow Squalls (CAPE + opad zamarznięty, nieweryfikowalny obserwacjami IMGW); sekcja sprawdza wycofany hazard BLIZZARD
## 5 (opis). Zamieć — definicja SWWF (porywy >= 15.5 m/s, widzialność <= 400 m, śnieg świeży/leżący) vs obserwowane godziny zamieci śnieżnej (ZMNI+ZMWS)
Uwaga: przebiegi bez pola widzialności (GEFS 2021) nie mogą dać flagi wg definicji SWWF, więc są z tej oceny wyłączone; wariant 'bez VIS' (porywy + śnieg) działa na wszystkich.
- k=0: obs zamieć >=1 h: 20 z 665 stacjodni
    definicja SWWF z VIS (tylko przebiegi z VIS, 665 stacjodni, 20 zdarzeń): P>=10%: traf. 9, fałsz. 18, przegap. 11 (POD 0.45, FAR 0.67, CSI 0.24) | P>=30%: traf. 2, fałsz. 7, przegap. 18 (POD 0.10, FAR 0.78, CSI 0.07)
    bez VIS (porywy >= 15.5 m/s + śnieg): P>=10%: traf. 11, fałsz. 99, przegap. 9 (POD 0.55, FAR 0.90, CSI 0.09) | P>=30%: traf. 8, fałsz. 55, przegap. 12 (POD 0.40, FAR 0.87, CSI 0.11) | P>=50%: traf. 7, fałsz. 48, przegap. 13 (POD 0.35, FAR 0.87, CSI 0.10)
    tylko porywy >= 15.5 m/s: P>=30%: traf. 11, fałsz. 123, przegap. 9 (POD 0.55, FAR 0.92, CSI 0.08) | P>=50%: traf. 8, fałsz. 102, przegap. 12 (POD 0.40, FAR 0.93, CSI 0.07)
    tylko porywy >= 20 m/s: P>=30%: traf. 2, fałsz. 28, przegap. 18 (POD 0.10, FAR 0.93, CSI 0.04) | P>=50%: traf. 1, fałsz. 18, przegap. 19 (POD 0.05, FAR 0.95, CSI 0.03)
- k=1: obs zamieć >=1 h: 24 z 672 stacjodni
    definicja SWWF z VIS (tylko przebiegi z VIS, 672 stacjodni, 24 zdarzeń): P>=10%: traf. 9, fałsz. 17, przegap. 15 (POD 0.38, FAR 0.65, CSI 0.22) | P>=30%: traf. 5, fałsz. 7, przegap. 19 (POD 0.21, FAR 0.58, CSI 0.16)
    bez VIS (porywy >= 15.5 m/s + śnieg): P>=10%: traf. 12, fałsz. 107, przegap. 12 (POD 0.50, FAR 0.90, CSI 0.09) | P>=30%: traf. 10, fałsz. 65, przegap. 14 (POD 0.42, FAR 0.87, CSI 0.11) | P>=50%: traf. 7, fałsz. 44, przegap. 17 (POD 0.29, FAR 0.86, CSI 0.10)
    tylko porywy >= 15.5 m/s: P>=30%: traf. 10, fałsz. 122, przegap. 14 (POD 0.42, FAR 0.92, CSI 0.07) | P>=50%: traf. 9, fałsz. 90, przegap. 15 (POD 0.38, FAR 0.91, CSI 0.08)
    tylko porywy >= 20 m/s: P>=30%: traf. 1, fałsz. 31, przegap. 23 (POD 0.04, FAR 0.97, CSI 0.02) | P>=50%: traf. 1, fałsz. 20, przegap. 23 (POD 0.04, FAR 0.95, CSI 0.02)

## 6. Fałszywe alarmy na dobach bez zdarzenia i trafienia na dobach ze zdarzeniem
Alarm = P(zdarzenia) >= 30% wg zespołu. Doba 'bez zdarzenia' = zdarzenie na <= 1 stacji (wtedy każdy alarm jest fałszywy); 'ze zdarzeniem' = na >= 5 stacjach. 'doby z >=3 stacjami' = ile dób miało alarm na co najmniej 3 stacjach naraz (tyle widziałby użytkownik jako plamę na mapie).
### wyprzedzenie k=0
- śnieg >= 3 mm: doby bez zdarzenia: 61, stacjodni 3375, fałszywych alarmów 36 (10.7 na 1000 stacjodni); doby z >=3 stacjami: 3 z 61
    doby ze zdarzeniem: 23, zdarzeń 284, trafionych 191 (POD 0.67), fałszywych alarmów na tych dobach 256
- opad >= 10 mm: doby bez zdarzenia: 74, stacjodni 4090, fałszywych alarmów 25 (6.1 na 1000 stacjodni); doby z >=3 stacjami: 5 z 74
    doby ze zdarzeniem: 12, zdarzeń 144, trafionych 125 (POD 0.87), fałszywych alarmów na tych dobach 66
- mróz TMIN <= -10 C: doby bez zdarzenia: 74, stacjodni 4098, fałszywych alarmów 11 (2.7 na 1000 stacjodni); doby z >=3 stacjami: 1 z 74
    doby ze zdarzeniem: 18, zdarzeń 461, trafionych 208 (POD 0.45), fałszywych alarmów na tych dobach 29
- mróz TMIN <= -15 C: doby bez zdarzenia: 84, stacjodni 4644, fałszywych alarmów 1 (0.2 na 1000 stacjodni); doby z >=3 stacjami: 0 z 84
    doby ze zdarzeniem: 8, zdarzeń 97, trafionych 50 (POD 0.52), fałszywych alarmów na tych dobach 8
- zamieć (porywy >= 15.5 m/s + śnieg, bez VIS): doby bez zdarzenia: 91, stacjodni 637, fałszywych alarmów 56 (87.9 na 1000 stacjodni); doby z >=3 stacjami: 7 z 91
    doby ze zdarzeniem: 1, zdarzeń 6, trafionych 3 (POD 0.50), fałszywych alarmów na tych dobach 0
### wyprzedzenie k=1
- śnieg >= 3 mm: doby bez zdarzenia: 58, stacjodni 3209, fałszywych alarmów 26 (8.1 na 1000 stacjodni); doby z >=3 stacjami: 4 z 58
    doby ze zdarzeniem: 25, zdarzeń 301, trafionych 167 (POD 0.55), fałszywych alarmów na tych dobach 235
- opad >= 10 mm: doby bez zdarzenia: 74, stacjodni 4084, fałszywych alarmów 18 (4.4 na 1000 stacjodni); doby z >=3 stacjami: 4 z 74
    doby ze zdarzeniem: 13, zdarzeń 153, trafionych 105 (POD 0.69), fałszywych alarmów na tych dobach 54
- mróz TMIN <= -10 C: doby bez zdarzenia: 73, stacjodni 4045, fałszywych alarmów 3 (0.7 na 1000 stacjodni); doby z >=3 stacjami: 0 z 73
    doby ze zdarzeniem: 21, zdarzeń 475, trafionych 217 (POD 0.46), fałszywych alarmów na tych dobach 57
- mróz TMIN <= -15 C: doby bez zdarzenia: 85, stacjodni 4696, fałszywych alarmów 6 (1.3 na 1000 stacjodni); doby z >=3 stacjami: 1 z 85
    doby ze zdarzeniem: 8, zdarzeń 88, trafionych 43 (POD 0.49), fałszywych alarmów na tych dobach 13
- zamieć (porywy >= 15.5 m/s + śnieg, bez VIS): doby bez zdarzenia: 91, stacjodni 637, fałszywych alarmów 64 (100.5 na 1000 stacjodni); doby z >=3 stacjami: 10 z 91
    doby ze zdarzeniem: 1, zdarzeń 6, trafionych 4 (POD 0.67), fałszywych alarmów na tych dobach 0
### wyprzedzenie k=2
- śnieg >= 3 mm: doby bez zdarzenia: 60, stacjodni 3316, fałszywych alarmów 83 (25.0 na 1000 stacjodni); doby z >=3 stacjami: 8 z 60
    doby ze zdarzeniem: 22, zdarzeń 266, trafionych 126 (POD 0.47), fałszywych alarmów na tych dobach 199
- opad >= 10 mm: doby bez zdarzenia: 77, stacjodni 4248, fałszywych alarmów 19 (4.5 na 1000 stacjodni); doby z >=3 stacjami: 2 z 77
    doby ze zdarzeniem: 12, zdarzeń 149, trafionych 67 (POD 0.45), fałszywych alarmów na tych dobach 46
- mróz TMIN <= -10 C: doby bez zdarzenia: 76, stacjodni 4210, fałszywych alarmów 13 (3.1 na 1000 stacjodni); doby z >=3 stacjami: 2 z 76
    doby ze zdarzeniem: 18, zdarzeń 417, trafionych 212 (POD 0.51), fałszywych alarmów na tych dobach 70
- mróz TMIN <= -15 C: doby bez zdarzenia: 84, stacjodni 4645, fałszywych alarmów 1 (0.2 na 1000 stacjodni); doby z >=3 stacjami: 0 z 84
    doby ze zdarzeniem: 8, zdarzeń 83, trafionych 34 (POD 0.41), fałszywych alarmów na tych dobach 10
- zamieć (porywy >= 15.5 m/s + śnieg, bez VIS): doby bez zdarzenia: 91, stacjodni 637, fałszywych alarmów 73 (114.6 na 1000 stacjodni); doby z >=3 stacjami: 12 z 91
    doby ze zdarzeniem: 1, zdarzeń 6, trafionych 3 (POD 0.50), fałszywych alarmów na tych dobach 0

## 7. Mróz — diagnoza niedoszacowania ogona zimna i test prostej korekty (TMIN, doba 00-24 UTC)
Błąd = obserwacja - prognoza (średnia zespołu min. T powietrza); UJEMNY = w rzeczywistości zimniej niż w prognozie (prognoza za ciepła). Przedziały wg PROGNOZY (wersja użyteczna do korekty; przedziały wg obserwacji zawyżają błąd przez regresję do średniej).
### wyprzedzenie k=0: n=5237
- błąd wg przedziałów prognozy: prog. < -15: n=49, błąd -2.98 C (mediana -2.68) | -15..-10: n=174, błąd -0.62 C (mediana -0.56) | -10..-5: n=656, błąd -1.75 C (mediana -1.73) | -5..0: n=1495, błąd -0.73 C (mediana -0.32) | > 0: n=2863, błąd -1.52 C (mediana -1.16)
- rozrzut zespołu (średnie odch. std) 0.37 C vs RMSE średniej zespołu 2.82 C; dla prognoz <= -5 C: rozrzut 0.39 C vs RMSE 3.54 C
- obserwacja zimniejsza niż WSZYSTKIE 30 członków: 54.1% stacjodni (przy dobrze rozproszonym zespole ~3%); dla prognoz <= -5 C: 57.6%
- błąd na dniach z prognozą <= -5 C wg stacji (n stacji=48): średnia -1.74 C, rozrzut między stacjami (std) 1.23 C
    najmniejszy błąd: LESZNO -3.9, JELENIA GÓRA -3.5, BIAŁYSTOK -3.5, ŁÓDŹ -3.5, SULEJÓW -3.2
    największy błąd: GDAŃSK-ŚWIBNO -0.0, BIELSKO-BIAŁA +0.2, LESKO +0.3, ZAKOPANE +0.4, KROSNO +0.5, NOWY SĄCZ +1.1
    korelacja błędu stacji z szerokością: -0.53, z długością: +0.20
- korekta liniowa po prognozie: MAE 2.09 -> 1.96 C; błąd średni -1.31 -> -0.42 C; średnie przesunięcie dla prognoz <= -10 C: -1.62 C (produkcja: -1.0 C); sigma resztowa ok. 2.45 C
- próg -5 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.72, FAR 0.11, CSI 0.66, fałszywych 101; na dobach bez zdarzenia 2.7 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.81, FAR 0.16, CSI 0.70, fałszywych 181; na dobach bez zdarzenia 8.5 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.81, FAR 0.18, CSI 0.69, fałszywych 196; na dobach bez zdarzenia 10.2 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.89, FAR 0.26, CSI 0.68, fałszywych 351; na dobach bez zdarzenia 24.5 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.89, FAR 0.26, CSI 0.68, fałszywych 357; na dobach bez zdarzenia 24.5 na 1000 stacjodni
- próg -10 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.44, FAR 0.17, CSI 0.41, fałszywych 42; na dobach bez zdarzenia 2.7 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.54, FAR 0.20, CSI 0.47, fałszywych 65; na dobach bez zdarzenia 3.7 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.59, FAR 0.23, CSI 0.50, fałszywych 85; na dobach bez zdarzenia 4.4 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.67, FAR 0.30, CSI 0.52, fałszywych 135; na dobach bez zdarzenia 6.3 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.69, FAR 0.32, CSI 0.52, fałszywych 151; na dobach bez zdarzenia 7.1 na 1000 stacjodni
- próg -15 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.46, FAR 0.15, CSI 0.43, fałszywych 9; na dobach bez zdarzenia 0.2 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.52, FAR 0.31, CSI 0.42, fałszywych 25; na dobach bez zdarzenia 0.2 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.55, FAR 0.41, CSI 0.40, fałszywych 41; na dobach bez zdarzenia 0.4 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.60, FAR 0.42, CSI 0.42, fałszywych 48; na dobach bez zdarzenia 0.6 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.63, FAR 0.51, CSI 0.38, fałszywych 71; na dobach bez zdarzenia 1.3 na 1000 stacjodni
### wyprzedzenie k=1: n=5290
- błąd wg przedziałów prognozy: prog. < -15: n=50, błąd -1.50 C (mediana -1.25) | -15..-10: n=198, błąd +0.03 C (mediana -0.17) | -10..-5: n=641, błąd -1.95 C (mediana -1.70) | -5..0: n=1303, błąd -0.99 C (mediana -0.42) | > 0: n=3098, błąd -1.48 C (mediana -1.14)
- rozrzut zespołu (średnie odch. std) 0.59 C vs RMSE średniej zespołu 2.88 C; dla prognoz <= -5 C: rozrzut 0.67 C vs RMSE 3.65 C
- obserwacja zimniejsza niż WSZYSTKIE 30 członków: 47.1% stacjodni (przy dobrze rozproszonym zespole ~3%); dla prognoz <= -5 C: 48.0%
- błąd na dniach z prognozą <= -5 C wg stacji (n stacji=50): średnia -1.50 C, rozrzut między stacjami (std) 1.34 C
    najmniejszy błąd: BIAŁYSTOK -3.8, JELENIA GÓRA -3.7, SŁUBICE -3.4, TERESPOL -3.3, LESZNO -3.2
    największy błąd: ZAKOPANE +0.3, KROSNO +0.8, LESKO +0.8, NOWY SĄCZ +1.0, GDAŃSK-ŚWIBNO +1.0, HEL +2.1
    korelacja błędu stacji z szerokością: -0.26, z długością: +0.13
- korekta liniowa po prognozie: MAE 2.14 -> 1.99 C; błąd średni -1.36 -> -0.37 C; średnie przesunięcie dla prognoz <= -10 C: -1.44 C (produkcja: -1.0 C); sigma resztowa ok. 2.55 C
- próg -5 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.73, FAR 0.10, CSI 0.68, fałszywych 94; na dobach bez zdarzenia 3.0 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.81, FAR 0.14, CSI 0.71, fałszywych 157; na dobach bez zdarzenia 10.1 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.81, FAR 0.15, CSI 0.71, fałszywych 171; na dobach bez zdarzenia 12.1 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.90, FAR 0.21, CSI 0.72, fałszywych 276; na dobach bez zdarzenia 24.3 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.90, FAR 0.22, CSI 0.72, fałszywych 293; na dobach bez zdarzenia 27.5 na 1000 stacjodni
- próg -10 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.45, FAR 0.23, CSI 0.40, fałszywych 63; na dobach bez zdarzenia 0.7 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.55, FAR 0.29, CSI 0.45, fałszywych 106; na dobach bez zdarzenia 2.0 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.56, FAR 0.31, CSI 0.45, fałszywych 124; na dobach bez zdarzenia 2.5 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.63, FAR 0.35, CSI 0.47, fałszywych 168; na dobach bez zdarzenia 3.7 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.64, FAR 0.37, CSI 0.46, fałszywych 179; na dobach bez zdarzenia 4.4 na 1000 stacjodni
- próg -15 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.44, FAR 0.34, CSI 0.36, fałszywych 23; na dobach bez zdarzenia 1.3 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.51, FAR 0.43, CSI 0.37, fałszywych 38; na dobach bez zdarzenia 2.3 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.56, FAR 0.50, CSI 0.36, fałszywych 57; na dobach bez zdarzenia 3.2 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.60, FAR 0.52, CSI 0.36, fałszywych 66; na dobach bez zdarzenia 3.4 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.62, FAR 0.54, CSI 0.36, fałszywych 73; na dobach bez zdarzenia 4.3 na 1000 stacjodni
### wyprzedzenie k=2: n=5292
- błąd wg przedziałów prognozy: prog. < -15: n=39, błąd -1.36 C (mediana -1.84) | -15..-10: n=218, błąd -0.07 C (mediana -0.10) | -10..-5: n=492, błąd -1.93 C (mediana -1.47) | -5..0: n=1431, błąd -0.85 C (mediana -0.27) | > 0: n=3112, błąd -1.04 C (mediana -0.83)
- rozrzut zespołu (średnie odch. std) 0.86 C vs RMSE średniej zespołu 2.73 C; dla prognoz <= -5 C: rozrzut 0.98 C vs RMSE 3.72 C
- obserwacja zimniejsza niż WSZYSTKIE 30 członków: 34.6% stacjodni (przy dobrze rozproszonym zespole ~3%); dla prognoz <= -5 C: 40.7%
- błąd na dniach z prognozą <= -5 C wg stacji (n stacji=49): średnia -1.41 C, rozrzut między stacjami (std) 1.45 C
    najmniejszy błąd: JELENIA GÓRA -4.9, LESZNO -4.0, SŁUBICE -3.9, BIAŁYSTOK -3.3, WŁODAWA -3.2
    największy błąd: ZAKOPANE +0.2, LESKO +0.9, NOWY SĄCZ +1.2, KROSNO +1.2, GDAŃSK-ŚWIBNO +1.3, HEL +2.4
    korelacja błędu stacji z szerokością: -0.10, z długością: +0.19
- korekta liniowa po prognozie: MAE 2.03 -> 1.97 C; błąd średni -1.03 -> -0.26 C; średnie przesunięcie dla prognoz <= -10 C: -1.38 C (produkcja: -1.0 C); sigma resztowa ok. 2.57 C
- próg -5 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.71, FAR 0.11, CSI 0.65, fałszywych 91; na dobach bez zdarzenia 4.7 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.80, FAR 0.17, CSI 0.69, fałszywych 167; na dobach bez zdarzenia 13.6 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.79, FAR 0.17, CSI 0.69, fałszywych 164; na dobach bez zdarzenia 13.6 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.88, FAR 0.25, CSI 0.68, fałszywych 304; na dobach bez zdarzenia 32.2 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.87, FAR 0.24, CSI 0.68, fałszywych 280; na dobach bez zdarzenia 29.0 na 1000 stacjodni
- próg -10 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.51, FAR 0.28, CSI 0.43, fałszywych 85; na dobach bez zdarzenia 2.6 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.57, FAR 0.35, CSI 0.44, fałszywych 129; na dobach bez zdarzenia 4.5 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.58, FAR 0.36, CSI 0.44, fałszywych 137; na dobach bez zdarzenia 4.5 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.62, FAR 0.38, CSI 0.45, fałszywych 163; na dobach bez zdarzenia 5.2 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.62, FAR 0.39, CSI 0.44, fałszywych 171; na dobach bez zdarzenia 5.5 na 1000 stacjodni
- próg -15 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.37, FAR 0.29, CSI 0.32, fałszywych 15; na dobach bez zdarzenia 0.2 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.46, FAR 0.44, CSI 0.34, fałszywych 36; na dobach bez zdarzenia 0.6 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.50, FAR 0.49, CSI 0.34, fałszywych 47; na dobach bez zdarzenia 0.9 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.52, FAR 0.49, CSI 0.35, fałszywych 49; na dobach bez zdarzenia 0.6 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.55, FAR 0.57, CSI 0.32, fałszywych 71; na dobach bez zdarzenia 1.3 na 1000 stacjodni

## 8. Śnieg — test skalowania ilości opadu zamarzniętego (wariant D) i progu alarmu
Skala f mnoży opad zamarznięty każdego członka (f=1,0 = obecna produkcja). Zdarzenie = obserwowany opad rodzaju S >= X mm (SMDB). Doby bez zdarzenia = zdarzenie na <= 1 stacji. Uwaga: to ilość WODY (mm), nie centymetry śniegu — przelicznik śnieg:woda jest osobną sprawą.
### wyprzedzenie k=0: n=5249
- stosunek średniej obserwowanego śniegu (mm) do średniej prognozy wg przedziałów prognozy: 0,5-1 mm: n=301, obs/prog. = 1.40 | 1-3 mm: n=484, obs/prog. = 0.76 | 3-6 mm: n=291, obs/prog. = 0.61 | >6 mm: n=131, obs/prog. = 0.72
- próg 3 mm:
    f=1.0, alarm przy P>=30%: POD 0.66, FAR 0.63, CSI 0.31, fałszywych 349; na dobach bez zdarzenia 10.4 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.58, FAR 0.59, CSI 0.32, fałszywych 260; na dobach bez zdarzenia 5.9 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.63, FAR 0.61, CSI 0.32, fałszywych 307; na dobach bez zdarzenia 8.0 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.56, FAR 0.55, CSI 0.33, fałszywych 213; na dobach bez zdarzenia 4.7 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.60, FAR 0.58, CSI 0.33, fałszywych 266; na dobach bez zdarzenia 6.8 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.52, FAR 0.51, CSI 0.34, fałszywych 173; na dobach bez zdarzenia 4.1 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.57, FAR 0.53, CSI 0.34, fałszywych 207; na dobach bez zdarzenia 4.7 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.47, FAR 0.47, CSI 0.33, fałszywych 132; na dobach bez zdarzenia 2.7 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.52, FAR 0.49, CSI 0.35, fałszywych 154; na dobach bez zdarzenia 4.1 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.38, FAR 0.44, CSI 0.29, fałszywych 94; na dobach bez zdarzenia 1.2 na 1000 stacjodni
- próg 5 mm:
    f=1.0, alarm przy P>=30%: POD 0.57, FAR 0.65, CSI 0.28, fałszywych 206; na dobach bez zdarzenia 12.3 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.46, FAR 0.58, CSI 0.28, fałszywych 124; na dobach bez zdarzenia 4.8 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.54, FAR 0.60, CSI 0.30, fałszywych 158; na dobach bez zdarzenia 8.8 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.40, FAR 0.52, CSI 0.28, fałszywych 86; na dobach bez zdarzenia 2.8 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.51, FAR 0.54, CSI 0.32, fałszywych 117; na dobach bez zdarzenia 5.0 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.30, FAR 0.50, CSI 0.23, fałszywych 57; na dobach bez zdarzenia 1.8 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.40, FAR 0.47, CSI 0.30, fałszywych 67; na dobach bez zdarzenia 2.5 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.25, FAR 0.41, CSI 0.21, fałszywych 34; na dobach bez zdarzenia 1.0 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.32, FAR 0.37, CSI 0.27, fałszywych 36; na dobach bez zdarzenia 1.3 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.18, FAR 0.38, CSI 0.16, fałszywych 21; na dobach bez zdarzenia 0.5 na 1000 stacjodni
### wyprzedzenie k=1: n=5304
- stosunek średniej obserwowanego śniegu (mm) do średniej prognozy wg przedziałów prognozy: 0,5-1 mm: n=345, obs/prog. = 1.62 | 1-3 mm: n=567, obs/prog. = 0.91 | 3-6 mm: n=282, obs/prog. = 0.71 | >6 mm: n=87, obs/prog. = 0.61
- próg 3 mm:
    f=1.0, alarm przy P>=30%: POD 0.54, FAR 0.64, CSI 0.28, fałszywych 319; na dobach bez zdarzenia 7.8 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.41, FAR 0.58, CSI 0.26, fałszywych 190; na dobach bez zdarzenia 3.1 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.51, FAR 0.61, CSI 0.28, fałszywych 269; na dobach bez zdarzenia 6.9 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.34, FAR 0.58, CSI 0.23, fałszywych 158; na dobach bez zdarzenia 2.5 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.47, FAR 0.59, CSI 0.28, fałszywych 232; na dobach bez zdarzenia 5.0 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.30, FAR 0.57, CSI 0.21, fałszywych 136; na dobach bez zdarzenia 1.6 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.43, FAR 0.55, CSI 0.28, fałszywych 178; na dobach bez zdarzenia 3.1 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.25, FAR 0.54, CSI 0.20, fałszywych 99; na dobach bez zdarzenia 0.3 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.35, FAR 0.54, CSI 0.25, fałszywych 136; na dobach bez zdarzenia 1.9 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.20, FAR 0.48, CSI 0.17, fałszywych 64; na dobach bez zdarzenia 0.0 na 1000 stacjodni
- próg 5 mm:
    f=1.0, alarm przy P>=30%: POD 0.35, FAR 0.73, CSI 0.18, fałszywych 185; na dobach bez zdarzenia 10.2 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.24, FAR 0.66, CSI 0.16, fałszywych 87; na dobach bez zdarzenia 3.1 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.29, FAR 0.71, CSI 0.17, fałszywych 137; na dobach bez zdarzenia 5.6 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.20, FAR 0.63, CSI 0.15, fałszywych 64; na dobach bez zdarzenia 2.3 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.25, FAR 0.68, CSI 0.16, fałszywych 99; na dobach bez zdarzenia 4.3 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.15, FAR 0.58, CSI 0.13, fałszywych 40; na dobach bez zdarzenia 1.0 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.23, FAR 0.58, CSI 0.17, fałszywych 62; na dobach bez zdarzenia 2.8 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.12, FAR 0.50, CSI 0.11, fałszywych 23; na dobach bez zdarzenia 0.8 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.17, FAR 0.51, CSI 0.14, fałszywych 33; na dobach bez zdarzenia 1.3 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.07, FAR 0.43, CSI 0.06, fałszywych 10; na dobach bez zdarzenia 0.3 na 1000 stacjodni
### wyprzedzenie k=2: n=5303
- stosunek średniej obserwowanego śniegu (mm) do średniej prognozy wg przedziałów prognozy: 0,5-1 mm: n=428, obs/prog. = 1.35 | 1-3 mm: n=631, obs/prog. = 0.69 | 3-6 mm: n=240, obs/prog. = 0.72 | >6 mm: n=60, obs/prog. = 0.70
- próg 3 mm:
    f=1.0, alarm przy P>=30%: POD 0.47, FAR 0.71, CSI 0.22, fałszywych 357; na dobach bez zdarzenia 24.1 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.33, FAR 0.62, CSI 0.22, fałszywych 165; na dobach bez zdarzenia 9.0 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.45, FAR 0.67, CSI 0.23, fałszywych 280; na dobach bez zdarzenia 19.3 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.29, FAR 0.59, CSI 0.20, fałszywych 130; na dobach bez zdarzenia 6.0 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.41, FAR 0.64, CSI 0.24, fałszywych 223; na dobach bez zdarzenia 13.3 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.25, FAR 0.56, CSI 0.19, fałszywych 97; na dobach bez zdarzenia 3.3 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.37, FAR 0.62, CSI 0.23, fałszywych 181; na dobach bez zdarzenia 10.0 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.19, FAR 0.56, CSI 0.15, fałszywych 75; na dobach bez zdarzenia 2.1 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.30, FAR 0.57, CSI 0.21, fałszywych 125; na dobach bez zdarzenia 5.7 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.13, FAR 0.53, CSI 0.11, fałszywych 45; na dobach bez zdarzenia 0.9 na 1000 stacjodni
- próg 5 mm:
    f=1.0, alarm przy P>=30%: POD 0.32, FAR 0.74, CSI 0.17, fałszywych 161; na dobach bez zdarzenia 11.5 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.12, FAR 0.74, CSI 0.09, fałszywych 63; na dobach bez zdarzenia 3.1 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.27, FAR 0.70, CSI 0.16, fałszywych 111; na dobach bez zdarzenia 7.1 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.09, FAR 0.77, CSI 0.07, fałszywych 49; na dobach bez zdarzenia 2.3 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.20, FAR 0.71, CSI 0.14, fałszywych 90; na dobach bez zdarzenia 5.1 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.06, FAR 0.73, CSI 0.05, fałszywych 30; na dobach bez zdarzenia 1.0 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.15, FAR 0.70, CSI 0.11, fałszywych 63; na dobach bez zdarzenia 4.3 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.03, FAR 0.75, CSI 0.03, fałszywych 15; na dobach bez zdarzenia 0.5 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.10, FAR 0.66, CSI 0.08, fałszywych 33; na dobach bez zdarzenia 2.0 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.02, FAR 0.73, CSI 0.02, fałszywych 8; na dobach bez zdarzenia 0.0 na 1000 stacjodni

## 9. Przelicznik śnieg:woda — przyrost pokrywy śnieżnej (PKSN) / opad dobowy (SMDB), doby z opadem śniegu
Doba D: ROOP = S, SMDB >= 2 mm, PKSN znane w D i D-1, przyrost > 0. Temperatura = (TMIN+TMAX)/2 doby. Wartość = cm śniegu na 1 mm wody (10 = klasyczne 10:1). Uwaga: przyrost pokrywy jest DOLNYM oszacowaniem (osiadanie, topnienie, zawianie), a niedoszacowanie opadu przez deszczomierz przy śniegu (wiatr) zawyża iloraz — wynik traktować jako rząd wielkości.
- dób z przyrostem pokrywy: 1317; mediana ilorazu 0.6 cm/mm (kwartyle 0.3-1.3)
- T śr. < -10 C: n=102, mediana 0.7 cm/mm (kwartyle 0.4-2.1); produkcja używa 1.5 cm/mm (15:1)
- T śr. -10..-5 C: n=262, mediana 0.7 cm/mm (kwartyle 0.3-1.4); produkcja używa 1.2 cm/mm (12:1)
- T śr. -5..0 C: n=604, mediana 0.7 cm/mm (kwartyle 0.3-1.4); produkcja używa 1.0 cm/mm (10:1)
- T śr. > 0 C: n=349, mediana 0.4 cm/mm (kwartyle 0.2-1.0); produkcja używa 0.7 cm/mm (7:1)

## 10. Śnieg w cm — prognoza produkcyjna vs przyrost pokrywy śnieżnej (PKSN D - PKSN D-1)
Prognoza = suma po 4 oknach: opad * frakcja zamarznięta (wariant D) / 10 * przelicznik (15/12/10/7 z T na końcu okna), skala g mnoży cm. Zdarzenie = przyrost pokrywy >= X cm. UWAGA: przyrost pokrywy to DOLNE oszacowanie świeżego śniegu (osiadanie, topnienie, zawianie), więc 'obs/prog.' < 1 częściowo wynika z samego pomiaru; interpretować porównawczo (czy g poprawia CSI), nie jako dokładny współczynnik.
### wyprzedzenie k=0: n=4459
- wg przedziałów prognozy (średnia zespołu): 1-3 cm: n=427, śr. prog. 1.9 cm, śr. obs 0.7 cm (obs/prog. = 0.38) | 3-6 cm: n=218, śr. prog. 4.3 cm, śr. obs 1.7 cm (obs/prog. = 0.40) | 6-10 cm: n=63, śr. prog. 7.5 cm, śr. obs 3.2 cm (obs/prog. = 0.43) | >10 cm: n=16, śr. prog. 12.5 cm, śr. obs 3.4 cm (obs/prog. = 0.28)
- próg 5 cm (zdarzeń 102):
    g=1.0, alarm przy P>=30%: POD 0.43, FAR 0.78, CSI 0.17, fałszywych 152; na dobach bez zdarzenia 19.2 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.36, FAR 0.73, CSI 0.18, fałszywych 101; na dobach bez zdarzenia 12.4 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.32, FAR 0.75, CSI 0.17, fałszywych 97; na dobach bez zdarzenia 11.6 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.15, FAR 0.78, CSI 0.10, fałszywych 54; na dobach bez zdarzenia 5.7 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.13, FAR 0.77, CSI 0.09, fałszywych 43; na dobach bez zdarzenia 4.3 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.08, FAR 0.75, CSI 0.06, fałszywych 24; na dobach bez zdarzenia 3.2 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.09, FAR 0.74, CSI 0.07, fałszywych 26; na dobach bez zdarzenia 3.8 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.07, FAR 0.59, CSI 0.06, fałszywych 10; na dobach bez zdarzenia 1.4 na 1000 stacjodni
- próg 10 cm (zdarzeń 16):
    g=1.0, alarm przy P>=30%: POD 0.12, FAR 0.94, CSI 0.04, fałszywych 33; na dobach bez zdarzenia 6.0 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 17; na dobach bez zdarzenia 3.0 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 15; na dobach bez zdarzenia 2.8 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 10; na dobach bez zdarzenia 1.9 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 4; na dobach bez zdarzenia 0.7 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.00, FAR 0.00, CSI 0.00, fałszywych 0; na dobach bez zdarzenia 0.0 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.00, FAR 0.00, CSI 0.00, fałszywych 0; na dobach bez zdarzenia 0.0 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.00, FAR 0.00, CSI 0.00, fałszywych 0; na dobach bez zdarzenia 0.0 na 1000 stacjodni
### wyprzedzenie k=1: n=4496
- wg przedziałów prognozy (średnia zespołu): 1-3 cm: n=471, śr. prog. 1.8 cm, śr. obs 1.1 cm (obs/prog. = 0.60) | 3-6 cm: n=195, śr. prog. 4.2 cm, śr. obs 1.6 cm (obs/prog. = 0.38) | 6-10 cm: n=38, śr. prog. 7.2 cm, śr. obs 2.7 cm (obs/prog. = 0.37) | >10 cm: n=15, śr. prog. 11.4 cm, śr. obs 3.2 cm (obs/prog. = 0.28)
- próg 5 cm (zdarzeń 128):
    g=1.0, alarm przy P>=30%: POD 0.27, FAR 0.79, CSI 0.13, fałszywych 129; na dobach bez zdarzenia 12.8 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.16, FAR 0.74, CSI 0.11, fałszywych 61; na dobach bez zdarzenia 4.7 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.16, FAR 0.77, CSI 0.10, fałszywych 72; na dobach bez zdarzenia 5.0 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.09, FAR 0.72, CSI 0.07, fałszywych 29; na dobach bez zdarzenia 2.8 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.10, FAR 0.70, CSI 0.08, fałszywych 30; na dobach bez zdarzenia 3.1 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.05, FAR 0.63, CSI 0.05, fałszywych 12; na dobach bez zdarzenia 1.7 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.08, FAR 0.64, CSI 0.07, fałszywych 18; na dobach bez zdarzenia 2.2 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.03, FAR 0.56, CSI 0.03, fałszywych 5; na dobach bez zdarzenia 0.6 na 1000 stacjodni
- próg 10 cm (zdarzeń 28):
    g=1.0, alarm przy P>=30%: POD 0.11, FAR 0.89, CSI 0.06, fałszywych 25; na dobach bez zdarzenia 4.5 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.04, FAR 0.89, CSI 0.03, fałszywych 8; na dobach bez zdarzenia 1.7 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.04, FAR 0.91, CSI 0.03, fałszywych 10; na dobach bez zdarzenia 1.9 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 2; na dobach bez zdarzenia 0.5 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 1; na dobach bez zdarzenia 0.2 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.00, FAR 0.00, CSI 0.00, fałszywych 0; na dobach bez zdarzenia 0.0 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.00, FAR 0.00, CSI 0.00, fałszywych 0; na dobach bez zdarzenia 0.0 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.00, FAR 0.00, CSI 0.00, fałszywych 0; na dobach bez zdarzenia 0.0 na 1000 stacjodni
### wyprzedzenie k=2: n=4551
- wg przedziałów prognozy (średnia zespołu): 1-3 cm: n=499, śr. prog. 1.8 cm, śr. obs 0.9 cm (obs/prog. = 0.51) | 3-6 cm: n=192, śr. prog. 4.1 cm, śr. obs 1.4 cm (obs/prog. = 0.34) | 6-10 cm: n=24, śr. prog. 7.3 cm, śr. obs 2.2 cm (obs/prog. = 0.30)
- próg 5 cm (zdarzeń 113):
    g=1.0, alarm przy P>=30%: POD 0.17, FAR 0.86, CSI 0.08, fałszywych 121; na dobach bez zdarzenia 16.5 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.08, FAR 0.82, CSI 0.06, fałszywych 42; na dobach bez zdarzenia 4.8 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.11, FAR 0.84, CSI 0.07, fałszywych 63; na dobach bez zdarzenia 6.9 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.05, FAR 0.71, CSI 0.05, fałszywych 15; na dobach bez zdarzenia 2.1 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.05, FAR 0.75, CSI 0.05, fałszywych 18; na dobach bez zdarzenia 2.4 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.03, FAR 0.50, CSI 0.03, fałszywych 3; na dobach bez zdarzenia 0.5 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.04, FAR 0.60, CSI 0.03, fałszywych 6; na dobach bez zdarzenia 1.1 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.02, FAR 0.33, CSI 0.02, fałszywych 1; na dobach bez zdarzenia 0.0 na 1000 stacjodni
- próg 10 cm (zdarzeń 18):
    g=1.0, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 10; na dobach bez zdarzenia 1.8 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 3; na dobach bez zdarzenia 0.5 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 3; na dobach bez zdarzenia 0.5 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 2; na dobach bez zdarzenia 0.2 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.00, FAR 0.00, CSI 0.00, fałszywych 0; na dobach bez zdarzenia 0.0 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.00, FAR 0.00, CSI 0.00, fałszywych 0; na dobach bez zdarzenia 0.0 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.00, FAR 0.00, CSI 0.00, fałszywych 0; na dobach bez zdarzenia 0.0 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.00, FAR 0.00, CSI 0.00, fałszywych 0; na dobach bez zdarzenia 0.0 na 1000 stacjodni

## 11. Mróz — test wygładzenia rozrzutu odtwarzający planowaną zmianę produkcyjną (stałe sigma wg wyprzedzenia)
Sigma całkowita wg wyprzedzenia: {0: 2.35, 1: 2.59, 2: 2.78}. Środek = temperatura członka + korekta produkcyjna -1.0 C. w = waga wygładzenia (0 = obecna produkcja). Doby bez zdarzenia = zdarzenie (TMIN <= próg) na <= 1 stacji. 'fałsz. bez zdarz.' = fałszywe alarmy na 1000 stacjodni z tych dób.
### wyprzedzenie k=0: n=5237, sigma całkowita 2.35 C, średni dodany rozrzut 2.31 C
- próg -5 C (zdarzeń 1135):
    w=0.00 (produkcja): P>=10%: POD 0.83 FAR 0.20 CSI 0.69 fałsz. bez zdarz. 14.6 | P>=20%: POD 0.82 FAR 0.18 CSI 0.69 fałsz. bez zdarz. 9.9 | P>=30%: POD 0.81 FAR 0.16 CSI 0.70 fałsz. bez zdarz. 8.5 | P>=50%: POD 0.80 FAR 0.15 CSI 0.70 fałsz. bez zdarz. 7.8
    w=0.50: P>=10%: POD 0.91 FAR 0.28 CSI 0.67 fałsz. bez zdarz. 31.3 | P>=20%: POD 0.88 FAR 0.24 CSI 0.69 fałsz. bez zdarz. 21.5 | P>=30%: POD 0.85 FAR 0.20 CSI 0.70 fałsz. bez zdarz. 14.6 | P>=50%: POD 0.80 FAR 0.15 CSI 0.70 fałsz. bez zdarz. 6.8
    w=0.75: P>=10%: POD 0.94 FAR 0.35 CSI 0.62 fałsz. bez zdarz. 61.3 | P>=20%: POD 0.91 FAR 0.27 CSI 0.68 fałsz. bez zdarz. 27.2 | P>=30%: POD 0.88 FAR 0.23 CSI 0.69 fałsz. bez zdarz. 20.8 | P>=50%: POD 0.80 FAR 0.15 CSI 0.70 fałsz. bez zdarz. 6.8
    w=1.00: P>=10%: POD 0.96 FAR 0.42 CSI 0.56 fałsz. bez zdarz. 102.9 | P>=20%: POD 0.94 FAR 0.32 CSI 0.65 fałsz. bez zdarz. 46.7 | P>=30%: POD 0.89 FAR 0.25 CSI 0.68 fałsz. bez zdarz. 23.8 | P>=50%: POD 0.80 FAR 0.15 CSI 0.70 fałsz. bez zdarz. 6.8
- próg -10 C (zdarzeń 472):
    w=0.00 (produkcja): P>=10%: POD 0.57 FAR 0.25 CSI 0.48 fałsz. bez zdarz. 4.1 | P>=20%: POD 0.55 FAR 0.21 CSI 0.48 fałsz. bez zdarz. 4.1 | P>=30%: POD 0.54 FAR 0.20 CSI 0.47 fałsz. bez zdarz. 3.7 | P>=50%: POD 0.53 FAR 0.18 CSI 0.47 fałsz. bez zdarz. 2.9
    w=0.50: P>=10%: POD 0.70 FAR 0.32 CSI 0.52 fałsz. bez zdarz. 6.8 | P>=20%: POD 0.63 FAR 0.28 CSI 0.51 fałsz. bez zdarz. 5.4 | P>=30%: POD 0.60 FAR 0.24 CSI 0.51 fałsz. bez zdarz. 4.4 | P>=50%: POD 0.53 FAR 0.18 CSI 0.47 fałsz. bez zdarz. 2.9
    w=0.75: P>=10%: POD 0.78 FAR 0.37 CSI 0.53 fałsz. bez zdarz. 10.2 | P>=20%: POD 0.69 FAR 0.31 CSI 0.53 fałsz. bez zdarz. 6.8 | P>=30%: POD 0.62 FAR 0.27 CSI 0.50 fałsz. bez zdarz. 4.9 | P>=50%: POD 0.53 FAR 0.18 CSI 0.47 fałsz. bez zdarz. 2.9
    w=1.00: P>=10%: POD 0.86 FAR 0.44 CSI 0.51 fałsz. bez zdarz. 14.4 | P>=20%: POD 0.74 FAR 0.34 CSI 0.54 fałsz. bez zdarz. 8.5 | P>=30%: POD 0.66 FAR 0.30 CSI 0.52 fałsz. bez zdarz. 6.3 | P>=50%: POD 0.53 FAR 0.18 CSI 0.47 fałsz. bez zdarz. 2.9
- próg -15 C (zdarzeń 108):
    w=0.00 (produkcja): P>=10%: POD 0.54 FAR 0.33 CSI 0.42 fałsz. bez zdarz. 0.4 | P>=20%: POD 0.52 FAR 0.31 CSI 0.42 fałsz. bez zdarz. 0.2 | P>=30%: POD 0.52 FAR 0.31 CSI 0.42 fałsz. bez zdarz. 0.2 | P>=50%: POD 0.52 FAR 0.28 CSI 0.43 fałsz. bez zdarz. 0.2
    w=0.50: P>=10%: POD 0.62 FAR 0.49 CSI 0.39 fałsz. bez zdarz. 0.9 | P>=20%: POD 0.56 FAR 0.41 CSI 0.40 fałsz. bez zdarz. 0.4 | P>=30%: POD 0.52 FAR 0.33 CSI 0.41 fałsz. bez zdarz. 0.2 | P>=50%: POD 0.52 FAR 0.27 CSI 0.43 fałsz. bez zdarz. 0.2
    w=0.75: P>=10%: POD 0.68 FAR 0.52 CSI 0.39 fałsz. bez zdarz. 1.9 | P>=20%: POD 0.62 FAR 0.46 CSI 0.41 fałsz. bez zdarz. 0.9 | P>=30%: POD 0.55 FAR 0.38 CSI 0.41 fałsz. bez zdarz. 0.2 | P>=50%: POD 0.52 FAR 0.27 CSI 0.43 fałsz. bez zdarz. 0.2
    w=1.00: P>=10%: POD 0.69 FAR 0.57 CSI 0.36 fałsz. bez zdarz. 2.6 | P>=20%: POD 0.65 FAR 0.50 CSI 0.39 fałsz. bez zdarz. 1.3 | P>=30%: POD 0.60 FAR 0.42 CSI 0.42 fałsz. bez zdarz. 0.4 | P>=50%: POD 0.52 FAR 0.27 CSI 0.43 fałsz. bez zdarz. 0.2
### wyprzedzenie k=1: n=5290, sigma całkowita 2.59 C, średni dodany rozrzut 2.50 C
- próg -5 C (zdarzeń 1159):
    w=0.00 (produkcja): P>=10%: POD 0.84 FAR 0.19 CSI 0.70 fałsz. bez zdarz. 22.2 | P>=20%: POD 0.82 FAR 0.16 CSI 0.71 fałsz. bez zdarz. 12.7 | P>=30%: POD 0.81 FAR 0.14 CSI 0.71 fałsz. bez zdarz. 10.1 | P>=50%: POD 0.80 FAR 0.13 CSI 0.71 fałsz. bez zdarz. 6.8
    w=0.50: P>=10%: POD 0.92 FAR 0.25 CSI 0.70 fałsz. bez zdarz. 40.9 | P>=20%: POD 0.89 FAR 0.20 CSI 0.73 fałsz. bez zdarz. 22.2 | P>=30%: POD 0.85 FAR 0.16 CSI 0.73 fałsz. bez zdarz. 13.0 | P>=50%: POD 0.80 FAR 0.13 CSI 0.71 fałsz. bez zdarz. 6.8
    w=0.75: P>=10%: POD 0.94 FAR 0.32 CSI 0.65 fałsz. bez zdarz. 70.5 | P>=20%: POD 0.92 FAR 0.24 CSI 0.71 fałsz. bez zdarz. 34.1 | P>=30%: POD 0.88 FAR 0.19 CSI 0.73 fałsz. bez zdarz. 17.5 | P>=50%: POD 0.80 FAR 0.13 CSI 0.71 fałsz. bez zdarz. 6.8
    w=1.00: P>=10%: POD 0.96 FAR 0.39 CSI 0.59 fałsz. bez zdarz. 117.0 | P>=20%: POD 0.93 FAR 0.28 CSI 0.68 fałsz. bez zdarz. 53.0 | P>=30%: POD 0.90 FAR 0.21 CSI 0.72 fałsz. bez zdarz. 25.5 | P>=50%: POD 0.80 FAR 0.13 CSI 0.71 fałsz. bez zdarz. 6.8
- próg -10 C (zdarzeń 484):
    w=0.00 (produkcja): P>=10%: POD 0.59 FAR 0.34 CSI 0.45 fałsz. bez zdarz. 3.5 | P>=20%: POD 0.56 FAR 0.31 CSI 0.45 fałsz. bez zdarz. 2.7 | P>=30%: POD 0.55 FAR 0.29 CSI 0.45 fałsz. bez zdarz. 2.0 | P>=50%: POD 0.52 FAR 0.25 CSI 0.45 fałsz. bez zdarz. 2.0
    w=0.50: P>=10%: POD 0.67 FAR 0.38 CSI 0.47 fałsz. bez zdarz. 4.7 | P>=20%: POD 0.63 FAR 0.35 CSI 0.47 fałsz. bez zdarz. 3.5 | P>=30%: POD 0.58 FAR 0.32 CSI 0.46 fałsz. bez zdarz. 2.7 | P>=50%: POD 0.52 FAR 0.26 CSI 0.44 fałsz. bez zdarz. 1.7
    w=0.75: P>=10%: POD 0.75 FAR 0.42 CSI 0.49 fałsz. bez zdarz. 6.2 | P>=20%: POD 0.65 FAR 0.37 CSI 0.47 fałsz. bez zdarz. 4.4 | P>=30%: POD 0.61 FAR 0.34 CSI 0.46 fałsz. bez zdarz. 3.2 | P>=50%: POD 0.52 FAR 0.26 CSI 0.44 fałsz. bez zdarz. 1.7
    w=1.00: P>=10%: POD 0.85 FAR 0.46 CSI 0.50 fałsz. bez zdarz. 9.6 | P>=20%: POD 0.71 FAR 0.39 CSI 0.48 fałsz. bez zdarz. 5.2 | P>=30%: POD 0.63 FAR 0.35 CSI 0.47 fałsz. bez zdarz. 3.7 | P>=50%: POD 0.52 FAR 0.26 CSI 0.44 fałsz. bez zdarz. 1.7
- próg -15 C (zdarzeń 100):
    w=0.00 (produkcja): P>=10%: POD 0.55 FAR 0.52 CSI 0.34 fałsz. bez zdarz. 3.6 | P>=20%: POD 0.53 FAR 0.48 CSI 0.36 fałsz. bez zdarz. 3.0 | P>=30%: POD 0.51 FAR 0.43 CSI 0.37 fałsz. bez zdarz. 2.3 | P>=50%: POD 0.50 FAR 0.37 CSI 0.39 fałsz. bez zdarz. 1.5
    w=0.50: P>=10%: POD 0.63 FAR 0.55 CSI 0.35 fałsz. bez zdarz. 4.3 | P>=20%: POD 0.59 FAR 0.52 CSI 0.36 fałsz. bez zdarz. 3.6 | P>=30%: POD 0.54 FAR 0.48 CSI 0.36 fałsz. bez zdarz. 2.6 | P>=50%: POD 0.48 FAR 0.38 CSI 0.37 fałsz. bez zdarz. 1.5
    w=0.75: P>=10%: POD 0.65 FAR 0.62 CSI 0.31 fałsz. bez zdarz. 5.7 | P>=20%: POD 0.62 FAR 0.54 CSI 0.36 fałsz. bez zdarz. 4.0 | P>=30%: POD 0.58 FAR 0.50 CSI 0.36 fałsz. bez zdarz. 3.2 | P>=50%: POD 0.48 FAR 0.38 CSI 0.37 fałsz. bez zdarz. 1.5
    w=1.00: P>=10%: POD 0.66 FAR 0.67 CSI 0.28 fałsz. bez zdarz. 6.8 | P>=20%: POD 0.63 FAR 0.57 CSI 0.34 fałsz. bez zdarz. 4.7 | P>=30%: POD 0.60 FAR 0.53 CSI 0.36 fałsz. bez zdarz. 3.4 | P>=50%: POD 0.48 FAR 0.38 CSI 0.37 fałsz. bez zdarz. 1.5
### wyprzedzenie k=2: n=5292, sigma całkowita 2.78 C, średni dodany rozrzut 2.61 C
- próg -5 C (zdarzeń 1036):
    w=0.00 (produkcja): P>=10%: POD 0.83 FAR 0.26 CSI 0.64 fałsz. bez zdarz. 34.9 | P>=20%: POD 0.81 FAR 0.19 CSI 0.68 fałsz. bez zdarz. 18.3 | P>=30%: POD 0.80 FAR 0.17 CSI 0.69 fałsz. bez zdarz. 13.6 | P>=50%: POD 0.77 FAR 0.14 CSI 0.68 fałsz. bez zdarz. 8.0
    w=0.50: P>=10%: POD 0.91 FAR 0.32 CSI 0.64 fałsz. bez zdarz. 58.9 | P>=20%: POD 0.88 FAR 0.25 CSI 0.68 fałsz. bez zdarz. 32.2 | P>=30%: POD 0.83 FAR 0.19 CSI 0.70 fałsz. bez zdarz. 17.2 | P>=50%: POD 0.76 FAR 0.13 CSI 0.68 fałsz. bez zdarz. 7.1
    w=0.75: P>=10%: POD 0.94 FAR 0.39 CSI 0.59 fałsz. bez zdarz. 88.5 | P>=20%: POD 0.91 FAR 0.30 CSI 0.66 fałsz. bez zdarz. 48.8 | P>=30%: POD 0.86 FAR 0.23 CSI 0.69 fałsz. bez zdarz. 25.1 | P>=50%: POD 0.77 FAR 0.13 CSI 0.68 fałsz. bez zdarz. 7.4
    w=1.00: P>=10%: POD 0.97 FAR 0.48 CSI 0.51 fałsz. bez zdarz. 146.2 | P>=20%: POD 0.93 FAR 0.34 CSI 0.62 fałsz. bez zdarz. 66.6 | P>=30%: POD 0.88 FAR 0.26 CSI 0.67 fałsz. bez zdarz. 35.5 | P>=50%: POD 0.77 FAR 0.13 CSI 0.68 fałsz. bez zdarz. 7.4
- próg -10 C (zdarzeń 427):
    w=0.00 (produkcja): P>=10%: POD 0.61 FAR 0.39 CSI 0.44 fałsz. bez zdarz. 6.4 | P>=20%: POD 0.59 FAR 0.37 CSI 0.44 fałsz. bez zdarz. 4.5 | P>=30%: POD 0.57 FAR 0.35 CSI 0.44 fałsz. bez zdarz. 4.5 | P>=50%: POD 0.54 FAR 0.29 CSI 0.44 fałsz. bez zdarz. 2.1
    w=0.50: P>=10%: POD 0.67 FAR 0.41 CSI 0.45 fałsz. bez zdarz. 7.6 | P>=20%: POD 0.63 FAR 0.38 CSI 0.45 fałsz. bez zdarz. 5.2 | P>=30%: POD 0.59 FAR 0.36 CSI 0.45 fałsz. bez zdarz. 4.3 | P>=50%: POD 0.53 FAR 0.29 CSI 0.44 fałsz. bez zdarz. 1.9
    w=0.75: P>=10%: POD 0.74 FAR 0.42 CSI 0.48 fałsz. bez zdarz. 9.7 | P>=20%: POD 0.65 FAR 0.40 CSI 0.45 fałsz. bez zdarz. 6.4 | P>=30%: POD 0.60 FAR 0.38 CSI 0.44 fałsz. bez zdarz. 4.8 | P>=50%: POD 0.53 FAR 0.28 CSI 0.44 fałsz. bez zdarz. 1.9
    w=1.00: P>=10%: POD 0.86 FAR 0.46 CSI 0.50 fałsz. bez zdarz. 15.0 | P>=20%: POD 0.71 FAR 0.41 CSI 0.48 fałsz. bez zdarz. 7.8 | P>=30%: POD 0.63 FAR 0.38 CSI 0.45 fałsz. bez zdarz. 5.2 | P>=50%: POD 0.53 FAR 0.28 CSI 0.44 fałsz. bez zdarz. 1.9
- próg -15 C (zdarzeń 98):
    w=0.00 (produkcja): P>=10%: POD 0.50 FAR 0.59 CSI 0.29 fałsz. bez zdarz. 2.4 | P>=20%: POD 0.47 FAR 0.51 CSI 0.32 fałsz. bez zdarz. 1.3 | P>=30%: POD 0.46 FAR 0.44 CSI 0.34 fałsz. bez zdarz. 0.6 | P>=50%: POD 0.42 FAR 0.38 CSI 0.33 fałsz. bez zdarz. 0.4
    w=0.50: P>=10%: POD 0.56 FAR 0.61 CSI 0.30 fałsz. bez zdarz. 2.4 | P>=20%: POD 0.51 FAR 0.55 CSI 0.32 fałsz. bez zdarz. 1.3 | P>=30%: POD 0.49 FAR 0.44 CSI 0.35 fałsz. bez zdarz. 0.6 | P>=50%: POD 0.42 FAR 0.34 CSI 0.34 fałsz. bez zdarz. 0.2
    w=0.75: P>=10%: POD 0.60 FAR 0.66 CSI 0.28 fałsz. bez zdarz. 3.4 | P>=20%: POD 0.55 FAR 0.58 CSI 0.31 fałsz. bez zdarz. 1.5 | P>=30%: POD 0.50 FAR 0.47 CSI 0.35 fałsz. bez zdarz. 0.6 | P>=50%: POD 0.42 FAR 0.32 CSI 0.35 fałsz. bez zdarz. 0.2
    w=1.00: P>=10%: POD 0.65 FAR 0.72 CSI 0.25 fałsz. bez zdarz. 5.2 | P>=20%: POD 0.58 FAR 0.62 CSI 0.30 fałsz. bez zdarz. 1.9 | P>=30%: POD 0.53 FAR 0.50 CSI 0.34 fałsz. bez zdarz. 0.6 | P>=50%: POD 0.42 FAR 0.32 CSI 0.35 fałsz. bez zdarz. 0.2

## 8. Oceny probabilistyczne (CRPS, Brier — niższe = lepiej; wektory zapisane do porównania modeli parami)
### wyprzedzenie k=0
- tmin_crps_k0: n=5237, średnia 1.9200
- tmin_le5_brier_k0: n=5237, średnia 0.0772
- tmin_le10_brier_k0: n=5237, średnia 0.0557
- tmin_le15_brier_k0: n=5237, średnia 0.0122
- precip_crps_k0: n=5249, średnia 0.6132
- precip_ge1_brier_k0: n=5249, średnia 0.0961
- precip_ge5_brier_k0: n=5249, średnia 0.0414
- precip_ge10_brier_k0: n=5249, średnia 0.0165
- snow_ge1_brier_k0: n=4980, średnia 0.0872
- snow_ge3_brier_k0: n=4980, średnia 0.0546
### wyprzedzenie k=1
- tmin_crps_k1: n=5290, średnia 1.8932
- tmin_le5_brier_k1: n=5290, średnia 0.0707
- tmin_le10_brier_k1: n=5290, średnia 0.0585
- tmin_le15_brier_k1: n=5290, średnia 0.0127
- precip_crps_k1: n=5304, średnia 0.7029
- precip_ge1_brier_k1: n=5304, średnia 0.1128
- precip_ge5_brier_k1: n=5304, średnia 0.0505
- precip_ge10_brier_k1: n=5304, średnia 0.0202
- snow_ge1_brier_k1: n=5089, średnia 0.0854
- snow_ge3_brier_k1: n=5089, średnia 0.0572
### wyprzedzenie k=2
- tmin_crps_k2: n=5292, średnia 1.7036
- tmin_le5_brier_k2: n=5292, średnia 0.0681
- tmin_le10_brier_k2: n=5292, średnia 0.0477
- tmin_le15_brier_k2: n=5292, średnia 0.0124
- precip_crps_k2: n=5303, średnia 0.8269
- precip_ge1_brier_k2: n=5303, średnia 0.1302
- precip_ge5_brier_k2: n=5303, średnia 0.0594
- precip_ge10_brier_k2: n=5303, średnia 0.0241
- snow_ge1_brier_k2: n=4981, średnia 0.0813
- snow_ge3_brier_k2: n=4981, średnia 0.0518

