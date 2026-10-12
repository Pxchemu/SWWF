# Kalibracja SWWF na obserwacjach IMGW — 2026-10-12 14:50
hindcast: /home/runner/work/SWWF/SWWF/hindcast_v2 (96 przebiegów 00Z z 30 członkami, okien na przebieg: [13]); obs: imgw_dobowe_2020-11-01_2026-03-31_mc-1-2-3-11-12.csv.gz (52851 stacjodni)
zespół POŁĄCZONY: hindcast_v2 x5 + hindcast_ifs x3 = 303 członków (waga modeli ~ 5*A : 3*B); korekta temperatury modelu A przed złączeniem: -1.30 C; średnia różnica T końca okna A - B (przed korektą): +0.74 C
Próba jest dobrana pod zdarzenia i dni spokojne (nie klimatologiczna) — FAR i odsetki zdarzeń z sekcji 1-5 dotyczą próby mieszanej; sekcja 6 rozdziela doby bez zdarzenia i ze zdarzeniem.

## 0. Kontrola okna doby IMGW (k=0)
- opad SMDB: start  0 UTC: r=0.835 | start  6 UTC: r=0.882 | start 12 UTC: r=0.817 | start 18 UTC: r=0.659  (najwyższe r = okno zgodne z IMGW)
- TMIN: start  0 UTC: r=0.920 | start  6 UTC: r=0.849 | start 12 UTC: r=0.832 | start 18 UTC: r=0.807  (najwyższe r = okno zgodne z IMGW)

## 1. Opad dobowy (okno 06->06 UTC)
### wyprzedzenie k=0: n=5249 stacjodni, mokrych (>=1 mm) 1338
- średnia obs 1.29 mm, GEFS+IFS 1.71 mm; korelacja sqrt = 0.882
- dni mokre: GEFS+IFS/obs = 1.10; obs > max zespołu: 3.0% dni mokrych
- P(opad>=1 mm): P=0: n=2199, zaszło 0% | P=0-20%: n=821, zaszło 4% | P=20-40%: n=309, zaszło 11% | P=40-60%: n=274, zaszło 25% | P=60-80%: n=302, zaszło 36% | P=80-100%: n=1344, zaszło 81%
- P(opad>=5 mm): P=0: n=3630, zaszło 0% | P=0-20%: n=834, zaszło 4% | P=20-40%: n=211, zaszło 16% | P=40-60%: n=138, zaszło 30% | P=60-80%: n=127, zaszło 52% | P=80-100%: n=309, zaszło 81%
- P(opad>=10 mm): P=0: n=4532, zaszło 0% | P=0-20%: n=433, zaszło 3% | P=20-40%: n=90, zaszło 31% | P=40-60%: n=69, zaszło 41% | P=60-80%: n=50, zaszło 60% | P=80-100%: n=75, zaszło 93%
### wyprzedzenie k=1: n=5304 stacjodni, mokrych (>=1 mm) 1496
- średnia obs 1.43 mm, GEFS+IFS 1.76 mm; korelacja sqrt = 0.848
- dni mokre: GEFS+IFS/obs = 0.98; obs > max zespołu: 2.6% dni mokrych
- P(opad>=1 mm): P=0: n=1543, zaszło 0% | P=0-20%: n=1131, zaszło 4% | P=20-40%: n=511, zaszło 15% | P=40-60%: n=438, zaszło 34% | P=60-80%: n=483, zaszło 50% | P=80-100%: n=1198, zaszło 82%
- P(opad>=5 mm): P=0: n=3154, zaszło 0% | P=0-20%: n=1273, zaszło 4% | P=20-40%: n=308, zaszło 21% | P=40-60%: n=181, zaszło 40% | P=60-80%: n=180, zaszło 59% | P=80-100%: n=208, zaszło 82%
- P(opad>=10 mm): P=0: n=4257, zaszło 0% | P=0-20%: n=765, zaszło 5% | P=20-40%: n=117, zaszło 24% | P=40-60%: n=80, zaszło 56% | P=60-80%: n=50, zaszło 72% | P=80-100%: n=35, zaszło 94%
### wyprzedzenie k=2: n=5303 stacjodni, mokrych (>=1 mm) 1438
- średnia obs 1.37 mm, GEFS+IFS 1.62 mm; korelacja sqrt = 0.773
- dni mokre: GEFS+IFS/obs = 0.82; obs > max zespołu: 2.9% dni mokrych
- P(opad>=1 mm): P=0: n=1100, zaszło 0% | P=0-20%: n=1446, zaszło 4% | P=20-40%: n=657, zaszło 18% | P=40-60%: n=575, zaszło 33% | P=60-80%: n=622, zaszło 56% | P=80-100%: n=903, zaszło 80%
- P(opad>=5 mm): P=0: n=2632, zaszło 0% | P=0-20%: n=1817, zaszło 5% | P=20-40%: n=416, zaszło 24% | P=40-60%: n=217, zaszło 50% | P=60-80%: n=148, zaszło 66% | P=80-100%: n=73, zaszło 78%
- P(opad>=10 mm): P=0: n=3931, zaszło 0% | P=0-20%: n=1128, zaszło 4% | P=20-40%: n=157, zaszło 42% | P=40-60%: n=68, zaszło 59% | P=60-80%: n=15, zaszło 80% | P=80-100%: n=4, zaszło 100%

## 2. Śnieg — metody rozpoznawania fazy opadu (okno 06->06 UTC)
Zdarzenie obserwowane: opad rodzaju S (śnieg) o sumie >= X mm. Prognoza: P(opad zamarznięty >= X mm) wg metody. Kolumna 'deszcz->śnieg' = odsetek dni z obserwowanym DESZCZEM >=3 mm, w których metoda daje P(śnieg>=3 mm) >= 30% (fałszywy śnieg).
(brak pól wilgotności w danych albo zespół z IFS (IFS nie ma wilgotności) — warianty z mokrym termometrem pominięte)
### wyprzedzenie k=0: n=5249; obs śnieg >=1 mm: 607, >=3 mm: 315, >=5 mm: 194; deszcz >=3 mm: 330
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A dawna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.55 | 0.56 | 0.32 | 0.76 | 0.50 | 7% |
| D obecna (produkcja): T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.82 | 0.62 | 0.35 | 0.94 | 0.56 | 29% |
| G: CPOFP (gdy ważny), inaczej D | 0.75 | 0.59 | 0.36 | 0.92 | 0.53 | 21% |
| E1: T zimniejsza z 2 próbek (1@0C->0@2C), progi o 1 C niżej niż D | 0.68 | 0.60 | 0.34 | 0.85 | 0.53 | 13% |
| E2: T zimniejsza z 2 próbek (1@0.5C->0@2.5C), progi o 0.5 C niżej niż D | 0.77 | 0.61 | 0.35 | 0.90 | 0.54 | 21% |
- wiarygodność P(śnieg>=3 mm), metoda 'D' (produkcyjna): P=0: n=3836, zaszło 0% | P=0-20%: n=634, zaszło 5% | P=20-40%: n=189, zaszło 14% | P=40-60%: n=159, zaszło 25% | P=60-80%: n=112, zaszło 30% | P=80-100%: n=319, zaszło 53%
### wyprzedzenie k=1: n=5304; obs śnieg >=1 mm: 650, >=3 mm: 336, >=5 mm: 191; deszcz >=3 mm: 402
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A dawna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.45 | 0.59 | 0.27 | 0.76 | 0.49 | 6% |
| D obecna (produkcja): T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.74 | 0.62 | 0.34 | 0.92 | 0.56 | 19% |
| G: CPOFP (gdy ważny), inaczej D | 0.65 | 0.59 | 0.33 | 0.89 | 0.53 | 15% |
| E1: T zimniejsza z 2 próbek (1@0C->0@2C), progi o 1 C niżej niż D | 0.58 | 0.60 | 0.31 | 0.80 | 0.52 | 8% |
| E2: T zimniejsza z 2 próbek (1@0.5C->0@2.5C), progi o 0.5 C niżej niż D | 0.67 | 0.61 | 0.33 | 0.86 | 0.55 | 14% |
- wiarygodność P(śnieg>=3 mm), metoda 'D' (produkcyjna): P=0: n=3493, zaszło 0% | P=0-20%: n=1024, zaszło 5% | P=20-40%: n=261, zaszło 20% | P=40-60%: n=185, zaszło 26% | P=60-80%: n=154, zaszło 43% | P=80-100%: n=187, zaszło 57%
### wyprzedzenie k=2: n=5303; obs śnieg >=1 mm: 612, >=3 mm: 308, >=5 mm: 176; deszcz >=3 mm: 419
| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |
|---|---|---|---|---|---|---|
| A dawna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C) | 0.40 | 0.61 | 0.25 | 0.74 | 0.54 | 4% |
| D obecna (produkcja): T = zimniejsza z 2 próbek (1@1C->0@3C) | 0.68 | 0.64 | 0.31 | 0.91 | 0.60 | 14% |
| G: CPOFP (gdy ważny), inaczej D | 0.58 | 0.60 | 0.31 | 0.88 | 0.57 | 8% |
| E1: T zimniejsza z 2 próbek (1@0C->0@2C), progi o 1 C niżej niż D | 0.51 | 0.65 | 0.26 | 0.81 | 0.56 | 7% |
| E2: T zimniejsza z 2 próbek (1@0.5C->0@2.5C), progi o 0.5 C niżej niż D | 0.60 | 0.65 | 0.29 | 0.87 | 0.58 | 10% |
- wiarygodność P(śnieg>=3 mm), metoda 'D' (produkcyjna): P=0: n=3061, zaszło 0% | P=0-20%: n=1422, zaszło 4% | P=20-40%: n=400, zaszło 18% | P=40-60%: n=204, zaszło 35% | P=60-80%: n=131, zaszło 40% | P=80-100%: n=85, zaszło 59%

