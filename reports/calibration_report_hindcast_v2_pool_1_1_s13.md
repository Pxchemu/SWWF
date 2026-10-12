# Kalibracja SWWF na obserwacjach IMGW — 2026-10-12 14:47
hindcast: /home/runner/work/SWWF/SWWF/hindcast_v2 (96 przebiegów 00Z z 30 członkami, okien na przebieg: [13]); obs: imgw_dobowe_2020-11-01_2026-03-31_mc-1-2-3-11-12.csv.gz (52851 stacjodni)
zespół POŁĄCZONY: hindcast_v2 x1 + hindcast_ifs x1 = 81 członków (waga modeli ~ 1*A : 1*B); korekta temperatury modelu A przed złączeniem: -1.30 C; średnia różnica T końca okna A - B (przed korektą): +0.74 C
Próba jest dobrana pod zdarzenia i dni spokojne (nie klimatologiczna) — FAR i odsetki zdarzeń z sekcji 1-5 dotyczą próby mieszanej; sekcja 6 rozdziela doby bez zdarzenia i ze zdarzeniem.

## 0. Kontrola okna doby IMGW (k=0)
- opad SMDB: start  0 UTC: r=0.835 | start  6 UTC: r=0.883 | start 12 UTC: r=0.818 | start 18 UTC: r=0.658  (najwyższe r = okno zgodne z IMGW)
- TMIN: start  0 UTC: r=0.925 | start  6 UTC: r=0.851 | start 12 UTC: r=0.833 | start 18 UTC: r=0.807  (najwyższe r = okno zgodne z IMGW)

## 1. Opad dobowy (okno 06->06 UTC)
### wyprzedzenie k=0: n=5249 stacjodni, mokrych (>=1 mm) 1338
- średnia obs 1.29 mm, GEFS+IFS 1.72 mm; korelacja sqrt = 0.883
- dni mokre: GEFS+IFS/obs = 1.11; obs > max zespołu: 3.0% dni mokrych
- P(opad>=1 mm): P=0: n=2199, zaszło 0% | P=0-20%: n=836, zaszło 4% | P=20-40%: n=293, zaszło 12% | P=40-60%: n=250, zaszło 22% | P=60-80%: n=292, zaszło 36% | P=80-100%: n=1379, zaszło 80%
- P(opad>=5 mm): P=0: n=3630, zaszło 0% | P=0-20%: n=843, zaszło 4% | P=20-40%: n=204, zaszło 16% | P=40-60%: n=120, zaszło 28% | P=60-80%: n=114, zaszło 47% | P=80-100%: n=338, zaszło 80%
- P(opad>=10 mm): P=0: n=4532, zaszło 0% | P=0-20%: n=440, zaszło 4% | P=20-40%: n=79, zaszło 27% | P=40-60%: n=62, zaszło 44% | P=60-80%: n=55, zaszło 56% | P=80-100%: n=81, zaszło 93%
### wyprzedzenie k=1: n=5304 stacjodni, mokrych (>=1 mm) 1496
- średnia obs 1.43 mm, GEFS+IFS 1.77 mm; korelacja sqrt = 0.850
- dni mokre: GEFS+IFS/obs = 0.99; obs > max zespołu: 2.6% dni mokrych
- P(opad>=1 mm): P=0: n=1543, zaszło 0% | P=0-20%: n=1156, zaszło 4% | P=20-40%: n=486, zaszło 16% | P=40-60%: n=419, zaszło 31% | P=60-80%: n=446, zaszło 49% | P=80-100%: n=1254, zaszło 81%
- P(opad>=5 mm): P=0: n=3154, zaszło 0% | P=0-20%: n=1285, zaszło 4% | P=20-40%: n=291, zaszło 20% | P=40-60%: n=170, zaszło 35% | P=60-80%: n=179, zaszło 63% | P=80-100%: n=225, zaszło 81%
- P(opad>=10 mm): P=0: n=4257, zaszło 0% | P=0-20%: n=766, zaszło 5% | P=20-40%: n=105, zaszło 27% | P=40-60%: n=88, zaszło 49% | P=60-80%: n=51, zaszło 73% | P=80-100%: n=37, zaszło 95%
### wyprzedzenie k=2: n=5303 stacjodni, mokrych (>=1 mm) 1438
- średnia obs 1.37 mm, GEFS+IFS 1.63 mm; korelacja sqrt = 0.781
- dni mokre: GEFS+IFS/obs = 0.84; obs > max zespołu: 2.9% dni mokrych
- P(opad>=1 mm): P=0: n=1100, zaszło 0% | P=0-20%: n=1486, zaszło 4% | P=20-40%: n=624, zaszło 18% | P=40-60%: n=552, zaszło 32% | P=60-80%: n=590, zaszło 54% | P=80-100%: n=951, zaszło 80%
- P(opad>=5 mm): P=0: n=2632, zaszło 0% | P=0-20%: n=1847, zaszło 5% | P=20-40%: n=367, zaszło 24% | P=40-60%: n=210, zaszło 47% | P=60-80%: n=164, zaszło 66% | P=80-100%: n=83, zaszło 78%
- P(opad>=10 mm): P=0: n=3931, zaszło 0% | P=0-20%: n=1129, zaszło 4% | P=20-40%: n=147, zaszło 43% | P=40-60%: n=64, zaszło 50% | P=60-80%: n=27, zaszło 85% | P=80-100%: n=5, zaszło 100%

## 2. Śnieg — metody rozpoznawania fazy opadu (okno 06->06 UTC)
Zdarzenie obserwowane: opad rodzaju S (śnieg) o sumie >= X mm. Prognoza: P(opad zamarznięty >= X mm) wg metody. Kolumna 'deszcz->śnieg' = odsetek dni z obserwowanym DESZCZEM >=3 mm, w których metoda daje P(śnieg>=3 mm) >= 30% (fałszywy śnieg).
(brak pól wilgotności w danych albo zespół z IFS (IFS nie ma wilgotności) — warianty z mokrym termometrem pominięte)
### wyprzedzenie k=0: n=5249; obs śnieg >=1 mm: 607, >=3 mm: 315, >=5 mm: 194; deszcz >=3 mm: 330
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A dawna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.56 | 0.56 | 0.32 | 0.76 | 0.50 | 7% |
| D obecna (produkcja): T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.82 | 0.61 | 0.36 | 0.94 | 0.56 | 27% |
| G: CPOFP (gdy ważny), inaczej D | 0.78 | 0.59 | 0.37 | 0.92 | 0.54 | 22% |
| E1: T zimniejsza z 2 próbek (1@0C->0@2C), progi o 1 C niżej niż D | 0.65 | 0.59 | 0.34 | 0.84 | 0.52 | 12% |
| E2: T zimniejsza z 2 próbek (1@0.5C->0@2.5C), progi o 0.5 C niżej niż D | 0.75 | 0.60 | 0.35 | 0.90 | 0.54 | 20% |
- wiarygodność P(śnieg>=3 mm), metoda 'D' (produkcyjna): P=0: n=3836, zaszło 0% | P=0-20%: n=645, zaszło 5% | P=20-40%: n=181, zaszło 14% | P=40-60%: n=141, zaszło 24% | P=60-80%: n=120, zaszło 30% | P=80-100%: n=326, zaszło 53%
### wyprzedzenie k=1: n=5304; obs śnieg >=1 mm: 650, >=3 mm: 336, >=5 mm: 191; deszcz >=3 mm: 402
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A dawna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.47 | 0.57 | 0.29 | 0.74 | 0.50 | 6% |
| D obecna (produkcja): T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.74 | 0.61 | 0.34 | 0.91 | 0.56 | 21% |
| G: CPOFP (gdy ważny), inaczej D | 0.68 | 0.59 | 0.34 | 0.89 | 0.54 | 18% |
| E1: T zimniejsza z 2 próbek (1@0C->0@2C), progi o 1 C niżej niż D | 0.57 | 0.59 | 0.31 | 0.79 | 0.52 | 8% |
| E2: T zimniejsza z 2 próbek (1@0.5C->0@2.5C), progi o 0.5 C niżej niż D | 0.66 | 0.60 | 0.33 | 0.86 | 0.54 | 14% |
- wiarygodność P(śnieg>=3 mm), metoda 'D' (produkcyjna): P=0: n=3493, zaszło 0% | P=0-20%: n=1040, zaszło 5% | P=20-40%: n=251, zaszło 20% | P=40-60%: n=161, zaszło 27% | P=60-80%: n=164, zaszło 43% | P=80-100%: n=195, zaszło 55%
### wyprzedzenie k=2: n=5303; obs śnieg >=1 mm: 612, >=3 mm: 308, >=5 mm: 176; deszcz >=3 mm: 419
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A dawna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.43 | 0.60 | 0.26 | 0.73 | 0.54 | 4% |
| D obecna (produkcja): T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.68 | 0.64 | 0.31 | 0.91 | 0.59 | 14% |
| G: CPOFP (gdy ważny), inaczej D | 0.61 | 0.61 | 0.32 | 0.89 | 0.57 | 10% |
| E1: T zimniejsza z 2 próbek (1@0C->0@2C), progi o 1 C niżej niż D | 0.51 | 0.64 | 0.27 | 0.81 | 0.55 | 6% |
| E2: T zimniejsza z 2 próbek (1@0.5C->0@2.5C), progi o 0.5 C niżej niż D | 0.61 | 0.63 | 0.30 | 0.86 | 0.57 | 10% |
- wiarygodność P(śnieg>=3 mm), metoda 'D' (produkcyjna): P=0: n=3061, zaszło 0% | P=0-20%: n=1457, zaszło 4% | P=20-40%: n=348, zaszło 19% | P=40-60%: n=215, zaszło 34% | P=60-80%: n=130, zaszło 38% | P=80-100%: n=92, zaszło 61%

