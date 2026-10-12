# Kalibracja SWWF na obserwacjach IMGW — 2026-10-12 14:22
hindcast: /home/runner/work/SWWF/SWWF/hindcast_ifs (96 przebiegów 00Z z 51 członkami, okien na przebieg: [13]); obs: imgw_dobowe_2020-11-01_2026-03-31_mc-1-2-3-11-12.csv.gz (52851 stacjodni)
Próba jest dobrana pod zdarzenia i dni spokojne (nie klimatologiczna) — FAR i odsetki zdarzeń z sekcji 1-5 dotyczą próby mieszanej; sekcja 6 rozdziela doby bez zdarzenia i ze zdarzeniem.

## 0. Kontrola okna doby IMGW (k=0)
- opad SMDB: start  0 UTC: r=0.829 | start  6 UTC: r=0.881 | start 12 UTC: r=0.813 | start 18 UTC: r=0.651  (najwyższe r = okno zgodne z IMGW)
- TMIN: start  0 UTC: r=0.931 | start  6 UTC: r=0.852 | start 12 UTC: r=0.831 | start 18 UTC: r=0.803  (najwyższe r = okno zgodne z IMGW)

## 1. Opad dobowy (okno 06->06 UTC)
### wyprzedzenie k=0: n=5249 stacjodni, mokrych (>=1 mm) 1338
- średnia obs 1.29 mm, IFS ENS 1.76 mm; korelacja sqrt = 0.881
- dni mokre: IFS ENS/obs = 1.13; obs > max zespołu: 5.2% dni mokrych
- P(opad>=1 mm): P=0: n=2412, zaszło 0% | P=0-20%: n=641, zaszło 5% | P=20-40%: n=254, zaszło 14% | P=40-60%: n=199, zaszło 20% | P=60-80%: n=240, zaszło 28% | P=80-100%: n=1503, zaszło 76%
- P(opad>=5 mm): P=0: n=3896, zaszło 0% | P=0-20%: n=611, zaszło 5% | P=20-40%: n=165, zaszło 20% | P=40-60%: n=92, zaszło 27% | P=60-80%: n=90, zaszło 33% | P=80-100%: n=395, zaszło 77%
- P(opad>=10 mm): P=0: n=4732, zaszło 0% | P=0-20%: n=252, zaszło 6% | P=20-40%: n=62, zaszło 27% | P=40-60%: n=48, zaszło 44% | P=60-80%: n=48, zaszło 60% | P=80-100%: n=107, zaszło 81%
### wyprzedzenie k=1: n=5304 stacjodni, mokrych (>=1 mm) 1496
- średnia obs 1.43 mm, IFS ENS 1.82 mm; korelacja sqrt = 0.849
- dni mokre: IFS ENS/obs = 1.02; obs > max zespołu: 5.1% dni mokrych
- P(opad>=1 mm): P=0: n=1802, zaszło 1% | P=0-20%: n=944, zaszło 5% | P=20-40%: n=412, zaszło 18% | P=40-60%: n=336, zaszło 25% | P=60-80%: n=406, zaszło 44% | P=80-100%: n=1404, zaszło 78%
- P(opad>=5 mm): P=0: n=3489, zaszło 0% | P=0-20%: n=974, zaszło 5% | P=20-40%: n=239, zaszło 21% | P=40-60%: n=156, zaszło 37% | P=60-80%: n=154, zaszło 54% | P=80-100%: n=292, zaszło 77%
- P(opad>=10 mm): P=0: n=4576, zaszło 0% | P=0-20%: n=446, zaszło 7% | P=20-40%: n=96, zaszło 27% | P=40-60%: n=70, zaszło 49% | P=60-80%: n=56, zaszło 61% | P=80-100%: n=60, zaszło 87%
### wyprzedzenie k=2: n=5303 stacjodni, mokrych (>=1 mm) 1438
- średnia obs 1.37 mm, IFS ENS 1.66 mm; korelacja sqrt = 0.789
- dni mokre: IFS ENS/obs = 0.88; obs > max zespołu: 5.6% dni mokrych
- P(opad>=1 mm): P=0: n=1399, zaszło 1% | P=0-20%: n=1263, zaszło 6% | P=20-40%: n=559, zaszło 19% | P=40-60%: n=464, zaszło 31% | P=60-80%: n=498, zaszło 48% | P=80-100%: n=1120, zaszło 78%
- P(opad>=5 mm): P=0: n=3177, zaszło 0% | P=0-20%: n=1321, zaszło 6% | P=20-40%: n=312, zaszło 23% | P=40-60%: n=183, zaszło 43% | P=60-80%: n=158, zaszło 57% | P=80-100%: n=152, zaszło 80%
- P(opad>=10 mm): P=0: n=4400, zaszło 0% | P=0-20%: n=657, zaszło 6% | P=20-40%: n=122, zaszło 43% | P=40-60%: n=64, zaszło 52% | P=60-80%: n=38, zaszło 58% | P=80-100%: n=22, zaszło 91%

## 2. Śnieg — metody rozpoznawania fazy opadu (okno 06->06 UTC)
Zdarzenie obserwowane: opad rodzaju S (śnieg) o sumie >= X mm. Prognoza: P(opad zamarznięty >= X mm) wg metody. Kolumna 'deszcz->śnieg' = odsetek dni z obserwowanym DESZCZEM >=3 mm, w których metoda daje P(śnieg>=3 mm) >= 30% (fałszywy śnieg).
(brak pól wilgotności w danych albo zespół z IFS (IFS nie ma wilgotności) — warianty z mokrym termometrem pominięte)
### wyprzedzenie k=0: n=5249; obs śnieg >=1 mm: 607, >=3 mm: 315, >=5 mm: 194; deszcz >=3 mm: 330
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A dawna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.56 | 0.57 | 0.32 | 0.74 | 0.51 | 9% |
| D obecna (produkcja): T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.80 | 0.60 | 0.36 | 0.92 | 0.56 | 25% |
| G: CPOFP (gdy ważny), inaczej D | 0.80 | 0.60 | 0.36 | 0.92 | 0.56 | 25% |
- wiarygodność P(śnieg>=3 mm), metoda 'D' (produkcyjna): P=0: n=4086, zaszło 0% | P=0-20%: n=453, zaszło 8% | P=20-40%: n=136, zaszło 14% | P=40-60%: n=93, zaszło 28% | P=60-80%: n=125, zaszło 26% | P=80-100%: n=356, zaszło 52%
### wyprzedzenie k=1: n=5304; obs śnieg >=1 mm: 650, >=3 mm: 336, >=5 mm: 191; deszcz >=3 mm: 402
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A dawna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.51 | 0.58 | 0.30 | 0.70 | 0.51 | 8% |
| D obecna (produkcja): T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.74 | 0.60 | 0.35 | 0.88 | 0.56 | 22% |
| G: CPOFP (gdy ważny), inaczej D | 0.74 | 0.60 | 0.35 | 0.88 | 0.56 | 22% |
- wiarygodność P(śnieg>=3 mm), metoda 'D' (produkcyjna): P=0: n=3850, zaszło 1% | P=0-20%: n=730, zaszło 7% | P=20-40%: n=191, zaszło 19% | P=40-60%: n=126, zaszło 28% | P=60-80%: n=148, zaszło 34% | P=80-100%: n=259, zaszło 54%
### wyprzedzenie k=2: n=5303; obs śnieg >=1 mm: 612, >=3 mm: 308, >=5 mm: 176; deszcz >=3 mm: 419
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A dawna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.46 | 0.63 | 0.26 | 0.72 | 0.54 | 5% |
| D obecna (produkcja): T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.69 | 0.63 | 0.32 | 0.89 | 0.58 | 15% |
| G: CPOFP (gdy ważny), inaczej D | 0.69 | 0.63 | 0.32 | 0.89 | 0.58 | 15% |
- wiarygodność P(śnieg>=3 mm), metoda 'D' (produkcyjna): P=0: n=3570, zaszło 0% | P=0-20%: n=987, zaszło 6% | P=20-40%: n=294, zaszło 15% | P=40-60%: n=187, zaszło 35% | P=60-80%: n=127, zaszło 35% | P=80-100%: n=138, zaszło 57%

