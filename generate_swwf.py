"""
SWWF — generowanie swwf.json.

Znajduje najnowszy DOSTĘPNY przebieg GEFS (sprawdzane na dwóch członkach — 1 i 30 —
bo synchronizacja na AWS bywa rozłożona w czasie), liczy dla każdego hazardu:
  - OPAD (mm), ŚNIEG (cm), MRÓZ (°C), SNOW SQUALLS (nagłe, gwałtowne opady śniegu)
  - oraz połączone GENERAL WINTER RISK

Hazardy MARZNĄCY DESZCZ (ICE) i ZAMIEĆ (BLIZZARD) zostały USUNIĘTE (2026-10): kalibracja na
obserwacjach IMGW (hindcast GEFS, 27 przebiegów, 1493 stacjodni) pokazała, że nie mają
wartości — gołoledź POD 0,35 przy 76% fałszywych alarmów, zamieć 94% fałszywych alarmów.

POZIOM ZAGROŻENIA — macierz prawdopodobieństwo × intensywność:
zamiast osobno klasyfikować kilka niezależnych progów po samym prawdopodobieństwie
(co ignorowało, że np. 20cm śniegu to dużo poważniejsza sytuacja niż 5cm przy tej
samej szansie wystąpienia), każdy punkt siatki dostaje JEDEN wynik. Dla KAŻDEGO z 6
progów intensywności liczymy, jaka część członków zespołu go osiąga (P(>= próg)) i
odczytujemy poziom z komórki macierzy (wiersz = to prawdopodobieństwo, kolumna = ten
próg). Ostateczny poziom to NAJWYŻSZY z sześciu odczytów — dzięki temu ogon zespołu
(np. 20% członków z dużym opadem śniegu) podnosi poziom, a nie ginie za medianą.

DLACZEGO NIE "prawdopodobieństwo względem mediany" (poprzednia wersja): wystarczy
połowa członków >= mediana z definicji, więc takie prawdopodobieństwo ZAWSZE wychodziło
>=50% i oś prawdopodobieństwa macierzy była martwa (potwierdzone backtestem 2025-12-30:
13 382 z 13 382 punktów z sygnałem w najwyższym przedziale). Obecne liczenie progowe
wykorzystuje całą macierz.

DETEKCJA HAZARDÓW (po kalibracji na obserwacjach IMGW):
  - SNOW: frakcja opadu zamarzniętego z TEMPERATURY — zimniejsza z dwóch próbek T2m
    (koniec i połowa okna 6 h), 1 przy <=1C, liniowo do 0 przy 3C (wariant "D" raportu
    kalibracji). Wygrał z CPOFP z modelu na każdym wyprzedzeniu (CSI 0,34/0,40/0,30 vs
    0,29/0,30/0,21), więc CPOFP nie jest już używane.
  - COLD: temperatura POWIETRZA (nie odczuwalna), minimum z 8 próbek na dobę, z korektą
    COLD_AIR_BIAS_C (-1,0C: obserwowane minima były średnio o ok. 1C niższe niż prognoza;
    sprawdzone walidacją krzyżową). Progi drabinki wg oficjalnych progów IMGW "silnego mrozu".
  - SNOW SQUALLS (nie weryfikowalne obserwacjami IMGW): CAPE + aktywny, w większości
    zamarznięty opad.

UWAGA: przelicznik gęstości śniegu (funkcja snow_density_ratio), progi SQUALLS
i sama macierz SWWF_MATRIX to celowo uproszczone wartości robocze — do skalibrowania
(patrz plan projektu).

UWAGA 2: produkt 0.25° (atmos.25) JEST w pełni dostępny na AWS dla wszystkich
30 członków — priority=["aws"] wymuszone wszędzie, żeby nigdy po cichu nie
spadać na zawodny NOMADS. Pobieramy tylko APCP, TMP 2 m (koniec i połowa okna) i CAPE.

UWAGA 3: polygony są wygładzane (interpolacja CIĄGŁYCH wielkości — mediany i
prawdopodobieństwa — PRZED klasyfikacją na poziomy, nie już-skategoryzowanego
wyniku), przycinane do Niemiec/Polski/Czech/Słowacji (Natural Earth, żeby nie
kolorować morza ani sąsiednich krajów), wygładzane Chaikinem (zaokrąglenie
narożników) i filtrowane z drobnych skrawków na granicach (prawdopodobne
artefakty interpolacji, nie realne obszary zagrożenia) — patrz grid_to_polygons().
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from herbie import Herbie
import numpy as np
import xarray as xr
import json
import os
import time
import matplotlib
matplotlib.use("Agg")  # bez tego matplotlib próbuje otworzyć okno, czego w GitHub Actions nie ma
import matplotlib.pyplot as plt
import geojsoncontour
import requests
from scipy.ndimage import zoom as ndimage_zoom
from shapely.geometry import shape as shapely_shape, box as shapely_box, mapping as shapely_mapping, Polygon as ShapelyPolygon, MultiPolygon as ShapelyMultiPolygon
from shapely.ops import unary_union

LAT_MIN, LAT_MAX = 46.8, 55.5   # Niemcy/Polska/Czechy/Słowacja
LON_MIN, LON_MAX = 5.5, 24.5
LON_MIN_360, LON_MAX_360 = LON_MIN % 360, LON_MAX % 360

# granice PAŃSTW (Natural Earth 10m — dokładniejsza siatka niż wcześniejsze 50m; domena
# publiczna), do przycinania hazardów TYLKO do Niemiec/Polski/Czech/Słowacji — to od razu
# wycina i morze (Bałtyk), i sąsiednie kraje (Austria, Ukraina itd.) w jednym kroku,
# więc osobna maska lądu nie jest już potrzebna
COUNTRIES_GEOJSON_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_0_countries.geojson"
TARGET_COUNTRY_ISO3 = {"DEU", "POL", "CZE", "SVK"}

# o ile zagęszczamy CIĄGŁE wielkości (mediana, prawdopodobieństwo) przed klasyfikacją
# na poziomy zagrożenia — wygładzamy dane WEJŚCIOWE, nie już-skategoryzowany wynik,
# żeby granice miały sens fizyczny, a nie tylko wizualny
POLYGON_SMOOTHING_FACTOR = 4
# minimalna powierzchnia polygonu (w stopniach²), poniżej której traktujemy go jako
# artefakt interpolacji/szum na granicy, nie realny obszar zagrożenia
MIN_POLYGON_AREA_DEG2 = 0.03
# tolerancja upraszczania geometrii (stopnie) — usuwa zbędne, mikroskopijne punkty
# na granicy polygonu bez widocznej zmiany kształtu, zmniejsza rozmiar pliku
POLYGON_SIMPLIFY_TOLERANCE = 0.01
# liczba iteracji wygładzania Chaikina (ścinanie narożników) — czysto kosmetyczne,
# zaokrągla kanciaste przejścia na bardziej "organiczne", bliżej ręcznie rysowanych map
CHAIKIN_ITERATIONS = 2

# trzy doby (DAY1/DAY2/DAY3), każda po 4 okna 6-godzinne — DAY1 to 0-24h od
# najnowszego przebiegu, DAY2 to 24-48h, DAY3 to 48-72h
DAY_WINDOWS = [
    {"label": "Dzień 1", "windows": [(0, 6), (6, 12), (12, 18), (18, 24)]},
    {"label": "Dzień 2", "windows": [(24, 30), (30, 36), (36, 42), (42, 48)]},
    {"label": "Dzień 3", "windows": [(48, 54), (54, 60), (60, 66), (66, 72)]},
]
MEMBERS = list(range(1, 31))
WARSAW_TZ = ZoneInfo("Europe/Warsaw")


def to_warsaw_iso(dt_utc):
    """Konwertuje datetime (UTC) na czas polski (automatycznie CET/CEST wg pory
    roku) i zwraca w formacie ISO z offsetem, żeby było jasne z jakiej strefy jest."""
    return dt_utc.astimezone(WARSAW_TZ).strftime("%Y-%m-%dT%H:%M:%S%z")

# SNOW SQUALLS: nagłe, gwałtowne opady śniegu o niemal burzowym charakterze —
# zupełnie nowy hazard, którego wcześniej nie mieliśmy. Nawet niewielkie CAPE ma
# znaczenie zimą (typowe wartości są dużo niższe niż latem)
SQUALL_CAPE_THRESHOLD_JKG = 50.0
MIN_PRECIP_FOR_SQUALL_MM = 0.5

# ---------- macierz SWWF: prawdopodobieństwo × intensywność -> poziom zagrożenia ----------
MATRIX_LEVEL_NAMES = ['NONE', 'SLIGHT', 'ENHANCED', 'MODERATE', 'HIGH', 'EXTREME']
MATRIX_LEVEL_COLORS = ['#ffffff', '#22c55e', '#fde047', '#fb923c', '#ef4444', '#c026d3']
MATRIX_PROB_BINS = [0, 5, 15, 30, 45, 50, 101]  # 6 przedziałów: <5,5-15,15-30,30-45,45-50,>=50

# ile członków zespołu musi osiągać dany próg intensywności, żeby traktować go jako realny
# sygnał. 1-2 członków z 30 to zwykle odstający szum, nie sygnał — a przy macierzy, w której
# niskie prawdopodobieństwo bardzo wysokiej intensywności daje HIGH/EXTREME, pojedynczy
# odstający członek zalewałby mapę. 3 z 30 = 10%. Do dostrojenia po backtestach.
MIN_MEMBERS_FOR_SIGNAL = 3

# wiersze = przedział prawdopodobieństwa (rosnąco), kolumny = przedział intensywności
# (rosnąco) -> wartość = indeks poziomu zagrożenia (1=SLIGHT .. 5=EXTREME).
#
# CELOWO intensywność jest tu dominującym czynnikiem, nie prawdopodobieństwo: kolumny 1-2
# (dwie najniższe intensywności, np. 1-10mm opadu) zostają SLIGHT NIEZALEŻNIE od
# prawdopodobieństwa — sama wysoka pewność wystąpienia nie czyni z małego opadu groźniejszego
# zjawiska. Prawdopodobieństwo działa jako modulator W RAMACH już podwyższonej intensywności
# (kolumna 3 wzwyż), nie jako samodzielny czynnik eskalujący niegroźne zjawisko.
SWWF_MATRIX = [
    [1, 1, 1, 2, 3, 4],
    [1, 1, 2, 2, 3, 4],
    [1, 1, 2, 3, 4, 5],
    [1, 1, 2, 3, 4, 5],
    [1, 1, 3, 4, 4, 5],
    [1, 1, 3, 4, 5, 5],
]

# przedziały intensywności per hazard — 7 granic definiujących 6 przedziałów (rosnąco)
SNOW_INTENSITY_BINS_CM = [1, 5, 10, 15, 20, 30, np.inf]
# MRÓZ: temperatura POWIETRZA (minimum doby). Drabinka zgodna z oficjalnymi progami IMGW dla
# "silnego mrozu": stopień 1 = od -15C do -25C, stopień 2 = od -25C do -30C, stopień 3 = poniżej
# -30C. Dwa najniższe progi (-6C, -10C) dają wg macierzy najwyżej SLIGHT (zwykły zimowy mróz);
# ENHANCED zaczyna się od -15C (= stopień 1 IMGW), HIGH od -25C, EXTREME od -30C. Dla
# porównania w 5 zimach IMGW (nizinne stacje, XII-II): TMIN <= -10C w 7% dni, <= -15C w 1,8%,
# <= -20C w 0,3%, <= -25C praktycznie nigdy.
COLD_INTENSITY_BINS_C = [-6, -10, -15, -20, -25, -30, -np.inf]   # malejąco (im zimniej, tym gorzej)
# Korekta prognozy temperatury powietrza (dodawana do T2m każdego członka przed liczeniem
# minimum): obserwowane minima IMGW były średnio o ok. 1C niższe od prognozy GEFS (liczone
# względem PROGNOZY, walidacja krzyżowa po miesiącach: poprawia wynik przy progach -5C i -10C,
# neutralna przy -15C). Stała korekta, bez rozszerzania rozrzutu zespołu (to pogarszało ogon).
COLD_AIR_BIAS_C = -1.0
# oparte o realny próg IMGW: "intensywne opady deszczu" = powyżej 30mm/24h (stopień 1),
# stopień 2 ~60-90mm, stopień 3 ~80-140mm (na podstawie faktycznych komunikatów IMGW) —
# nasze wcześniejsze przedziały eskalowały dużo wcześniej niż realny próg ostrzeżenia
PRECIP_INTENSITY_BINS_MM = [1, 10, 20, 30, 50, 80, np.inf]
SQUALL_INTENSITY_BINS_JKG = [50, 100, 150, 200, 300, 400, np.inf]  # szczytowe CAPE w oknie ze śniegiem


def snow_density_ratio(t2m_c):
    """Przelicznik gęstości śniegu (snow:liquid ratio) zależny od temperatury —
    UŻYWANY TYLKO do przeliczenia już-zamarzniętej części opadu na grubość śniegu.
    Decyzja 'czy to w ogóle śnieg' pochodzi z frakcji opadu zamarzniętego liczonej
    z temperatury (patrz main). Do skalibrowania w przyszłości."""
    return xr.where(t2m_c <= -10, 15.0,
           xr.where(t2m_c <= -5, 12.0,
           xr.where(t2m_c <= 0, 10.0, 7.0)))


def wind_chill_c(t2m_c, gust_ms):
    """Temperatura odczuwalna (wind chill, wzór NWS/Environment Canada). NIE jest używana w
    produkcji (COLD liczy temperaturę powietrza — IMGW mierzy tylko powietrze, więc odczuwalnej
    nie da się zweryfikować, a z porywów zawyżała mróz o ok. 8C); zostaje dla narzędzi
    diagnostycznych (diagnose_point.py)."""
    wind_kmh = gust_ms * 3.6
    wc = (13.12 + 0.6215 * t2m_c - 11.37 * (wind_kmh ** 0.16)
          + 0.3965 * t2m_c * (wind_kmh ** 0.16))
    valid = (t2m_c <= 10) & (wind_kmh > 4.8)
    return xr.where(valid, wc, t2m_c)


def find_latest_run():
    """Zwraca najnowszy dostępny przebieg GEFS, a gdy ten, który POWINIEN już być gotowy, jeszcze
    się nie pojawił — czeka na niego (do SWWF_WAIT_MINUTES, domyślnie 0 = bez czekania).

    Po co: cron startuje o 05/11/17/23 UTC, czyli ~5 h po przebiegu. Przebieg 00z bywa o tej
    porze jeszcze niekompletny na fxx=72 i wtedy generator cofał się na 18z z poprzedniego dnia —
    przez co archive/RRRR-MM-DD_00z.json prawie nigdy nie powstawał, a weryfikacja opadu (która
    używa WYŁĄCZNIE 00z, bo tylko jego Dzień 1 = pełna doba UTC) kończyła się błędem.
    „Powinien być gotowy" = najnowsza godzina synoptyczna (00/06/12/18) sprzed co najmniej 4 h."""
    wait_min = int(os.environ.get("SWWF_WAIT_MINUTES", "0") or 0)
    deadline = time.time() + wait_min * 60
    while True:
        run = _find_latest_run_once()
        expected = datetime.now(timezone.utc) - timedelta(hours=4)
        expected = expected.replace(minute=0, second=0, microsecond=0)
        expected -= timedelta(hours=expected.hour % 6)
        if run >= expected or time.time() >= deadline:
            if run < expected:
                print(f"UWAGA: przebieg {expected:%Y-%m-%d %Hz} nadal niedostepny po {wait_min} min — "
                      f"uzywam {run:%Y-%m-%d %Hz}", flush=True)
            return run
        print(f"Przebieg {expected:%Y-%m-%d %Hz} jeszcze niegotowy (najnowszy dostepny: "
              f"{run:%Y-%m-%d %Hz}) — czekam 5 min...", flush=True)
        time.sleep(300)