## 3. Mróz — temperatura powietrza vs odczuwalna (okno doby kalendarzowej 00-24 UTC; obserwacja = TMIN powietrza)
Uwaga: IMGW mierzy tylko temperaturę powietrza, więc odczuwalnej NIE da się zweryfikować wprost; poniżej sprawdzamy, jak daleko od powietrza jest każda wersja i czy 'odczuwalna' nie robi fałszywych alarmów względem realnego mrozu.
### wyprzedzenie k=0: n=5237
- prognoza min. T powietrza: błąd średni +0.08 C, MAE 1.55 C; w mroźnych dniach (obs <= -10 C): błąd +1.58 C
- próg -5 C (obs zdarzeń 1135), powietrze: P>=30%: traf. 996, fałsz. 198, przegap. 139 (POD 0.88, FAR 0.17, CSI 0.75)
- próg -10 C (obs zdarzeń 472), powietrze: P>=30%: traf. 367, fałsz. 92, przegap. 105 (POD 0.78, FAR 0.20, CSI 0.65)
- próg -15 C (obs zdarzeń 108), powietrze: P>=30%: traf. 68, fałsz. 36, przegap. 40 (POD 0.63, FAR 0.35, CSI 0.47)
- próg -20 C (obs zdarzeń 23), powietrze: P>=30%: traf. 21, fałsz. 10, przegap. 2 (POD 0.91, FAR 0.32, CSI 0.64)
### wyprzedzenie k=1: n=5290
- prognoza min. T powietrza: błąd średni +0.10 C, MAE 1.70 C; w mroźnych dniach (obs <= -10 C): błąd +1.57 C
- próg -5 C (obs zdarzeń 1159), powietrze: P>=30%: traf. 1014, fałsz. 194, przegap. 145 (POD 0.87, FAR 0.16, CSI 0.75)
- próg -10 C (obs zdarzeń 484), powietrze: P>=30%: traf. 340, fałsz. 136, przegap. 144 (POD 0.70, FAR 0.29, CSI 0.55)
- próg -15 C (obs zdarzeń 100), powietrze: P>=30%: traf. 62, fałsz. 66, przegap. 38 (POD 0.62, FAR 0.52, CSI 0.37)
- próg -20 C (obs zdarzeń 17), powietrze: P>=30%: traf. 15, fałsz. 14, przegap. 2 (POD 0.88, FAR 0.48, CSI 0.48)
### wyprzedzenie k=2: n=5292
- prognoza min. T powietrza: błąd średni -0.16 C, MAE 1.75 C; w mroźnych dniach (obs <= -10 C): błąd +1.42 C
- próg -5 C (obs zdarzeń 1036), powietrze: P>=30%: traf. 883, fałsz. 211, przegap. 153 (POD 0.85, FAR 0.19, CSI 0.71)
- próg -10 C (obs zdarzeń 427), powietrze: P>=30%: traf. 320, fałsz. 141, przegap. 107 (POD 0.75, FAR 0.31, CSI 0.56)
- próg -15 C (obs zdarzeń 98), powietrze: P>=30%: traf. 63, fałsz. 66, przegap. 35 (POD 0.64, FAR 0.51, CSI 0.38)
- próg -20 C (obs zdarzeń 13), powietrze: P>=30%: traf. 12, fałsz. 13, przegap. 1 (POD 0.92, FAR 0.52, CSI 0.46)

## 6. Fałszywe alarmy na dobach bez zdarzenia i trafienia na dobach ze zdarzeniem
Alarm = P(zdarzenia) >= 30% wg zespołu. Doba 'bez zdarzenia' = zdarzenie na <= 1 stacji (wtedy każdy alarm jest fałszywy); 'ze zdarzeniem' = na >= 5 stacjach. 'doby z >=3 stacjami' = ile dób miało alarm na co najmniej 3 stacjach naraz (tyle widziałby użytkownik jako plamę na mapie).
### wyprzedzenie k=0
- śnieg >= 3 mm: doby bez zdarzenia: 61, stacjodni 3375, fałszywych alarmów 37 (11.0 na 1000 stacjodni); doby z >=3 stacjami: 2 z 61
    doby ze zdarzeniem: 23, zdarzeń 284, trafionych 234 (POD 0.82), fałszywych alarmów na tych dobach 283
- opad >= 10 mm: doby bez zdarzenia: 74, stacjodni 4090, fałszywych alarmów 15 (3.7 na 1000 stacjodni); doby z >=3 stacjami: 3 z 74
    doby ze zdarzeniem: 12, zdarzeń 144, trafionych 130 (POD 0.90), fałszywych alarmów na tych dobach 59
- mróz TMIN <= -10 C: doby bez zdarzenia: 74, stacjodni 4098, fałszywych alarmów 18 (4.4 na 1000 stacjodni); doby z >=3 stacjami: 2 z 74
    doby ze zdarzeniem: 18, zdarzeń 461, trafionych 363 (POD 0.79), fałszywych alarmów na tych dobach 70
- mróz TMIN <= -15 C: doby bez zdarzenia: 84, stacjodni 4644, fałszywych alarmów 6 (1.3 na 1000 stacjodni); doby z >=3 stacjami: 0 z 84
    doby ze zdarzeniem: 8, zdarzeń 97, trafionych 66 (POD 0.68), fałszywych alarmów na tych dobach 29
### wyprzedzenie k=1
- śnieg >= 3 mm: doby bez zdarzenia: 58, stacjodni 3209, fałszywych alarmów 23 (7.2 na 1000 stacjodni); doby z >=3 stacjami: 4 z 58
    doby ze zdarzeniem: 25, zdarzeń 301, trafionych 226 (POD 0.75), fałszywych alarmów na tych dobach 290
- opad >= 10 mm: doby bez zdarzenia: 74, stacjodni 4084, fałszywych alarmów 12 (2.9 na 1000 stacjodni); doby z >=3 stacjami: 3 z 74
    doby ze zdarzeniem: 13, zdarzeń 153, trafionych 117 (POD 0.76), fałszywych alarmów na tych dobach 60
- mróz TMIN <= -10 C: doby bez zdarzenia: 73, stacjodni 4045, fałszywych alarmów 13 (3.2 na 1000 stacjodni); doby z >=3 stacjami: 2 z 73
    doby ze zdarzeniem: 21, zdarzeń 475, trafionych 338 (POD 0.71), fałszywych alarmów na tych dobach 115
- mróz TMIN <= -15 C: doby bez zdarzenia: 85, stacjodni 4696, fałszywych alarmów 18 (3.8 na 1000 stacjodni); doby z >=3 stacjami: 1 z 85
    doby ze zdarzeniem: 8, zdarzeń 88, trafionych 59 (POD 0.67), fałszywych alarmów na tych dobach 37
