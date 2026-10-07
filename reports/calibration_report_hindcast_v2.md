# Kalibracja SWWF na obserwacjach IMGW — 2026-10-07 22:50
hindcast: /home/runner/work/SWWF/SWWF/hindcast_v2 (63 przebiegów 00Z z 30 członkami, okien na przebieg: [13]); obs: imgw_dobowe_2020-11-01_2026-03-31_mc-1-2-3-11-12.csv.gz (52851 stacjodni)
Próba jest dobrana pod zdarzenia i dni spokojne (nie klimatologiczna) — FAR i odsetki zdarzeń z sekcji 1-5 dotyczą próby mieszanej; sekcja 6 rozdziela doby bez zdarzenia i ze zdarzeniem.

## 0. Kontrola okna doby IMGW (k=0)
- opad SMDB: start  0 UTC: r=0.806 | start  6 UTC: r=0.854 | start 12 UTC: r=0.765 | start 18 UTC: r=0.638  (najwyższe r = okno zgodne z IMGW)
- TMIN: start  0 UTC: r=0.924 | start  6 UTC: r=0.875 | start 12 UTC: r=0.856 | start 18 UTC: r=0.835  (najwyższe r = okno zgodne z IMGW)

## 1. Opad dobowy (okno 06->06 UTC)
### wyprzedzenie k=0: n=3485 stacjodni, mokrych (>=1 mm) 987
- średnia obs 1.18 mm, GEFS 1.60 mm; korelacja sqrt = 0.854
- dni mokre: GEFS/obs = 1.13; obs > max zespołu: 6.5% dni mokrych
- P(opad>=1 mm): P=0: n=1595, zaszło 1% | P=0-20%: n=387, zaszło 9% | P=20-40%: n=177, zaszło 23% | P=40-60%: n=165, zaszło 27% | P=60-80%: n=178, zaszło 44% | P=80-100%: n=983, zaszło 79%
- P(opad>=5 mm): P=0: n=2532, zaszło 0% | P=0-20%: n=399, zaszło 6% | P=20-40%: n=181, zaszło 18% | P=40-60%: n=108, zaszło 33% | P=60-80%: n=102, zaszło 48% | P=80-100%: n=163, zaszło 63%
- P(opad>=10 mm): P=0: n=3119, zaszło 0% | P=0-20%: n=224, zaszło 4% | P=20-40%: n=56, zaszło 5% | P=40-60%: n=35, zaszło 54% | P=60-80%: n=27, zaszło 37% | P=80-100%: n=24, zaszło 46%
### wyprzedzenie k=1: n=3485 stacjodni, mokrych (>=1 mm) 995
- średnia obs 1.31 mm, GEFS 1.76 mm; korelacja sqrt = 0.815
- dni mokre: GEFS/obs = 1.04; obs > max zespołu: 4.8% dni mokrych
- P(opad>=1 mm): P=0: n=1086, zaszło 0% | P=0-20%: n=611, zaszło 3% | P=20-40%: n=282, zaszło 15% | P=40-60%: n=271, zaszło 27% | P=60-80%: n=281, zaszło 38% | P=80-100%: n=954, zaszło 79%
- P(opad>=5 mm): P=0: n=2270, zaszło 0% | P=0-20%: n=550, zaszło 6% | P=20-40%: n=229, zaszło 19% | P=40-60%: n=168, zaszło 36% | P=60-80%: n=125, zaszło 50% | P=80-100%: n=143, zaszło 69%
- P(opad>=10 mm): P=0: n=2949, zaszło 0% | P=0-20%: n=363, zaszło 4% | P=20-40%: n=96, zaszło 18% | P=40-60%: n=41, zaszło 29% | P=60-80%: n=26, zaszło 38% | P=80-100%: n=10, zaszło 60%
### wyprzedzenie k=2: n=3483 stacjodni, mokrych (>=1 mm) 1158
- średnia obs 1.53 mm, GEFS 1.89 mm; korelacja sqrt = 0.759
- dni mokre: GEFS/obs = 0.92; obs > max zespołu: 7.1% dni mokrych
- P(opad>=1 mm): P=0: n=788, zaszło 1% | P=0-20%: n=690, zaszło 10% | P=20-40%: n=408, zaszło 21% | P=40-60%: n=276, zaszło 32% | P=60-80%: n=367, zaszło 44% | P=80-100%: n=954, zaszło 78%
- P(opad>=5 mm): P=0: n=1969, zaszło 1% | P=0-20%: n=765, zaszło 6% | P=20-40%: n=302, zaszło 22% | P=40-60%: n=207, zaszło 38% | P=60-80%: n=144, zaszło 67% | P=80-100%: n=96, zaszło 64%
- P(opad>=10 mm): P=0: n=2748, zaszło 0% | P=0-20%: n=518, zaszło 5% | P=20-40%: n=140, zaszło 27% | P=40-60%: n=61, zaszło 36% | P=60-80%: n=15, zaszło 27% | P=80-100%: n=1, zaszło 0%