def _find_latest_run_once():
    """Szuka najnowszego przebiegu GEFS, który faktycznie już jest dostępny na AWS —
    sprawdzane na dwóch członkach (1 i 30), bo synchronizacja bywa rozłożona w czasie.

    WAŻNE: sprawdzamy gotowość na fxx=72 (nasza najdalsza potrzebna godzina, dla Dnia 3),
    nie na fxx=6 jak wcześniej — model liczy do przodu w czasie, więc dalsze godziny
    prognozy pojawiają się na AWS PÓŹNIEJ niż wczesne. Sprawdzanie tylko fxx=6 (jak
    robiliśmy, gdy liczyliśmy tylko dobę do przodu) potrafiło złapać przebieg gotowy
    na +6h, ale jeszcze nie na +72h, dając błędy "No index file was found" przy
    pobieraniu dalszych godzin."""
    now = datetime.now(timezone.utc)
    candidate = now.replace(minute=0, second=0, microsecond=0)
    candidate -= timedelta(hours=candidate.hour % 6)
    max_needed_fxx = DAY_WINDOWS[-1]["windows"][-1][1]  # najdalsza godzina, jakiej potrzebujemy (72)
    for i in range(8):
        test_time = candidate - timedelta(hours=6 * i)
        try:
            H1 = Herbie(test_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                        member=1, fxx=max_needed_fxx, priority=["aws"], verbose=False)
            H30 = Herbie(test_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                         member=30, fxx=max_needed_fxx, priority=["aws"], verbose=False)
            if H1.grib is not None and H30.grib is not None:
                return test_time
        except Exception:
            continue
    raise RuntimeError("Nie znaleziono żadnego dostępnego przebiegu GEFS w ostatnich 48h")