## 3. Mróz — temperatura powietrza vs odczuwalna (okno doby kalendarzowej 00-24 UTC; obserwacja = TMIN powietrza)
Uwaga: IMGW mierzy tylko temperaturę powietrza, więc odczuwalnej NIE da się zweryfikować wprost; poniżej sprawdzamy, jak daleko od powietrza jest każda wersja i czy 'odczuwalna' nie robi fałszywych alarmów względem realnego mrozu.
### wyprzedzenie k=0: n=5237
- prognoza min. T powietrza: błąd średni +0.07 C, MAE 1.61 C; w mroźnych dniach (obs <= -10 C): błąd +1.73 C
- próg -5 C (obs zdarzeń 1135), powietrze: P>=30%: traf. 997, fałsz. 210, przegap. 138 (POD 0.88, FAR 0.17, CSI 0.74)
- próg -10 C (obs zdarzeń 472), powietrze: P>=30%: traf. 360, fałsz. 92, przegap. 112 (POD 0.76, FAR 0.20, CSI 0.64)
- próg -15 C (obs zdarzeń 108), powietrze: P>=30%: traf. 67, fałsz. 37, przegap. 41 (POD 0.62, FAR 0.36, CSI 0.46)
- próg -20 C (obs zdarzeń 23), powietrze: P>=30%: traf. 21, fałsz. 10, przegap. 2 (POD 0.91, FAR 0.32, CSI 0.64)
### wyprzedzenie k=1: n=5290
- prognoza min. T powietrza: błąd średni +0.09 C, MAE 1.74 C; w mroźnych dniach (obs <= -10 C): błąd +1.72 C
- próg -5 C (obs zdarzeń 1159), powietrze: P>=30%: traf. 1012, fałsz. 196, przegap. 147 (POD 0.87, FAR 0.16, CSI 0.75)
- próg -10 C (obs zdarzeń 484), powietrze: P>=30%: traf. 331, fałsz. 139, przegap. 153 (POD 0.68, FAR 0.30, CSI 0.53)
- próg -15 C (obs zdarzeń 100), powietrze: P>=30%: traf. 62, fałsz. 62, przegap. 38 (POD 0.62, FAR 0.50, CSI 0.38)
- próg -20 C (obs zdarzeń 17), powietrze: P>=30%: traf. 15, fałsz. 14, przegap. 2 (POD 0.88, FAR 0.48, CSI 0.48)
### wyprzedzenie k=2: n=5292
- prognoza min. T powietrza: błąd średni -0.18 C, MAE 1.78 C; w mroźnych dniach (obs <= -10 C): błąd +1.61 C
- próg -5 C (obs zdarzeń 1036), powietrze: P>=30%: traf. 886, fałsz. 210, przegap. 150 (POD 0.86, FAR 0.19, CSI 0.71)
- próg -10 C (obs zdarzeń 427), powietrze: P>=30%: traf. 317, fałsz. 148, przegap. 110 (POD 0.74, FAR 0.32, CSI 0.55)
- próg -15 C (obs zdarzeń 98), powietrze: P>=30%: traf. 62, fałsz. 60, przegap. 36 (POD 0.63, FAR 0.49, CSI 0.39)
- próg -20 C (obs zdarzeń 13), powietrze: P>=30%: traf. 12, fałsz. 11, przegap. 1 (POD 0.92, FAR 0.48, CSI 0.50)

## 6. Fałszywe alarmy na dobach bez zdarzenia i trafienia na dobach ze zdarzeniem
Alarm = P(zdarzenia) >= 30% wg zespołu. Doba 'bez zdarzenia' = zdarzenie na <= 1 stacji (wtedy każdy alarm jest fałszywy); 'ze zdarzeniem' = na >= 5 stacjach. 'doby z >=3 stacjami' = ile dób miało alarm na co najmniej 3 stacjach naraz (tyle widziałby użytkownik jako plamę na mapie).
### wyprzedzenie k=0
- śnieg >= 3 mm: doby bez zdarzenia: 61, stacjodni 3375, fałszywych alarmów 41 (12.1 na 1000 stacjodni); doby z >=3 stacjami: 2 z 61
    doby ze zdarzeniem: 23, zdarzeń 284, trafionych 234 (POD 0.82), fałszywych alarmów na tych dobach 296
- opad >= 10 mm: doby bez zdarzenia: 74, stacjodni 4090, fałszywych alarmów 17 (4.2 na 1000 stacjodni); doby z >=3 stacjami: 4 z 74
    doby ze zdarzeniem: 12, zdarzeń 144, trafionych 130 (POD 0.90), fałszywych alarmów na tych dobach 61
- mróz TMIN <= -10 C: doby bez zdarzenia: 74, stacjodni 4098, fałszywych alarmów 18 (4.4 na 1000 stacjodni); doby z >=3 stacjami: 2 z 74
    doby ze zdarzeniem: 18, zdarzeń 461, trafionych 356 (POD 0.77), fałszywych alarmów na tych dobach 71
- mróz TMIN <= -15 C: doby bez zdarzenia: 84, stacjodni 4644, fałszywych alarmów 4 (0.9 na 1000 stacjodni); doby z >=3 stacjami: 0 z 84
    doby ze zdarzeniem: 8, zdarzeń 97, trafionych 66 (POD 0.68), fałszywych alarmów na tych dobach 31
### wyprzedzenie k=1
- śnieg >= 3 mm: doby bez zdarzenia: 58, stacjodni 3209, fałszywych alarmów 24 (7.5 na 1000 stacjodni); doby z >=3 stacjami: 4 z 58
    doby ze zdarzeniem: 25, zdarzeń 301, trafionych 226 (POD 0.75), fałszywych alarmów na tych dobach 295
- opad >= 10 mm: doby bez zdarzenia: 74, stacjodni 4084, fałszywych alarmów 12 (2.9 na 1000 stacjodni); doby z >=3 stacjami: 3 z 74
    doby ze zdarzeniem: 13, zdarzeń 153, trafionych 114 (POD 0.75), fałszywych alarmów na tych dobach 61
- mróz TMIN <= -10 C: doby bez zdarzenia: 73, stacjodni 4045, fałszywych alarmów 13 (3.2 na 1000 stacjodni); doby z >=3 stacjami: 2 z 73
    doby ze zdarzeniem: 21, zdarzeń 475, trafionych 329 (POD 0.69), fałszywych alarmów na tych dobach 120
- mróz TMIN <= -15 C: doby bez zdarzenia: 85, stacjodni 4696, fałszywych alarmów 17 (3.6 na 1000 stacjodni); doby z >=3 stacjami: 1 z 85
    doby ze zdarzeniem: 8, zdarzeń 88, trafionych 59 (POD 0.67), fałszywych alarmów na tych dobach 34
### wyprzedzenie k=2
- śnieg >= 3 mm: doby bez zdarzenia: 60, stacjodni 3316, fałszywych alarmów 68 (20.5 na 1000 stacjodni); doby z >=3 stacjami: 8 z 60
    doby ze zdarzeniem: 22, zdarzeń 266, trafionych 187 (POD 0.70), fałszywych alarmów na tych dobach 232