## 3. Mróz — temperatura powietrza vs odczuwalna (okno doby kalendarzowej 00-24 UTC; obserwacja = TMIN powietrza)
Uwaga: IMGW mierzy tylko temperaturę powietrza, więc odczuwalnej NIE da się zweryfikować wprost; poniżej sprawdzamy, jak daleko od powietrza jest każda wersja i czy 'odczuwalna' nie robi fałszywych alarmów względem realnego mrozu.
### wyprzedzenie k=0: n=5237
- prognoza min. T powietrza: błąd średni +0.13 C, MAE 1.48 C; w mroźnych dniach (obs <= -10 C): błąd +1.11 C
- próg -5 C (obs zdarzeń 1135), powietrze: P>=30%: traf. 976, fałsz. 153, przegap. 159 (POD 0.86, FAR 0.14, CSI 0.76)
- próg -10 C (obs zdarzeń 472), powietrze: P>=30%: traf. 363, fałsz. 81, przegap. 109 (POD 0.77, FAR 0.18, CSI 0.66)
- próg -15 C (obs zdarzeń 108), powietrze: P>=30%: traf. 68, fałsz. 28, przegap. 40 (POD 0.63, FAR 0.29, CSI 0.50)
- próg -20 C (obs zdarzeń 23), powietrze: P>=30%: traf. 21, fałsz. 12, przegap. 2 (POD 0.91, FAR 0.36, CSI 0.60)
### wyprzedzenie k=1: n=5290
- prognoza min. T powietrza: błąd średni +0.13 C, MAE 1.68 C; w mroźnych dniach (obs <= -10 C): błąd +1.13 C
- próg -5 C (obs zdarzeń 1159), powietrze: P>=30%: traf. 999, fałsz. 171, przegap. 160 (POD 0.86, FAR 0.15, CSI 0.75)
- próg -10 C (obs zdarzeń 484), powietrze: P>=30%: traf. 333, fałsz. 124, przegap. 151 (POD 0.69, FAR 0.27, CSI 0.55)
- próg -15 C (obs zdarzeń 100), powietrze: P>=30%: traf. 64, fałsz. 64, przegap. 36 (POD 0.64, FAR 0.50, CSI 0.39)
- próg -20 C (obs zdarzeń 17), powietrze: P>=30%: traf. 15, fałsz. 18, przegap. 2 (POD 0.88, FAR 0.55, CSI 0.43)
### wyprzedzenie k=2: n=5292
- prognoza min. T powietrza: błąd średni -0.09 C, MAE 1.75 C; w mroźnych dniach (obs <= -10 C): błąd +0.86 C
- próg -5 C (obs zdarzeń 1036), powietrze: P>=30%: traf. 869, fałsz. 205, przegap. 167 (POD 0.84, FAR 0.19, CSI 0.70)
- próg -10 C (obs zdarzeń 427), powietrze: P>=30%: traf. 326, fałsz. 131, przegap. 101 (POD 0.76, FAR 0.29, CSI 0.58)
- próg -15 C (obs zdarzeń 98), powietrze: P>=30%: traf. 65, fałsz. 82, przegap. 33 (POD 0.66, FAR 0.56, CSI 0.36)
- próg -20 C (obs zdarzeń 13), powietrze: P>=30%: traf. 12, fałsz. 14, przegap. 1 (POD 0.92, FAR 0.54, CSI 0.44)

## 6. Fałszywe alarmy na dobach bez zdarzenia i trafienia na dobach ze zdarzeniem
Alarm = P(zdarzenia) >= 30% wg zespołu. Doba 'bez zdarzenia' = zdarzenie na <= 1 stacji (wtedy każdy alarm jest fałszywy); 'ze zdarzeniem' = na >= 5 stacjach. 'doby z >=3 stacjami' = ile dób miało alarm na co najmniej 3 stacjach naraz (tyle widziałby użytkownik jako plamę na mapie).
### wyprzedzenie k=0
- śnieg >= 3 mm: doby bez zdarzenia: 61, stacjodni 3375, fałszywych alarmów 34 (10.1 na 1000 stacjodni); doby z >=3 stacjami: 2 z 61
    doby ze zdarzeniem: 23, zdarzeń 284, trafionych 229 (POD 0.81), fałszywych alarmów na tych dobach 262
- opad >= 10 mm: doby bez zdarzenia: 74, stacjodni 4090, fałszywych alarmów 14 (3.4 na 1000 stacjodni); doby z >=3 stacjami: 2 z 74
    doby ze zdarzeniem: 12, zdarzeń 144, trafionych 129 (POD 0.90), fałszywych alarmów na tych dobach 59
- mróz TMIN <= -10 C: doby bez zdarzenia: 74, stacjodni 4098, fałszywych alarmów 16 (3.9 na 1000 stacjodni); doby z >=3 stacjami: 1 z 74
    doby ze zdarzeniem: 18, zdarzeń 461, trafionych 359 (POD 0.78), fałszywych alarmów na tych dobach 60
- mróz TMIN <= -15 C: doby bez zdarzenia: 84, stacjodni 4644, fałszywych alarmów 5 (1.1 na 1000 stacjodni); doby z >=3 stacjami: 0 z 84
    doby ze zdarzeniem: 8, zdarzeń 97, trafionych 66 (POD 0.68), fałszywych alarmów na tych dobach 22
### wyprzedzenie k=1
- śnieg >= 3 mm: doby bez zdarzenia: 58, stacjodni 3209, fałszywych alarmów 22 (6.9 na 1000 stacjodni); doby z >=3 stacjami: 3 z 58
    doby ze zdarzeniem: 25, zdarzeń 301, trafionych 226 (POD 0.75), fałszywych alarmów na tych dobach 281
- opad >= 10 mm: doby bez zdarzenia: 74, stacjodni 4084, fałszywych alarmów 13 (3.2 na 1000 stacjodni); doby z >=3 stacjami: 2 z 74
    doby ze zdarzeniem: 13, zdarzeń 153, trafionych 120 (POD 0.78), fałszywych alarmów na tych dobach 61
- mróz TMIN <= -10 C: doby bez zdarzenia: 73, stacjodni 4045, fałszywych alarmów 12 (3.0 na 1000 stacjodni); doby z >=3 stacjami: 2 z 73
    doby ze zdarzeniem: 21, zdarzeń 475, trafionych 329 (POD 0.69), fałszywych alarmów na tych dobach 105
- mróz TMIN <= -15 C: doby bez zdarzenia: 85, stacjodni 4696, fałszywych alarmów 18 (3.8 na 1000 stacjodni); doby z >=3 stacjami: 1 z 85
    doby ze zdarzeniem: 8, zdarzeń 88, trafionych 61 (POD 0.69), fałszywych alarmów na tych dobach 34
### wyprzedzenie k=2
- śnieg >= 3 mm: doby bez zdarzenia: 60, stacjodni 3316, fałszywych alarmów 61 (18.4 na 1000 stacjodni); doby z >=3 stacjami: 7 z 60
    doby ze zdarzeniem: 22, zdarzeń 266, trafionych 189 (POD 0.71), fałszywych alarmów na tych dobach 231
- opad >= 10 mm: doby bez zdarzenia: 77, stacjodni 4248, fałszywych alarmów 18 (4.2 na 1000 stacjodni); doby z >=3 stacjami: 2 z 77
    doby ze zdarzeniem: 12, zdarzeń 149, trafionych 95 (POD 0.64), fałszywych alarmów na tych dobach 51
- mróz TMIN <= -10 C: doby bez zdarzenia: 76, stacjodni 4210, fałszywych alarmów 21 (5.0 na 1000 stacjodni); doby z >=3 stacjami: 3 z 76
    doby ze zdarzeniem: 18, zdarzeń 417, trafionych 321 (POD 0.77), fałszywych alarmów na tych dobach 111
- mróz TMIN <= -15 C: doby bez zdarzenia: 84, stacjodni 4645, fałszywych alarmów 2 (0.4 na 1000 stacjodni); doby z >=3 stacjami: 0 z 84
    doby ze zdarzeniem: 8, zdarzeń 83, trafionych 58 (POD 0.70), fałszywych alarmów na tych dobach 57