def xarray_with_retry(H, search, attempts=3):
    """H.xarray(...) z ponawianiem. Pojedyncze zerwania połączenia z AWS (np. "Connection reset
    by peer") albo urwany plik tymczasowy Herbie zdarzają się sporadycznie i dawniej kosztowały
    nas całego członka zespołu (2 z 30 w przebiegu 2026-10-06 12z). Ponowienie jednego żądania
    jest tanie, utrata członka — nie."""
    last_error = None
    for i in range(attempts):
        try:
            return H.xarray(search, remove_grib=True)
        except Exception as e:
            last_error = e
            time.sleep(2 * (i + 1))
    raise last_error


def crop_to_region(da):
    lat = da.latitude
    if float(lat[0]) > float(lat[-1]):
        lat_slice = slice(LAT_MAX, LAT_MIN)
    else:
        lat_slice = slice(LAT_MIN, LAT_MAX)
    return da.sel(latitude=lat_slice, longitude=slice(LON_MIN_360, LON_MAX_360))


def build_country_mask():
    """Pobiera granice państw (Natural Earth) i buduje jedną geometrię (unię) tylko
    z Niemiec/Polski/Czech/Słowacji — to jednocześnie wycina morze (Bałtyk) i sąsiednie
    kraje (Austria, Ukraina itd.), bez potrzeby osobnej maski lądu."""
    resp = requests.get(COUNTRIES_GEOJSON_URL, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    relevant = [shapely_shape(f["geometry"]) for f in data["features"]
                if f["properties"].get("ISO_A3") in TARGET_COUNTRY_ISO3]
    return unary_union(relevant)


def _chaikin_smooth_coords(coords, iterations=CHAIKIN_ITERATIONS):
    """Wygładzanie Chaikina — zaokrągla naroża przez iteracyjne "ścinanie" rogów.
    Czysto kosmetyczne: nie zmienia danych, tylko sposób rysowania granicy."""
    pts = list(coords)
    is_closed = len(pts) > 1 and pts[0] == pts[-1]
    if is_closed:
        pts = pts[:-1]
    for _ in range(iterations):
        new_pts = []
        n = len(pts)
        if n < 3:
            return coords  # za mało punktów, żeby to miało sens
        for i in range(n):
            p0, p1 = pts[i], pts[(i + 1) % n]
            q = (0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1])
            r = (0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1])
            new_pts.extend([q, r])
        pts = new_pts
    if is_closed:
        pts = pts + [pts[0]]
    return pts