## 2. Śnieg — metody rozpoznawania fazy opadu (okno 06->06 UTC)
Zdarzenie obserwowane: opad rodzaju S (śnieg) o sumie >= X mm. Prognoza: P(opad zamarznięty >= X mm) wg metody. Kolumna 'deszcz->śnieg' = odsetek dni z obserwowanym DESZCZEM >=3 mm, w których metoda daje P(śnieg>=3 mm) >= 30% (fałszywy śnieg).
### wyprzedzenie k=0: n=3485; obs śnieg >=1 mm: 467, >=3 mm: 245, >=5 mm: 124; deszcz >=3 mm: 202
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A dawna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.48 | 0.55 | 0.30 | 0.65 | 0.45 | 1% |
| D obecna (produkcja): T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.68 | 0.57 | 0.36 | 0.84 | 0.49 | 4% |
| G: CPOFP (gdy ważny), inaczej D | 0.62 | 0.56 | 0.35 | 0.81 | 0.47 | 2% |
| W0: mokry termometr, zimniejsza z 2 próbek (1@0C->0@2C) | 0.67 | 0.55 | 0.37 | 0.85 | 0.49 | 2% |
| W1: mokry termometr (1@0.5C->0@2.5C) | 0.72 | 0.57 | 0.37 | 0.89 | 0.52 | 7% |
| W2: mokry termometr (1@1C->0@3C) | 0.79 | 0.58 | 0.38 | 0.91 | 0.55 | 13% |
- wiarygodność P(śnieg>=3 mm), metoda 'D' (produkcyjna): P=0: n=2785, zaszło 1% | P=0-20%: n=259, zaszło 12% | P=20-40%: n=120, zaszło 22% | P=40-60%: n=70, zaszło 24% | P=60-80%: n=70, zaszło 46% | P=80-100%: n=181, zaszło 56%
### wyprzedzenie k=1: n=3485; obs śnieg >=1 mm: 439, >=3 mm: 245, >=5 mm: 141; deszcz >=3 mm: 275
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A dawna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.44 | 0.60 | 0.27 | 0.63 | 0.56 | 2% |
| D obecna (produkcja): T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.68 | 0.58 | 0.35 | 0.85 | 0.56 | 3% |
| G: CPOFP (gdy ważny), inaczej D | 0.54 | 0.61 | 0.29 | 0.78 | 0.57 | 3% |
| W0: mokry termometr, zimniejsza z 2 próbek (1@0C->0@2C) | 0.61 | 0.59 | 0.32 | 0.87 | 0.57 | 4% |
| W1: mokry termometr (1@0.5C->0@2.5C) | 0.70 | 0.60 | 0.34 | 0.92 | 0.59 | 5% |
| W2: mokry termometr (1@1C->0@3C) | 0.76 | 0.60 | 0.35 | 0.95 | 0.61 | 9% |
- wiarygodność P(śnieg>=3 mm), metoda 'D' (produkcyjna): P=0: n=2568, zaszło 1% | P=0-20%: n=444, zaszło 9% | P=20-40%: n=150, zaszło 19% | P=40-60%: n=112, zaszło 33% | P=60-80%: n=99, zaszło 45% | P=80-100%: n=112, zaszło 62%
### wyprzedzenie k=2: n=3483; obs śnieg >=1 mm: 460, >=3 mm: 243, >=5 mm: 143; deszcz >=3 mm: 320
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A dawna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.37 | 0.70 | 0.20 | 0.59 | 0.63 | 1% |
| D obecna (produkcja): T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.58 | 0.68 | 0.26 | 0.78 | 0.63 | 6% |
| G: CPOFP (gdy ważny), inaczej D | 0.49 | 0.69 | 0.24 | 0.73 | 0.64 | 2% |
| W0: mokry termometr, zimniejsza z 2 próbek (1@0C->0@2C) | 0.54 | 0.68 | 0.25 | 0.79 | 0.63 | 6% |
| W1: mokry termometr (1@0.5C->0@2.5C) | 0.62 | 0.67 | 0.27 | 0.83 | 0.64 | 8% |
| W2: mokry termometr (1@1C->0@3C) | 0.69 | 0.68 | 0.28 | 0.87 | 0.66 | 12% |
- wiarygodność P(śnieg>=3 mm), metoda 'D' (produkcyjna): P=0: n=2359, zaszło 1% | P=0-20%: n=561, zaszło 9% | P=20-40%: n=234, zaszło 17% | P=40-60%: n=133, zaszło 32% | P=60-80%: n=110, zaszło 36% | P=80-100%: n=86, zaszło 41%