- opad >= 10 mm: doby bez zdarzenia: 77, stacjodni 4248, fałszywych alarmów 19 (4.5 na 1000 stacjodni); doby z >=3 stacjami: 2 z 77
    doby ze zdarzeniem: 12, zdarzeń 149, trafionych 86 (POD 0.58), fałszywych alarmów na tych dobach 45
- mróz TMIN <= -10 C: doby bez zdarzenia: 76, stacjodni 4210, fałszywych alarmów 22 (5.2 na 1000 stacjodni); doby z >=3 stacjami: 3 z 76
    doby ze zdarzeniem: 18, zdarzeń 417, trafionych 310 (POD 0.74), fałszywych alarmów na tych dobach 124
- mróz TMIN <= -15 C: doby bez zdarzenia: 84, stacjodni 4645, fałszywych alarmów 3 (0.6 na 1000 stacjodni); doby z >=3 stacjami: 0 z 84
    doby ze zdarzeniem: 8, zdarzeń 83, trafionych 55 (POD 0.66), fałszywych alarmów na tych dobach 39

## 7. Mróz — diagnoza niedoszacowania ogona zimna i test prostej korekty (TMIN, doba 00-24 UTC)
Błąd = obserwacja - prognoza (średnia zespołu min. T powietrza); UJEMNY = w rzeczywistości zimniej niż w prognozie (prognoza za ciepła). Przedziały wg PROGNOZY (wersja użyteczna do korekty; przedziały wg obserwacji zawyżają błąd przez regresję do średniej).
### wyprzedzenie k=0: n=5237
- błąd wg przedziałów prognozy: prog. < -15: n=76, błąd +0.28 C (mediana +0.27) | -15..-10: n=263, błąd -0.21 C (mediana -0.01) | -10..-5: n=772, błąd -0.30 C (mediana -0.33) | -5..0: n=1855, błąd +0.31 C (mediana +0.54) | > 0: n=2271, błąd -0.29 C (mediana -0.10)
- rozrzut zespołu (średnie odch. std) 0.85 C vs RMSE średniej zespołu 2.10 C; dla prognoz <= -5 C: rozrzut 1.11 C vs RMSE 2.63 C
- obserwacja zimniejsza niż WSZYSTKIE 30 członków: 21.0% stacjodni (przy dobrze rozproszonym zespole ~3%); dla prognoz <= -5 C: 23.3%
- błąd na dniach z prognozą <= -5 C wg stacji (n stacji=50): średnia -0.31 C, rozrzut między stacjami (std) 0.93 C
    najmniejszy błąd: KOSZALIN -1.9, JELENIA GÓRA -1.8, PIŁA -1.6, POZNAŃ-ŁAWICA -1.6, ŁÓDŹ -1.6
    największy błąd: LESKO +1.0, BIELSKO-BIAŁA +1.2, ZIELONA GÓRA +1.2, KROSNO +1.2, NOWY SĄCZ +2.1, ZAKOPANE +2.2
    korelacja błędu stacji z szerokością: -0.49, z długością: +0.30
- korekta liniowa po prognozie: MAE 1.61 -> 1.62 C; błąd średni -0.07 -> -0.14 C; średnie przesunięcie dla prognoz <= -10 C: -0.11 C (produkcja: -1.0 C); sigma resztowa ok. 2.09 C
- próg -5 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.88, FAR 0.17, CSI 0.74, fałszywych 210; na dobach bez zdarzenia 11.6 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.93, FAR 0.26, CSI 0.70, fałszywych 381; na dobach bez zdarzenia 26.2 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.88, FAR 0.17, CSI 0.74, fałszywych 210; na dobach bez zdarzenia 11.6 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.96, FAR 0.30, CSI 0.68, fałszywych 470; na dobach bez zdarzenia 35.4 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.91, FAR 0.21, CSI 0.73, fałszywych 278; na dobach bez zdarzenia 15.0 na 1000 stacjodni
- próg -10 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.76, FAR 0.20, CSI 0.64, fałszywych 92; na dobach bez zdarzenia 4.1 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.86, FAR 0.31, CSI 0.62, fałszywych 181; na dobach bez zdarzenia 7.8 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.77, FAR 0.21, CSI 0.64, fałszywych 96; na dobach bez zdarzenia 4.4 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.90, FAR 0.35, CSI 0.61, fałszywych 227; na dobach bez zdarzenia 9.0 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.81, FAR 0.26, CSI 0.63, fałszywych 132; na dobach bez zdarzenia 5.4 na 1000 stacjodni
- próg -15 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.62, FAR 0.36, CSI 0.46, fałszywych 37; na dobach bez zdarzenia 0.9 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.72, FAR 0.49, CSI 0.42, fałszywych 76; na dobach bez zdarzenia 2.2 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.63, FAR 0.36, CSI 0.47, fałszywych 38; na dobach bez zdarzenia 0.9 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.74, FAR 0.50, CSI 0.42, fałszywych 81; na dobach bez zdarzenia 1.9 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.66, FAR 0.42, CSI 0.44, fałszywych 52; na dobach bez zdarzenia 1.1 na 1000 stacjodni
### wyprzedzenie k=1: n=5290
- błąd wg przedziałów prognozy: prog. < -15: n=92, błąd +1.31 C (mediana +1.23) | -15..-10: n=266, błąd +0.67 C (mediana +0.57) | -10..-5: n=758, błąd -0.61 C (mediana -0.54) | -5..0: n=1760, błąd +0.30 C (mediana +0.60) | > 0: n=2414, błąd -0.36 C (mediana -0.19)
- rozrzut zespołu (średnie odch. std) 0.97 C vs RMSE średniej zespołu 2.26 C; dla prognoz <= -5 C: rozrzut 1.27 C vs RMSE 2.95 C
- obserwacja zimniejsza niż WSZYSTKIE 30 członków: 18.2% stacjodni (przy dobrze rozproszonym zespole ~3%); dla prognoz <= -5 C: 20.6%
- błąd na dniach z prognozą <= -5 C wg stacji (n stacji=52): średnia -0.18 C, rozrzut między stacjami (std) 0.98 C
    najmniejszy błąd: ŁEBA -2.2, JELENIA GÓRA -1.9, BIAŁYSTOK -1.6, KOZIENICE -1.3, SZCZECIN -1.2
    największy błąd: LESKO +1.4, KROSNO +1.5, BIELSKO-BIAŁA +1.5, HEL +1.6, NOWY SĄCZ +2.1, ZAKOPANE +2.3
    korelacja błędu stacji z szerokością: -0.41, z długością: +0.13
- korekta liniowa po prognozie: MAE 1.74 -> 1.74 C; błąd średni -0.09 -> -0.13 C; średnie przesunięcie dla prognoz <= -10 C: +0.16 C (produkcja: -1.0 C); sigma resztowa ok. 2.26 C
- próg -5 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.87, FAR 0.16, CSI 0.75, fałszywych 196; na dobach bez zdarzenia 14.5 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.93, FAR 0.22, CSI 0.74, fałszywych 302; na dobach bez zdarzenia 29.3 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.87, FAR 0.16, CSI 0.75, fałszywych 185; na dobach bez zdarzenia 13.0 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.95, FAR 0.28, CSI 0.69, fałszywych 426; na dobach bez zdarzenia 51.5 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.91, FAR 0.19, CSI 0.75, fałszywych 251; na dobach bez zdarzenia 19.5 na 1000 stacjodni
- próg -10 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.68, FAR 0.30, CSI 0.53, fałszywych 139; na dobach bez zdarzenia 3.2 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.82, FAR 0.36, CSI 0.56, fałszywych 219; na dobach bez zdarzenia 5.4 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.65, FAR 0.29, CSI 0.52, fałszywych 129; na dobach bez zdarzenia 3.2 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.86, FAR 0.38, CSI 0.56, fałszywych 260; na dobach bez zdarzenia 6.7 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.72, FAR 0.32, CSI 0.54, fałszywych 164; na dobach bez zdarzenia 3.7 na 1000 stacjodni
- próg -15 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.62, FAR 0.50, CSI 0.38, fałszywych 62; na dobach bez zdarzenia 3.6 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.69, FAR 0.59, CSI 0.35, fałszywych 99; na dobach bez zdarzenia 5.3 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.61, FAR 0.47, CSI 0.39, fałszywych 55; na dobach bez zdarzenia 3.2 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.69, FAR 0.61, CSI 0.33, fałszywych 108; na dobach bez zdarzenia 5.5 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.65, FAR 0.51, CSI 0.38, fałszywych 69; na dobach bez zdarzenia 3.8 na 1000 stacjodni
### wyprzedzenie k=2: n=5292
- błąd wg przedziałów prognozy: prog. < -15: n=79, błąd +1.07 C (mediana +1.23) | -15..-10: n=272, błąd +0.91 C (mediana +1.07) | -10..-5: n=625, błąd -0.58 C (mediana -0.57) | -5..0: n=1898, błąd +0.43 C (mediana +0.78) | > 0: n=2418, błąd +0.07 C (mediana +0.16)
- rozrzut zespołu (średnie odch. std) 1.19 C vs RMSE średniej zespołu 2.27 C; dla prognoz <= -5 C: rozrzut 1.59 C vs RMSE 2.98 C
- obserwacja zimniejsza niż WSZYSTKIE 30 członków: 11.8% stacjodni (przy dobrze rozproszonym zespole ~3%); dla prognoz <= -5 C: 15.9%
- błąd na dniach z prognozą <= -5 C wg stacji (n stacji=52): średnia -0.07 C, rozrzut między stacjami (std) 1.02 C
    najmniejszy błąd: JELENIA GÓRA -2.7, SŁUBICE -1.7, ŁÓDŹ -1.6, SZCZECIN -1.2, LESZNO -1.2
    największy błąd: GDAŃSK-ŚWIBNO +1.4, BIELSKO-BIAŁA +1.5, KROSNO +1.8, ZAKOPANE +2.0, HEL +2.2, NOWY SĄCZ +2.5
    korelacja błędu stacji z szerokością: -0.23, z długością: +0.19