### wyprzedzenie k=2
- śnieg >= 3 mm: doby bez zdarzenia: 60, stacjodni 3316, fałszywych alarmów 63 (19.0 na 1000 stacjodni); doby z >=3 stacjami: 7 z 60
    doby ze zdarzeniem: 22, zdarzeń 266, trafionych 185 (POD 0.70), fałszywych alarmów na tych dobach 230
- opad >= 10 mm: doby bez zdarzenia: 77, stacjodni 4248, fałszywych alarmów 17 (4.0 na 1000 stacjodni); doby z >=3 stacjami: 2 z 77
    doby ze zdarzeniem: 12, zdarzeń 149, trafionych 90 (POD 0.60), fałszywych alarmów na tych dobach 38
- mróz TMIN <= -10 C: doby bez zdarzenia: 76, stacjodni 4210, fałszywych alarmów 20 (4.8 na 1000 stacjodni); doby z >=3 stacjami: 2 z 76
    doby ze zdarzeniem: 18, zdarzeń 417, trafionych 313 (POD 0.75), fałszywych alarmów na tych dobach 120
- mróz TMIN <= -15 C: doby bez zdarzenia: 84, stacjodni 4645, fałszywych alarmów 2 (0.4 na 1000 stacjodni); doby z >=3 stacjami: 0 z 84
    doby ze zdarzeniem: 8, zdarzeń 83, trafionych 57 (POD 0.69), fałszywych alarmów na tych dobach 46

## 7. Mróz — diagnoza niedoszacowania ogona zimna i test prostej korekty (TMIN, doba 00-24 UTC)
Błąd = obserwacja - prognoza (średnia zespołu min. T powietrza); UJEMNY = w rzeczywistości zimniej niż w prognozie (prognoza za ciepła). Przedziały wg PROGNOZY (wersja użyteczna do korekty; przedziały wg obserwacji zawyżają błąd przez regresję do średniej).
### wyprzedzenie k=0: n=5237
- błąd wg przedziałów prognozy: prog. < -15: n=79, błąd +0.50 C (mediana +0.46) | -15..-10: n=283, błąd -0.34 C (mediana -0.15) | -10..-5: n=753, błąd -0.19 C (mediana -0.20) | -5..0: n=1809, błąd +0.23 C (mediana +0.42) | > 0: n=2313, błąd -0.28 C (mediana -0.12)
- rozrzut zespołu (średnie odch. std) 0.85 C vs RMSE średniej zespołu 2.04 C; dla prognoz <= -5 C: rozrzut 1.11 C vs RMSE 2.57 C
- obserwacja zimniejsza niż WSZYSTKIE 30 członków: 21.0% stacjodni (przy dobrze rozproszonym zespole ~3%); dla prognoz <= -5 C: 23.5%
- błąd na dniach z prognozą <= -5 C wg stacji (n stacji=50): średnia -0.25 C, rozrzut między stacjami (std) 0.91 C
    najmniejszy błąd: JELENIA GÓRA -1.7, KOSZALIN -1.6, PIŁA -1.6, LESZNO -1.5, ŁÓDŹ -1.5
    największy błąd: GDAŃSK-ŚWIBNO +0.9, KROSNO +1.1, BIELSKO-BIAŁA +1.1, ZIELONA GÓRA +1.4, NOWY SĄCZ +2.2, ZAKOPANE +2.5
    korelacja błędu stacji z szerokością: -0.45, z długością: +0.28
- korekta liniowa po prognozie: MAE 1.55 -> 1.56 C; błąd średni -0.08 -> -0.09 C; średnie przesunięcie dla prognoz <= -10 C: -0.03 C (produkcja: -1.0 C); sigma resztowa ok. 2.04 C
- próg -5 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.88, FAR 0.17, CSI 0.75, fałszywych 198; na dobach bez zdarzenia 10.6 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.93, FAR 0.25, CSI 0.71, fałszywych 352; na dobach bez zdarzenia 22.1 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.88, FAR 0.17, CSI 0.75, fałszywych 199; na dobach bez zdarzenia 10.6 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.96, FAR 0.29, CSI 0.69, fałszywych 435; na dobach bez zdarzenia 30.7 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.92, FAR 0.21, CSI 0.74, fałszywych 268; na dobach bez zdarzenia 12.6 na 1000 stacjodni
- próg -10 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.78, FAR 0.20, CSI 0.65, fałszywych 92; na dobach bez zdarzenia 4.4 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.87, FAR 0.31, CSI 0.63, fałszywych 180; na dobach bez zdarzenia 6.6 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.78, FAR 0.20, CSI 0.65, fałszywych 93; na dobach bez zdarzenia 4.4 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.91, FAR 0.34, CSI 0.62, fałszywych 222; na dobach bez zdarzenia 7.6 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.81, FAR 0.25, CSI 0.64, fałszywych 126; na dobach bez zdarzenia 5.1 na 1000 stacjodni
- próg -15 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.63, FAR 0.35, CSI 0.47, fałszywych 36; na dobach bez zdarzenia 1.1 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.72, FAR 0.49, CSI 0.42, fałszywych 76; na dobach bez zdarzenia 2.2 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.64, FAR 0.35, CSI 0.48, fałszywych 37; na dobach bez zdarzenia 1.1 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.75, FAR 0.51, CSI 0.42, fałszywych 83; na dobach bez zdarzenia 2.4 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.68, FAR 0.41, CSI 0.46, fałszywych 51; na dobach bez zdarzenia 1.3 na 1000 stacjodni
### wyprzedzenie k=1: n=5290
- błąd wg przedziałów prognozy: prog. < -15: n=91, błąd +1.52 C (mediana +1.36) | -15..-10: n=270, błąd +0.67 C (mediana +0.59) | -10..-5: n=760, błąd -0.51 C (mediana -0.51) | -5..0: n=1716, błąd +0.22 C (mediana +0.51) | > 0: n=2453, błąd -0.35 C (mediana -0.20)
- rozrzut zespołu (średnie odch. std) 0.96 C vs RMSE średniej zespołu 2.22 C; dla prognoz <= -5 C: rozrzut 1.27 C vs RMSE 2.93 C
- obserwacja zimniejsza niż WSZYSTKIE 30 członków: 18.2% stacjodni (przy dobrze rozproszonym zespole ~3%); dla prognoz <= -5 C: 20.7%
- błąd na dniach z prognozą <= -5 C wg stacji (n stacji=52): średnia -0.11 C, rozrzut między stacjami (std) 0.95 C
    najmniejszy błąd: ŁEBA -2.1, JELENIA GÓRA -1.7, BIAŁYSTOK -1.4, KOZIENICE -1.2, SZCZECIN -1.1
    największy błąd: LESKO +1.2, HEL +1.3, KROSNO +1.4, BIELSKO-BIAŁA +1.5, NOWY SĄCZ +2.2, ZAKOPANE +2.7
    korelacja błędu stacji z szerokością: -0.41, z długością: +0.11