## 7. Mróz — diagnoza niedoszacowania ogona zimna i test prostej korekty (TMIN, doba 00-24 UTC)
Błąd = obserwacja - prognoza (średnia zespołu min. T powietrza); UJEMNY = w rzeczywistości zimniej niż w prognozie (prognoza za ciepła). Przedziały wg PROGNOZY (wersja użyteczna do korekty; przedziały wg obserwacji zawyżają błąd przez regresję do średniej).
### wyprzedzenie k=0: n=5237
- błąd wg przedziałów prognozy: prog. < -15: n=90, błąd +1.42 C (mediana +1.47) | -15..-10: n=313, błąd -0.23 C (mediana -0.35) | -10..-5: n=690, błąd +0.00 C (mediana -0.11) | -5..0: n=1761, błąd -0.00 C (mediana +0.04) | > 0: n=2383, błąd -0.30 C (mediana -0.26)
- rozrzut zespołu (średnie odch. std) 0.56 C vs RMSE średniej zespołu 1.98 C; dla prognoz <= -5 C: rozrzut 0.74 C vs RMSE 2.49 C
- obserwacja zimniejsza niż WSZYSTKIE 30 członków: 27.6% stacjodni (przy dobrze rozproszonym zespole ~3%); dla prognoz <= -5 C: 26.4%
- błąd na dniach z prognozą <= -5 C wg stacji (n stacji=51): średnia -0.04 C, rozrzut między stacjami (std) 0.93 C
    najmniejszy błąd: ŁEBA -2.5, PIŁA -1.3, ŁÓDŹ -1.2, JELENIA GÓRA -1.1, POZNAŃ-ŁAWICA -1.1
    największy błąd: TERESPOL +0.8, BIELSKO-BIAŁA +1.0, GDAŃSK-ŚWIBNO +1.1, ZIELONA GÓRA +2.1, NOWY SĄCZ +2.2, ZAKOPANE +3.0
    korelacja błędu stacji z szerokością: -0.34, z długością: +0.20
- korekta liniowa po prognozie: MAE 1.48 -> 1.48 C; błąd średni -0.13 -> -0.06 C; średnie przesunięcie dla prognoz <= -10 C: +0.24 C (produkcja: -1.0 C); sigma resztowa ok. 1.98 C
- próg -5 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.86, FAR 0.14, CSI 0.76, fałszywych 153; na dobach bez zdarzenia 7.2 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.92, FAR 0.20, CSI 0.75, fałszywych 256; na dobach bez zdarzenia 12.6 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.86, FAR 0.14, CSI 0.76, fałszywych 154; na dobach bez zdarzenia 7.2 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.96, FAR 0.26, CSI 0.72, fałszywych 384; na dobach bez zdarzenia 23.8 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.92, FAR 0.18, CSI 0.76, fałszywych 230; na dobach bez zdarzenia 10.2 na 1000 stacjodni
- próg -10 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.77, FAR 0.18, CSI 0.66, fałszywych 81; na dobach bez zdarzenia 3.9 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.86, FAR 0.28, CSI 0.65, fałszywych 159; na dobach bez zdarzenia 5.4 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.74, FAR 0.18, CSI 0.64, fałszywych 75; na dobach bez zdarzenia 3.7 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.93, FAR 0.34, CSI 0.63, fałszywych 226; na dobach bez zdarzenia 6.3 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.82, FAR 0.23, CSI 0.65, fałszywych 116; na dobach bez zdarzenia 4.6 na 1000 stacjodni
- próg -15 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.63, FAR 0.29, CSI 0.50, fałszywych 28; na dobach bez zdarzenia 0.9 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.74, FAR 0.46, CSI 0.45, fałszywych 68; na dobach bez zdarzenia 2.2 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.62, FAR 0.27, CSI 0.50, fałszywych 25; na dobach bez zdarzenia 0.9 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.78, FAR 0.51, CSI 0.43, fałszywych 87; na dobach bez zdarzenia 2.6 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.64, FAR 0.37, CSI 0.46, fałszywych 41; na dobach bez zdarzenia 1.3 na 1000 stacjodni
### wyprzedzenie k=1: n=5290
- błąd wg przedziałów prognozy: prog. < -15: n=104, błąd +2.40 C (mediana +2.23) | -15..-10: n=299, błąd +0.72 C (mediana +0.59) | -10..-5: n=728, błąd -0.34 C (mediana -0.32) | -5..0: n=1609, błąd +0.10 C (mediana +0.28) | > 0: n=2550, błąd -0.42 C (mediana -0.25)
- rozrzut zespołu (średnie odch. std) 0.74 C vs RMSE średniej zespołu 2.22 C; dla prognoz <= -5 C: rozrzut 0.96 C vs RMSE 2.94 C
- obserwacja zimniejsza niż WSZYSTKIE 30 członków: 24.3% stacjodni (przy dobrze rozproszonym zespole ~3%); dla prognoz <= -5 C: 24.1%
- błąd na dniach z prognozą <= -5 C wg stacji (n stacji=52): średnia +0.10 C, rozrzut między stacjami (std) 0.94 C
    najmniejszy błąd: ŁEBA -1.8, ŚWINOUJŚCIE -1.4, KOZIENICE -1.0, SUWAŁKI -1.0, JELENIA GÓRA -1.0
    największy błąd: BIELSKO-BIAŁA +1.5, GDAŃSK-ŚWIBNO +1.5, ZIELONA GÓRA +1.7, USTKA +1.7, NOWY SĄCZ +2.2, ZAKOPANE +3.4
    korelacja błędu stacji z szerokością: -0.42, z długością: +0.06
- korekta liniowa po prognozie: MAE 1.68 -> 1.67 C; błąd średni -0.13 -> -0.04 C; średnie przesunięcie dla prognoz <= -10 C: +0.66 C (produkcja: -1.0 C); sigma resztowa ok. 2.22 C
- próg -5 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.86, FAR 0.15, CSI 0.75, fałszywych 171; na dobach bez zdarzenia 13.3 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.92, FAR 0.20, CSI 0.75, fałszywych 267; na dobach bez zdarzenia 24.6 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.86, FAR 0.14, CSI 0.75, fałszywych 164; na dobach bez zdarzenia 13.0 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.95, FAR 0.25, CSI 0.72, fałszywych 373; na dobach bez zdarzenia 40.3 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.91, FAR 0.18, CSI 0.76, fałszywych 228; na dobach bez zdarzenia 18.4 na 1000 stacjodni
- próg -10 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.69, FAR 0.27, CSI 0.55, fałszywych 124; na dobach bez zdarzenia 3.0 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.82, FAR 0.34, CSI 0.57, fałszywych 206; na dobach bez zdarzenia 4.7 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.64, FAR 0.25, CSI 0.53, fałszywych 102; na dobach bez zdarzenia 2.0 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.88, FAR 0.39, CSI 0.56, fałszywych 278; na dobach bez zdarzenia 6.2 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.75, FAR 0.28, CSI 0.58, fałszywych 140; na dobach bez zdarzenia 3.5 na 1000 stacjodni
- próg -15 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.64, FAR 0.50, CSI 0.39, fałszywych 64; na dobach bez zdarzenia 3.8 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.67, FAR 0.59, CSI 0.34, fałszywych 95; na dobach bez zdarzenia 5.1 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.59, FAR 0.45, CSI 0.40, fałszywych 48; na dobach bez zdarzenia 3.4 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.72, FAR 0.61, CSI 0.33, fałszywych 115; na dobach bez zdarzenia 5.7 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.62, FAR 0.50, CSI 0.38, fałszywych 62; na dobach bez zdarzenia 4.3 na 1000 stacjodni
### wyprzedzenie k=2: n=5292
- błąd wg przedziałów prognozy: prog. < -15: n=105, błąd +2.03 C (mediana +2.11) | -15..-10: n=293, błąd +0.81 C (mediana +1.09) | -10..-5: n=599, błąd -0.11 C (mediana -0.06) | -5..0: n=1705, błąd +0.23 C (mediana +0.54) | > 0: n=2590, błąd -0.11 C (mediana -0.08)
- rozrzut zespołu (średnie odch. std) 0.98 C vs RMSE średniej zespołu 2.24 C; dla prognoz <= -5 C: rozrzut 1.33 C vs RMSE 2.93 C
- obserwacja zimniejsza niż WSZYSTKIE 30 członków: 17.1% stacjodni (przy dobrze rozproszonym zespole ~3%); dla prognoz <= -5 C: 18.0%
- błąd na dniach z prognozą <= -5 C wg stacji (n stacji=50): średnia +0.31 C, rozrzut między stacjami (std) 0.92 C
    najmniejszy błąd: JELENIA GÓRA -1.4, ŁÓDŹ -1.1, SZCZECIN -1.0, SŁUBICE -1.0, KOSZALIN -0.8
    największy błąd: ZIELONA GÓRA +1.6, KROSNO +1.6, USTKA +1.7, BIELSKO-BIAŁA +2.0, NOWY SĄCZ +2.6, ZAKOPANE +3.0
    korelacja błędu stacji z szerokością: -0.37, z długością: +0.10