def chaikin_smooth_geometry(geom):
    """Stosuje wygładzanie Chaikina do zewnętrznej granicy i dziur każdego wielokąta
    (obsługuje zarówno Polygon jak i MultiPolygon).

    UWAGA: przy bardzo wklęsłych/skomplikowanych kształtach (np. granice państw)
    samo ścinanie rogów może czasem stworzyć samoprzecinającą się (nieprawidłową)
    geometrię — naprawiamy to przez buffer(0) (standardowa sztuczka shapely), a jeśli
    i to zawiedzie, bezpiecznie wracamy do ORYGINALNEGO (niewygładzonego) kształtu
    dla tego konkretnego wielokąta, zamiast wywalać cały skrypt."""
    def smooth_one(poly):
        exterior = _chaikin_smooth_coords(list(poly.exterior.coords))
        interiors = [_chaikin_smooth_coords(list(ring.coords)) for ring in poly.interiors]
        candidate = ShapelyPolygon(exterior, interiors)
        if not candidate.is_valid:
            candidate = candidate.buffer(0)
        if candidate.is_empty or not candidate.is_valid:
            return poly  # bezpieczny fallback: oryginalny, niewygładzony kształt
        return candidate

    if geom.geom_type == "Polygon":
        return smooth_one(geom)
    elif geom.geom_type == "MultiPolygon":
        smoothed = [smooth_one(p) for p in geom.geoms]
        # smooth_one może czasem zwrócić MultiPolygon po buffer(0) — spłaszczamy
        flat = []
        for g in smoothed:
            if g.geom_type == "MultiPolygon":
                flat.extend(g.geoms)
            else:
                flat.append(g)
        return ShapelyMultiPolygon(flat)
    return geom



def grid_to_polygons(lats, lons, level_idx_grid, country_mask=None):
    """Zamienia JUŻ WYGŁADZONĄ siatkę indeksów poziomu zagrożenia (0-5) na gotowe
    polygony GeoJSON: 1) kontury, 2) przycięcie do Niemiec/Polski/Czech/Słowacji
    (wycina morze i sąsiednie kraje jednym krokiem), 3) wygładzanie Chaikina
    (zaokrąglenie narożników — kosmetyczne), 4) uproszczenie geometrii (mniej
    zbędnych punktów), 5) odrzucenie drobnych, prawdopodobnie fałszywych skrawków.

    UWAGA: samo wygładzanie DANYCH dzieje się WCZEŚNIEJ, w classify_hazard() — na
    ciągłych wielkościach (mediana, prawdopodobieństwo) przed klasyfikacją na poziomy,
    nie tutaj na już-skategoryzowanym wyniku. Wygładzanie Chaikina TUTAJ to coś innego —
    czysto kosmetyczne zaokrąglenie już poprawnie wyznaczonej granicy."""
    arr = np.array(level_idx_grid, dtype=float)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    try:
        bounds = [i - 0.5 for i in range(len(MATRIX_LEVEL_NAMES) + 1)]  # -0.5 .. 5.5
        cs = ax.contourf(lons, lats, arr, levels=bounds, colors=MATRIX_LEVEL_COLORS)
        geojson_str = geojsoncontour.contourf_to_geojson(contourf=cs, ndigits=3, fill_opacity=0.5)
    finally:
        plt.close(fig)

    data = json.loads(geojson_str)
    features_out = []
    for feature in data.get("features", []):
        title = feature["properties"].get("title", "")
        try:
            lower_bound = float(title.split("-")[0].strip())
        except (ValueError, IndexError):
            lower_bound = -0.5
        idx = max(0, min(len(MATRIX_LEVEL_NAMES) - 1, int(round(lower_bound + 0.5))))
        level_name = MATRIX_LEVEL_NAMES[idx]
        if level_name == "NONE":
            continue

        geom = shapely_shape(feature["geometry"])

        # --- przycinamy do Niemiec/Polski/Czech/Słowacji (wycina morze i sąsiadów) ---
        if country_mask is not None:
            geom = geom.intersection(country_mask)
            if geom.is_empty:
                continue

        # --- wygładzanie Chaikina: zaokrąglamy naroża (czysto kosmetyczne) ---
        geom = chaikin_smooth_geometry(geom)
        if geom.is_empty:
            continue

        # --- upraszczamy geometrię: mniej zbędnych punktów, ten sam kształt ---
        geom = geom.simplify(POLYGON_SIMPLIFY_TOLERANCE, preserve_topology=True)
        if geom.is_empty:
            continue

        # --- odrzucamy drobne skrawki (artefakty interpolacji na granicach) ---
        if geom.geom_type == "MultiPolygon":
            kept = [g for g in geom.geoms if g.area >= MIN_POLYGON_AREA_DEG2]
            if not kept:
                continue
            geom = kept[0] if len(kept) == 1 else unary_union(kept)
        elif geom.area < MIN_POLYGON_AREA_DEG2:
            continue

        feature["geometry"] = shapely_mapping(geom)
        feature["properties"]["level"] = level_name
        features_out.append(feature)

    return {"type": "FeatureCollection", "features": features_out}