## 3. Mróz — temperatura powietrza vs odczuwalna (okno doby kalendarzowej 00-24 UTC; obserwacja = TMIN powietrza)
Uwaga: IMGW mierzy tylko temperaturę powietrza, więc odczuwalnej NIE da się zweryfikować wprost; poniżej sprawdzamy, jak daleko od powietrza jest każda wersja i czy 'odczuwalna' nie robi fałszywych alarmów względem realnego mrozu.
### wyprzedzenie k=0: n=3484
- prognoza min. T powietrza: błąd średni +0.69 C, MAE 1.74 C; w mroźnych dniach (obs <= -10 C): błąd +2.60 C
- odczuwalna z PORYWÓW (dawna wersja hazardu; produkcja używa T powietrza): chłodniejsza od powietrza średnio o 6.6 C
- odczuwalna z wiatru ŚREDNIEGO: chłodniejsza od powietrza średnio o 4.8 C
- próg -5 C (obs zdarzeń 895), powietrze: P>=30%: traf. 694, fałsz. 64, przegap. 201 (POD 0.78, FAR 0.08, CSI 0.72)
- próg -10 C (obs zdarzeń 440), powietrze: P>=30%: traf. 281, fałsz. 38, przegap. 159 (POD 0.64, FAR 0.12, CSI 0.59)
- próg -15 C (obs zdarzeń 133), powietrze: P>=30%: traf. 51, fałsz. 18, przegap. 82 (POD 0.38, FAR 0.26, CSI 0.34)
- próg -20 C (obs zdarzeń 23), powietrze: P>=30%: traf. 3, fałsz. 0, przegap. 20 (POD 0.13, FAR 0.00, CSI 0.13)
### wyprzedzenie k=1: n=3481
- prognoza min. T powietrza: błąd średni +0.88 C, MAE 1.85 C; w mroźnych dniach (obs <= -10 C): błąd +3.24 C
- odczuwalna z PORYWÓW (dawna wersja hazardu; produkcja używa T powietrza): chłodniejsza od powietrza średnio o 6.4 C
- odczuwalna z wiatru ŚREDNIEGO: chłodniejsza od powietrza średnio o 4.6 C
- próg -5 C (obs zdarzeń 758), powietrze: P>=30%: traf. 592, fałsz. 51, przegap. 166 (POD 0.78, FAR 0.08, CSI 0.73)
- próg -10 C (obs zdarzeń 437), powietrze: P>=30%: traf. 266, fałsz. 44, przegap. 171 (POD 0.61, FAR 0.14, CSI 0.55)
- próg -15 C (obs zdarzeń 127), powietrze: P>=30%: traf. 40, fałsz. 19, przegap. 87 (POD 0.31, FAR 0.32, CSI 0.27)
- próg -20 C (obs zdarzeń 24), powietrze: P>=30%: traf. 0, fałsz. 1, przegap. 24 (POD 0.00, FAR 1.00, CSI 0.00)
### wyprzedzenie k=2: n=3480
- prognoza min. T powietrza: błąd średni +0.64 C, MAE 1.95 C; w mroźnych dniach (obs <= -10 C): błąd +3.83 C
- odczuwalna z PORYWÓW (dawna wersja hazardu; produkcja używa T powietrza): chłodniejsza od powietrza średnio o 6.3 C
- odczuwalna z wiatru ŚREDNIEGO: chłodniejsza od powietrza średnio o 4.6 C
- próg -5 C (obs zdarzeń 659), powietrze: P>=30%: traf. 503, fałsz. 66, przegap. 156 (POD 0.76, FAR 0.12, CSI 0.69)
- próg -10 C (obs zdarzeń 327), powietrze: P>=30%: traf. 189, fałsz. 68, przegap. 138 (POD 0.58, FAR 0.26, CSI 0.48)
- próg -15 C (obs zdarzeń 100), powietrze: P>=30%: traf. 25, fałsz. 15, przegap. 75 (POD 0.25, FAR 0.38, CSI 0.22)
- próg -20 C (obs zdarzeń 7), powietrze: P>=30%: traf. 0, fałsz. 0, przegap. 7 (POD 0.00, FAR 0.00, CSI 0.00)