- korekta liniowa po prognozie: MAE 1.75 -> 1.73 C; błąd średni +0.09 -> -0.07 C; średnie przesunięcie dla prognoz <= -10 C: +0.70 C (produkcja: -1.0 C); sigma resztowa ok. 2.25 C
- próg -5 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.84, FAR 0.19, CSI 0.70, fałszywych 205; na dobach bez zdarzenia 16.9 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.89, FAR 0.25, CSI 0.69, fałszywych 304; na dobach bez zdarzenia 28.7 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.83, FAR 0.17, CSI 0.71, fałszywych 170; na dobach bez zdarzenia 13.6 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.93, FAR 0.31, CSI 0.66, fałszywych 428; na dobach bez zdarzenia 48.2 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.86, FAR 0.20, CSI 0.71, fałszywych 224; na dobach bez zdarzenia 20.1 na 1000 stacjodni
- próg -10 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.76, FAR 0.29, CSI 0.58, fałszywych 131; na dobach bez zdarzenia 4.5 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.86, FAR 0.33, CSI 0.60, fałszywych 184; na dobach bez zdarzenia 6.9 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.68, FAR 0.26, CSI 0.55, fałszywych 103; na dobach bez zdarzenia 3.1 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.89, FAR 0.37, CSI 0.59, fałszywych 221; na dobach bez zdarzenia 7.8 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.78, FAR 0.28, CSI 0.60, fałszywych 127; na dobach bez zdarzenia 4.0 na 1000 stacjodni
- próg -15 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.66, FAR 0.56, CSI 0.36, fałszywych 82; na dobach bez zdarzenia 0.4 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.71, FAR 0.62, CSI 0.33, fałszywych 114; na dobach bez zdarzenia 0.9 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.60, FAR 0.51, CSI 0.37, fałszywych 61; na dobach bez zdarzenia 0.2 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.71, FAR 0.64, CSI 0.32, fałszywych 124; na dobach bez zdarzenia 0.9 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.63, FAR 0.54, CSI 0.36, fałszywych 72; na dobach bez zdarzenia 0.4 na 1000 stacjodni

## 8. Śnieg — test skalowania ilości opadu zamarzniętego (wariant D) i progu alarmu
Skala f mnoży opad zamarznięty każdego członka (f=1,0 = obecna produkcja). Zdarzenie = obserwowany opad rodzaju S >= X mm (SMDB). Doby bez zdarzenia = zdarzenie na <= 1 stacji. Uwaga: to ilość WODY (mm), nie centymetry śniegu — przelicznik śnieg:woda jest osobną sprawą.
### wyprzedzenie k=0: n=5249
- stosunek średniej obserwowanego śniegu (mm) do średniej prognozy wg przedziałów prognozy: 0,5-1 mm: n=385, obs/prog. = 0.50 | 1-3 mm: n=607, obs/prog. = 0.56 | 3-6 mm: n=350, obs/prog. = 0.63 | >6 mm: n=203, obs/prog. = 0.69
- próg 3 mm:
    f=1.0, alarm przy P>=30%: POD 0.80, FAR 0.60, CSI 0.36, fałszywych 379; na dobach bez zdarzenia 9.8 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.75, FAR 0.56, CSI 0.38, fałszywych 296; na dobach bez zdarzenia 7.1 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.77, FAR 0.58, CSI 0.37, fałszywych 335; na dobach bez zdarzenia 8.0 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.69, FAR 0.54, CSI 0.38, fałszywych 259; na dobach bez zdarzenia 6.5 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.73, FAR 0.55, CSI 0.39, fałszywych 279; na dobach bez zdarzenia 7.4 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.64, FAR 0.50, CSI 0.39, fałszywych 201; na dobach bez zdarzenia 6.5 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.68, FAR 0.51, CSI 0.40, fałszywych 226; na dobach bez zdarzenia 6.8 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.58, FAR 0.46, CSI 0.39, fałszywych 157; na dobach bez zdarzenia 5.6 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.60, FAR 0.45, CSI 0.40, fałszywych 155; na dobach bez zdarzenia 5.9 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.50, FAR 0.40, CSI 0.37, fałszywych 104; na dobach bez zdarzenia 3.9 na 1000 stacjodni
- próg 5 mm:
    f=1.0, alarm przy P>=30%: POD 0.72, FAR 0.59, CSI 0.35, fałszywych 204; na dobach bez zdarzenia 11.1 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.62, FAR 0.54, CSI 0.36, fałszywych 141; na dobach bez zdarzenia 6.8 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.67, FAR 0.55, CSI 0.37, fałszywych 162; na dobach bez zdarzenia 7.8 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.57, FAR 0.50, CSI 0.37, fałszywych 109; na dobach bez zdarzenia 4.0 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.59, FAR 0.50, CSI 0.37, fałszywych 114; na dobach bez zdarzenia 4.3 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.51, FAR 0.43, CSI 0.37, fałszywych 75; na dobach bez zdarzenia 2.5 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.53, FAR 0.45, CSI 0.37, fałszywych 83; na dobach bez zdarzenia 3.0 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.43, FAR 0.38, CSI 0.34, fałszywych 51; na dobach bez zdarzenia 1.8 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.45, FAR 0.32, CSI 0.37, fałszywych 41; na dobach bez zdarzenia 1.5 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.34, FAR 0.30, CSI 0.29, fałszywych 28; na dobach bez zdarzenia 0.3 na 1000 stacjodni
### wyprzedzenie k=1: n=5304
- stosunek średniej obserwowanego śniegu (mm) do średniej prognozy wg przedziałów prognozy: 0,5-1 mm: n=426, obs/prog. = 0.63 | 1-3 mm: n=707, obs/prog. = 0.68 | 3-6 mm: n=347, obs/prog. = 0.66 | >6 mm: n=163, obs/prog. = 0.69
- próg 3 mm:
    f=1.0, alarm przy P>=30%: POD 0.74, FAR 0.60, CSI 0.35, fałszywych 372; na dobach bez zdarzenia 6.5 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.61, FAR 0.56, CSI 0.34, fałszywych 263; na dobach bez zdarzenia 2.8 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.70, FAR 0.58, CSI 0.36, fałszywych 324; na dobach bez zdarzenia 4.7 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.58, FAR 0.54, CSI 0.35, fałszywych 228; na dobach bez zdarzenia 2.8 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.66, FAR 0.56, CSI 0.36, fałszywych 283; na dobach bez zdarzenia 3.7 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.54, FAR 0.49, CSI 0.36, fałszywych 175; na dobach bez zdarzenia 1.2 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.61, FAR 0.52, CSI 0.37, fałszywych 218; na dobach bez zdarzenia 2.5 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.48, FAR 0.46, CSI 0.34, fałszywych 135; na dobach bez zdarzenia 0.9 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.54, FAR 0.47, CSI 0.36, fałszywych 159; na dobach bez zdarzenia 1.2 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.40, FAR 0.40, CSI 0.32, fałszywych 88; na dobach bez zdarzenia 0.9 na 1000 stacjodni