- korekta liniowa po prognozie: MAE 1.70 -> 1.71 C; błąd średni -0.10 -> -0.10 C; średnie przesunięcie dla prognoz <= -10 C: +0.26 C (produkcja: -1.0 C); sigma resztowa ok. 2.23 C
- próg -5 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.87, FAR 0.16, CSI 0.75, fałszywych 194; na dobach bez zdarzenia 13.6 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.93, FAR 0.21, CSI 0.74, fałszywych 286; na dobach bez zdarzenia 26.9 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.87, FAR 0.16, CSI 0.75, fałszywych 187; na dobach bez zdarzenia 13.0 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.95, FAR 0.27, CSI 0.70, fałszywych 404; na dobach bez zdarzenia 46.5 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.91, FAR 0.18, CSI 0.76, fałszywych 238; na dobach bez zdarzenia 17.8 na 1000 stacjodni
- próg -10 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.70, FAR 0.29, CSI 0.55, fałszywych 136; na dobach bez zdarzenia 3.2 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.83, FAR 0.36, CSI 0.56, fałszywych 229; na dobach bez zdarzenia 5.9 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.67, FAR 0.28, CSI 0.53, fałszywych 124; na dobach bez zdarzenia 3.0 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.87, FAR 0.39, CSI 0.56, fałszywych 265; na dobach bez zdarzenia 6.4 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.74, FAR 0.30, CSI 0.56, fałszywych 156; na dobach bez zdarzenia 3.7 na 1000 stacjodni
- próg -15 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.62, FAR 0.52, CSI 0.37, fałszywych 66; na dobach bez zdarzenia 3.8 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.68, FAR 0.59, CSI 0.35, fałszywych 97; na dobach bez zdarzenia 5.3 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.61, FAR 0.49, CSI 0.39, fałszywych 58; na dobach bez zdarzenia 3.6 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.70, FAR 0.61, CSI 0.34, fałszywych 108; na dobach bez zdarzenia 6.2 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.63, FAR 0.52, CSI 0.38, fałszywych 67; na dobach bez zdarzenia 3.8 na 1000 stacjodni
### wyprzedzenie k=2: n=5292
- błąd wg przedziałów prognozy: prog. < -15: n=86, błąd +1.28 C (mediana +1.29) | -15..-10: n=278, błąd +0.89 C (mediana +1.15) | -10..-5: n=617, błąd -0.47 C (mediana -0.46) | -5..0: n=1846, błąd +0.36 C (mediana +0.73) | > 0: n=2465, błąd +0.04 C (mediana +0.12)
- rozrzut zespołu (średnie odch. std) 1.19 C vs RMSE średniej zespołu 2.24 C; dla prognoz <= -5 C: rozrzut 1.61 C vs RMSE 2.95 C
- obserwacja zimniejsza niż WSZYSTKIE 30 członków: 11.8% stacjodni (przy dobrze rozproszonym zespole ~3%); dla prognoz <= -5 C: 16.1%
- błąd na dniach z prognozą <= -5 C wg stacji (n stacji=52): średnia +0.00 C, rozrzut między stacjami (std) 0.98 C
    najmniejszy błąd: JELENIA GÓRA -2.4, SŁUBICE -1.5, ŁÓDŹ -1.4, ŁEBA -1.1, KOZIENICE -1.1
    największy błąd: GDAŃSK-ŚWIBNO +1.4, BIELSKO-BIAŁA +1.5, KROSNO +1.7, HEL +1.8, NOWY SĄCZ +2.4, ZAKOPANE +2.5
    korelacja błędu stacji z szerokością: -0.27, z długością: +0.18
- korekta liniowa po prognozie: MAE 1.75 -> 1.74 C; błąd średni +0.16 -> -0.11 C; średnie przesunięcie dla prognoz <= -10 C: +0.22 C (produkcja: -1.0 C); sigma resztowa ok. 2.25 C
- próg -5 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.85, FAR 0.19, CSI 0.71, fałszywych 211; na dobach bez zdarzenia 17.5 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.91, FAR 0.26, CSI 0.69, fałszywych 335; na dobach bez zdarzenia 33.7 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.83, FAR 0.18, CSI 0.71, fałszywych 184; na dobach bez zdarzenia 14.5 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.94, FAR 0.32, CSI 0.65, fałszywych 458; na dobach bez zdarzenia 54.7 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.87, FAR 0.20, CSI 0.72, fałszywych 224; na dobach bez zdarzenia 18.6 na 1000 stacjodni
- próg -10 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.75, FAR 0.31, CSI 0.56, fałszywych 141; na dobach bez zdarzenia 4.0 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.84, FAR 0.35, CSI 0.58, fałszywych 193; na dobach bez zdarzenia 6.4 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.71, FAR 0.31, CSI 0.54, fałszywych 133; na dobach bez zdarzenia 3.8 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.87, FAR 0.36, CSI 0.58, fałszywych 212; na dobach bez zdarzenia 7.6 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.76, FAR 0.31, CSI 0.57, fałszywych 144; na dobach bez zdarzenia 4.0 na 1000 stacjodni
- próg -15 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.64, FAR 0.51, CSI 0.38, fałszywych 66; na dobach bez zdarzenia 0.4 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.68, FAR 0.61, CSI 0.33, fałszywych 105; na dobach bez zdarzenia 0.9 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.61, FAR 0.50, CSI 0.38, fałszywych 60; na dobach bez zdarzenia 0.4 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.69, FAR 0.62, CSI 0.33, fałszywych 111; na dobach bez zdarzenia 0.9 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.64, FAR 0.52, CSI 0.38, fałszywych 68; na dobach bez zdarzenia 0.4 na 1000 stacjodni

## 8. Śnieg — test skalowania ilości opadu zamarzniętego (wariant D) i progu alarmu
Skala f mnoży opad zamarznięty każdego członka (f=1,0 = obecna produkcja). Zdarzenie = obserwowany opad rodzaju S >= X mm (SMDB). Doby bez zdarzenia = zdarzenie na <= 1 stacji. Uwaga: to ilość WODY (mm), nie centymetry śniegu — przelicznik śnieg:woda jest osobną sprawą.
### wyprzedzenie k=0: n=5249
- stosunek średniej obserwowanego śniegu (mm) do średniej prognozy wg przedziałów prognozy: 0,5-1 mm: n=356, obs/prog. = 0.45 | 1-3 mm: n=607, obs/prog. = 0.59 | 3-6 mm: n=329, obs/prog. = 0.62 | >6 mm: n=183, obs/prog. = 0.71
- próg 3 mm:
    f=1.0, alarm przy P>=30%: POD 0.82, FAR 0.61, CSI 0.36, fałszywych 405; na dobach bez zdarzenia 10.7 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.72, FAR 0.55, CSI 0.38, fałszywych 282; na dobach bez zdarzenia 7.7 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.78, FAR 0.59, CSI 0.37, fałszywych 354; na dobach bez zdarzenia 9.2 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.68, FAR 0.52, CSI 0.39, fałszywych 233; na dobach bez zdarzenia 6.8 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.75, FAR 0.55, CSI 0.39, fałszywych 293; na dobach bez zdarzenia 8.6 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.63, FAR 0.50, CSI 0.39, fałszywych 195; na dobach bez zdarzenia 6.5 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.70, FAR 0.51, CSI 0.40, fałszywych 230; na dobach bez zdarzenia 7.7 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.57, FAR 0.45, CSI 0.39, fałszywych 148; na dobach bez zdarzenia 5.9 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.62, FAR 0.47, CSI 0.40, fałszywych 175; na dobach bez zdarzenia 6.8 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.50, FAR 0.38, CSI 0.38, fałszywych 98; na dobach bez zdarzenia 3.6 na 1000 stacjodni
- próg 5 mm:
    f=1.0, alarm przy P>=30%: POD 0.73, FAR 0.62, CSI 0.33, fałszywych 228; na dobach bez zdarzenia 13.1 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.61, FAR 0.53, CSI 0.36, fałszywych 136; na dobach bez zdarzenia 6.8 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.69, FAR 0.55, CSI 0.38, fałszywych 163; na dobach bez zdarzenia 8.8 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.55, FAR 0.50, CSI 0.36, fałszywych 105; na dobach bez zdarzenia 4.0 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.63, FAR 0.50, CSI 0.38, fałszywych 124; na dobach bez zdarzenia 5.8 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.49, FAR 0.44, CSI 0.36, fałszywych 75; na dobach bez zdarzenia 2.8 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.54, FAR 0.44, CSI 0.38, fałszywych 82; na dobach bez zdarzenia 3.5 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.42, FAR 0.37, CSI 0.34, fałszywych 48; na dobach bez zdarzenia 1.5 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.44, FAR 0.33, CSI 0.36, fałszywych 42; na dobach bez zdarzenia 1.3 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.31, FAR 0.26, CSI 0.28, fałszywych 21; na dobach bez zdarzenia 0.3 na 1000 stacjodni
