# Kalibracja SWWF na obserwacjach IMGW — 2026-10-07 15:45
hindcast: /home/runner/work/SWWF/SWWF/hindcast_v2 (17 przebiegów 00Z z 30 członkami, okien na przebieg: [13]); obs: imgw_dobowe_2020-11-01_2026-03-31_mc-1-2-3-11-12.csv.gz (52851 stacjodni)
Próba jest dobrana pod zdarzenia (nie klimatologiczna) — FAR i odsetki dni zdarzeń nie są częstościami klimatologicznymi.

## 0. Kontrola okna doby IMGW (k=0)
- opad SMDB: start  0 UTC: r=0.797 | start  6 UTC: r=0.822 | start 12 UTC: r=0.750 | start 18 UTC: r=0.623  (najwyższe r = okno zgodne z IMGW)
- TMIN: start  0 UTC: r=0.929 | start  6 UTC: r=0.878 | start 12 UTC: r=0.857 | start 18 UTC: r=0.830  (najwyższe r = okno zgodne z IMGW)

## 1. Opad dobowy (okno 06->06 UTC)
### wyprzedzenie k=0: n=941 stacjodni, mokrych (>=1 mm) 232
- średnia obs 0.98 mm, GEFS 1.67 mm; korelacja sqrt = 0.822
- dni mokre: GEFS/obs = 1.33; obs > max zespołu: 5.2% dni mokrych
- P(opad>=1 mm): P=0: n=443, zaszło 0% | P=0-20%: n=93, zaszło 8% | P=20-40%: n=45, zaszło 16% | P=40-60%: n=59, zaszło 14% | P=60-80%: n=42, zaszło 38% | P=80-100%: n=259, zaszło 75%
- P(opad>=5 mm): P=0: n=692, zaszło 0% | P=0-20%: n=105, zaszło 4% | P=20-40%: n=44, zaszło 20% | P=40-60%: n=21, zaszło 19% | P=60-80%: n=24, zaszło 38% | P=80-100%: n=55, zaszło 51%
- P(opad>=10 mm): P=0: n=858, zaszło 0% | P=0-20%: n=37, zaszło 5% | P=20-40%: n=10, zaszło 0% | P=40-60%: n=11, zaszło 27% | P=60-80%: n=13, zaszło 15% | P=80-100%: n=12, zaszło 8%
### wyprzedzenie k=1: n=941 stacjodni, mokrych (>=1 mm) 264
- średnia obs 1.24 mm, GEFS 1.79 mm; korelacja sqrt = 0.767
- dni mokre: GEFS/obs = 1.07; obs > max zespołu: 6.4% dni mokrych
- P(opad>=1 mm): P=0: n=248, zaszło 0% | P=0-20%: n=164, zaszło 4% | P=20-40%: n=113, zaszło 14% | P=40-60%: n=85, zaszło 28% | P=60-80%: n=79, zaszło 32% | P=80-100%: n=252, zaszło 76%
- P(opad>=5 mm): P=0: n=634, zaszło 1% | P=0-20%: n=150, zaszło 7% | P=20-40%: n=57, zaszło 16% | P=40-60%: n=34, zaszło 50% | P=60-80%: n=26, zaszło 38% | P=80-100%: n=40, zaszło 62%
- P(opad>=10 mm): P=0: n=813, zaszło 0% | P=0-20%: n=75, zaszło 8% | P=20-40%: n=18, zaszło 0% | P=40-60%: n=16, zaszło 31% | P=60-80%: n=17, zaszło 24% | P=80-100%: n=2, zaszło 0%
### wyprzedzenie k=2: n=941 stacjodni, mokrych (>=1 mm) 300
- średnia obs 1.42 mm, GEFS 2.17 mm; korelacja sqrt = 0.677
- dni mokre: GEFS/obs = 1.01; obs > max zespołu: 7.0% dni mokrych
- P(opad>=1 mm): P=0: n=117, zaszło 2% | P=0-20%: n=187, zaszło 6% | P=20-40%: n=127, zaszło 25% | P=40-60%: n=101, zaszło 27% | P=60-80%: n=151, zaszło 35% | P=80-100%: n=258, zaszło 67%
- P(opad>=5 mm): P=0: n=479, zaszło 0% | P=0-20%: n=248, zaszło 8% | P=20-40%: n=83, zaszło 28% | P=40-60%: n=50, zaszło 26% | P=60-80%: n=25, zaszło 40% | P=80-100%: n=56, zaszło 52%
- P(opad>=10 mm): P=0: n=726, zaszło 0% | P=0-20%: n=147, zaszło 3% | P=20-40%: n=40, zaszło 15% | P=40-60%: n=18, zaszło 6% | P=60-80%: n=9, zaszło 11% | P=80-100%: n=1, zaszło 0%