- korekta liniowa po prognozie: MAE 1.78 -> 1.77 C; błąd średni +0.18 -> -0.13 C; średnie przesunięcie dla prognoz <= -10 C: +0.11 C (produkcja: -1.0 C); sigma resztowa ok. 2.28 C
- próg -5 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.86, FAR 0.19, CSI 0.71, fałszywych 210; na dobach bez zdarzenia 16.3 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.91, FAR 0.27, CSI 0.68, fałszywych 350; na dobach bez zdarzenia 36.1 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.83, FAR 0.17, CSI 0.71, fałszywych 178; na dobach bez zdarzenia 13.3 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.94, FAR 0.33, CSI 0.64, fałszywych 473; na dobach bez zdarzenia 57.4 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.88, FAR 0.20, CSI 0.72, fałszywych 229; na dobach bez zdarzenia 19.2 na 1000 stacjodni
- próg -10 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.74, FAR 0.32, CSI 0.55, fałszywych 148; na dobach bez zdarzenia 4.5 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.82, FAR 0.36, CSI 0.56, fałszywych 197; na dobach bez zdarzenia 7.1 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.70, FAR 0.32, CSI 0.53, fałszywych 138; na dobach bez zdarzenia 3.8 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.85, FAR 0.37, CSI 0.57, fałszywych 214; na dobach bez zdarzenia 7.6 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.74, FAR 0.33, CSI 0.54, fałszywych 153; na dobach bez zdarzenia 4.3 na 1000 stacjodni
- próg -15 C, alarm przy P>=30%:
    surowe (bez korekty): POD 0.63, FAR 0.49, CSI 0.39, fałszywych 60; na dobach bez zdarzenia 0.4 na 1000 stacjodni
    produkcja (-1.0 C): POD 0.67, FAR 0.60, CSI 0.34, fałszywych 98; na dobach bez zdarzenia 0.9 na 1000 stacjodni
    korekta liniowa (LORO): POD 0.61, FAR 0.49, CSI 0.38, fałszywych 58; na dobach bez zdarzenia 0.4 na 1000 stacjodni
    produkcja + wygładzenie rozrzutu (sigma z LORO): POD 0.67, FAR 0.62, CSI 0.32, fałszywych 106; na dobach bez zdarzenia 1.1 na 1000 stacjodni
    korekta liniowa + wygładzenie rozrzutu: POD 0.65, FAR 0.51, CSI 0.39, fałszywych 67; na dobach bez zdarzenia 0.4 na 1000 stacjodni

## 8. Śnieg — test skalowania ilości opadu zamarzniętego (wariant D) i progu alarmu
Skala f mnoży opad zamarznięty każdego członka (f=1,0 = obecna produkcja). Zdarzenie = obserwowany opad rodzaju S >= X mm (SMDB). Doby bez zdarzenia = zdarzenie na <= 1 stacji. Uwaga: to ilość WODY (mm), nie centymetry śniegu — przelicznik śnieg:woda jest osobną sprawą.
### wyprzedzenie k=0: n=5249
- stosunek średniej obserwowanego śniegu (mm) do średniej prognozy wg przedziałów prognozy: 0,5-1 mm: n=354, obs/prog. = 0.43 | 1-3 mm: n=610, obs/prog. = 0.63 | 3-6 mm: n=328, obs/prog. = 0.62 | >6 mm: n=186, obs/prog. = 0.68
- próg 3 mm:
    f=1.0, alarm przy P>=30%: POD 0.82, FAR 0.62, CSI 0.35, fałszywych 426; na dobach bez zdarzenia 11.9 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.71, FAR 0.56, CSI 0.38, fałszywych 279; na dobach bez zdarzenia 7.7 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.79, FAR 0.59, CSI 0.37, fałszywych 365; na dobach bez zdarzenia 10.4 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.67, FAR 0.53, CSI 0.38, fałszywych 238; na dobach bez zdarzenia 7.7 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.75, FAR 0.56, CSI 0.39, fałszywych 296; na dobach bez zdarzenia 9.5 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.63, FAR 0.49, CSI 0.39, fałszywych 189; na dobach bez zdarzenia 6.8 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.71, FAR 0.52, CSI 0.40, fałszywych 246; na dobach bez zdarzenia 8.0 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.58, FAR 0.44, CSI 0.40, fałszywych 143; na dobach bez zdarzenia 5.6 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.65, FAR 0.47, CSI 0.41, fałszywych 179; na dobach bez zdarzenia 7.4 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.49, FAR 0.38, CSI 0.38, fałszywych 97; na dobach bez zdarzenia 3.3 na 1000 stacjodni
- próg 5 mm:
    f=1.0, alarm przy P>=30%: POD 0.75, FAR 0.62, CSI 0.34, fałszywych 238; na dobach bez zdarzenia 13.8 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.61, FAR 0.53, CSI 0.36, fałszywych 134; na dobach bez zdarzenia 6.3 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.70, FAR 0.56, CSI 0.37, fałszywych 173; na dobach bez zdarzenia 10.3 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.56, FAR 0.50, CSI 0.36, fałszywych 106; na dobach bez zdarzenia 4.8 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.65, FAR 0.51, CSI 0.39, fałszywych 130; na dobach bez zdarzenia 6.5 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.49, FAR 0.44, CSI 0.35, fałszywych 76; na dobach bez zdarzenia 3.0 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.53, FAR 0.45, CSI 0.37, fałszywych 84; na dobach bez zdarzenia 4.3 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.42, FAR 0.36, CSI 0.34, fałszywych 45; na dobach bez zdarzenia 1.3 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.46, FAR 0.35, CSI 0.37, fałszywych 47; na dobach bez zdarzenia 1.5 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.30, FAR 0.25, CSI 0.28, fałszywych 20; na dobach bez zdarzenia 0.0 na 1000 stacjodni
### wyprzedzenie k=1: n=5304
- stosunek średniej obserwowanego śniegu (mm) do średniej prognozy wg przedziałów prognozy: 0,5-1 mm: n=408, obs/prog. = 0.63 | 1-3 mm: n=716, obs/prog. = 0.67 | 3-6 mm: n=351, obs/prog. = 0.73 | >6 mm: n=146, obs/prog. = 0.71
- próg 3 mm:
    f=1.0, alarm przy P>=30%: POD 0.74, FAR 0.62, CSI 0.34, fałszywych 395; na dobach bez zdarzenia 7.2 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.58, FAR 0.54, CSI 0.35, fałszywych 226; na dobach bez zdarzenia 1.9 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.71, FAR 0.58, CSI 0.35, fałszywych 334; na dobach bez zdarzenia 5.6 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.55, FAR 0.51, CSI 0.35, fałszywych 189; na dobach bez zdarzenia 1.9 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.65, FAR 0.55, CSI 0.36, fałszywych 273; na dobach bez zdarzenia 2.5 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.51, FAR 0.46, CSI 0.35, fałszywych 147; na dobach bez zdarzenia 1.2 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.61, FAR 0.52, CSI 0.37, fałszywych 218; na dobach bez zdarzenia 1.9 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.43, FAR 0.43, CSI 0.33, fałszywych 109; na dobach bez zdarzenia 0.9 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.54, FAR 0.45, CSI 0.37, fałszywych 147; na dobach bez zdarzenia 1.2 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.35, FAR 0.39, CSI 0.28, fałszywych 73; na dobach bez zdarzenia 0.9 na 1000 stacjodni
