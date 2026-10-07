# Kalibracja SWWF na obserwacjach IMGW — 2026-10-07 17:44
hindcast: /home/runner/work/SWWF/SWWF/hindcast_v2 (27 przebiegów 00Z z 30 członkami, okien na przebieg: [13]); obs: imgw_dobowe_2020-11-01_2026-03-31_mc-1-2-3-11-12.csv.gz (52851 stacjodni)
Próba jest dobrana pod zdarzenia (nie klimatologiczna) — FAR i odsetki dni zdarzeń nie są częstościami klimatologicznymi.

## 0. Kontrola okna doby IMGW (k=0)
- opad SMDB: start  0 UTC: r=0.831 | start  6 UTC: r=0.844 | start 12 UTC: r=0.734 | start 18 UTC: r=0.613  (najwyższe r = okno zgodne z IMGW)
- TMIN: start  0 UTC: r=0.930 | start  6 UTC: r=0.874 | start 12 UTC: r=0.850 | start 18 UTC: r=0.827  (najwyższe r = okno zgodne z IMGW)

## 1. Opad dobowy (okno 06->06 UTC)
### wyprzedzenie k=0: n=1493 stacjodni, mokrych (>=1 mm) 433
- średnia obs 1.30 mm, GEFS 1.89 mm; korelacja sqrt = 0.844
- dni mokre: GEFS/obs = 1.18; obs > max zespołu: 4.2% dni mokrych
- P(opad>=1 mm): P=0: n=662, zaszło 0% | P=0-20%: n=132, zaszło 6% | P=20-40%: n=64, zaszło 14% | P=40-60%: n=79, zaszło 15% | P=60-80%: n=65, zaszło 35% | P=80-100%: n=491, zaszło 78%
- P(opad>=5 mm): P=0: n=1023, zaszło 0% | P=0-20%: n=174, zaszło 5% | P=20-40%: n=79, zaszło 22% | P=40-60%: n=60, zaszło 28% | P=60-80%: n=58, zaszło 52% | P=80-100%: n=99, zaszło 56%
- P(opad>=10 mm): P=0: n=1310, zaszło 0% | P=0-20%: n=104, zaszło 5% | P=20-40%: n=32, zaszło 9% | P=40-60%: n=17, zaszło 35% | P=60-80%: n=17, zaszło 29% | P=80-100%: n=13, zaszło 15%
### wyprzedzenie k=1: n=1493 stacjodni, mokrych (>=1 mm) 483
- średnia obs 1.57 mm, GEFS 2.05 mm; korelacja sqrt = 0.812
- dni mokre: GEFS/obs = 1.03; obs > max zespołu: 5.6% dni mokrych
- P(opad>=1 mm): P=0: n=442, zaszło 0% | P=0-20%: n=206, zaszło 5% | P=20-40%: n=145, zaszło 14% | P=40-60%: n=109, zaszło 28% | P=60-80%: n=124, zaszło 36% | P=80-100%: n=467, zaszło 80%
- P(opad>=5 mm): P=0: n=922, zaszło 1% | P=0-20%: n=238, zaszło 7% | P=20-40%: n=105, zaszło 23% | P=40-60%: n=78, zaszło 46% | P=60-80%: n=57, zaszło 47% | P=80-100%: n=93, zaszło 69%
- P(opad>=10 mm): P=0: n=1239, zaszło 0% | P=0-20%: n=163, zaszło 7% | P=20-40%: n=40, zaszło 12% | P=40-60%: n=26, zaszło 23% | P=60-80%: n=18, zaszło 22% | P=80-100%: n=7, zaszło 57%
### wyprzedzenie k=2: n=1493 stacjodni, mokrych (>=1 mm) 493
- średnia obs 1.50 mm, GEFS 2.14 mm; korelacja sqrt = 0.715
- dni mokre: GEFS/obs = 0.98; obs > max zespołu: 6.5% dni mokrych
- P(opad>=1 mm): P=0: n=243, zaszło 1% | P=0-20%: n=253, zaszło 6% | P=20-40%: n=185, zaszło 21% | P=40-60%: n=170, zaszło 28% | P=60-80%: n=223, zaszło 41% | P=80-100%: n=419, zaszło 71%
- P(opad>=5 mm): P=0: n=751, zaszło 1% | P=0-20%: n=399, zaszło 6% | P=20-40%: n=146, zaszło 25% | P=40-60%: n=83, zaszło 36% | P=60-80%: n=51, zaszło 63% | P=80-100%: n=63, zaszło 56%
- P(opad>=10 mm): P=0: n=1159, zaszło 0% | P=0-20%: n=233, zaszło 5% | P=20-40%: n=59, zaszło 15% | P=40-60%: n=30, zaszło 23% | P=60-80%: n=11, zaszło 9% | P=80-100%: n=1, zaszło 0%