- próg 5 mm:
    f=1.0, alarm przy P>=30%: POD 0.66, FAR 0.63, CSI 0.32, fałszywych 212; na dobach bez zdarzenia 6.9 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.51, FAR 0.56, CSI 0.31, fałszywych 124; na dobach bez zdarzenia 3.3 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.61, FAR 0.57, CSI 0.34, fałszywych 157; na dobach bez zdarzenia 4.1 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.44, FAR 0.51, CSI 0.30, fałszywych 87; na dobach bez zdarzenia 2.0 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.57, FAR 0.51, CSI 0.36, fałszywych 113; na dobach bez zdarzenia 2.6 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.35, FAR 0.50, CSI 0.26, fałszywych 66; na dobach bez zdarzenia 1.0 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.46, FAR 0.48, CSI 0.32, fałszywych 81; na dobach bez zdarzenia 1.8 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.28, FAR 0.44, CSI 0.23, fałszywych 42; na dobach bez zdarzenia 0.8 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.32, FAR 0.41, CSI 0.26, fałszywych 42; na dobach bez zdarzenia 1.0 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.16, FAR 0.44, CSI 0.14, fałszywych 24; na dobach bez zdarzenia 0.5 na 1000 stacjodni
### wyprzedzenie k=2: n=5303
- stosunek średniej obserwowanego śniegu (mm) do średniej prognozy wg przedziałów prognozy: 0,5-1 mm: n=479, obs/prog. = 0.59 | 1-3 mm: n=786, obs/prog. = 0.68 | 3-6 mm: n=306, obs/prog. = 0.69 | >6 mm: n=131, obs/prog. = 0.68
- próg 3 mm:
    f=1.0, alarm przy P>=30%: POD 0.69, FAR 0.63, CSI 0.32, fałszywych 364; na dobach bez zdarzenia 17.5 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.49, FAR 0.56, CSI 0.30, fałszywych 195; na dobach bez zdarzenia 7.5 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.66, FAR 0.60, CSI 0.33, fałszywych 305; na dobach bez zdarzenia 13.6 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.45, FAR 0.54, CSI 0.30, fałszywych 161; na dobach bez zdarzenia 5.7 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.57, FAR 0.58, CSI 0.32, fałszywych 242; na dobach bez zdarzenia 10.0 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.42, FAR 0.50, CSI 0.29, fałszywych 130; na dobach bez zdarzenia 4.5 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.51, FAR 0.55, CSI 0.31, fałszywych 193; na dobach bez zdarzenia 7.5 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.37, FAR 0.45, CSI 0.28, fałszywych 94; na dobach bez zdarzenia 3.0 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.46, FAR 0.48, CSI 0.32, fałszywych 132; na dobach bez zdarzenia 4.5 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.28, FAR 0.44, CSI 0.23, fałszywych 67; na dobach bez zdarzenia 2.1 na 1000 stacjodni
- próg 5 mm:
    f=1.0, alarm przy P>=30%: POD 0.54, FAR 0.65, CSI 0.27, fałszywych 179; na dobach bez zdarzenia 8.2 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.36, FAR 0.59, CSI 0.24, fałszywych 91; na dobach bez zdarzenia 3.8 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.51, FAR 0.62, CSI 0.28, fałszywych 143; na dobach bez zdarzenia 6.1 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.33, FAR 0.53, CSI 0.24, fałszywych 65; na dobach bez zdarzenia 3.1 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.45, FAR 0.57, CSI 0.28, fałszywych 103; na dobach bez zdarzenia 4.8 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.26, FAR 0.50, CSI 0.21, fałszywych 46; na dobach bez zdarzenia 2.6 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.38, FAR 0.53, CSI 0.27, fałszywych 76; na dobach bez zdarzenia 4.1 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.18, FAR 0.45, CSI 0.15, fałszywych 25; na dobach bez zdarzenia 1.0 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.28, FAR 0.45, CSI 0.23, fałszywych 40; na dobach bez zdarzenia 1.8 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.13, FAR 0.36, CSI 0.12, fałszywych 13; na dobach bez zdarzenia 0.5 na 1000 stacjodni

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
- wg przedziałów prognozy (średnia zespołu): 1-3 cm: n=519, śr. prog. 1.9 cm, śr. obs 0.9 cm (obs/prog. = 0.46) | 3-6 cm: n=269, śr. prog. 4.2 cm, śr. obs 1.1 cm (obs/prog. = 0.27) | 6-10 cm: n=84, śr. prog. 7.7 cm, śr. obs 1.9 cm (obs/prog. = 0.25) | >10 cm: n=33, śr. prog. 13.9 cm, śr. obs 2.1 cm (obs/prog. = 0.15)
- próg 5 cm (zdarzeń 102):
    g=1.0, alarm przy P>=30%: POD 0.29, FAR 0.86, CSI 0.11, fałszywych 179; na dobach bez zdarzenia 29.2 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.23, FAR 0.86, CSI 0.10, fałszywych 140; na dobach bez zdarzenia 22.7 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.20, FAR 0.86, CSI 0.09, fałszywych 123; na dobach bez zdarzenia 20.3 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.15, FAR 0.86, CSI 0.08, fałszywych 92; na dobach bez zdarzenia 14.9 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.10, FAR 0.86, CSI 0.06, fałszywych 63; na dobach bez zdarzenia 10.3 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.08, FAR 0.85, CSI 0.05, fałszywych 46; na dobach bez zdarzenia 7.3 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.07, FAR 0.85, CSI 0.05, fałszywych 40; na dobach bez zdarzenia 6.2 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.05, FAR 0.84, CSI 0.04, fałszywych 26; na dobach bez zdarzenia 3.2 na 1000 stacjodni
- próg 10 cm (zdarzeń 16):
    g=1.0, alarm przy P>=30%: POD 0.06, FAR 0.98, CSI 0.02, fałszywych 46; na dobach bez zdarzenia 8.1 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.06, FAR 0.97, CSI 0.02, fałszywych 30; na dobach bez zdarzenia 4.6 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.06, FAR 0.96, CSI 0.03, fałszywych 23; na dobach bez zdarzenia 3.7 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.06, FAR 0.94, CSI 0.03, fałszywych 15; na dobach bez zdarzenia 2.1 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 10; na dobach bez zdarzenia 1.6 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 8; na dobach bez zdarzenia 1.2 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 6; na dobach bez zdarzenia 0.9 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 3; na dobach bez zdarzenia 0.2 na 1000 stacjodni
### wyprzedzenie k=1: n=4496
- wg przedziałów prognozy (średnia zespołu): 1-3 cm: n=599, śr. prog. 1.8 cm, śr. obs 0.9 cm (obs/prog. = 0.50) | 3-6 cm: n=264, śr. prog. 4.2 cm, śr. obs 1.0 cm (obs/prog. = 0.25) | 6-10 cm: n=69, śr. prog. 7.4 cm, śr. obs 2.2 cm (obs/prog. = 0.30) | >10 cm: n=21, śr. prog. 14.7 cm, śr. obs 2.5 cm (obs/prog. = 0.17)
- próg 5 cm (zdarzeń 128):
    g=1.0, alarm przy P>=30%: POD 0.23, FAR 0.86, CSI 0.10, fałszywych 177; na dobach bez zdarzenia 28.1 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.17, FAR 0.83, CSI 0.09, fałszywych 104; na dobach bez zdarzenia 13.6 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.16, FAR 0.84, CSI 0.09, fałszywych 109; na dobach bez zdarzenia 14.5 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.09, FAR 0.83, CSI 0.06, fałszywych 58; na dobach bez zdarzenia 6.1 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.09, FAR 0.80, CSI 0.06, fałszywych 43; na dobach bez zdarzenia 4.5 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.05, FAR 0.79, CSI 0.05, fałszywych 27; na dobach bez zdarzenia 3.1 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.06, FAR 0.79, CSI 0.05, fałszywych 30; na dobach bez zdarzenia 3.1 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.03, FAR 0.80, CSI 0.03, fałszywych 16; na dobach bez zdarzenia 1.9 na 1000 stacjodni