## 2. Śnieg — metody rozpoznawania fazy opadu (okno 06->06 UTC)
Zdarzenie obserwowane: opad rodzaju S (śnieg) o sumie >= X mm. Prognoza: P(opad zamarznięty >= X mm) wg metody. Kolumna 'deszcz->śnieg' = odsetek dni z obserwowanym DESZCZEM >=3 mm, w których metoda daje P(śnieg>=3 mm) >= 30% (fałszywy śnieg).
### wyprzedzenie k=0: n=941; obs śnieg >=1 mm: 156, >=3 mm: 83, >=5 mm: 39; deszcz >=3 mm: 25
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A obecna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.73 | 0.54 | 0.40 | 0.82 | 0.48 | 4% |
| D: T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.83 | 0.56 | 0.41 | 0.92 | 0.51 | 12% |
| G: CPOFP (gdy ważny), inaczej D | 0.83 | 0.56 | 0.41 | 0.92 | 0.51 | 12% |
| W0: mokry termometr, zimniejsza z 2 próbek (1@0C->0@2C) | 0.82 | 0.54 | 0.41 | 0.94 | 0.51 | 4% |
| W1: mokry termometr (1@0.5C->0@2.5C) | 0.83 | 0.56 | 0.40 | 0.95 | 0.52 | 12% |
| W2: mokry termometr (1@1C->0@3C) | 0.88 | 0.57 | 0.41 | 0.95 | 0.54 | 20% |
- wiarygodność P(śnieg>=3 mm), metoda 'A': P=0: n=740, zaszło 2% | P=0-20%: n=57, zaszło 11% | P=20-40%: n=24, zaszło 21% | P=40-60%: n=15, zaszło 33% | P=60-80%: n=16, zaszło 19% | P=80-100%: n=89, zaszło 55%
### wyprzedzenie k=1: n=941; obs śnieg >=1 mm: 141, >=3 mm: 67, >=5 mm: 34; deszcz >=3 mm: 61
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A obecna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.87 | 0.54 | 0.43 | 0.82 | 0.57 | 2% |
| D: T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.88 | 0.58 | 0.40 | 0.92 | 0.60 | 2% |
| G: CPOFP (gdy ważny), inaczej D | 0.88 | 0.58 | 0.40 | 0.92 | 0.60 | 2% |
| W0: mokry termometr, zimniejsza z 2 próbek (1@0C->0@2C) | 0.87 | 0.57 | 0.40 | 0.92 | 0.59 | 2% |
| W1: mokry termometr (1@0.5C->0@2.5C) | 0.88 | 0.58 | 0.40 | 0.94 | 0.61 | 2% |
| W2: mokry termometr (1@1C->0@3C) | 0.88 | 0.59 | 0.39 | 0.96 | 0.61 | 2% |
- wiarygodność P(śnieg>=3 mm), metoda 'A': P=0: n=705, zaszło 1% | P=0-20%: n=92, zaszło 3% | P=20-40%: n=33, zaszło 9% | P=40-60%: n=28, zaszło 36% | P=60-80%: n=24, zaszło 42% | P=80-100%: n=59, zaszło 61%
### wyprzedzenie k=2: n=941; obs śnieg >=1 mm: 147, >=3 mm: 78, >=5 mm: 43; deszcz >=3 mm: 73
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A obecna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.49 | 0.73 | 0.21 | 0.69 | 0.66 | 0% |
| D: T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.72 | 0.67 | 0.29 | 0.86 | 0.66 | 0% |
| G: CPOFP (gdy ważny), inaczej D | 0.72 | 0.67 | 0.29 | 0.86 | 0.66 | 0% |
| W0: mokry termometr, zimniejsza z 2 próbek (1@0C->0@2C) | 0.71 | 0.67 | 0.29 | 0.84 | 0.64 | 0% |
| W1: mokry termometr (1@0.5C->0@2.5C) | 0.76 | 0.66 | 0.31 | 0.90 | 0.65 | 0% |
| W2: mokry termometr (1@1C->0@3C) | 0.82 | 0.65 | 0.32 | 0.93 | 0.67 | 1% |
- wiarygodność P(śnieg>=3 mm), metoda 'A': P=0: n=634, zaszło 4% | P=0-20%: n=131, zaszło 8% | P=20-40%: n=72, zaszło 14% | P=40-60%: n=31, zaszło 32% | P=60-80%: n=35, zaszło 17% | P=80-100%: n=38, zaszło 37%