- próg 5 mm:
    f=1.0, alarm przy P>=30%: POD 0.64, FAR 0.62, CSI 0.31, fałszywych 205; na dobach bez zdarzenia 7.7 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.43, FAR 0.56, CSI 0.28, fałszywych 106; na dobach bez zdarzenia 3.1 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.61, FAR 0.57, CSI 0.34, fałszywych 154; na dobach bez zdarzenia 5.9 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.37, FAR 0.52, CSI 0.26, fałszywych 78; na dobach bez zdarzenia 1.8 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.51, FAR 0.53, CSI 0.33, fałszywych 110; na dobach bez zdarzenia 3.1 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.31, FAR 0.48, CSI 0.24, fałszywych 54; na dobach bez zdarzenia 1.0 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.41, FAR 0.49, CSI 0.29, fałszywych 75; na dobach bez zdarzenia 2.0 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.22, FAR 0.41, CSI 0.19, fałszywych 29; na dobach bez zdarzenia 0.5 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.32, FAR 0.42, CSI 0.26, fałszywych 45; na dobach bez zdarzenia 1.0 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.14, FAR 0.33, CSI 0.13, fałszywych 13; na dobach bez zdarzenia 0.3 na 1000 stacjodni
### wyprzedzenie k=2: n=5303
- stosunek średniej obserwowanego śniegu (mm) do średniej prognozy wg przedziałów prognozy: 0,5-1 mm: n=478, obs/prog. = 0.62 | 1-3 mm: n=843, obs/prog. = 0.69 | 3-6 mm: n=275, obs/prog. = 0.77 | >6 mm: n=102, obs/prog. = 0.74
- próg 3 mm:
    f=1.0, alarm przy P>=30%: POD 0.68, FAR 0.64, CSI 0.31, fałszywych 375; na dobach bez zdarzenia 19.6 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.45, FAR 0.53, CSI 0.30, fałszywych 157; na dobach bez zdarzenia 7.5 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.63, FAR 0.62, CSI 0.31, fałszywych 313; na dobach bez zdarzenia 14.5 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.38, FAR 0.53, CSI 0.27, fałszywych 132; na dobach bez zdarzenia 6.0 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.58, FAR 0.58, CSI 0.32, fałszywych 248; na dobach bez zdarzenia 10.9 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.34, FAR 0.51, CSI 0.25, fałszywych 109; na dobach bez zdarzenia 4.5 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.51, FAR 0.53, CSI 0.32, fałszywych 180; na dobach bez zdarzenia 6.9 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.31, FAR 0.43, CSI 0.25, fałszywych 73; na dobach bez zdarzenia 2.1 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.43, FAR 0.47, CSI 0.31, fałszywych 115; na dobach bez zdarzenia 4.8 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.25, FAR 0.43, CSI 0.21, fałszywych 58; na dobach bez zdarzenia 1.5 na 1000 stacjodni
- próg 5 mm:
    f=1.0, alarm przy P>=30%: POD 0.50, FAR 0.64, CSI 0.26, fałszywych 159; na dobach bez zdarzenia 8.9 na 1000 stacjodni
    f=1.0, alarm przy P>=50%: POD 0.29, FAR 0.62, CSI 0.20, fałszywych 84; na dobach bez zdarzenia 3.8 na 1000 stacjodni
    f=0.9, alarm przy P>=30%: POD 0.44, FAR 0.63, CSI 0.25, fałszywych 135; na dobach bez zdarzenia 7.7 na 1000 stacjodni
    f=0.9, alarm przy P>=50%: POD 0.25, FAR 0.54, CSI 0.19, fałszywych 52; na dobach bez zdarzenia 2.3 na 1000 stacjodni
    f=0.8, alarm przy P>=30%: POD 0.40, FAR 0.58, CSI 0.26, fałszywych 100; na dobach bez zdarzenia 5.1 na 1000 stacjodni
    f=0.8, alarm przy P>=50%: POD 0.19, FAR 0.46, CSI 0.16, fałszywych 28; na dobach bez zdarzenia 1.0 na 1000 stacjodni
    f=0.7, alarm przy P>=30%: POD 0.32, FAR 0.54, CSI 0.23, fałszywych 68; na dobach bez zdarzenia 3.3 na 1000 stacjodni
    f=0.7, alarm przy P>=50%: POD 0.11, FAR 0.41, CSI 0.11, fałszywych 14; na dobach bez zdarzenia 0.5 na 1000 stacjodni
    f=0.6, alarm przy P>=30%: POD 0.22, FAR 0.48, CSI 0.18, fałszywych 36; na dobach bez zdarzenia 1.3 na 1000 stacjodni
    f=0.6, alarm przy P>=50%: POD 0.09, FAR 0.12, CSI 0.08, fałszywych 2; na dobach bez zdarzenia 0.0 na 1000 stacjodni

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
- wg przedziałów prognozy (średnia zespołu): 1-3 cm: n=534, śr. prog. 1.9 cm, śr. obs 0.7 cm (obs/prog. = 0.37) | 3-6 cm: n=247, śr. prog. 4.3 cm, śr. obs 1.5 cm (obs/prog. = 0.35) | 6-10 cm: n=86, śr. prog. 7.4 cm, śr. obs 1.9 cm (obs/prog. = 0.25) | >10 cm: n=32, śr. prog. 13.0 cm, śr. obs 2.7 cm (obs/prog. = 0.21)
- próg 5 cm (zdarzeń 102):
    g=1.0, alarm przy P>=30%: POD 0.38, FAR 0.84, CSI 0.13, fałszywych 202; na dobach bez zdarzenia 32.4 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.26, FAR 0.84, CSI 0.11, fałszywych 141; na dobach bez zdarzenia 22.4 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.27, FAR 0.83, CSI 0.12, fałszywych 135; na dobach bez zdarzenia 20.8 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.18, FAR 0.83, CSI 0.10, fałszywych 87; na dobach bez zdarzenia 13.5 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.14, FAR 0.83, CSI 0.08, fałszywych 67; na dobach bez zdarzenia 9.7 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.12, FAR 0.79, CSI 0.08, fałszywych 46; na dobach bez zdarzenia 7.0 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.11, FAR 0.80, CSI 0.08, fałszywych 43; na dobach bez zdarzenia 6.2 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.07, FAR 0.78, CSI 0.06, fałszywych 25; na dobach bez zdarzenia 3.5 na 1000 stacjodni
- próg 10 cm (zdarzeń 16):
    g=1.0, alarm przy P>=30%: POD 0.06, FAR 0.98, CSI 0.01, fałszywych 53; na dobach bez zdarzenia 9.5 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.06, FAR 0.97, CSI 0.02, fałszywych 31; na dobach bez zdarzenia 4.9 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.06, FAR 0.96, CSI 0.02, fałszywych 25; na dobach bez zdarzenia 4.4 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.06, FAR 0.92, CSI 0.04, fałszywych 11; na dobach bez zdarzenia 1.6 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 9; na dobach bez zdarzenia 1.4 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 5; na dobach bez zdarzenia 0.7 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 4; na dobach bez zdarzenia 0.5 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.00, FAR 0.00, CSI 0.00, fałszywych 0; na dobach bez zdarzenia 0.0 na 1000 stacjodni