- próg 10 cm (zdarzeń 28):
    g=1.0, alarm przy P>=30%: POD 0.04, FAR 0.97, CSI 0.02, fałszywych 37; na dobach bez zdarzenia 5.2 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.04, FAR 0.95, CSI 0.02, fałszywych 19; na dobach bez zdarzenia 2.6 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.04, FAR 0.95, CSI 0.02, fałszywych 18; na dobach bez zdarzenia 2.4 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.04, FAR 0.94, CSI 0.02, fałszywych 15; na dobach bez zdarzenia 1.9 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 8; na dobach bez zdarzenia 1.2 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 7; na dobach bez zdarzenia 1.2 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 6; na dobach bez zdarzenia 1.2 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 2; na dobach bez zdarzenia 0.5 na 1000 stacjodni
### wyprzedzenie k=2: n=4551
- wg przedziałów prognozy (średnia zespołu): 1-3 cm: n=656, śr. prog. 1.8 cm, śr. obs 0.8 cm (obs/prog. = 0.45) | 3-6 cm: n=228, śr. prog. 4.2 cm, śr. obs 1.2 cm (obs/prog. = 0.29) | 6-10 cm: n=50, śr. prog. 7.4 cm, śr. obs 1.1 cm (obs/prog. = 0.14) | >10 cm: n=18, śr. prog. 13.1 cm, śr. obs 1.8 cm (obs/prog. = 0.14)
- próg 5 cm (zdarzeń 113):
    g=1.0, alarm przy P>=30%: POD 0.14, FAR 0.91, CSI 0.06, fałszywych 165; na dobach bez zdarzenia 22.9 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.09, FAR 0.89, CSI 0.05, fałszywych 83; na dobach bez zdarzenia 10.7 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.10, FAR 0.91, CSI 0.05, fałszywych 106; na dobach bez zdarzenia 13.3 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.05, FAR 0.89, CSI 0.04, fałszywych 48; na dobach bez zdarzenia 5.9 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.04, FAR 0.90, CSI 0.03, fałszywych 44; na dobach bez zdarzenia 5.9 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.03, FAR 0.88, CSI 0.02, fałszywych 21; na dobach bez zdarzenia 2.4 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.04, FAR 0.84, CSI 0.04, fałszywych 27; na dobach bez zdarzenia 2.4 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.03, FAR 0.82, CSI 0.02, fałszywych 14; na dobach bez zdarzenia 1.9 na 1000 stacjodni
- próg 10 cm (zdarzeń 18):
    g=1.0, alarm przy P>=30%: POD 0.06, FAR 0.97, CSI 0.02, fałszywych 31; na dobach bez zdarzenia 3.4 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.06, FAR 0.94, CSI 0.03, fałszywych 16; na dobach bez zdarzenia 2.0 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.06, FAR 0.95, CSI 0.03, fałszywych 20; na dobach bez zdarzenia 2.3 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 8; na dobach bez zdarzenia 1.6 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 6; na dobach bez zdarzenia 1.1 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 1; na dobach bez zdarzenia 0.2 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 2; na dobach bez zdarzenia 0.2 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 1; na dobach bez zdarzenia 0.2 na 1000 stacjodni

## 11. Mróz — test wygładzenia rozrzutu odtwarzający planowaną zmianę produkcyjną (stałe sigma wg wyprzedzenia)
Sigma całkowita wg wyprzedzenia: {0: 2.35, 1: 2.59, 2: 2.78}. Środek = temperatura członka + korekta produkcyjna -1.0 C. w = waga wygładzenia (0 = obecna produkcja). Doby bez zdarzenia = zdarzenie (TMIN <= próg) na <= 1 stacji. 'fałsz. bez zdarz.' = fałszywe alarmy na 1000 stacjodni z tych dób.
### wyprzedzenie k=0: n=5237, sigma całkowita 2.35 C, średni dodany rozrzut 2.26 C
- próg -5 C (zdarzeń 1135):
    w=0.00 (produkcja): P>=10%: POD 0.94 FAR 0.23 CSI 0.74 fałsz. bez zdarz. 17.0 | P>=20%: POD 0.93 FAR 0.21 CSI 0.75 fałsz. bez zdarz. 15.3 | P>=30%: POD 0.92 FAR 0.20 CSI 0.75 fałsz. bez zdarz. 12.6 | P>=50%: POD 0.91 FAR 0.18 CSI 0.76 fałsz. bez zdarz. 10.2
    w=0.50: P>=10%: POD 0.97 FAR 0.32 CSI 0.67 fałsz. bez zdarz. 45.3 | P>=20%: POD 0.96 FAR 0.26 CSI 0.71 fałsz. bez zdarz. 25.2 | P>=30%: POD 0.95 FAR 0.23 CSI 0.74 fałsz. bez zdarz. 17.0 | P>=50%: POD 0.91 FAR 0.18 CSI 0.76 fałsz. bez zdarz. 9.9
    w=0.75: P>=10%: POD 0.98 FAR 0.41 CSI 0.59 fałsz. bez zdarz. 85.5 | P>=20%: POD 0.97 FAR 0.31 CSI 0.68 fałsz. bez zdarz. 38.5 | P>=30%: POD 0.96 FAR 0.25 CSI 0.72 fałsz. bez zdarz. 22.1 | P>=50%: POD 0.91 FAR 0.18 CSI 0.76 fałsz. bez zdarz. 9.9
    w=1.00: P>=10%: POD 0.99 FAR 0.50 CSI 0.50 fałsz. bez zdarz. 159.4 | P>=20%: POD 0.98 FAR 0.36 CSI 0.63 fałsz. bez zdarz. 61.0 | P>=30%: POD 0.96 FAR 0.28 CSI 0.70 fałsz. bez zdarz. 31.3 | P>=50%: POD 0.91 FAR 0.18 CSI 0.76 fałsz. bez zdarz. 9.5
- próg -10 C (zdarzeń 472):
    w=0.00 (produkcja): P>=10%: POD 0.91 FAR 0.34 CSI 0.62 fałsz. bez zdarz. 6.6 | P>=20%: POD 0.89 FAR 0.30 CSI 0.64 fałsz. bez zdarz. 6.1 | P>=30%: POD 0.86 FAR 0.28 CSI 0.65 fałsz. bez zdarz. 5.4 | P>=50%: POD 0.83 FAR 0.24 CSI 0.65 fałsz. bez zdarz. 4.9
    w=0.50: P>=10%: POD 0.96 FAR 0.41 CSI 0.57 fałsz. bez zdarz. 9.3 | P>=20%: POD 0.93 FAR 0.35 CSI 0.62 fałsz. bez zdarz. 6.6 | P>=30%: POD 0.90 FAR 0.31 CSI 0.64 fałsz. bez zdarz. 5.9 | P>=50%: POD 0.82 FAR 0.24 CSI 0.65 fałsz. bez zdarz. 4.9
    w=0.75: P>=10%: POD 0.98 FAR 0.46 CSI 0.53 fałsz. bez zdarz. 12.9 | P>=20%: POD 0.95 FAR 0.39 CSI 0.59 fałsz. bez zdarz. 8.5 | P>=30%: POD 0.93 FAR 0.33 CSI 0.63 fałsz. bez zdarz. 6.3 | P>=50%: POD 0.82 FAR 0.24 CSI 0.65 fałsz. bez zdarz. 4.9
    w=1.00: P>=10%: POD 0.99 FAR 0.51 CSI 0.49 fałsz. bez zdarz. 19.8 | P>=20%: POD 0.97 FAR 0.43 CSI 0.56 fałsz. bez zdarz. 10.5 | P>=30%: POD 0.94 FAR 0.36 CSI 0.61 fałsz. bez zdarz. 7.1 | P>=50%: POD 0.83 FAR 0.24 CSI 0.66 fałsz. bez zdarz. 4.6