## 2. Śnieg — metody rozpoznawania fazy opadu (okno 06->06 UTC)
Zdarzenie obserwowane: opad rodzaju S (śnieg) o sumie >= X mm. Prognoza: P(opad zamarznięty >= X mm) wg metody. Kolumna 'deszcz->śnieg' = odsetek dni z obserwowanym DESZCZEM >=3 mm, w których metoda daje P(śnieg>=3 mm) >= 30% (fałszywy śnieg).
### wyprzedzenie k=0: n=1493; obs śnieg >=1 mm: 253, >=3 mm: 143, >=5 mm: 74; deszcz >=3 mm: 83
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A obecna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.48 | 0.57 | 0.29 | 0.66 | 0.47 | 2% |
| D: T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.66 | 0.58 | 0.34 | 0.86 | 0.50 | 5% |
| G: CPOFP (gdy ważny), inaczej D | 0.63 | 0.58 | 0.33 | 0.83 | 0.49 | 5% |
| W0: mokry termometr, zimniejsza z 2 próbek (1@0C->0@2C) | 0.64 | 0.58 | 0.34 | 0.90 | 0.51 | 4% |
| W1: mokry termometr (1@0.5C->0@2.5C) | 0.72 | 0.59 | 0.36 | 0.93 | 0.55 | 13% |
| W2: mokry termometr (1@1C->0@3C) | 0.80 | 0.59 | 0.37 | 0.95 | 0.57 | 23% |
- wiarygodność P(śnieg>=3 mm), metoda 'A': P=0: n=1233, zaszło 5% | P=0-20%: n=85, zaszło 19% | P=20-40%: n=27, zaszło 22% | P=40-60%: n=22, zaszło 23% | P=60-80%: n=22, zaszło 18% | P=80-100%: n=104, zaszło 54%
### wyprzedzenie k=1: n=1493; obs śnieg >=1 mm: 262, >=3 mm: 158, >=5 mm: 95; deszcz >=3 mm: 109
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A obecna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.47 | 0.55 | 0.30 | 0.58 | 0.56 | 1% |
| D: T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.70 | 0.52 | 0.40 | 0.84 | 0.54 | 1% |
| G: CPOFP (gdy ważny), inaczej D | 0.58 | 0.56 | 0.34 | 0.76 | 0.56 | 1% |
| W0: mokry termometr, zimniejsza z 2 próbek (1@0C->0@2C) | 0.62 | 0.53 | 0.36 | 0.86 | 0.54 | 3% |
| W1: mokry termometr (1@0.5C->0@2.5C) | 0.73 | 0.53 | 0.40 | 0.92 | 0.57 | 5% |
| W2: mokry termometr (1@1C->0@3C) | 0.79 | 0.54 | 0.41 | 0.96 | 0.59 | 9% |
- wiarygodność P(śnieg>=3 mm), metoda 'A': P=0: n=1152, zaszło 5% | P=0-20%: n=153, zaszło 18% | P=20-40%: n=49, zaszło 14% | P=40-60%: n=39, zaszło 33% | P=60-80%: n=30, zaszło 47% | P=80-100%: n=70, zaszło 61%
### wyprzedzenie k=2: n=1493; obs śnieg >=1 mm: 259, >=3 mm: 147, >=5 mm: 87; deszcz >=3 mm: 101
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A obecna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.39 | 0.68 | 0.21 | 0.60 | 0.64 | 0% |
| D: T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.63 | 0.63 | 0.30 | 0.82 | 0.64 | 1% |
| G: CPOFP (gdy ważny), inaczej D | 0.54 | 0.64 | 0.28 | 0.79 | 0.64 | 1% |
| W0: mokry termometr, zimniejsza z 2 próbek (1@0C->0@2C) | 0.61 | 0.63 | 0.30 | 0.83 | 0.64 | 0% |
| W1: mokry termometr (1@0.5C->0@2.5C) | 0.67 | 0.63 | 0.32 | 0.89 | 0.65 | 3% |
| W2: mokry termometr (1@1C->0@3C) | 0.76 | 0.63 | 0.33 | 0.91 | 0.67 | 9% |
- wiarygodność P(śnieg>=3 mm), metoda 'A': P=0: n=1020, zaszło 5% | P=0-20%: n=239, zaszło 15% | P=20-40%: n=104, zaszło 22% | P=40-60%: n=45, zaszło 36% | P=60-80%: n=44, zaszło 20% | P=80-100%: n=41, zaszło 41%