## 3. Mróz — temperatura powietrza vs odczuwalna (okno doby kalendarzowej 00-24 UTC; obserwacja = TMIN powietrza)
Uwaga: IMGW mierzy tylko temperaturę powietrza, więc odczuwalnej NIE da się zweryfikować wprost; poniżej sprawdzamy, jak daleko od powietrza jest każda wersja i czy 'odczuwalna' nie robi fałszywych alarmów względem realnego mrozu.
### wyprzedzenie k=0: n=941
- prognoza min. T powietrza: błąd średni +0.79 C, MAE 1.79 C; w mroźnych dniach (obs <= -10 C): błąd +1.66 C
- odczuwalna z PORYWÓW (obecna): chłodniejsza od powietrza średnio o 8.0 C
- odczuwalna z wiatru ŚREDNIEGO: chłodniejsza od powietrza średnio o 6.0 C
- próg -5 C (obs zdarzeń 443), powietrze: P>=30%: traf. 401, fałsz. 23, przegap. 42 (POD 0.91, FAR 0.05, CSI 0.86)
- próg -10 C (obs zdarzeń 262), powietrze: P>=30%: traf. 182, fałsz. 24, przegap. 80 (POD 0.69, FAR 0.12, CSI 0.64)
- próg -15 C (obs zdarzeń 65), powietrze: P>=30%: traf. 27, fałsz. 17, przegap. 38 (POD 0.42, FAR 0.39, CSI 0.33)
- próg -20 C (obs zdarzeń 5), powietrze: P>=30%: traf. 0, fałsz. 0, przegap. 5 (POD 0.00, FAR 0.00, CSI 0.00)
### wyprzedzenie k=1: n=941
- prognoza min. T powietrza: błąd średni +0.86 C, MAE 1.88 C; w mroźnych dniach (obs <= -10 C): błąd +1.27 C
- odczuwalna z PORYWÓW (obecna): chłodniejsza od powietrza średnio o 7.6 C
- odczuwalna z wiatru ŚREDNIEGO: chłodniejsza od powietrza średnio o 5.5 C
- próg -5 C (obs zdarzeń 405), powietrze: P>=30%: traf. 356, fałsz. 5, przegap. 49 (POD 0.88, FAR 0.01, CSI 0.87)
- próg -10 C (obs zdarzeń 228), powietrze: P>=30%: traf. 179, fałsz. 39, przegap. 49 (POD 0.79, FAR 0.18, CSI 0.67)
- próg -15 C (obs zdarzeń 48), powietrze: P>=30%: traf. 20, fałsz. 17, przegap. 28 (POD 0.42, FAR 0.46, CSI 0.31)
- próg -20 C (obs zdarzeń 5), powietrze: P>=30%: traf. 0, fałsz. 1, przegap. 5 (POD 0.00, FAR 1.00, CSI 0.00)
### wyprzedzenie k=2: n=941
- prognoza min. T powietrza: błąd średni +0.65 C, MAE 2.08 C; w mroźnych dniach (obs <= -10 C): błąd +1.61 C
- odczuwalna z PORYWÓW (obecna): chłodniejsza od powietrza średnio o 7.1 C
- odczuwalna z wiatru ŚREDNIEGO: chłodniejsza od powietrza średnio o 5.1 C
- próg -5 C (obs zdarzeń 328), powietrze: P>=30%: traf. 294, fałsz. 22, przegap. 34 (POD 0.90, FAR 0.07, CSI 0.84)
- próg -10 C (obs zdarzeń 171), powietrze: P>=30%: traf. 146, fałsz. 64, przegap. 25 (POD 0.85, FAR 0.30, CSI 0.62)
- próg -15 C (obs zdarzeń 45), powietrze: P>=30%: traf. 14, fałsz. 14, przegap. 31 (POD 0.31, FAR 0.50, CSI 0.24)