### wyprzedzenie k=1: n=4496
- wg przedziałów prognozy (średnia zespołu): 1-3 cm: n=611, śr. prog. 1.8 cm, śr. obs 0.8 cm (obs/prog. = 0.44) | 3-6 cm: n=267, śr. prog. 4.2 cm, śr. obs 1.1 cm (obs/prog. = 0.26) | 6-10 cm: n=60, śr. prog. 7.5 cm, śr. obs 2.3 cm (obs/prog. = 0.30) | >10 cm: n=24, śr. prog. 12.1 cm, śr. obs 3.2 cm (obs/prog. = 0.27)
- próg 5 cm (zdarzeń 128):
    g=1.0, alarm przy P>=30%: POD 0.26, FAR 0.85, CSI 0.11, fałszywych 181; na dobach bez zdarzenia 25.6 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.16, FAR 0.81, CSI 0.10, fałszywych 90; na dobach bez zdarzenia 11.1 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.18, FAR 0.82, CSI 0.10, fałszywych 108; na dobach bez zdarzenia 14.5 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.11, FAR 0.78, CSI 0.08, fałszywych 50; na dobach bez zdarzenia 5.3 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.12, FAR 0.75, CSI 0.09, fałszywych 45; na dobach bez zdarzenia 5.6 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.07, FAR 0.72, CSI 0.06, fałszywych 23; na dobach bez zdarzenia 2.2 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.08, FAR 0.75, CSI 0.06, fałszywych 30; na dobach bez zdarzenia 3.3 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.05, FAR 0.65, CSI 0.04, fałszywych 11; na dobach bez zdarzenia 1.7 na 1000 stacjodni
- próg 10 cm (zdarzeń 28):
    g=1.0, alarm przy P>=30%: POD 0.07, FAR 0.95, CSI 0.03, fałszywych 38; na dobach bez zdarzenia 5.5 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.04, FAR 0.94, CSI 0.02, fałszywych 16; na dobach bez zdarzenia 2.4 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.04, FAR 0.96, CSI 0.02, fałszywych 22; na dobach bez zdarzenia 3.1 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 4; na dobach bez zdarzenia 0.5 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 7; na dobach bez zdarzenia 1.2 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 2; na dobach bez zdarzenia 0.5 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 3; na dobach bez zdarzenia 0.7 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.00, FAR 0.00, CSI 0.00, fałszywych 0; na dobach bez zdarzenia 0.0 na 1000 stacjodni
### wyprzedzenie k=2: n=4551
- wg przedziałów prognozy (średnia zespołu): 1-3 cm: n=676, śr. prog. 1.8 cm, śr. obs 0.7 cm (obs/prog. = 0.39) | 3-6 cm: n=217, śr. prog. 4.2 cm, śr. obs 1.1 cm (obs/prog. = 0.26) | 6-10 cm: n=50, śr. prog. 7.6 cm, śr. obs 2.1 cm (obs/prog. = 0.28)
- próg 5 cm (zdarzeń 113):
    g=1.0, alarm przy P>=30%: POD 0.16, FAR 0.90, CSI 0.07, fałszywych 156; na dobach bez zdarzenia 21.9 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.10, FAR 0.86, CSI 0.06, fałszywych 66; na dobach bez zdarzenia 7.2 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.12, FAR 0.87, CSI 0.07, fałszywych 95; na dobach bez zdarzenia 12.0 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.08, FAR 0.76, CSI 0.06, fałszywych 28; na dobach bez zdarzenia 3.7 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.10, FAR 0.78, CSI 0.07, fałszywych 39; na dobach bez zdarzenia 5.1 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.04, FAR 0.71, CSI 0.03, fałszywych 10; na dobach bez zdarzenia 1.1 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.07, FAR 0.76, CSI 0.06, fałszywych 25; na dobach bez zdarzenia 3.2 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.01, FAR 0.67, CSI 0.01, fałszywych 2; na dobach bez zdarzenia 0.3 na 1000 stacjodni
- próg 10 cm (zdarzeń 18):
    g=1.0, alarm przy P>=30%: POD 0.06, FAR 0.97, CSI 0.02, fałszywych 32; na dobach bez zdarzenia 4.1 na 1000 stacjodni
    g=1.0, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 3; na dobach bez zdarzenia 0.5 na 1000 stacjodni
    g=0.8, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 12; na dobach bez zdarzenia 1.6 na 1000 stacjodni
    g=0.8, alarm przy P>=50%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 1; na dobach bez zdarzenia 0.2 na 1000 stacjodni
    g=0.6, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 1; na dobach bez zdarzenia 0.2 na 1000 stacjodni
    g=0.6, alarm przy P>=50%: POD 0.00, FAR 0.00, CSI 0.00, fałszywych 0; na dobach bez zdarzenia 0.0 na 1000 stacjodni
    g=0.5, alarm przy P>=30%: POD 0.00, FAR 1.00, CSI 0.00, fałszywych 1; na dobach bez zdarzenia 0.2 na 1000 stacjodni
    g=0.5, alarm przy P>=50%: POD 0.00, FAR 0.00, CSI 0.00, fałszywych 0; na dobach bez zdarzenia 0.0 na 1000 stacjodni

## 11. Mróz — test wygładzenia rozrzutu odtwarzający planowaną zmianę produkcyjną (stałe sigma wg wyprzedzenia)
Sigma całkowita wg wyprzedzenia: {0: 2.35, 1: 2.59, 2: 2.78}. Środek = temperatura członka + korekta produkcyjna -1.0 C. w = waga wygładzenia (0 = obecna produkcja). Doby bez zdarzenia = zdarzenie (TMIN <= próg) na <= 1 stacji. 'fałsz. bez zdarz.' = fałszywe alarmy na 1000 stacjodni z tych dób.
### wyprzedzenie k=0: n=5237, sigma całkowita 2.35 C, średni dodany rozrzut 2.13 C
- próg -5 C (zdarzeń 1135):
    w=0.00 (produkcja): P>=10%: POD 0.94 FAR 0.30 CSI 0.67 fałsz. bez zdarz. 38.8 | P>=20%: POD 0.94 FAR 0.28 CSI 0.69 fałsz. bez zdarz. 29.6 | P>=30%: POD 0.93 FAR 0.26 CSI 0.70 fałsz. bez zdarz. 26.2 | P>=50%: POD 0.91 FAR 0.21 CSI 0.73 fałsz. bez zdarz. 12.9
    w=0.50: P>=10%: POD 0.97 FAR 0.38 CSI 0.61 fałsz. bez zdarz. 77.3 | P>=20%: POD 0.96 FAR 0.31 CSI 0.67 fałsz. bez zdarz. 40.5 | P>=30%: POD 0.94 FAR 0.27 CSI 0.69 fałsz. bez zdarz. 27.2 | P>=50%: POD 0.91 FAR 0.21 CSI 0.74 fałsz. bez zdarz. 14.0
    w=0.75: P>=10%: POD 0.99 FAR 0.45 CSI 0.55 fałsz. bez zdarz. 116.5 | P>=20%: POD 0.97 FAR 0.35 CSI 0.63 fałsz. bez zdarz. 61.3 | P>=30%: POD 0.95 FAR 0.29 CSI 0.68 fałsz. bez zdarz. 32.0 | P>=50%: POD 0.91 FAR 0.21 CSI 0.74 fałsz. bez zdarz. 14.0
    w=1.00: P>=10%: POD 0.99 FAR 0.53 CSI 0.47 fałsz. bez zdarz. 192.1 | P>=20%: POD 0.98 FAR 0.40 CSI 0.59 fałsz. bez zdarz. 87.2 | P>=30%: POD 0.96 FAR 0.32 CSI 0.66 fałsz. bez zdarz. 44.6 | P>=50%: POD 0.91 FAR 0.21 CSI 0.74 fałsz. bez zdarz. 14.0
- próg -10 C (zdarzeń 472):
    w=0.00 (produkcja): P>=10%: POD 0.91 FAR 0.36 CSI 0.60 fałsz. bez zdarz. 10.2 | P>=20%: POD 0.89 FAR 0.33 CSI 0.62 fałsz. bez zdarz. 8.3 | P>=30%: POD 0.86 FAR 0.31 CSI 0.62 fałsz. bez zdarz. 7.8 | P>=50%: POD 0.77 FAR 0.25 CSI 0.61 fałsz. bez zdarz. 5.4
    w=0.50: P>=10%: POD 0.95 FAR 0.43 CSI 0.56 fałsz. bez zdarz. 13.2 | P>=20%: POD 0.92 FAR 0.37 CSI 0.60 fałsz. bez zdarz. 10.0 | P>=30%: POD 0.87 FAR 0.32 CSI 0.61 fałsz. bez zdarz. 8.3 | P>=50%: POD 0.77 FAR 0.24 CSI 0.62 fałsz. bez zdarz. 4.9
    w=0.75: P>=10%: POD 0.96 FAR 0.48 CSI 0.51 fałsz. bez zdarz. 16.3 | P>=20%: POD 0.93 FAR 0.39 CSI 0.58 fałsz. bez zdarz. 10.5 | P>=30%: POD 0.89 FAR 0.34 CSI 0.61 fałsz. bez zdarz. 9.0 | P>=50%: POD 0.78 FAR 0.24 CSI 0.62 fałsz. bez zdarz. 4.6
    w=1.00: P>=10%: POD 0.99 FAR 0.52 CSI 0.48 fałsz. bez zdarz. 22.2 | P>=20%: POD 0.95 FAR 0.43 CSI 0.55 fałsz. bez zdarz. 12.9 | P>=30%: POD 0.91 FAR 0.36 CSI 0.60 fałsz. bez zdarz. 9.0 | P>=50%: POD 0.78 FAR 0.24 CSI 0.62 fałsz. bez zdarz. 4.9