- próg -15 C (zdarzeń 108):
    w=0.00 (produkcja): P>=10%: POD 0.77 FAR 0.52 CSI 0.42 fałsz. bez zdarz. 3.2 | P>=20%: POD 0.74 FAR 0.48 CSI 0.44 fałsz. bez zdarz. 2.6 | P>=30%: POD 0.74 FAR 0.46 CSI 0.45 fałsz. bez zdarz. 2.2 | P>=50%: POD 0.69 FAR 0.38 CSI 0.48 fałsz. bez zdarz. 1.5
    w=0.50: P>=10%: POD 0.81 FAR 0.58 CSI 0.38 fałsz. bez zdarz. 4.7 | P>=20%: POD 0.78 FAR 0.53 CSI 0.41 fałsz. bez zdarz. 3.2 | P>=30%: POD 0.77 FAR 0.48 CSI 0.45 fałsz. bez zdarz. 2.4 | P>=50%: POD 0.69 FAR 0.38 CSI 0.48 fałsz. bez zdarz. 1.5
    w=0.75: P>=10%: POD 0.84 FAR 0.63 CSI 0.35 fałsz. bez zdarz. 6.9 | P>=20%: POD 0.81 FAR 0.56 CSI 0.40 fałsz. bez zdarz. 4.1 | P>=30%: POD 0.78 FAR 0.50 CSI 0.44 fałsz. bez zdarz. 2.6 | P>=50%: POD 0.69 FAR 0.38 CSI 0.48 fałsz. bez zdarz. 1.5
    w=1.00: P>=10%: POD 0.91 FAR 0.67 CSI 0.32 fałsz. bez zdarz. 9.3 | P>=20%: POD 0.82 FAR 0.59 CSI 0.38 fałsz. bez zdarz. 5.4 | P>=30%: POD 0.78 FAR 0.54 CSI 0.40 fałsz. bez zdarz. 3.0 | P>=50%: POD 0.69 FAR 0.38 CSI 0.48 fałsz. bez zdarz. 1.5
### wyprzedzenie k=1: n=5290, sigma całkowita 2.59 C, średni dodany rozrzut 2.45 C
- próg -5 C (zdarzeń 1159):
    w=0.00 (produkcja): P>=10%: POD 0.93 FAR 0.23 CSI 0.73 fałsz. bez zdarz. 34.4 | P>=20%: POD 0.93 FAR 0.21 CSI 0.74 fałsz. bez zdarz. 26.9 | P>=30%: POD 0.92 FAR 0.20 CSI 0.75 fałsz. bez zdarz. 24.6 | P>=50%: POD 0.91 FAR 0.17 CSI 0.76 fałsz. bez zdarz. 17.2
    w=0.50: P>=10%: POD 0.96 FAR 0.33 CSI 0.66 fałsz. bez zdarz. 75.2 | P>=20%: POD 0.95 FAR 0.26 CSI 0.71 fałsz. bez zdarz. 44.1 | P>=30%: POD 0.94 FAR 0.21 CSI 0.75 fałsz. bez zdarz. 27.2 | P>=50%: POD 0.91 FAR 0.17 CSI 0.76 fałsz. bez zdarz. 17.5
    w=0.75: P>=10%: POD 0.98 FAR 0.39 CSI 0.60 fałsz. bez zdarz. 115.5 | P>=20%: POD 0.96 FAR 0.31 CSI 0.67 fałsz. bez zdarz. 66.6 | P>=30%: POD 0.94 FAR 0.24 CSI 0.72 fałsz. bez zdarz. 36.7 | P>=50%: POD 0.91 FAR 0.17 CSI 0.76 fałsz. bez zdarz. 17.5
    w=1.00: P>=10%: POD 0.98 FAR 0.50 CSI 0.50 fałsz. bez zdarz. 210.8 | P>=20%: POD 0.97 FAR 0.36 CSI 0.63 fałsz. bez zdarz. 90.9 | P>=30%: POD 0.95 FAR 0.27 CSI 0.70 fałsz. bez zdarz. 47.4 | P>=50%: POD 0.91 FAR 0.17 CSI 0.76 fałsz. bez zdarz. 17.5
- próg -10 C (zdarzeń 484):
    w=0.00 (produkcja): P>=10%: POD 0.86 FAR 0.39 CSI 0.55 fałsz. bez zdarz. 7.4 | P>=20%: POD 0.84 FAR 0.36 CSI 0.57 fałsz. bez zdarz. 6.2 | P>=30%: POD 0.82 FAR 0.34 CSI 0.57 fałsz. bez zdarz. 4.7 | P>=50%: POD 0.78 FAR 0.30 CSI 0.58 fałsz. bez zdarz. 4.0
    w=0.50: P>=10%: POD 0.93 FAR 0.45 CSI 0.53 fałsz. bez zdarz. 9.9 | P>=20%: POD 0.89 FAR 0.40 CSI 0.56 fałsz. bez zdarz. 6.9 | P>=30%: POD 0.85 FAR 0.36 CSI 0.57 fałsz. bez zdarz. 5.2 | P>=50%: POD 0.79 FAR 0.30 CSI 0.59 fałsz. bez zdarz. 4.0
    w=0.75: P>=10%: POD 0.95 FAR 0.50 CSI 0.49 fałsz. bez zdarz. 13.3 | P>=20%: POD 0.92 FAR 0.42 CSI 0.55 fałsz. bez zdarz. 8.2 | P>=30%: POD 0.88 FAR 0.39 CSI 0.57 fałsz. bez zdarz. 5.7 | P>=50%: POD 0.78 FAR 0.30 CSI 0.59 fałsz. bez zdarz. 3.7
    w=1.00: P>=10%: POD 0.98 FAR 0.54 CSI 0.46 fałsz. bez zdarz. 21.0 | P>=20%: POD 0.94 FAR 0.46 CSI 0.52 fałsz. bez zdarz. 10.6 | P>=30%: POD 0.89 FAR 0.41 CSI 0.55 fałsz. bez zdarz. 6.9 | P>=50%: POD 0.78 FAR 0.30 CSI 0.59 fałsz. bez zdarz. 3.7
- próg -15 C (zdarzeń 100):
    w=0.00 (produkcja): P>=10%: POD 0.75 FAR 0.64 CSI 0.32 fałsz. bez zdarz. 7.7 | P>=20%: POD 0.72 FAR 0.61 CSI 0.34 fałsz. bez zdarz. 5.7 | P>=30%: POD 0.67 FAR 0.59 CSI 0.34 fałsz. bez zdarz. 5.1 | P>=50%: POD 0.66 FAR 0.54 CSI 0.37 fałsz. bez zdarz. 4.9
    w=0.50: P>=10%: POD 0.78 FAR 0.68 CSI 0.29 fałsz. bez zdarz. 10.4 | P>=20%: POD 0.75 FAR 0.64 CSI 0.32 fałsz. bez zdarz. 7.0 | P>=30%: POD 0.72 FAR 0.60 CSI 0.35 fałsz. bez zdarz. 5.5 | P>=50%: POD 0.66 FAR 0.54 CSI 0.37 fałsz. bez zdarz. 4.7
    w=0.75: P>=10%: POD 0.80 FAR 0.71 CSI 0.27 fałsz. bez zdarz. 12.1 | P>=20%: POD 0.77 FAR 0.66 CSI 0.31 fałsz. bez zdarz. 8.9 | P>=30%: POD 0.72 FAR 0.61 CSI 0.34 fałsz. bez zdarz. 5.7 | P>=50%: POD 0.66 FAR 0.54 CSI 0.37 fałsz. bez zdarz. 4.7
    w=1.00: P>=10%: POD 0.82 FAR 0.75 CSI 0.24 fałsz. bez zdarz. 16.2 | P>=20%: POD 0.79 FAR 0.68 CSI 0.30 fałsz. bez zdarz. 10.0 | P>=30%: POD 0.74 FAR 0.63 CSI 0.32 fałsz. bez zdarz. 6.8 | P>=50%: POD 0.66 FAR 0.54 CSI 0.37 fałsz. bez zdarz. 4.9