## 4. Gołoledź — opad w warunkach marznących (CFRZR >= 0.5) vs obserwowane godziny gołoledzi (GOLO)
- k=0, obs GOLO>=1 h: 89 zdarzeń z 2421; prognoza P(opad marznący >= 0.1 mm): P>=10%: traf. 25, fałsz. 127, przegap. 64 (POD 0.28, FAR 0.84, CSI 0.12) | P>=30%: traf. 14, fałsz. 50, przegap. 75 (POD 0.16, FAR 0.78, CSI 0.10)
- k=0, obs GOLO>=1 h: 89 zdarzeń z 2421; prognoza P(opad marznący >= 1.0 mm): P>=10%: traf. 12, fałsz. 40, przegap. 77 (POD 0.13, FAR 0.77, CSI 0.09) | P>=30%: traf. 6, fałsz. 6, przegap. 83 (POD 0.07, FAR 0.50, CSI 0.06)
- k=1, obs GOLO>=1 h: 90 zdarzeń z 2421; prognoza P(opad marznący >= 0.1 mm): P>=10%: traf. 23, fałsz. 100, przegap. 67 (POD 0.26, FAR 0.81, CSI 0.12) | P>=30%: traf. 12, fałsz. 34, przegap. 78 (POD 0.13, FAR 0.74, CSI 0.10)
- k=1, obs GOLO>=1 h: 90 zdarzeń z 2421; prognoza P(opad marznący >= 1.0 mm): P>=10%: traf. 10, fałsz. 29, przegap. 80 (POD 0.11, FAR 0.74, CSI 0.08) | P>=30%: traf. 8, fałsz. 6, przegap. 82 (POD 0.09, FAR 0.43, CSI 0.08)
- k=2, obs GOLO>=1 h: 91 zdarzeń z 2420; prognoza P(opad marznący >= 0.1 mm): P>=10%: traf. 20, fałsz. 70, przegap. 71 (POD 0.22, FAR 0.78, CSI 0.12) | P>=30%: traf. 6, fałsz. 15, przegap. 85 (POD 0.07, FAR 0.71, CSI 0.06)
- k=2, obs GOLO>=1 h: 91 zdarzeń z 2420; prognoza P(opad marznący >= 1.0 mm): P>=10%: traf. 8, fałsz. 25, przegap. 83 (POD 0.09, FAR 0.76, CSI 0.07) | P>=30%: traf. 1, fałsz. 2, przegap. 90 (POD 0.01, FAR 0.67, CSI 0.01)