- próg -15 C (zdarzeń 108):
    w=0.00 (produkcja): P>=10%: POD 0.78 FAR 0.54 CSI 0.40 fałsz. bez zdarz. 3.4 | P>=20%: POD 0.75 FAR 0.52 CSI 0.41 fałsz. bez zdarz. 2.4 | P>=30%: POD 0.72 FAR 0.49 CSI 0.42 fałsz. bez zdarz. 2.2 | P>=50%: POD 0.66 FAR 0.38 CSI 0.47 fałsz. bez zdarz. 0.9
    w=0.50: P>=10%: POD 0.79 FAR 0.59 CSI 0.37 fałsz. bez zdarz. 4.1 | P>=20%: POD 0.77 FAR 0.54 CSI 0.40 fałsz. bez zdarz. 2.6 | P>=30%: POD 0.73 FAR 0.50 CSI 0.42 fałsz. bez zdarz. 2.2 | P>=50%: POD 0.64 FAR 0.39 CSI 0.45 fałsz. bez zdarz. 0.6
    w=0.75: P>=10%: POD 0.81 FAR 0.62 CSI 0.35 fałsz. bez zdarz. 5.0 | P>=20%: POD 0.78 FAR 0.55 CSI 0.40 fałsz. bez zdarz. 3.2 | P>=30%: POD 0.74 FAR 0.50 CSI 0.43 fałsz. bez zdarz. 1.9 | P>=50%: POD 0.63 FAR 0.39 CSI 0.45 fałsz. bez zdarz. 0.6
    w=1.00: P>=10%: POD 0.81 FAR 0.66 CSI 0.32 fałsz. bez zdarz. 6.5 | P>=20%: POD 0.78 FAR 0.58 CSI 0.37 fałsz. bez zdarz. 3.4 | P>=30%: POD 0.75 FAR 0.51 CSI 0.42 fałsz. bez zdarz. 1.9 | P>=50%: POD 0.64 FAR 0.37 CSI 0.46 fałsz. bez zdarz. 0.6
### wyprzedzenie k=1: n=5290, sigma całkowita 2.59 C, średni dodany rozrzut 2.35 C
- próg -5 C (zdarzeń 1159):
    w=0.00 (produkcja): P>=10%: POD 0.94 FAR 0.28 CSI 0.69 fałsz. bez zdarz. 52.4 | P>=20%: POD 0.93 FAR 0.25 CSI 0.71 fałsz. bez zdarz. 40.0 | P>=30%: POD 0.93 FAR 0.22 CSI 0.74 fałsz. bez zdarz. 29.3 | P>=50%: POD 0.91 FAR 0.18 CSI 0.76 fałsz. bez zdarz. 15.7
    w=0.50: P>=10%: POD 0.97 FAR 0.36 CSI 0.62 fałsz. bez zdarz. 96.2 | P>=20%: POD 0.95 FAR 0.29 CSI 0.68 fałsz. bez zdarz. 57.7 | P>=30%: POD 0.94 FAR 0.24 CSI 0.72 fałsz. bez zdarz. 35.8 | P>=50%: POD 0.91 FAR 0.18 CSI 0.76 fałsz. bez zdarz. 16.3
    w=0.75: P>=10%: POD 0.98 FAR 0.43 CSI 0.57 fałsz. bez zdarz. 141.5 | P>=20%: POD 0.96 FAR 0.33 CSI 0.65 fałsz. bez zdarz. 80.5 | P>=30%: POD 0.94 FAR 0.27 CSI 0.70 fałsz. bez zdarz. 46.8 | P>=50%: POD 0.91 FAR 0.18 CSI 0.76 fałsz. bez zdarz. 16.6
    w=1.00: P>=10%: POD 0.99 FAR 0.52 CSI 0.47 fałsz. bez zdarz. 239.9 | P>=20%: POD 0.97 FAR 0.38 CSI 0.61 fałsz. bez zdarz. 107.8 | P>=30%: POD 0.95 FAR 0.29 CSI 0.68 fałsz. bez zdarz. 56.6 | P>=50%: POD 0.91 FAR 0.18 CSI 0.76 fałsz. bez zdarz. 16.9
- próg -10 C (zdarzeń 484):
    w=0.00 (produkcja): P>=10%: POD 0.86 FAR 0.42 CSI 0.53 fałsz. bez zdarz. 7.7 | P>=20%: POD 0.84 FAR 0.39 CSI 0.55 fałsz. bez zdarz. 6.4 | P>=30%: POD 0.82 FAR 0.36 CSI 0.56 fałsz. bez zdarz. 5.4 | P>=50%: POD 0.69 FAR 0.31 CSI 0.53 fałsz. bez zdarz. 3.7
    w=0.50: P>=10%: POD 0.91 FAR 0.45 CSI 0.52 fałsz. bez zdarz. 8.7 | P>=20%: POD 0.87 FAR 0.40 CSI 0.55 fałsz. bez zdarz. 7.2 | P>=30%: POD 0.82 FAR 0.38 CSI 0.55 fałsz. bez zdarz. 6.4 | P>=50%: POD 0.69 FAR 0.31 CSI 0.53 fałsz. bez zdarz. 3.7
    w=0.75: P>=10%: POD 0.95 FAR 0.50 CSI 0.49 fałsz. bez zdarz. 12.9 | P>=20%: POD 0.89 FAR 0.43 CSI 0.53 fałsz. bez zdarz. 8.7 | P>=30%: POD 0.84 FAR 0.38 CSI 0.55 fałsz. bez zdarz. 6.7 | P>=50%: POD 0.70 FAR 0.31 CSI 0.53 fałsz. bez zdarz. 3.5
    w=1.00: P>=10%: POD 0.98 FAR 0.54 CSI 0.45 fałsz. bez zdarz. 19.8 | P>=20%: POD 0.92 FAR 0.46 CSI 0.52 fałsz. bez zdarz. 9.9 | P>=30%: POD 0.87 FAR 0.40 CSI 0.55 fałsz. bez zdarz. 7.4 | P>=50%: POD 0.70 FAR 0.31 CSI 0.53 fałsz. bez zdarz. 3.5
- próg -15 C (zdarzeń 100):
    w=0.00 (produkcja): P>=10%: POD 0.73 FAR 0.65 CSI 0.31 fałsz. bez zdarz. 7.9 | P>=20%: POD 0.69 FAR 0.63 CSI 0.32 fałsz. bez zdarz. 6.8 | P>=30%: POD 0.69 FAR 0.59 CSI 0.35 fałsz. bez zdarz. 5.3 | P>=50%: POD 0.62 FAR 0.50 CSI 0.38 fałsz. bez zdarz. 3.4
    w=0.50: P>=10%: POD 0.76 FAR 0.68 CSI 0.29 fałsz. bez zdarz. 8.7 | P>=20%: POD 0.71 FAR 0.63 CSI 0.32 fałsz. bez zdarz. 7.0 | P>=30%: POD 0.69 FAR 0.60 CSI 0.34 fałsz. bez zdarz. 5.3 | P>=50%: POD 0.63 FAR 0.50 CSI 0.39 fałsz. bez zdarz. 3.4
    w=0.75: P>=10%: POD 0.76 FAR 0.71 CSI 0.26 fałsz. bez zdarz. 10.4 | P>=20%: POD 0.72 FAR 0.65 CSI 0.31 fałsz. bez zdarz. 7.5 | P>=30%: POD 0.69 FAR 0.60 CSI 0.34 fałsz. bez zdarz. 5.5 | P>=50%: POD 0.62 FAR 0.50 CSI 0.38 fałsz. bez zdarz. 3.4
    w=1.00: P>=10%: POD 0.76 FAR 0.74 CSI 0.24 fałsz. bez zdarz. 12.1 | P>=20%: POD 0.75 FAR 0.67 CSI 0.30 fałsz. bez zdarz. 7.9 | P>=30%: POD 0.70 FAR 0.63 CSI 0.32 fałsz. bez zdarz. 6.4 | P>=50%: POD 0.62 FAR 0.51 CSI 0.38 fałsz. bez zdarz. 3.4