### wyprzedzenie k=2: n=5292, sigma całkowita 2.78 C, średni dodany rozrzut 2.55 C
- próg -5 C (zdarzeń 1036):
    w=0.00 (produkcja): P>=10%: POD 0.92 FAR 0.32 CSI 0.65 fałsz. bez zdarz. 51.8 | P>=20%: POD 0.90 FAR 0.28 CSI 0.67 fałsz. bez zdarz. 36.7 | P>=30%: POD 0.89 FAR 0.25 CSI 0.69 fałsz. bez zdarz. 28.7 | P>=50%: POD 0.87 FAR 0.21 CSI 0.71 fałsz. bez zdarz. 20.1
    w=0.50: P>=10%: POD 0.96 FAR 0.41 CSI 0.58 fałsz. bez zdarz. 97.3 | P>=20%: POD 0.94 FAR 0.33 CSI 0.64 fałsz. bez zdarz. 57.7 | P>=30%: POD 0.91 FAR 0.28 CSI 0.67 fałsz. bez zdarz. 37.0 | P>=50%: POD 0.87 FAR 0.21 CSI 0.71 fałsz. bez zdarz. 20.4
    w=0.75: P>=10%: POD 0.98 FAR 0.49 CSI 0.51 fałsz. bez zdarz. 154.7 | P>=20%: POD 0.96 FAR 0.38 CSI 0.60 fałsz. bez zdarz. 82.8 | P>=30%: POD 0.93 FAR 0.31 CSI 0.66 fałsz. bez zdarz. 47.3 | P>=50%: POD 0.87 FAR 0.21 CSI 0.71 fałsz. bez zdarz. 20.4
    w=1.00: P>=10%: POD 0.99 FAR 0.57 CSI 0.43 fałsz. bez zdarz. 253.0 | P>=20%: POD 0.97 FAR 0.43 CSI 0.56 fałsz. bez zdarz. 113.9 | P>=30%: POD 0.94 FAR 0.34 CSI 0.63 fałsz. bez zdarz. 60.7 | P>=50%: POD 0.87 FAR 0.21 CSI 0.71 fałsz. bez zdarz. 20.7
- próg -10 C (zdarzeń 427):
    w=0.00 (produkcja): P>=10%: POD 0.89 FAR 0.41 CSI 0.55 fałsz. bez zdarz. 12.1 | P>=20%: POD 0.89 FAR 0.36 CSI 0.59 fałsz. bez zdarz. 9.0 | P>=30%: POD 0.86 FAR 0.33 CSI 0.60 fałsz. bez zdarz. 6.9 | P>=50%: POD 0.81 FAR 0.29 CSI 0.61 fałsz. bez zdarz. 4.5
    w=0.50: P>=10%: POD 0.94 FAR 0.46 CSI 0.52 fałsz. bez zdarz. 18.5 | P>=20%: POD 0.91 FAR 0.40 CSI 0.57 fałsz. bez zdarz. 10.5 | P>=30%: POD 0.89 FAR 0.35 CSI 0.60 fałsz. bez zdarz. 7.6 | P>=50%: POD 0.82 FAR 0.29 CSI 0.61 fałsz. bez zdarz. 4.5
    w=0.75: P>=10%: POD 0.96 FAR 0.51 CSI 0.48 fałsz. bez zdarz. 24.2 | P>=20%: POD 0.93 FAR 0.43 CSI 0.55 fałsz. bez zdarz. 14.5 | P>=30%: POD 0.89 FAR 0.36 CSI 0.59 fałsz. bez zdarz. 7.6 | P>=50%: POD 0.82 FAR 0.29 CSI 0.62 fałsz. bez zdarz. 4.8
    w=1.00: P>=10%: POD 0.99 FAR 0.55 CSI 0.44 fałsz. bez zdarz. 36.3 | P>=20%: POD 0.95 FAR 0.46 CSI 0.52 fałsz. bez zdarz. 17.1 | P>=30%: POD 0.92 FAR 0.39 CSI 0.58 fałsz. bez zdarz. 9.5 | P>=50%: POD 0.82 FAR 0.29 CSI 0.62 fałsz. bez zdarz. 4.8
- próg -15 C (zdarzeń 98):
    w=0.00 (produkcja): P>=10%: POD 0.76 FAR 0.68 CSI 0.29 fałsz. bez zdarz. 2.6 | P>=20%: POD 0.71 FAR 0.66 CSI 0.30 fałsz. bez zdarz. 1.5 | P>=30%: POD 0.71 FAR 0.62 CSI 0.33 fałsz. bez zdarz. 0.9 | P>=50%: POD 0.66 FAR 0.56 CSI 0.36 fałsz. bez zdarz. 0.4
    w=0.50: P>=10%: POD 0.77 FAR 0.72 CSI 0.26 fałsz. bez zdarz. 3.7 | P>=20%: POD 0.73 FAR 0.67 CSI 0.29 fałsz. bez zdarz. 2.6 | P>=30%: POD 0.71 FAR 0.63 CSI 0.33 fałsz. bez zdarz. 0.9 | P>=50%: POD 0.67 FAR 0.55 CSI 0.37 fałsz. bez zdarz. 0.4
    w=0.75: P>=10%: POD 0.82 FAR 0.73 CSI 0.25 fałsz. bez zdarz. 4.5 | P>=20%: POD 0.76 FAR 0.68 CSI 0.29 fałsz. bez zdarz. 2.6 | P>=30%: POD 0.71 FAR 0.64 CSI 0.31 fałsz. bez zdarz. 0.9 | P>=50%: POD 0.67 FAR 0.55 CSI 0.37 fałsz. bez zdarz. 0.4
    w=1.00: P>=10%: POD 0.86 FAR 0.76 CSI 0.23 fałsz. bez zdarz. 6.2 | P>=20%: POD 0.79 FAR 0.70 CSI 0.28 fałsz. bez zdarz. 3.0 | P>=30%: POD 0.73 FAR 0.65 CSI 0.31 fałsz. bez zdarz. 1.9 | P>=50%: POD 0.66 FAR 0.56 CSI 0.36 fałsz. bez zdarz. 0.6

## 8. Oceny probabilistyczne (CRPS, Brier — niższe = lepiej; wektory zapisane do porównania modeli parami)
### wyprzedzenie k=0
- tmin_crps_k0: n=5237, średnia 1.2365
- tmin_le5_brier_k0: n=5237, średnia 0.0498
- tmin_le10_brier_k0: n=5237, średnia 0.0308
- tmin_le15_brier_k0: n=5237, średnia 0.0110
- precip_crps_k0: n=5249, średnia 0.6093
- precip_ge1_brier_k0: n=5249, średnia 0.1018
- precip_ge5_brier_k0: n=5249, średnia 0.0373
- precip_ge10_brier_k0: n=5249, średnia 0.0136
- snow_ge1_brier_k0: n=5249, średnia 0.0981
- snow_ge3_brier_k0: n=5249, średnia 0.0566
### wyprzedzenie k=1
- tmin_crps_k1: n=5290, średnia 1.3729
- tmin_le5_brier_k1: n=5290, średnia 0.0505
- tmin_le10_brier_k1: n=5290, średnia 0.0418
- tmin_le15_brier_k1: n=5290, średnia 0.0136
- precip_crps_k1: n=5304, średnia 0.6681
- precip_ge1_brier_k1: n=5304, średnia 0.1131
- precip_ge5_brier_k1: n=5304, średnia 0.0440
- precip_ge10_brier_k1: n=5304, średnia 0.0168
- snow_ge1_brier_k1: n=5304, średnia 0.0935
- snow_ge3_brier_k1: n=5304, średnia 0.0541
### wyprzedzenie k=2
- tmin_crps_k2: n=5292, średnia 1.3701
- tmin_le5_brier_k2: n=5292, średnia 0.0522
- tmin_le10_brier_k2: n=5292, średnia 0.0323
- tmin_le15_brier_k2: n=5292, średnia 0.0131
- precip_crps_k2: n=5303, średnia 0.7247
- precip_ge1_brier_k2: n=5303, średnia 0.1221
- precip_ge5_brier_k2: n=5303, średnia 0.0480
- precip_ge10_brier_k2: n=5303, średnia 0.0187
- snow_ge1_brier_k2: n=5303, średnia 0.0875
- snow_ge3_brier_k2: n=5303, średnia 0.0475