def _bucket_by_bins(values, bin_edges):
    """Przydziela każdą wartość do jednego z 6 przedziałów (0-5) wg rosnących granic
    (7 elementów), albo -1 gdy poniżej najniższej granicy."""
    idx = np.full(values.shape, -1, dtype=int)
    for i in range(6):
        lo, hi = bin_edges[i], bin_edges[i + 1]
        mask = (values >= lo) if i == 5 else ((values >= lo) & (values < hi))
        idx[mask] = i
    return idx


def _bucket_prob(prob):
    idx = np.zeros(prob.shape, dtype=int)
    for i in range(6):
        lo, hi = MATRIX_PROB_BINS[i], MATRIX_PROB_BINS[i + 1]
        mask = (prob >= lo) if i == 5 else ((prob >= lo) & (prob < hi))
        idx[mask] = i
    return idx


def _apply_matrix(intensity_idx, prob_idx):
    matrix_np = np.array(SWWF_MATRIX)
    level_idx = np.zeros(intensity_idx.shape, dtype=int)
    has_signal = intensity_idx >= 0
    level_idx[has_signal] = matrix_np[prob_idx[has_signal], intensity_idx[has_signal]]
    return level_idx


def _threshold_levels(prob_stack, n_members):
    """Poziom zagrożenia z KAŻDEGO z 6 progów intensywności, a z nich najwyższy.

    prob_stack: (6, lat, lon) — P(>= dolna granica k-tego przedziału) w %, k=0..5.
    Dla progu k odczytujemy komórkę macierzy (wiersz = przedział tego prawdopodobieństwa,
    kolumna = k), o ile próg osiąga co najmniej MIN_MEMBERS_FOR_SIGNAL członków.

    Zwraca: level (lat, lon) 0-5, k_star (lat, lon) — numer progu, który zdecydował
    (przy remisie poziomów wygrywa większe prawdopodobieństwo)."""
    min_prob = MIN_MEMBERS_FOR_SIGNAL / n_members * 100.0
    matrix_np = np.array(SWWF_MATRIX)
    level_k = np.zeros(prob_stack.shape, dtype=int)
    for k in range(6):
        cell = matrix_np[_bucket_prob(prob_stack[k]), k]
        level_k[k] = np.where(prob_stack[k] >= min_prob - 1e-9, cell, 0)
    k_star = np.argmax(level_k * 1000.0 + prob_stack, axis=0)
    level = np.take_along_axis(level_k, k_star[None, :, :], axis=0)[0]
    return level, k_star


def classify_hazard(stacked, intensity_bins, lats, lons, direction="ge"):
    """Serce systemu SWWF: łączy prawdopodobieństwo i intensywność w jeden poziom.

    stacked: xr.DataArray (member, lat, lon)
    intensity_bins: 7 granic (rosnąco) definiujących 6 przedziałów intensywności
    direction="ge": więcej/wyżej = gorzej (opad, śnieg, SQUALLS)
    direction="le": mniej/niżej = gorzej (mróz — ujemne temperatury)

    Dla każdego z 6 progów liczymy P(>= próg) po członkach zespołu i bierzemy najwyższy
    poziom z macierzy (patrz _threshold_levels). Mediana zespołu NIE decyduje o poziomie —
    jest tylko informacją pokazywaną w popupie.

    WAŻNE: wygładzanie (zagęszczanie siatki) dzieje się TUTAJ, na CIĄGŁYCH wielkościach
    (prawdopodobieństwa progowe) — PRZED klasyfikacją na poziomy, nie po niej.
    Uśrednianie już-skategoryzowanych poziomów (SLIGHT/MODERATE/...) nie miałoby
    dobrej interpretacji fizycznej — to tylko liczby porządkowe, nie ciągła skala.

    Zwraca:
      level_idx_native (lista list) — do zapisu w JSON / podglądu surowej siatki
      median_native (lista list) — mediana zespołu w realnych jednostkach, do JSON
      level_idx_smooth, lats_smooth, lons_smooth — wygładzona wersja, do polygonów
      prob_native — P(>= decydujący próg) w %, a bez sygnału P(>= najniższy próg)
      intensity_idx_out — numer decydującego przedziału 1-6 (0 = brak sygnału)
      prob_bin_out — przedział prawdopodobieństwa 1-6 decydującej komórki macierzy
    """
    values = np.asarray(stacked.values)  # (member, lat, lon)
    n_members = values.shape[0]

    if direction == "le":
        work = -values
        bins = [-b for b in intensity_bins]
    else:
        work = values
        bins = list(intensity_bins)

    # P(>= próg k) w %, dla k = 0..5 — to jedyna wielkość, od której zależy poziom
    prob_stack = np.stack([(work >= bins[k]).mean(axis=0) * 100.0 for k in range(6)], axis=0)

    # --- wersja natywna (do JSON / podglądu surowej siatki) ---
    level_native, k_star = _threshold_levels(prob_stack, n_members)
    has_signal = level_native > 0
    prob_deciding = np.take_along_axis(prob_stack, k_star[None, :, :], axis=0)[0]
    prob_shown = np.where(has_signal, prob_deciding, prob_stack[0])
    real_median = np.median(values.astype(np.float64), axis=0)

    # --- wygładzanie: zagęszczamy prawdopodobieństwa progowe, DOPIERO PÓŹNIEJ klasyfikujemy ---
    prob_stack_smooth = np.stack(
        [np.clip(ndimage_zoom(prob_stack[k], POLYGON_SMOOTHING_FACTOR, order=3, mode="nearest"), 0, 100)
         for k in range(6)], axis=0)
    level_smooth, _ = _threshold_levels(prob_stack_smooth, n_members)
    lats_smooth = np.linspace(lats[0], lats[-1], prob_stack_smooth.shape[1])
    lons_smooth = np.linspace(lons[0], lons[-1], prob_stack_smooth.shape[2])

    # zapisujemy SUROWE prawdopodobieństwo i przedziały (indeksy 1-6) decydującej komórki
    # macierzy — potrzebne do interaktywnego popupu na mapie (klik na polygon pokazuje
    # macierz z zaznaczoną dokładną komórką, która zdecydowała o poziomie)
    intensity_idx_out = np.where(has_signal, k_star + 1, 0)
    prob_bin_out = _bucket_prob(prob_shown) + 1

    return (level_native.tolist(), np.round(real_median, 1).tolist(), level_smooth,
            lats_smooth, lons_smooth, np.round(prob_shown, 0).astype(int).tolist(),
            intensity_idx_out.tolist(), prob_bin_out.tolist())