## 5. Zamieć — definicja SWWF (porywy >= 15.5 m/s, widzialność <= 400 m, śnieg świeży/leżący) vs obserwowane godziny zamieci śnieżnej (ZMNI+ZMWS)
Uwaga: przebiegi bez pola widzialności (GEFS 2021) nie mogą dać flagi wg definicji SWWF, więc są z tej oceny wyłączone; wariant 'bez VIS' (porywy + śnieg) działa na wszystkich.
- k=0: obs zamieć >=1 h: 67 z 2421 stacjodni
    bez VIS (porywy >= 15.5 m/s + śnieg): P>=10%: traf. 33, fałsz. 655, przegap. 34 (POD 0.49, FAR 0.95, CSI 0.05) | P>=30%: traf. 28, fałsz. 502, przegap. 39 (POD 0.42, FAR 0.95, CSI 0.05) | P>=50%: traf. 22, fałsz. 431, przegap. 45 (POD 0.33, FAR 0.95, CSI 0.04)
    tylko porywy >= 15.5 m/s: P>=30%: traf. 30, fałsz. 817, przegap. 37 (POD 0.45, FAR 0.96, CSI 0.03) | P>=50%: traf. 28, fałsz. 713, przegap. 39 (POD 0.42, FAR 0.96, CSI 0.04)
    tylko porywy >= 20 m/s: P>=30%: traf. 5, fałsz. 304, przegap. 62 (POD 0.07, FAR 0.98, CSI 0.01) | P>=50%: traf. 1, fałsz. 251, przegap. 66 (POD 0.01, FAR 1.00, CSI 0.00)
- k=1: obs zamieć >=1 h: 87 z 2421 stacjodni
    definicja SWWF z VIS (tylko przebiegi z VIS, 431 stacjodni, 4 zdarzeń): P>=10%: traf. 2, fałsz. 22, przegap. 2 (POD 0.50, FAR 0.92, CSI 0.08) | P>=30%: traf. 0, fałsz. 4, przegap. 4 (POD 0.00, FAR 1.00, CSI 0.00)
    bez VIS (porywy >= 15.5 m/s + śnieg): P>=10%: traf. 43, fałsz. 816, przegap. 44 (POD 0.49, FAR 0.95, CSI 0.05) | P>=30%: traf. 30, fałsz. 599, przegap. 57 (POD 0.34, FAR 0.95, CSI 0.04) | P>=50%: traf. 21, fałsz. 469, przegap. 66 (POD 0.24, FAR 0.96, CSI 0.04)
    tylko porywy >= 15.5 m/s: P>=30%: traf. 37, fałsz. 915, przegap. 50 (POD 0.43, FAR 0.96, CSI 0.04) | P>=50%: traf. 31, fałsz. 774, przegap. 56 (POD 0.36, FAR 0.96, CSI 0.04)
    tylko porywy >= 20 m/s: P>=30%: traf. 3, fałsz. 282, przegap. 84 (POD 0.03, FAR 0.99, CSI 0.01) | P>=50%: traf. 2, fałsz. 209, przegap. 85 (POD 0.02, FAR 0.99, CSI 0.01)

## 6. Fałszywe alarmy na dobach bez zdarzenia i trafienia na dobach ze zdarzeniem
Alarm = P(zdarzenia) >= 30% wg zespołu. Doba 'bez zdarzenia' = zdarzenie na <= 1 stacji (wtedy każdy alarm jest fałszywy); 'ze zdarzeniem' = na >= 5 stacjach. 'doby z >=3 stacjami' = ile dób miało alarm na co najmniej 3 stacjach naraz (tyle widziałby użytkownik jako plamę na mapie).
### wyprzedzenie k=0
- śnieg >= 3 mm: doby bez zdarzenia: 40, stacjodni 2215, fałszywych alarmów 12 (5.4 na 1000 stacjodni); doby z >=3 stacjami: 1 z 40
    doby ze zdarzeniem: 16, zdarzeń 218, trafionych 149 (POD 0.68), fałszywych alarmów na tych dobach 161
- opad >= 10 mm: doby bez zdarzenia: 54, stacjodni 2988, fałszywych alarmów 17 (5.7 na 1000 stacjodni); doby z >=3 stacjami: 3 z 54
    doby ze zdarzeniem: 3, zdarzeń 34, trafionych 29 (POD 0.85), fałszywych alarmów na tych dobach 16
- mróz TMIN <= -10 C: doby bez zdarzenia: 47, stacjodni 2601, fałszywych alarmów 3 (1.2 na 1000 stacjodni); doby z >=3 stacjami: 0 z 47
    doby ze zdarzeniem: 13, zdarzeń 430, trafionych 281 (POD 0.65), fałszywych alarmów na tych dobach 34
- mróz TMIN <= -15 C: doby bez zdarzenia: 52, stacjodni 2878, fałszywych alarmów 0 (0.0 na 1000 stacjodni); doby z >=3 stacjami: 0 z 52
    doby ze zdarzeniem: 8, zdarzeń 121, trafionych 45 (POD 0.37), fałszywych alarmów na tych dobach 10