### wyprzedzenie k=1: n=5304
- stosunek średniej obserwowanego śniegu (mm) do średniej prognozy wg przedziałów prognozy: 0,5-1 mm: n=399, obs/prog. = 0.55 | 1-3 mm: n=697, obs/prog. = 0.68 | 3-6 mm: n=353, obs/prog. = 0.73 | >6 mm: n=149, obs/prog. = 0.70
- próg 3 mm:
    f=1.0, alarm przy P>=30%: POD 0.74, FAR 0.61, CSI 0.34, fałszywych 385; na dobach bez zdarzenia 6.9 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.59, FAR 0.55, CSI 0.34, fałszywych 243; na dobach bez zdarzenia 2.2 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.70, FAR 0.58, CSI 0.35, fałszywych 326; na dobach bez zdarzenia 4.7 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.56, FAR 0.52, CSI 0.35, fałszywych 202; na dobach bez zdarzenia 1.9 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.65, FAR 0.56, CSI 0.36, fałszywych 272; na dobach bez zdarzenia 2.5 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.52, FAR 0.47, CSI 0.36, fałszywych 152; na dobach bez zdarzenia 0.9 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.61, FAR 0.51, CSI 0.37, fałszywych 217; na dobach bez zdarzenia 2.2 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.45, FAR 0.42, CSI 0.34, fałszywych 109; na dobach bez zdarzenia 0.9 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.54, FAR 0.45, CSI 0.37, fałszywych 147; na dobach bez zdarzenia 1.2 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.35, FAR 0.38, CSI 0.29, fałszywych 72; na dobach bez zdarzenia 0.9 na 1000 stacjodni
- próg 5 mm:
    f=1.0, alarm przy P>=30%: POD 0.65, FAR 0.62, CSI 0.32, fałszywych 202; na dobach bez zdarzenia 6.6 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.46, FAR 0.54, CSI 0.29, fałszywych 104; na dobach bez zdarzenia 2.8 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.59, FAR 0.58, CSI 0.33, fałszywych 155; na dobach bez zdarzenia 5.6 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.38, FAR 0.52, CSI 0.27, fałszywych 79; na dobach bez zdarzenia 1.8 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.53, FAR 0.51, CSI 0.34, fałszywych 106; na dobach bez zdarzenia 3.1 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.33, FAR 0.47, CSI 0.25, fałszywych 57; na dobach bez zdarzenia 1.3 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.42, FAR 0.48, CSI 0.30, fałszywych 76; na dobach bez zdarzenia 2.0 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.23, FAR 0.44, CSI 0.19, fałszywych 34; na dobach bez zdarzenia 0.5 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.31, FAR 0.41, CSI 0.26, fałszywych 41; na dobach bez zdarzenia 1.3 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.15, FAR 0.33, CSI 0.14, fałszywych 14; na dobach bez zdarzenia 0.3 na 1000 stacjodni
### wyprzedzenie k=2: n=5303
- stosunek średniej obserwowanego śniegu (mm) do średniej prognozy wg przedziałów prognozy: 0,5-1 mm: n=468, obs/prog. = 0.55 | 1-3 mm: n=798, obs/prog. = 0.71 | 3-6 mm: n=291, obs/prog. = 0.75 | >6 mm: n=103, obs/prog. = 0.73
- próg 3 mm:
    f=1.0, alarm przy P>=30%: POD 0.68, FAR 0.64, CSI 0.31, fałszywych 366; na dobach bez zdarzenia 18.1 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.45, FAR 0.53, CSI 0.30, fałszywych 159; na dobach bez zdarzenia 6.9 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.63, FAR 0.61, CSI 0.32, fałszywych 303; na dobach bez zdarzenia 14.8 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.40, FAR 0.53, CSI 0.27, fałszywych 137; na dobach bez zdarzenia 5.7 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.58, FAR 0.57, CSI 0.33, fałszywych 242; na dobach bez zdarzenia 10.3 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.35, FAR 0.51, CSI 0.25, fałszywych 113; na dobach bez zdarzenia 4.8 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.52, FAR 0.52, CSI 0.33, fałszywych 175; na dobach bez zdarzenia 6.6 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.32, FAR 0.45, CSI 0.25, fałszywych 79; na dobach bez zdarzenia 2.7 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.44, FAR 0.47, CSI 0.32, fałszywych 120; na dobach bez zdarzenia 4.2 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.26, FAR 0.41, CSI 0.22, fałszywych 57; na dobach bez zdarzenia 1.5 na 1000 stacjodni
- próg 5 mm:
    f=1.0, alarm przy P>=30%: POD 0.52, FAR 0.64, CSI 0.27, fałszywych 164; na dobach bez zdarzenia 7.9 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.32, FAR 0.59, CSI 0.22, fałszywych 81; na dobach bez zdarzenia 3.6 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.47, FAR 0.61, CSI 0.27, fałszywych 129; na dobach bez zdarzenia 5.9 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.27, FAR 0.55, CSI 0.20, fałszywych 57; na dobach bez zdarzenia 2.8 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.40, FAR 0.60, CSI 0.25, fałszywych 103; na dobach bez zdarzenia 5.4 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.21, FAR 0.45, CSI 0.18, fałszywych 30; na dobach bez zdarzenia 1.3 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.34, FAR 0.53, CSI 0.25, fałszywych 68; na dobach bez zdarzenia 3.6 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.12, FAR 0.41, CSI 0.12, fałszywych 15; na dobach bez zdarzenia 0.8 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.25, FAR 0.46, CSI 0.21, fałszywych 37; na dobach bez zdarzenia 1.5 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.09, FAR 0.33, CSI 0.09, fałszywych 8; na dobach bez zdarzenia 0.3 na 1000 stacjodni

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
- wg przedziałów prognozy (średnia zespołu): 1-3 cm: n=523, śr. prog. 1.8 cm, śr. obs 0.7 cm (obs/prog. = 0.38) | 3-6 cm: n=259, śr. prog. 4.2 cm, śr. obs 1.5 cm (obs/prog. = 0.35) | 6-10 cm: n=83, śr. prog. 7.6 cm, śr. obs 2.0 cm (obs/prog. = 0.27) | >10 cm: n=29, śr. prog. 13.4 cm, śr. obs 2.6 cm (obs/prog. = 0.19)
- próg 5 cm (zdarzeń 102):
    g=1.0, alarm przy P>=30%: POD 0.33, FAR 0.85, CSI 0.12, fałszywych 192; na dobach bez zdarzenia 31.6 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.25, FAR 0.85, CSI 0.10, fałszywych 140; na dobach bez zdarzenia 22.2 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.23, FAR 0.85, CSI 0.10, fałszywych 127; na dobach bez zdarzenia 19.5 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.18, FAR 0.83, CSI 0.10, fałszywych 86; na dobach bez zdarzenia 13.8 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.14, FAR 0.82, CSI 0.08, fałszywych 64; na dobach bez zdarzenia 10.0 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.10, FAR 0.82, CSI 0.07, fałszywych 45; na dobach bez zdarzenia 7.0 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.10, FAR 0.81, CSI 0.07, fałszywych 42; na dobach bez zdarzenia 6.2 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.06, FAR 0.81, CSI 0.05, fałszywych 26; na dobach bez zdarzenia 4.1 na 1000 stacjodni
- próg 10 cm (zdarzeń 16):
    g=1.0, alarm przy P>=30%: POD 0.06, FAR 0.98, CSI 0.01, fałszywych 51; na dobach bez zdarzenia 9.0 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.06, FAR 0.97, CSI 0.02, fałszywych 31; na dobach bez zdarzenia 5.1 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.06, FAR 0.95, CSI 0.03, fałszywych 21; na dobach bez zdarzenia 3.5 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.06, FAR 0.93, CSI 0.03, fałszywych 13; na dobach bez zdarzenia 1.9 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 9; na dobach bez zdarzenia 1.4 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 7; na dobach bez zdarzenia 0.9 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 4; na dobach bez zdarzenia 0.5 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 1; na dobach bez zdarzenia 0.2 na 1000 stacjodni
### wyprzedzenie k=1: n=4496
- wg przedziałów prognozy (średnia zespołu): 1-3 cm: n=597, śr. prog. 1.8 cm, śr. obs 0.8 cm (obs/prog. = 0.47) | 3-6 cm: n=261, śr. prog. 4.2 cm, śr. obs 1.0 cm (obs/prog. = 0.25) | 6-10 cm: n=66, śr. prog. 7.5 cm, śr. obs 2.3 cm (obs/prog. = 0.31) | >10 cm: n=21, śr. prog. 12.8 cm, śr. obs 2.7 cm (obs/prog. = 0.21)
- próg 5 cm (zdarzeń 128):
    g=1.0, alarm przy P>=30%: POD 0.25, FAR 0.85, CSI 0.10, fałszywych 182; na dobach bez zdarzenia 25.9 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.17, FAR 0.81, CSI 0.10, fałszywych 93; na dobach bez zdarzenia 11.7 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.17, FAR 0.82, CSI 0.10, fałszywych 103; na dobach bez zdarzenia 13.6 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.11, FAR 0.78, CSI 0.08, fałszywych 51; na dobach bez zdarzenia 5.3 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.10, FAR 0.77, CSI 0.08, fałszywych 44; na dobach bez zdarzenia 5.3 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.07, FAR 0.74, CSI 0.06, fałszywych 25; na dobach bez zdarzenia 2.5 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.08, FAR 0.76, CSI 0.06, fałszywych 31; na dobach bez zdarzenia 3.3 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.04, FAR 0.71, CSI 0.04, fałszywych 12; na dobach bez zdarzenia 1.9 na 1000 stacjodni