## 4. Gołoledź — opad w warunkach marznących (CFRZR >= 0.5) vs obserwowane godziny gołoledzi (GOLO)
- k=0, obs GOLO>=1 h: 68 zdarzeń z 941; prognoza P(opad marznący >= 0.1 mm): P>=10%: traf. 24, fałsz. 75, przegap. 44 (POD 0.35, FAR 0.76, CSI 0.17) | P>=30%: traf. 14, fałsz. 41, przegap. 54 (POD 0.21, FAR 0.75, CSI 0.13)
- k=0, obs GOLO>=1 h: 68 zdarzeń z 941; prognoza P(opad marznący >= 1.0 mm): P>=10%: traf. 12, fałsz. 15, przegap. 56 (POD 0.18, FAR 0.56, CSI 0.14) | P>=30%: traf. 6, fałsz. 4, przegap. 62 (POD 0.09, FAR 0.40, CSI 0.08)
- k=1, obs GOLO>=1 h: 69 zdarzeń z 941; prognoza P(opad marznący >= 0.1 mm): P>=10%: traf. 23, fałsz. 63, przegap. 46 (POD 0.33, FAR 0.73, CSI 0.17) | P>=30%: traf. 12, fałsz. 23, przegap. 57 (POD 0.17, FAR 0.66, CSI 0.13)
- k=1, obs GOLO>=1 h: 69 zdarzeń z 941; prognoza P(opad marznący >= 1.0 mm): P>=10%: traf. 10, fałsz. 14, przegap. 59 (POD 0.14, FAR 0.58, CSI 0.12) | P>=30%: traf. 8, fałsz. 5, przegap. 61 (POD 0.12, FAR 0.38, CSI 0.11)
- k=2, obs GOLO>=1 h: 71 zdarzeń z 941; prognoza P(opad marznący >= 0.1 mm): P>=10%: traf. 16, fałsz. 53, przegap. 55 (POD 0.23, FAR 0.77, CSI 0.13) | P>=30%: traf. 4, fałsz. 11, przegap. 67 (POD 0.06, FAR 0.73, CSI 0.05)
- k=2, obs GOLO>=1 h: 71 zdarzeń z 941; prognoza P(opad marznący >= 1.0 mm): P>=10%: traf. 6, fałsz. 20, przegap. 65 (POD 0.08, FAR 0.77, CSI 0.07) | P>=30%: traf. 1, fałsz. 2, przegap. 70 (POD 0.01, FAR 0.67, CSI 0.01)

## 5. Zamieć — definicja SWWF (porywy >= 15.5 m/s, widzialność <= 400 m, śnieg świeży/leżący) vs obserwowane godziny zamieci śnieżnej (ZMNI+ZMWS)
Uwaga: przebiegi bez pola widzialności (GEFS 2021) nie mogą dać flagi wg definicji SWWF, więc są z tej oceny wyłączone; wariant 'bez VIS' (porywy + śnieg) działa na wszystkich.
- k=0: obs zamieć >=1 h: 57 z 941 stacjodni
    bez VIS (porywy >= 15.5 m/s + śnieg): P>=10%: traf. 28, fałsz. 223, przegap. 29 (POD 0.49, FAR 0.89, CSI 0.10) | P>=30%: traf. 25, fałsz. 164, przegap. 32 (POD 0.44, FAR 0.87, CSI 0.11) | P>=50%: traf. 20, fałsz. 133, przegap. 37 (POD 0.35, FAR 0.87, CSI 0.11)
    tylko porywy >= 15.5 m/s: P>=30%: traf. 26, fałsz. 339, przegap. 31 (POD 0.46, FAR 0.93, CSI 0.07) | P>=50%: traf. 25, fałsz. 286, przegap. 32 (POD 0.44, FAR 0.92, CSI 0.07)
    tylko porywy >= 20 m/s: P>=30%: traf. 4, fałsz. 62, przegap. 53 (POD 0.07, FAR 0.94, CSI 0.03) | P>=50%: traf. 0, fałsz. 38, przegap. 57 (POD 0.00, FAR 1.00, CSI 0.00)
- k=1: obs zamieć >=1 h: 72 z 941 stacjodni
    bez VIS (porywy >= 15.5 m/s + śnieg): P>=10%: traf. 36, fałsz. 257, przegap. 36 (POD 0.50, FAR 0.88, CSI 0.11) | P>=30%: traf. 26, fałsz. 179, przegap. 46 (POD 0.36, FAR 0.87, CSI 0.10) | P>=50%: traf. 17, fałsz. 132, przegap. 55 (POD 0.24, FAR 0.89, CSI 0.08)
    tylko porywy >= 15.5 m/s: P>=30%: traf. 32, fałsz. 342, przegap. 40 (POD 0.44, FAR 0.91, CSI 0.08) | P>=50%: traf. 27, fałsz. 285, przegap. 45 (POD 0.38, FAR 0.91, CSI 0.08)
    tylko porywy >= 20 m/s: P>=30%: traf. 1, fałsz. 30, przegap. 71 (POD 0.01, FAR 0.97, CSI 0.01) | P>=50%: traf. 0, fałsz. 7, przegap. 72 (POD 0.00, FAR 1.00, CSI 0.00)