- zamieć (porywy >= 15.5 m/s + śnieg, bez VIS): doby bez zdarzenia: 56, stacjodni 2036, fałszywych alarmów 430 (211.2 na 1000 stacjodni); doby z >=3 stacjami: 18 z 56
    doby ze zdarzeniem: 4, zdarzeń 55, trafionych 24 (POD 0.44), fałszywych alarmów na tych dobach 42
### wyprzedzenie k=1
- śnieg >= 3 mm: doby bez zdarzenia: 40, stacjodni 2215, fałszywych alarmów 28 (12.6 na 1000 stacjodni); doby z >=3 stacjami: 3 z 40
    doby ze zdarzeniem: 17, zdarzeń 226, trafionych 158 (POD 0.70), fałszywych alarmów na tych dobach 176
- opad >= 10 mm: doby bez zdarzenia: 51, stacjodni 2823, fałszywych alarmów 9 (3.2 na 1000 stacjodni); doby z >=3 stacjami: 1 z 51
    doby ze zdarzeniem: 5, zdarzeń 44, trafionych 28 (POD 0.64), fałszywych alarmów na tych dobach 28
- mróz TMIN <= -10 C: doby bez zdarzenia: 49, stacjodni 2710, fałszywych alarmów 2 (0.7 na 1000 stacjodni); doby z >=3 stacjami: 0 z 49
    doby ze zdarzeniem: 12, zdarzeń 429, trafionych 266 (POD 0.62), fałszywych alarmów na tych dobach 41
- mróz TMIN <= -15 C: doby bez zdarzenia: 53, stacjodni 2930, fałszywych alarmów 0 (0.0 na 1000 stacjodni); doby z >=3 stacjami: 0 z 53
    doby ze zdarzeniem: 8, zdarzeń 121, trafionych 38 (POD 0.31), fałszywych alarmów na tych dobach 12
- zamieć (porywy >= 15.5 m/s + śnieg, bez VIS): doby bez zdarzenia: 52, stacjodni 1864, fałszywych alarmów 466 (250.0 na 1000 stacjodni); doby z >=3 stacjami: 18 z 52
    doby ze zdarzeniem: 5, zdarzeń 65, trafionych 23 (POD 0.35), fałszywych alarmów na tych dobach 42
### wyprzedzenie k=2
- śnieg >= 3 mm: doby bez zdarzenia: 42, stacjodni 2326, fałszywych alarmów 51 (21.9 na 1000 stacjodni); doby z >=3 stacjami: 5 z 42
    doby ze zdarzeniem: 16, zdarzeń 223, trafionych 131 (POD 0.59), fałszywych alarmów na tych dobach 208
- opad >= 10 mm: doby bez zdarzenia: 47, stacjodni 2598, fałszywych alarmów 18 (6.9 na 1000 stacjodni); doby z >=3 stacjami: 2 z 47
    doby ze zdarzeniem: 9, zdarzeń 76, trafionych 37 (POD 0.49), fałszywych alarmów na tych dobach 38
- mróz TMIN <= -10 C: doby bez zdarzenia: 49, stacjodni 2708, fałszywych alarmów 3 (1.1 na 1000 stacjodni); doby z >=3 stacjami: 0 z 49
    doby ze zdarzeniem: 11, zdarzeń 320, trafionych 187 (POD 0.58), fałszywych alarmów na tych dobach 59
- mróz TMIN <= -15 C: doby bez zdarzenia: 55, stacjodni 3040, fałszywych alarmów 2 (0.7 na 1000 stacjodni); doby z >=3 stacjami: 0 z 55
    doby ze zdarzeniem: 7, zdarzeń 96, trafionych 25 (POD 0.26), fałszywych alarmów na tych dobach 13
- zamieć (porywy >= 15.5 m/s + śnieg, bez VIS): doby bez zdarzenia: 54, stacjodni 1973, fałszywych alarmów 548 (277.7 na 1000 stacjodni); doby z >=3 stacjami: 18 z 54
    doby ze zdarzeniem: 4, zdarzeń 56, trafionych 17 (POD 0.30), fałszywych alarmów na tych dobach 7