- próg 10 cm (zdarzeń 28):
    g=1.0, alarm przy P>=30%: POD 0.07, FAR 0.95, CSI 0.03, fałszywych 39; na dobach bez zdarzenia 5.7 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.04, FAR 0.94, CSI 0.02, fałszywych 16; na dobach bez zdarzenia 2.4 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.04, FAR 0.95, CSI 0.02, fałszywych 21; na dobach bez zdarzenia 2.6 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.04, FAR 0.90, CSI 0.03, fałszywych 9; na dobach bez zdarzenia 1.4 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 7; na dobach bez zdarzenia 1.2 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 4; na dobach bez zdarzenia 0.7 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 3; na dobach bez zdarzenia 0.7 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.00, FAR 0.00, CSI 0.00, fałszywych 0; na dobach bez zdarzenia 0.0 na 1000 stacjodni
### wyprzedzenie k=2: n=4551
- wg przedziałów prognozy (średnia zespołu): 1-3 cm: n=670, śr. prog. 1.8 cm, śr. obs 0.7 cm (obs/prog. = 0.40) | 3-6 cm: n=213, śr. prog. 4.2 cm, śr. obs 1.1 cm (obs/prog. = 0.26) | 6-10 cm: n=48, śr. prog. 7.6 cm, śr. obs 2.1 cm (obs/prog. = 0.28)
- próg 5 cm (zdarzeń 113):
    g=1.0, alarm przy P>=30%: POD 0.16, FAR 0.89, CSI 0.07, fałszywych 151; na dobach bez zdarzenia 20.5 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.09, FAR 0.88, CSI 0.05, fałszywych 70; na dobach bez zdarzenia 7.7 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.11, FAR 0.88, CSI 0.06, fałszywych 92; na dobach bez zdarzenia 11.5 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.07, FAR 0.80, CSI 0.06, fałszywych 32; na dobach bez zdarzenia 4.3 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.07, FAR 0.84, CSI 0.05, fałszywych 41; na dobach bez zdarzenia 5.6 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.04, FAR 0.73, CSI 0.03, fałszywych 11; na dobach bez zdarzenia 1.6 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.06, FAR 0.75, CSI 0.05, fałszywych 21; na dobach bez zdarzenia 2.1 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.01, FAR 0.88, CSI 0.01, fałszywych 7; na dobach bez zdarzenia 0.8 na 1000 stacjodni
- próg 10 cm (zdarzeń 18):
    g=1.0, alarm przy P>=30%: POD 0.06, FAR 0.96, CSI 0.02, fałszywych 27; na dobach bez zdarzenia 3.2 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 8; na dobach bez zdarzenia 1.1 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 13; na dobach bez zdarzenia 1.8 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 2; na dobach bez zdarzenia 0.5 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 3; na dobach bez zdarzenia 0.5 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 1; na dobach bez zdarzenia 0.2 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 1; na dobach bez zdarzenia 0.2 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.00, FAR 0.00, CSI 0.00, fałszywych 0; na dobach bez zdarzenia 0.0 na 1000 stacjodni

## 11. Mróz — test wygładzenia rozrzutu odtwarzający planowaną zmianę produkcyjną (stałe sigma wg wyprzedzenia)
Sigma całkowita wg wyprzedzenia: {0: 2.35, 1: 2.59, 2: 2.78}. Środek = temperatura członka + korekta produkcyjna -1.0 C. w = waga wygładzenia (0 = obecna produkcja). Doby bez zdarzenia = zdarzenie (TMIN <= próg) na <= 1 stacji. 'fałsz. bez zdarz.' = fałszywe alarmy na 1000 stacjodni z tych dób.
### wyprzedzenie k=0: n=5237, sigma całkowita 2.35 C, średni dodany rozrzut 2.13 C
- próg -5 C (zdarzeń 1135):
    w=0.00 (produkcja): P>=10%: POD 0.95 FAR 0.29 CSI 0.68 fałsz. bez zdarz. 35.1 | P>=20%: POD 0.94 FAR 0.27 CSI 0.69 fałsz. bez zdarz. 29.0 | P>=30%: POD 0.93 FAR 0.25 CSI 0.71 fałsz. bez zdarz. 22.1 | P>=50%: POD 0.91 FAR 0.19 CSI 0.75 fałsz. bez zdarz. 11.2
    w=0.50: P>=10%: POD 0.98 FAR 0.37 CSI 0.62 fałsz. bez zdarz. 69.8 | P>=20%: POD 0.96 FAR 0.30 CSI 0.68 fałsz. bez zdarz. 35.1 | P>=30%: POD 0.94 FAR 0.26 CSI 0.71 fałsz. bez zdarz. 22.5 | P>=50%: POD 0.91 FAR 0.20 CSI 0.74 fałsz. bez zdarz. 12.3
    w=0.75: P>=10%: POD 0.99 FAR 0.44 CSI 0.56 fałsz. bez zdarz. 109.0 | P>=20%: POD 0.97 FAR 0.34 CSI 0.64 fałsz. bez zdarz. 54.5 | P>=30%: POD 0.95 FAR 0.28 CSI 0.70 fałsz. bez zdarz. 27.6 | P>=50%: POD 0.91 FAR 0.20 CSI 0.74 fałsz. bez zdarz. 12.3
    w=1.00: P>=10%: POD 0.99 FAR 0.52 CSI 0.48 fałsz. bez zdarz. 182.6 | P>=20%: POD 0.98 FAR 0.39 CSI 0.60 fałsz. bez zdarz. 77.3 | P>=30%: POD 0.96 FAR 0.30 CSI 0.68 fałsz. bez zdarz. 37.8 | P>=50%: POD 0.91 FAR 0.20 CSI 0.74 fałsz. bez zdarz. 11.9
- próg -10 C (zdarzeń 472):
    w=0.00 (produkcja): P>=10%: POD 0.92 FAR 0.36 CSI 0.60 fałsz. bez zdarz. 9.8 | P>=20%: POD 0.90 FAR 0.33 CSI 0.62 fałsz. bez zdarz. 8.3 | P>=30%: POD 0.87 FAR 0.31 CSI 0.63 fałsz. bez zdarz. 6.6 | P>=50%: POD 0.80 FAR 0.24 CSI 0.64 fałsz. bez zdarz. 4.9
    w=0.50: P>=10%: POD 0.96 FAR 0.42 CSI 0.56 fałsz. bez zdarz. 12.0 | P>=20%: POD 0.92 FAR 0.37 CSI 0.60 fałsz. bez zdarz. 9.3 | P>=30%: POD 0.89 FAR 0.32 CSI 0.63 fałsz. bez zdarz. 7.1 | P>=50%: POD 0.80 FAR 0.23 CSI 0.64 fałsz. bez zdarz. 4.6
    w=0.75: P>=10%: POD 0.96 FAR 0.48 CSI 0.51 fałsz. bez zdarz. 16.1 | P>=20%: POD 0.94 FAR 0.40 CSI 0.58 fałsz. bez zdarz. 11.0 | P>=30%: POD 0.91 FAR 0.33 CSI 0.63 fałsz. bez zdarz. 7.6 | P>=50%: POD 0.79 FAR 0.24 CSI 0.64 fałsz. bez zdarz. 4.4
    w=1.00: P>=10%: POD 0.99 FAR 0.51 CSI 0.49 fałsz. bez zdarz. 21.0 | P>=20%: POD 0.96 FAR 0.43 CSI 0.56 fałsz. bez zdarz. 12.2 | P>=30%: POD 0.92 FAR 0.35 CSI 0.61 fałsz. bez zdarz. 7.8 | P>=50%: POD 0.80 FAR 0.23 CSI 0.64 fałsz. bez zdarz. 4.4