def combine_general_risk(snow_idx, cold_idx, squall_idx):
    """GENERAL WINTER RISK — celowo NIE prosta suma: bazowy poziom to NAJGROŹNIEJSZY
    z trzech hazardów w danym punkcie, ale jeśli co najmniej DWA jednocześnie
    osiągają ENHANCED (indeks >=2) lub wyżej, całość podbijamy o jeden poziom."""
    arrs = [np.array(x) for x in (snow_idx, cold_idx, squall_idx)]
    max_idx = np.maximum.reduce(arrs)
    compound_count = sum((a >= 2).astype(int) for a in arrs)
    bump = (compound_count >= 2).astype(int)
    general_idx = np.minimum(max_idx + bump, len(MATRIX_LEVEL_NAMES) - 1)
    return general_idx.tolist()


def main():
    run_time = find_latest_run()
    print(f"Używam przebiegu: {run_time.isoformat()}")

    print("Pobieram granice lądu (Natural Earth)...")
    country_mask = build_country_mask()
    print(f"Maska panstw gotowa ({country_mask.geom_type})")

    # zbieramy osobno dla każdej z trzech dób — precip_member_grids[0] to DAY1, [1] DAY2, [2] DAY3
    precip_member_grids = [[] for _ in DAY_WINDOWS]
    snow_member_grids = [[] for _ in DAY_WINDOWS]
    cold_member_grids = [[] for _ in DAY_WINDOWS]
    squall_cape_member_grids = [[] for _ in DAY_WINDOWS]
    failed = []
    lats = lons = None

    for m in MEMBERS:
        # wyniki członka trzymamy osobno i dopisujemy do wspólnych list DOPIERO, gdy udały się
        # wszystkie doby — częściowo pobrany członek nie rozjeżdża liczności między dobami
        staged = []
        try:
            for day_idx, day_info in enumerate(DAY_WINDOWS):
                precip_total = None
                snow_total = None
                min_air_c = None
                squall_max_cape = None
                for start, end in day_info["windows"]:
                    fxx = end
                    mid_fxx = start + 3

                    H_p = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                                 member=m, fxx=fxx, priority=["aws"], verbose=False)
                    ds_p = xarray_with_retry(H_p, f":APCP:surface:{start}-{end} hour acc")
                    precip_window = crop_to_region(ds_p["tp"])

                    # T2m na końcu okna i w jego połowie (GEFS ma dane co 3 h) — obie próbki służą
                    # i do fazy opadu (SNOW), i do minimum temperatury (COLD): 8 próbek na dobę
                    H_t = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                                 member=m, fxx=fxx, priority=["aws"], verbose=False)
                    ds_t = xarray_with_retry(H_t, ":TMP:2 m above ground:")
                    t2m_end_c = crop_to_region(ds_t["t2m"]) - 273.15

                    H_t_mid = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                                     member=m, fxx=mid_fxx, priority=["aws"], verbose=False)
                    ds_t_mid = xarray_with_retry(H_t_mid, ":TMP:2 m above ground:")
                    t2m_mid_c = crop_to_region(ds_t_mid["t2m"]) - 273.15

                    # --- SNOW: frakcja opadu zamarzniętego z TEMPERATURY (wariant "D" kalibracji) ---
                    # zimniejsza z dwóch próbek okna: 1 przy <=1C, liniowo do 0 przy 3C. Wygrało z
                    # CPOFP z modelu na każdym wyprzedzeniu (patrz docstring), więc CPOFP nie jest
                    # już pobierane. Przelicznik gęstości liczony z T2m na końcu okna (jak dotąd).
                    t2m_coldest_c = xr.where(t2m_end_c < t2m_mid_c, t2m_end_c, t2m_mid_c)
                    frozen_fraction = ((3.0 - t2m_coldest_c) / 2.0).clip(0.0, 1.0)
                    ratio = snow_density_ratio(t2m_end_c)
                    snow_window_cm = precip_window * frozen_fraction / 10.0 * ratio

                    precip_total = precip_window if precip_total is None else precip_total + precip_window
                    snow_total = snow_window_cm if snow_total is None else snow_total + snow_window_cm

                    # --- COLD: temperatura POWIETRZA z korektą COLD_AIR_BIAS_C, minimum z 8 próbek ---
                    air_min_window = t2m_coldest_c + COLD_AIR_BIAS_C
                    min_air_c = air_min_window if min_air_c is None else \
                        xr.where(air_min_window < min_air_c, air_min_window, min_air_c)

                    # --- SNOW SQUALLS: CAPE + aktywny, w większości zamarznięty opad ---
                    H_cape = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                                    member=m, fxx=fxx, priority=["aws"], verbose=False)
                    ds_cape = xarray_with_retry(H_cape, ":CAPE:surface:")
                    cape_window = crop_to_region(ds_cape[list(ds_cape.data_vars)[0]])
                    squall_condition = (cape_window >= SQUALL_CAPE_THRESHOLD_JKG) & \
                                       (frozen_fraction >= 0.5) & \
                                       (precip_window >= MIN_PRECIP_FOR_SQUALL_MM)
                    cape_during_squall = xr.where(squall_condition, cape_window, 0.0)
                    squall_max_cape = cape_during_squall if squall_max_cape is None else \
                        xr.where(cape_during_squall > squall_max_cape, cape_during_squall, squall_max_cape)

                if lats is None:
                    lats = [round(float(x), 3) for x in precip_total.latitude.values]
                    lons = [round(float(x) - 360 if float(x) > 180 else float(x), 3) for x in precip_total.longitude.values]
                staged.append((day_idx, precip_total, snow_total, min_air_c, squall_max_cape))
            for d_idx, p_t, s_t, c_t, q_t in staged:
                precip_member_grids[d_idx].append(p_t)
                snow_member_grids[d_idx].append(s_t)
                cold_member_grids[d_idx].append(c_t)
                squall_cape_member_grids[d_idx].append(q_t)
            print(f"  człon {m:>2}: OK")
        except Exception as e:
            failed.append(m)
            print(f"  człon {m:>2}: BŁĄD ({e})")

    if not precip_member_grids[0]:
        raise RuntimeError("Żaden człon się nie udał — przerywam bez zapisu pliku")

    days_out = []
    for day_idx, day_info in enumerate(DAY_WINDOWS):
        stacked_precip = xr.concat(precip_member_grids[day_idx], dim="member")
        stacked_snow = xr.concat(snow_member_grids[day_idx], dim="member")
        stacked_cold = xr.concat(cold_member_grids[day_idx], dim="member")
        stacked_squall_cape = xr.concat(squall_cape_member_grids[day_idx], dim="member")

        precip_level, precip_median, precip_smooth, lats_s, lons_s, precip_prob, precip_iidx, precip_pidx = classify_hazard(stacked_precip, PRECIP_INTENSITY_BINS_MM, lats, lons)
        snow_level, snow_median, snow_smooth, _, _, snow_prob, snow_iidx, snow_pidx = classify_hazard(stacked_snow, SNOW_INTENSITY_BINS_CM, lats, lons)
        cold_level, cold_median, cold_smooth, _, _, cold_prob, cold_iidx, cold_pidx = classify_hazard(stacked_cold, COLD_INTENSITY_BINS_C, lats, lons, direction="le")
        squall_level, squall_median, squall_smooth, _, _, squall_prob, squall_iidx, squall_pidx = classify_hazard(stacked_squall_cape, SQUALL_INTENSITY_BINS_JKG, lats, lons)

        # combine_general_risk liczymy na WYGŁADZONYCH siatkach (ten sam kształt dla
        # wszystkich trzech, bo ten sam współczynnik zagęszczenia i ta sama siatka natywna)
        general_level = combine_general_risk(snow_level, cold_level, squall_level)
        general_smooth = combine_general_risk(snow_smooth, cold_smooth, squall_smooth)

        day_start_h, day_end_h = day_info["windows"][0][0], day_info["windows"][-1][1]
        valid_from = run_time + timedelta(hours=day_start_h)
        valid_to = run_time + timedelta(hours=day_end_h)

        days_out.append({
            "label": day_info["label"],
            "valid_from": to_warsaw_iso(valid_from),
            "valid_to": to_warsaw_iso(valid_to),
            "hazards": {
                "precip_24h_mm": {
                    "note": "Poziom zagrozenia z macierzy prawdopodobienstwo x intensywnosc (opad "
                            "wody, mm/24h), nie osobne progi.",
                    "level_grid": precip_level,
                    "median_intensity": precip_median,
                    "probability_grid": precip_prob,
                    "intensity_bin_grid": precip_iidx,
                    "probability_bin_grid": precip_pidx,
                    "areas": grid_to_polygons(lats_s, lons_s, precip_smooth, country_mask),
                },
                "snow_24h_cm": {
                    "note": "Poziom zagrozenia z macierzy prawdopodobienstwo x intensywnosc (grubosc "
                            "sniegu, cm/24h). Snieg = opad razy frakcja zamarznieta (z temperatury: "
                            "zimniejsza z dwoch probek T2m w oknie, 1 przy <=1C do 0 przy 3C) razy "
                            "przelicznik gestosci zalezny od temperatury. Wariant wybrany po kalibracji "
                            "na obserwacjach IMGW.",
                    "level_grid": snow_level,
                    "median_intensity": snow_median,
                    "probability_grid": snow_prob,
                    "intensity_bin_grid": snow_iidx,
                    "probability_bin_grid": snow_pidx,
                    "areas": grid_to_polygons(lats_s, lons_s, snow_smooth, country_mask),
                },
                "cold_min_t2m_c": {
                    "note": "Poziom zagrozenia z macierzy prawdopodobienstwo x intensywnosc (minimum "
                            "temperatury POWIETRZA z 8 odczytow co 3h w ciagu doby, z korekta -1C "
                            "wynikajaca z kalibracji na obserwacjach IMGW; progi wg oficjalnych "
                            "progow IMGW dla silnego mrozu).",
                    "level_grid": cold_level,
                    "median_intensity": cold_median,
                    "probability_grid": cold_prob,
                    "intensity_bin_grid": cold_iidx,
                    "probability_bin_grid": cold_pidx,
                    "areas": grid_to_polygons(lats_s, lons_s, cold_smooth, country_mask),
                },
                "snow_squalls": {
                    "note": "NOWY hazard - poziom zagrozenia z macierzy prawdopodobienstwo x "
                            "intensywnosc. Nagle, gwaltowne opady sniegu o niemal burzowym "
                            "charakterze. Intensywnosc = szczytowe CAPE (J/kg) w oknach gdzie "
                            f"jednoczesnie CAPE >= {SQUALL_CAPE_THRESHOLD_JKG} J/kg, opad w "
                            f"wiekszosci zamarzniety (frakcja z temperatury >= 50%) i opad >= "
                            f"{MIN_PRECIP_FOR_SQUALL_MM}mm.",
                    "level_grid": squall_level,
                    "median_intensity": squall_median,
                    "probability_grid": squall_prob,
                    "intensity_bin_grid": squall_iidx,
                    "probability_bin_grid": squall_pidx,
                    "areas": grid_to_polygons(lats_s, lons_s, squall_smooth, country_mask),
                },
                "general_winter_risk": {
                    "note": "Polaczenie SNOW+COLD+SNOW_SQUALLS w jeden wskaznik - NIE "
                            "prosta suma. Bazowy poziom to najgrozniejszy z trzech hazardow w danym "
                            "punkcie; jesli co najmniej DWA hazardy jednoczesnie osiagaja ENHANCED "
                            "lub wyzej, calosc podbijana o jeden poziom.",
                    "level_grid": general_level,
                    "areas": grid_to_polygons(lats_s, lons_s, general_smooth, country_mask),
                },
            },
        })
        print(f"  {day_info['label']}: sklasyfikowano i wygenerowano polygony")

    result = {
        "issued": to_warsaw_iso(datetime.now(timezone.utc)),
        "model_run": to_warsaw_iso(run_time),
        "members_used": len(precip_member_grids[0]),
        "members_failed": failed,
        "grid": {"lat": lats, "lon": lons},
        "level_names": MATRIX_LEVEL_NAMES,
        "level_colors": MATRIX_LEVEL_COLORS,
        "swwf_matrix": SWWF_MATRIX,
        "swwf_prob_bin_labels": ["<5", "5", "15", "30", "45", ">50"],
        "hazard_info": {
            "precip_24h_mm": {
                "description": "Suma opadu wody w ciągu doby. Przedziały intensywności oparte na "
                               "oficjalnych progach ostrzeżeń IMGW (intensywne opady deszczu "
                               "powyżej 30mm/24h to próg stopnia 1; realne komunikaty stopnia 2 "
                               "to zwykle 60-90mm, stopnia 3 nawet 80-140mm).",
                "unit": "mm / 24h",
                "intensity_bins": [b if b != float("inf") else None for b in PRECIP_INTENSITY_BINS_MM],
            },
            "snow_24h_cm": {
                "description": "Grubość świeżego śniegu w ciągu doby. Opad razy frakcja zamarznięta "
                               "(liczona z temperatury: zimniejsza z dwóch próbek T2m w oknie, 1 "
                               "przy <=1°C, liniowo do 0 przy 3°C — wariant wybrany po kalibracji na "
                               "obserwacjach IMGW) razy przelicznik gęstości zależny od temperatury. "
                               "Przedziały zbliżone do progu IMGW dla intensywnych opadów śniegu "
                               "(powyżej 15cm/24h).",
                "unit": "cm / 24h",
                "intensity_bins": [b if b != float("inf") else None for b in SNOW_INTENSITY_BINS_CM],
            },
            "cold_min_t2m_c": {
                "description": "Minimum temperatury POWIETRZA (2 m) w ciągu doby, z 8 odczytów co 3h, "
                               "z korektą -1°C wynikającą z kalibracji na obserwacjach IMGW (minima "
                               "były średnio o ok. 1°C niższe od prognozy GEFS). Drabinka zgodna z "
                               "oficjalnymi progami IMGW dla silnego mrozu: stopień 1 to -15…-25°C "
                               "(u nas od ENHANCED), stopień 2 -25…-30°C (HIGH), stopień 3 poniżej "
                               "-30°C (EXTREME). Mróz od -6°C do -15°C to najwyżej SLIGHT.",
                "unit": "°C (temperatura powietrza)",
                "intensity_bins": [b if b != float("-inf") else None for b in COLD_INTENSITY_BINS_C],
            },
            "snow_squalls": {
                "description": "Szczytowe CAPE w oknach, gdzie jednocześnie: CAPE powyżej progu, "
                               "opad w większości zamarznięty (frakcja z temperatury >=50%), i realny opad. To "
                               "zupełnie nowy hazard (nagłe, gwałtowne opady śniegu o niemal "
                               "burzowym charakterze) — IMGW nie ma takiej kategorii, przedziały "
                               "są własną, roboczą propozycją bazującą na typowych wartościach "
                               "zimowego CAPE (dużo niższych niż latem).",
                "unit": "J/kg (szczytowe CAPE)",
                "intensity_bins": [b if b != float("inf") else None for b in SQUALL_INTENSITY_BINS_JKG],
            },
        },
        "days": days_out,
    }

    with open("swwf.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # --- Archiwizacja (Faza 5 planu) — lekka kopia Dnia 1 do przyszłego porównania
    # prognoza-vs-rzeczywistość. Celowo BEZ polygonów (dużo miejsca, łatwe do odtworzenia
    # z level_grid gdyby były kiedyś potrzebne) — tylko to, co potrzebne do weryfikacji
    # liczbowej: siatka, poziomy zagrożenia i mediana intensywności per hazard.
    os.makedirs("archive", exist_ok=True)
    archive_record = {
        "issued": result["issued"],
        "model_run": result["model_run"],
        "valid_from": days_out[0]["valid_from"],
        "valid_to": days_out[0]["valid_to"],
        "grid": result["grid"],
        "hazards": {
            key: {"level_grid": h["level_grid"], "median_intensity": h.get("median_intensity")}
            for key, h in days_out[0]["hazards"].items()
        },
    }
    archive_filename = f"archive/{run_time.strftime('%Y-%m-%d_%Hz')}.json"
    with open(archive_filename, "w", encoding="utf-8") as f:
        json.dump(archive_record, f, ensure_ascii=False, indent=2)

    print(f"\nZapisano swwf.json ({len(precip_member_grids[0])}/{len(MEMBERS)} członków użytych, "
          f"{len(DAY_WINDOWS)} doby)")
    print(f"Zapisano archiwum: {archive_filename}")


if __name__ == "__main__":
    main()