## 3. Mróz — temperatura powietrza vs odczuwalna (okno doby kalendarzowej 00-24 UTC; obserwacja = TMIN powietrza)
Uwaga: IMGW mierzy tylko temperaturę powietrza, więc odczuwalnej NIE da się zweryfikować wprost; poniżej sprawdzamy, jak daleko od powietrza jest każda wersja i czy 'odczuwalna' nie robi fałszywych alarmów względem realnego mrozu.
### wyprzedzenie k=0: n=1492
- prognoza min. T powietrza: błąd średni +0.82 C, MAE 1.97 C; w mroźnych dniach (obs <= -10 C): błąd +2.51 C
- odczuwalna z PORYWÓW (obecna): chłodniejsza od powietrza średnio o 8.1 C
- odczuwalna z wiatru ŚREDNIEGO: chłodniejsza od powietrza średnio o 6.0 C
- próg -5 C (obs zdarzeń 691), powietrze: P>=30%: traf. 619, fałsz. 34, przegap. 72 (POD 0.90, FAR 0.05, CSI 0.85)
- próg -10 C (obs zdarzeń 424), powietrze: P>=30%: traf. 280, fałsz. 35, przegap. 144 (POD 0.66, FAR 0.11, CSI 0.61)
- próg -15 C (obs zdarzeń 132), powietrze: P>=30%: traf. 51, fałsz. 18, przegap. 81 (POD 0.39, FAR 0.26, CSI 0.34)
- próg -20 C (obs zdarzeń 23), powietrze: P>=30%: traf. 3, fałsz. 0, przegap. 20 (POD 0.13, FAR 0.00, CSI 0.13)
### wyprzedzenie k=1: n=1490
- prognoza min. T powietrza: błąd średni +1.19 C, MAE 2.19 C; w mroźnych dniach (obs <= -10 C): błąd +2.99 C
- odczuwalna z PORYWÓW (obecna): chłodniejsza od powietrza średnio o 7.5 C
- odczuwalna z wiatru ŚREDNIEGO: chłodniejsza od powietrza średnio o 5.5 C
- próg -5 C (obs zdarzeń 616), powietrze: P>=30%: traf. 547, fałsz. 11, przegap. 69 (POD 0.89, FAR 0.02, CSI 0.87)
- próg -10 C (obs zdarzeń 406), powietrze: P>=30%: traf. 265, fałsz. 42, przegap. 141 (POD 0.65, FAR 0.14, CSI 0.59)
- próg -15 C (obs zdarzeń 125), powietrze: P>=30%: traf. 40, fałsz. 19, przegap. 85 (POD 0.32, FAR 0.32, CSI 0.28)
- próg -20 C (obs zdarzeń 24), powietrze: P>=30%: traf. 0, fałsz. 1, przegap. 24 (POD 0.00, FAR 1.00, CSI 0.00)
### wyprzedzenie k=2: n=1490
- prognoza min. T powietrza: błąd średni +0.98 C, MAE 2.39 C; w mroźnych dniach (obs <= -10 C): błąd +3.69 C
- odczuwalna z PORYWÓW (obecna): chłodniejsza od powietrza średnio o 7.1 C
- odczuwalna z wiatru ŚREDNIEGO: chłodniejsza od powietrza średnio o 5.1 C
- próg -5 C (obs zdarzeń 511), powietrze: P>=30%: traf. 422, fałsz. 32, przegap. 89 (POD 0.83, FAR 0.07, CSI 0.78)
- próg -10 C (obs zdarzeń 297), powietrze: P>=30%: traf. 188, fałsz. 66, przegap. 109 (POD 0.63, FAR 0.26, CSI 0.52)
- próg -15 C (obs zdarzeń 100), powietrze: P>=30%: traf. 25, fałsz. 15, przegap. 75 (POD 0.25, FAR 0.38, CSI 0.22)
- próg -20 C (obs zdarzeń 7), powietrze: P>=30%: traf. 0, fałsz. 0, przegap. 7 (POD 0.00, FAR 0.00, CSI 0.00)