- próg -15 C (zdarzeń 108):
    w=0.00 (produkcja): P>=10%: POD 0.78 FAR 0.54 CSI 0.40 fałsz. bez zdarz. 3.4 | P>=20%: POD 0.76 FAR 0.53 CSI 0.41 fałsz. bez zdarz. 2.6 | P>=30%: POD 0.72 FAR 0.49 CSI 0.42 fałsz. bez zdarz. 2.2 | P>=50%: POD 0.66 FAR 0.38 CSI 0.47 fałsz. bez zdarz. 1.3
    w=0.50: P>=10%: POD 0.81 FAR 0.58 CSI 0.38 fałsz. bez zdarz. 4.5 | P>=20%: POD 0.77 FAR 0.54 CSI 0.40 fałsz. bez zdarz. 2.8 | P>=30%: POD 0.75 FAR 0.49 CSI 0.43 fałsz. bez zdarz. 2.4 | P>=50%: POD 0.66 FAR 0.37 CSI 0.48 fałsz. bez zdarz. 1.1
    w=0.75: P>=10%: POD 0.81 FAR 0.62 CSI 0.35 fałsz. bez zdarz. 5.2 | P>=20%: POD 0.78 FAR 0.57 CSI 0.38 fałsz. bez zdarz. 3.2 | P>=30%: POD 0.75 FAR 0.51 CSI 0.42 fałsz. bez zdarz. 2.4 | P>=50%: POD 0.66 FAR 0.36 CSI 0.48 fałsz. bez zdarz. 1.1
    w=1.00: P>=10%: POD 0.81 FAR 0.66 CSI 0.32 fałsz. bez zdarz. 6.0 | P>=20%: POD 0.79 FAR 0.58 CSI 0.38 fałsz. bez zdarz. 3.4 | P>=30%: POD 0.76 FAR 0.52 CSI 0.42 fałsz. bez zdarz. 2.4 | P>=50%: POD 0.65 FAR 0.37 CSI 0.47 fałsz. bez zdarz. 1.1
### wyprzedzenie k=1: n=5290, sigma całkowita 2.59 C, średni dodany rozrzut 2.35 C
- próg -5 C (zdarzeń 1159):
    w=0.00 (produkcja): P>=10%: POD 0.94 FAR 0.28 CSI 0.69 fałsz. bez zdarz. 52.1 | P>=20%: POD 0.93 FAR 0.24 CSI 0.72 fałsz. bez zdarz. 38.2 | P>=30%: POD 0.93 FAR 0.21 CSI 0.74 fałsz. bez zdarz. 26.9 | P>=50%: POD 0.91 FAR 0.18 CSI 0.76 fałsz. bez zdarz. 17.2
    w=0.50: P>=10%: POD 0.97 FAR 0.36 CSI 0.63 fałsz. bez zdarz. 92.1 | P>=20%: POD 0.95 FAR 0.29 CSI 0.69 fałsz. bez zdarz. 55.4 | P>=30%: POD 0.94 FAR 0.23 CSI 0.73 fałsz. bez zdarz. 33.2 | P>=50%: POD 0.91 FAR 0.18 CSI 0.76 fałsz. bez zdarz. 16.9
    w=0.75: P>=10%: POD 0.98 FAR 0.42 CSI 0.57 fałsz. bez zdarz. 135.6 | P>=20%: POD 0.96 FAR 0.33 CSI 0.65 fałsz. bez zdarz. 78.8 | P>=30%: POD 0.94 FAR 0.26 CSI 0.71 fałsz. bez zdarz. 42.0 | P>=50%: POD 0.91 FAR 0.18 CSI 0.76 fałsz. bez zdarz. 16.9
    w=1.00: P>=10%: POD 0.99 FAR 0.51 CSI 0.48 fałsz. bez zdarz. 228.3 | P>=20%: POD 0.97 FAR 0.38 CSI 0.61 fałsz. bez zdarz. 103.1 | P>=30%: POD 0.95 FAR 0.29 CSI 0.69 fałsz. bez zdarz. 55.1 | P>=50%: POD 0.91 FAR 0.18 CSI 0.75 fałsz. bez zdarz. 17.2
- próg -10 C (zdarzeń 484):
    w=0.00 (produkcja): P>=10%: POD 0.86 FAR 0.42 CSI 0.53 fałsz. bez zdarz. 7.9 | P>=20%: POD 0.84 FAR 0.39 CSI 0.55 fałsz. bez zdarz. 6.4 | P>=30%: POD 0.83 FAR 0.36 CSI 0.56 fałsz. bez zdarz. 5.9 | P>=50%: POD 0.74 FAR 0.30 CSI 0.56 fałsz. bez zdarz. 4.0
    w=0.50: P>=10%: POD 0.92 FAR 0.45 CSI 0.52 fałsz. bez zdarz. 9.1 | P>=20%: POD 0.88 FAR 0.40 CSI 0.55 fałsz. bez zdarz. 7.2 | P>=30%: POD 0.83 FAR 0.38 CSI 0.56 fałsz. bez zdarz. 5.9 | P>=50%: POD 0.74 FAR 0.30 CSI 0.56 fałsz. bez zdarz. 3.5
    w=0.75: P>=10%: POD 0.95 FAR 0.50 CSI 0.49 fałsz. bez zdarz. 12.4 | P>=20%: POD 0.90 FAR 0.43 CSI 0.53 fałsz. bez zdarz. 8.7 | P>=30%: POD 0.86 FAR 0.38 CSI 0.56 fałsz. bez zdarz. 6.2 | P>=50%: POD 0.74 FAR 0.30 CSI 0.56 fałsz. bez zdarz. 3.5
    w=1.00: P>=10%: POD 0.99 FAR 0.54 CSI 0.45 fałsz. bez zdarz. 19.8 | P>=20%: POD 0.93 FAR 0.46 CSI 0.52 fałsz. bez zdarz. 9.6 | P>=30%: POD 0.88 FAR 0.40 CSI 0.56 fałsz. bez zdarz. 6.7 | P>=50%: POD 0.74 FAR 0.29 CSI 0.56 fałsz. bez zdarz. 3.5
- próg -15 C (zdarzeń 100):
    w=0.00 (produkcja): P>=10%: POD 0.74 FAR 0.65 CSI 0.31 fałsz. bez zdarz. 8.1 | P>=20%: POD 0.69 FAR 0.63 CSI 0.32 fałsz. bez zdarz. 6.6 | P>=30%: POD 0.68 FAR 0.59 CSI 0.35 fałsz. bez zdarz. 5.3 | P>=50%: POD 0.65 FAR 0.52 CSI 0.38 fałsz. bez zdarz. 3.6
    w=0.50: P>=10%: POD 0.76 FAR 0.68 CSI 0.29 fałsz. bez zdarz. 9.2 | P>=20%: POD 0.71 FAR 0.64 CSI 0.31 fałsz. bez zdarz. 7.0 | P>=30%: POD 0.69 FAR 0.60 CSI 0.34 fałsz. bez zdarz. 6.0 | P>=50%: POD 0.65 FAR 0.50 CSI 0.39 fałsz. bez zdarz. 3.6
    w=0.75: P>=10%: POD 0.76 FAR 0.72 CSI 0.26 fałsz. bez zdarz. 11.3 | P>=20%: POD 0.73 FAR 0.65 CSI 0.31 fałsz. bez zdarz. 7.5 | P>=30%: POD 0.69 FAR 0.61 CSI 0.33 fałsz. bez zdarz. 6.2 | P>=50%: POD 0.65 FAR 0.50 CSI 0.39 fałsz. bez zdarz. 3.6
    w=1.00: P>=10%: POD 0.76 FAR 0.75 CSI 0.23 fałsz. bez zdarz. 12.8 | P>=20%: POD 0.76 FAR 0.67 CSI 0.30 fałsz. bez zdarz. 7.9 | P>=30%: POD 0.71 FAR 0.62 CSI 0.33 fałsz. bez zdarz. 6.2 | P>=50%: POD 0.65 FAR 0.51 CSI 0.39 fałsz. bez zdarz. 3.6