### wyprzedzenie k=2: n=5292, sigma całkowita 2.78 C, średni dodany rozrzut 2.45 C
- próg -5 C (zdarzeń 1036):
    w=0.00 (produkcja): P>=10%: POD 0.94 FAR 0.36 CSI 0.61 fałsz. bez zdarz. 73.4 | P>=20%: POD 0.92 FAR 0.32 CSI 0.64 fałsz. bez zdarz. 53.6 | P>=30%: POD 0.91 FAR 0.27 CSI 0.68 fałsz. bez zdarz. 36.1 | P>=50%: POD 0.88 FAR 0.20 CSI 0.72 fałsz. bez zdarz. 18.9
    w=0.50: P>=10%: POD 0.96 FAR 0.45 CSI 0.54 fałsz. bez zdarz. 123.4 | P>=20%: POD 0.94 FAR 0.36 CSI 0.62 fałsz. bez zdarz. 72.5 | P>=30%: POD 0.93 FAR 0.30 CSI 0.66 fałsz. bez zdarz. 46.7 | P>=50%: POD 0.88 FAR 0.20 CSI 0.72 fałsz. bez zdarz. 19.2
    w=0.75: P>=10%: POD 0.98 FAR 0.51 CSI 0.48 fałsz. bez zdarz. 174.9 | P>=20%: POD 0.95 FAR 0.41 CSI 0.57 fałsz. bez zdarz. 101.2 | P>=30%: POD 0.94 FAR 0.33 CSI 0.65 fałsz. bez zdarz. 56.8 | P>=50%: POD 0.88 FAR 0.20 CSI 0.72 fałsz. bez zdarz. 20.1
    w=1.00: P>=10%: POD 0.99 FAR 0.60 CSI 0.40 fałsz. bez zdarz. 281.7 | P>=20%: POD 0.97 FAR 0.47 CSI 0.53 fałsz. bez zdarz. 135.2 | P>=30%: POD 0.94 FAR 0.36 CSI 0.62 fałsz. bez zdarz. 71.0 | P>=50%: POD 0.88 FAR 0.20 CSI 0.72 fałsz. bez zdarz. 19.8
- próg -10 C (zdarzeń 427):
    w=0.00 (produkcja): P>=10%: POD 0.89 FAR 0.43 CSI 0.54 fałsz. bez zdarz. 13.1 | P>=20%: POD 0.86 FAR 0.38 CSI 0.56 fałsz. bez zdarz. 9.5 | P>=30%: POD 0.82 FAR 0.36 CSI 0.56 fałsz. bez zdarz. 7.1 | P>=50%: POD 0.71 FAR 0.32 CSI 0.54 fałsz. bez zdarz. 3.6
    w=0.50: P>=10%: POD 0.93 FAR 0.46 CSI 0.51 fałsz. bez zdarz. 17.8 | P>=20%: POD 0.89 FAR 0.39 CSI 0.56 fałsz. bez zdarz. 10.2 | P>=30%: POD 0.83 FAR 0.36 CSI 0.56 fałsz. bez zdarz. 7.4 | P>=50%: POD 0.71 FAR 0.32 CSI 0.53 fałsz. bez zdarz. 3.8
    w=0.75: P>=10%: POD 0.95 FAR 0.50 CSI 0.48 fałsz. bez zdarz. 22.6 | P>=20%: POD 0.91 FAR 0.42 CSI 0.55 fałsz. bez zdarz. 12.6 | P>=30%: POD 0.85 FAR 0.37 CSI 0.57 fałsz. bez zdarz. 7.6 | P>=50%: POD 0.71 FAR 0.32 CSI 0.53 fałsz. bez zdarz. 3.8
    w=1.00: P>=10%: POD 0.98 FAR 0.54 CSI 0.45 fałsz. bez zdarz. 31.6 | P>=20%: POD 0.93 FAR 0.46 CSI 0.52 fałsz. bez zdarz. 16.4 | P>=30%: POD 0.88 FAR 0.38 CSI 0.57 fałsz. bez zdarz. 8.8 | P>=50%: POD 0.71 FAR 0.32 CSI 0.53 fałsz. bez zdarz. 3.8
- próg -15 C (zdarzeń 98):
    w=0.00 (produkcja): P>=10%: POD 0.73 FAR 0.70 CSI 0.27 fałsz. bez zdarz. 4.1 | P>=20%: POD 0.71 FAR 0.64 CSI 0.32 fałsz. bez zdarz. 2.4 | P>=30%: POD 0.67 FAR 0.60 CSI 0.34 fałsz. bez zdarz. 0.9 | P>=50%: POD 0.56 FAR 0.50 CSI 0.36 fałsz. bez zdarz. 0.4
    w=0.50: P>=10%: POD 0.77 FAR 0.72 CSI 0.26 fałsz. bez zdarz. 5.0 | P>=20%: POD 0.73 FAR 0.65 CSI 0.31 fałsz. bez zdarz. 2.4 | P>=30%: POD 0.67 FAR 0.61 CSI 0.33 fałsz. bez zdarz. 0.9 | P>=50%: POD 0.56 FAR 0.51 CSI 0.35 fałsz. bez zdarz. 0.4
    w=0.75: P>=10%: POD 0.77 FAR 0.73 CSI 0.25 fałsz. bez zdarz. 6.0 | P>=20%: POD 0.74 FAR 0.67 CSI 0.29 fałsz. bez zdarz. 2.8 | P>=30%: POD 0.67 FAR 0.62 CSI 0.32 fałsz. bez zdarz. 1.1 | P>=50%: POD 0.55 FAR 0.51 CSI 0.35 fałsz. bez zdarz. 0.4
    w=1.00: P>=10%: POD 0.77 FAR 0.76 CSI 0.22 fałsz. bez zdarz. 6.9 | P>=20%: POD 0.76 FAR 0.69 CSI 0.28 fałsz. bez zdarz. 3.2 | P>=30%: POD 0.68 FAR 0.63 CSI 0.31 fałsz. bez zdarz. 1.3 | P>=50%: POD 0.57 FAR 0.51 CSI 0.36 fałsz. bez zdarz. 0.4

## 12. Oceny probabilistyczne (CRPS, Brier — niższe = lepiej; wektory zapisane do porównania modeli parami)
### wyprzedzenie k=0
- tmin_crps_k0: n=5237, średnia 1.2772
- tmin_le5_brier_k0: n=5237, średnia 0.0521
- tmin_le10_brier_k0: n=5237, średnia 0.0336
- tmin_le15_brier_k0: n=5237, średnia 0.0107
- precip_crps_k0: n=5249, średnia 0.5577
- precip_ge1_brier_k0: n=5249, średnia 0.0918
- precip_ge5_brier_k0: n=5249, średnia 0.0355
- precip_ge10_brier_k0: n=5249, średnia 0.0135
- snow_ge1_brier_k0: n=4980, średnia 0.0906
- snow_ge3_brier_k0: n=4980, średnia 0.0531
### wyprzedzenie k=1
- tmin_crps_k1: n=5290, średnia 1.3685
- tmin_le5_brier_k1: n=5290, średnia 0.0500
- tmin_le10_brier_k1: n=5290, średnia 0.0431
- tmin_le15_brier_k1: n=5290, średnia 0.0124
- precip_crps_k1: n=5304, średnia 0.6353
- precip_ge1_brier_k1: n=5304, średnia 0.1058
- precip_ge5_brier_k1: n=5304, średnia 0.0437
- precip_ge10_brier_k1: n=5304, średnia 0.0169
- snow_ge1_brier_k1: n=5089, średnia 0.0856
- snow_ge3_brier_k1: n=5089, średnia 0.0515
### wyprzedzenie k=2
- tmin_crps_k2: n=5292, średnia 1.3587
- tmin_le5_brier_k2: n=5292, średnia 0.0492
- tmin_le10_brier_k2: n=5292, średnia 0.0357
- tmin_le15_brier_k2: n=5292, średnia 0.0117
- precip_crps_k2: n=5303, średnia 0.7219
- precip_ge1_brier_k2: n=5303, średnia 0.1182
- precip_ge5_brier_k2: n=5303, średnia 0.0494
- precip_ge10_brier_k2: n=5303, średnia 0.0199
- snow_ge1_brier_k2: n=4981, średnia 0.0806
- snow_ge3_brier_k2: n=4981, średnia 0.0453