## 4. Gołoledź — opad w warunkach marznących (CFRZR >= 0.5) vs obserwowane godziny gołoledzi (GOLO)
- k=0, obs GOLO>=1 h: 68 zdarzeń z 1251; prognoza P(opad marznący >= 0.1 mm): P>=10%: traf. 24, fałsz. 78, przegap. 44 (POD 0.35, FAR 0.76, CSI 0.16) | P>=30%: traf. 14, fałsz. 41, przegap. 54 (POD 0.21, FAR 0.75, CSI 0.13)
- k=0, obs GOLO>=1 h: 68 zdarzeń z 1251; prognoza P(opad marznący >= 1.0 mm): P>=10%: traf. 12, fałsz. 15, przegap. 56 (POD 0.18, FAR 0.56, CSI 0.14) | P>=30%: traf. 6, fałsz. 4, przegap. 62 (POD 0.09, FAR 0.40, CSI 0.08)
- k=1, obs GOLO>=1 h: 69 zdarzeń z 1251; prognoza P(opad marznący >= 0.1 mm): P>=10%: traf. 23, fałsz. 68, przegap. 46 (POD 0.33, FAR 0.75, CSI 0.17) | P>=30%: traf. 12, fałsz. 26, przegap. 57 (POD 0.17, FAR 0.68, CSI 0.13)
- k=1, obs GOLO>=1 h: 69 zdarzeń z 1251; prognoza P(opad marznący >= 1.0 mm): P>=10%: traf. 10, fałsz. 18, przegap. 59 (POD 0.14, FAR 0.64, CSI 0.11) | P>=30%: traf. 8, fałsz. 6, przegap. 61 (POD 0.12, FAR 0.43, CSI 0.11)
- k=2, obs GOLO>=1 h: 77 zdarzeń z 1251; prognoza P(opad marznący >= 0.1 mm): P>=10%: traf. 20, fałsz. 58, przegap. 57 (POD 0.26, FAR 0.74, CSI 0.15) | P>=30%: traf. 6, fałsz. 13, przegap. 71 (POD 0.08, FAR 0.68, CSI 0.07)
- k=2, obs GOLO>=1 h: 77 zdarzeń z 1251; prognoza P(opad marznący >= 1.0 mm): P>=10%: traf. 8, fałsz. 23, przegap. 69 (POD 0.10, FAR 0.74, CSI 0.08) | P>=30%: traf. 1, fałsz. 2, przegap. 76 (POD 0.01, FAR 0.67, CSI 0.01)

## 5. Zamieć — definicja SWWF (porywy >= 15.5 m/s, widzialność <= 400 m, śnieg świeży/leżący) vs obserwowane godziny zamieci śnieżnej (ZMNI+ZMWS)
Uwaga: przebiegi bez pola widzialności (GEFS 2021) nie mogą dać flagi wg definicji SWWF, więc są z tej oceny wyłączone; wariant 'bez VIS' (porywy + śnieg) działa na wszystkich.
- k=0: obs zamieć >=1 h: 59 z 1251 stacjodni
    bez VIS (porywy >= 15.5 m/s + śnieg): P>=10%: traf. 30, fałsz. 475, przegap. 29 (POD 0.51, FAR 0.94, CSI 0.06) | P>=30%: traf. 27, fałsz. 404, przegap. 32 (POD 0.46, FAR 0.94, CSI 0.06) | P>=50%: traf. 21, fałsz. 360, przegap. 38 (POD 0.36, FAR 0.94, CSI 0.05)
    tylko porywy >= 15.5 m/s: P>=30%: traf. 28, fałsz. 601, przegap. 31 (POD 0.47, FAR 0.96, CSI 0.04) | P>=50%: traf. 26, fałsz. 546, przegap. 33 (POD 0.44, FAR 0.95, CSI 0.04)
    tylko porywy >= 20 m/s: P>=30%: traf. 4, fałsz. 267, przegap. 55 (POD 0.07, FAR 0.99, CSI 0.01) | P>=50%: traf. 0, fałsz. 233, przegap. 59 (POD 0.00, FAR 1.00, CSI 0.00)
- k=1: obs zamieć >=1 h: 75 z 1251 stacjodni
    bez VIS (porywy >= 15.5 m/s + śnieg): P>=10%: traf. 38, fałsz. 530, przegap. 37 (POD 0.51, FAR 0.93, CSI 0.06) | P>=30%: traf. 28, fałsz. 427, przegap. 47 (POD 0.37, FAR 0.94, CSI 0.06) | P>=50%: traf. 19, fałsz. 364, przegap. 56 (POD 0.25, FAR 0.95, CSI 0.04)
    tylko porywy >= 15.5 m/s: P>=30%: traf. 34, fałsz. 616, przegap. 41 (POD 0.45, FAR 0.95, CSI 0.05) | P>=50%: traf. 29, fałsz. 553, przegap. 46 (POD 0.39, FAR 0.95, CSI 0.05)
    tylko porywy >= 20 m/s: P>=30%: traf. 3, fałsz. 241, przegap. 72 (POD 0.04, FAR 0.99, CSI 0.01) | P>=50%: traf. 2, fałsz. 188, przegap. 73 (POD 0.03, FAR 0.99, CSI 0.01)