### wyprzedzenie k=2: n=5292, sigma całkowita 2.78 C, średni dodany rozrzut 2.45 C
- próg -5 C (zdarzeń 1036):
    w=0.00 (produkcja): P>=10%: POD 0.94 FAR 0.36 CSI 0.61 fałsz. bez zdarz. 71.9 | P>=20%: POD 0.92 FAR 0.31 CSI 0.65 fałsz. bez zdarz. 49.4 | P>=30%: POD 0.91 FAR 0.26 CSI 0.69 fałsz. bez zdarz. 33.7 | P>=50%: POD 0.87 FAR 0.20 CSI 0.71 fałsz. bez zdarz. 18.6
    w=0.50: P>=10%: POD 0.96 FAR 0.44 CSI 0.55 fałsz. bez zdarz. 119.2 | P>=20%: POD 0.94 FAR 0.35 CSI 0.62 fałsz. bez zdarz. 68.3 | P>=30%: POD 0.92 FAR 0.29 CSI 0.67 fałsz. bez zdarz. 42.6 | P>=50%: POD 0.88 FAR 0.20 CSI 0.72 fałsz. bez zdarz. 18.0
    w=0.75: P>=10%: POD 0.98 FAR 0.51 CSI 0.49 fałsz. bez zdarz. 169.8 | P>=20%: POD 0.95 FAR 0.40 CSI 0.58 fałsz. bez zdarz. 96.2 | P>=30%: POD 0.94 FAR 0.32 CSI 0.65 fałsz. bez zdarz. 52.7 | P>=50%: POD 0.88 FAR 0.20 CSI 0.72 fałsz. bez zdarz. 18.0
    w=1.00: P>=10%: POD 0.99 FAR 0.59 CSI 0.41 fałsz. bez zdarz. 274.6 | P>=20%: POD 0.97 FAR 0.46 CSI 0.53 fałsz. bez zdarz. 131.1 | P>=30%: POD 0.95 FAR 0.35 CSI 0.63 fałsz. bez zdarz. 66.0 | P>=50%: POD 0.88 FAR 0.20 CSI 0.72 fałsz. bez zdarz. 18.0
- próg -10 C (zdarzeń 427):
    w=0.00 (produkcja): P>=10%: POD 0.89 FAR 0.43 CSI 0.54 fałsz. bez zdarz. 13.8 | P>=20%: POD 0.87 FAR 0.38 CSI 0.56 fałsz. bez zdarz. 9.5 | P>=30%: POD 0.84 FAR 0.35 CSI 0.58 fałsz. bez zdarz. 6.4 | P>=50%: POD 0.79 FAR 0.30 CSI 0.59 fałsz. bez zdarz. 4.3
    w=0.50: P>=10%: POD 0.93 FAR 0.47 CSI 0.51 fałsz. bez zdarz. 18.5 | P>=20%: POD 0.89 FAR 0.40 CSI 0.56 fałsz. bez zdarz. 10.9 | P>=30%: POD 0.85 FAR 0.36 CSI 0.58 fałsz. bez zdarz. 7.1 | P>=50%: POD 0.78 FAR 0.30 CSI 0.58 fałsz. bez zdarz. 4.0
    w=0.75: P>=10%: POD 0.96 FAR 0.50 CSI 0.49 fałsz. bez zdarz. 23.0 | P>=20%: POD 0.91 FAR 0.42 CSI 0.55 fałsz. bez zdarz. 13.8 | P>=30%: POD 0.87 FAR 0.37 CSI 0.58 fałsz. bez zdarz. 7.8 | P>=50%: POD 0.78 FAR 0.30 CSI 0.58 fałsz. bez zdarz. 4.0
    w=1.00: P>=10%: POD 0.98 FAR 0.55 CSI 0.45 fałsz. bez zdarz. 31.4 | P>=20%: POD 0.93 FAR 0.45 CSI 0.52 fałsz. bez zdarz. 16.2 | P>=30%: POD 0.89 FAR 0.38 CSI 0.58 fałsz. bez zdarz. 8.6 | P>=50%: POD 0.77 FAR 0.30 CSI 0.58 fałsz. bez zdarz. 4.0
- próg -15 C (zdarzeń 98):
    w=0.00 (produkcja): P>=10%: POD 0.76 FAR 0.69 CSI 0.28 fałsz. bez zdarz. 4.1 | P>=20%: POD 0.72 FAR 0.64 CSI 0.32 fałsz. bez zdarz. 1.5 | P>=30%: POD 0.68 FAR 0.61 CSI 0.33 fałsz. bez zdarz. 0.9 | P>=50%: POD 0.62 FAR 0.50 CSI 0.38 fałsz. bez zdarz. 0.4
    w=0.50: P>=10%: POD 0.77 FAR 0.71 CSI 0.26 fałsz. bez zdarz. 5.0 | P>=20%: POD 0.73 FAR 0.65 CSI 0.31 fałsz. bez zdarz. 1.7 | P>=30%: POD 0.69 FAR 0.62 CSI 0.33 fałsz. bez zdarz. 1.1 | P>=50%: POD 0.63 FAR 0.50 CSI 0.39 fałsz. bez zdarz. 0.4
    w=0.75: P>=10%: POD 0.77 FAR 0.74 CSI 0.24 fałsz. bez zdarz. 5.2 | P>=20%: POD 0.76 FAR 0.67 CSI 0.30 fałsz. bez zdarz. 2.2 | P>=30%: POD 0.69 FAR 0.63 CSI 0.32 fałsz. bez zdarz. 1.1 | P>=50%: POD 0.63 FAR 0.51 CSI 0.38 fałsz. bez zdarz. 0.4
    w=1.00: P>=10%: POD 0.78 FAR 0.76 CSI 0.22 fałsz. bez zdarz. 6.7 | P>=20%: POD 0.76 FAR 0.69 CSI 0.28 fałsz. bez zdarz. 2.8 | P>=30%: POD 0.70 FAR 0.63 CSI 0.32 fałsz. bez zdarz. 1.1 | P>=50%: POD 0.63 FAR 0.51 CSI 0.38 fałsz. bez zdarz. 0.4

## 12. Oceny probabilistyczne (CRPS, Brier — niższe = lepiej; wektory zapisane do porównania modeli parami)
### wyprzedzenie k=0
- tmin_crps_k0: n=5237, średnia 1.2276
- tmin_le5_brier_k0: n=5237, średnia 0.0502
- tmin_le10_brier_k0: n=5237, średnia 0.0317
- tmin_le15_brier_k0: n=5237, średnia 0.0105
- precip_crps_k0: n=5249, średnia 0.5608
- precip_ge1_brier_k0: n=5249, średnia 0.0930
- precip_ge5_brier_k0: n=5249, średnia 0.0352
- precip_ge10_brier_k0: n=5249, średnia 0.0132
- snow_ge1_brier_k0: n=4980, średnia 0.0910
- snow_ge3_brier_k0: n=4980, średnia 0.0533
### wyprzedzenie k=1
- tmin_crps_k1: n=5290, średnia 1.3382
- tmin_le5_brier_k1: n=5290, średnia 0.0491
- tmin_le10_brier_k1: n=5290, średnia 0.0418
- tmin_le15_brier_k1: n=5290, średnia 0.0125
- precip_crps_k1: n=5304, średnia 0.6343
- precip_ge1_brier_k1: n=5304, średnia 0.1062
- precip_ge5_brier_k1: n=5304, średnia 0.0431
- precip_ge10_brier_k1: n=5304, średnia 0.0166
- snow_ge1_brier_k1: n=5089, średnia 0.0861
- snow_ge3_brier_k1: n=5089, średnia 0.0518
### wyprzedzenie k=2
- tmin_crps_k2: n=5292, średnia 1.3328
- tmin_le5_brier_k2: n=5292, średnia 0.0489
- tmin_le10_brier_k2: n=5292, średnia 0.0340
- tmin_le15_brier_k2: n=5292, średnia 0.0118
- precip_crps_k2: n=5303, średnia 0.7128
- precip_ge1_brier_k2: n=5303, średnia 0.1177
- precip_ge5_brier_k2: n=5303, średnia 0.0483
- precip_ge10_brier_k2: n=5303, średnia 0.0194
- snow_ge1_brier_k2: n=4981, średnia 0.0806
- snow_ge3_brier_k2: n=4981, średnia 0.0452

