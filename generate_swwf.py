"""
SWWF — generowanie swwf.json.

Znajduje najnowszy DOSTĘPNY przebieg GEFS (sprawdzane na dwóch członkach — 1 i 30 —
bo synchronizacja na AWS bywa rozłożona w czasie), liczy dla każdego hazardu:
  - OPAD (mm), ŚNIEG (cm), MRÓZ (°C), MARZNĄCY DESZCZ (ICE), ZAMIEĆ (BLIZZARD),
    SNOW SQUALLS (nagłe, gwałtowne opady śniegu)
  - oraz połączone GENERAL WINTER RISK

POZIOM ZAGROŻENIA — styl CESTOF/ESTOFEX (macierz prawdopodobieństwo × intensywność):
zamiast osobno klasyfikować kilka niezależnych progów po samym prawdopodobieństwie
(co ignorowało, że np. 20cm śniegu to dużo poważniejsza sytuacja niż 5cm przy tej
samej szansie wystąpienia), każdy punkt siatki dostaje JEDEN wynik: mediana z ensemble
wyznacza "diagnozowaną" intensywność (1-6), a prawdopodobieństwo osiągnięcia co
najmniej tej intensywności trafia w wiersz macierzy — przecięcie obu daje ostateczny
poziom NONE/SLIGHT/ENHANCED/MODERATE/HIGH/EXTREME.

DETEKCJA HAZARDÓW — oparta na "gotowych" diagnostycznych zmiennych GEFS zamiast
naszych własnych, uproszczonych progów:
  - SNOW: CPOFP (procent opadu zamarzniętego, z mikrofizyki modelu) zamiast sztywnego
    progu T2m — płynne przejście deszcz/śnieg, nie "wszystko albo nic"
  - ICE: CFRZR (kategoryczna flaga marznącego deszczu WPROST z modelu) zamiast
    naszego dawnego, dwupoziomowego testu T2m/T850 — model sam analizuje cały
    profil pionowy
  - BLIZZARD: VIS (widzialność — prawdziwa definicja zamieci) + GUST + snieg ŚWIEŻY
    LUB JUŻ LEŻĄCY na ziemi (SNOD) — to drugie łapie "ground blizzard" (wiatr
    wzbijający stary śnieg bez nowych opadów), czego wcześniej nie wykrywaliśmy
  - SNOW SQUALLS (nowy hazard): CAPE + aktywny, w większości zamarznięty opad —
    nagłe, gwałtowne opady śniegu o niemal burzowym charakterze

Intensywność hazardów tak/nie budujemy z fizycznie powiązanych składników: dla ICE
to ilość opadu w oknach z CFRZR, dla BLIZZARD to szczytowy poryw wiatru w oknach
z zamiecią, dla SQUALLS to szczytowe CAPE w oknach z aktywnym opadem śniegu.

UWAGA: przelicznik gęstości śniegu (funkcja snow_density_ratio), progi
ICE/BLIZZARD/SQUALLS i sama macierz CESTOF_MATRIX to celowo uproszczone wartości
robocze — do skalibrowania danymi z weryfikacji (patrz plan projektu, sekcja 4, 8 i 9).

UWAGA 2: produkt 0.25° (atmos.25) JEST w pełni dostępny na AWS dla wszystkich
30 członków — priority=["aws"] wymuszone wszędzie, żeby nigdy po cichu nie
spadać na zawodny NOMADS. Wszystkie zmienne (w tym CPOFP/CFRZR/VIS/SNOD/CAPE)
są dostępne bezpośrednio w atmos.25 — osobne pobieranie T850 z atmos.5 nie jest
już potrzebne (CFRZR zastąpił nasz dawny test warm-nose).

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

# BLIZZARD: klasyczna definicja (NWS) — poryw wiatru >=35mph (~15.5 m/s) + słaba
# widzialność (śnieg unoszony/padający) — teraz naprawdę mierzona (VIS), nie zgadywana
BLIZZARD_GUST_THRESHOLD_MS = 15.5
BLIZZARD_VIS_THRESHOLD_M = 400.0            # ~1/4 mili, standardowy próg NWS
MIN_FRESH_SNOW_FOR_BLIZZARD_CM = 0.5        # świeży śnieg — klasyczny scenariusz
MIN_SNOW_DEPTH_FOR_GROUND_BLIZZARD_CM = 5.0  # ISTNIEJĄCA pokrywa — "ground blizzard"

# SNOW SQUALLS: nagłe, gwałtowne opady śniegu o niemal burzowym charakterze —
# zupełnie nowy hazard, którego wcześniej nie mieliśmy. Nawet niewielkie CAPE ma
# znaczenie zimą (typowe wartości są dużo niższe niż latem)
SQUALL_CAPE_THRESHOLD_JKG = 50.0
MIN_PRECIP_FOR_SQUALL_MM = 0.5

# ---------- macierz CESTOF: prawdopodobieństwo × intensywność -> poziom zagrożenia ----------
MATRIX_LEVEL_NAMES = ['NONE', 'SLIGHT', 'ENHANCED', 'MODERATE', 'HIGH', 'EXTREME']
MATRIX_LEVEL_COLORS = ['#ffffff', '#22c55e', '#fde047', '#fb923c', '#ef4444', '#c026d3']
MATRIX_PROB_BINS = [0, 5, 15, 30, 45, 50, 101]  # 6 przedziałów: <5,5-15,15-30,30-45,45-50,>=50

# wiersze = przedział prawdopodobieństwa (rosnąco), kolumny = przedział intensywności
# (rosnąco) -> wartość = indeks poziomu zagrożenia (1=SLIGHT .. 5=EXTREME)
CESTOF_MATRIX = [
    [1, 1, 1, 2, 2, 3],
    [1, 1, 2, 2, 3, 4],
    [1, 2, 2, 3, 3, 4],
    [2, 2, 3, 3, 4, 5],
    [2, 3, 3, 4, 4, 5],
    [2, 3, 4, 4, 5, 5],
]

# przedziały intensywności per hazard — 7 granic definiujących 6 przedziałów (rosnąco)
SNOW_INTENSITY_BINS_CM = [1, 5, 10, 15, 20, 30, np.inf]
COLD_INTENSITY_BINS_C = [-5, -8, -11, -14, -17, -20, -np.inf]  # malejąco (im zimniej, tym gorzej)
PRECIP_INTENSITY_BINS_MM = [1, 5, 10, 20, 35, 50, np.inf]
ICE_INTENSITY_BINS_MM = [0.1, 1, 2, 4, 6, 10, np.inf]           # mm opadu w warunkach marznących (CFRZR)
BLIZZARD_INTENSITY_BINS_MS = [15.5, 18, 21, 24, 28, 33, np.inf]  # szczytowy poryw, m/s
SQUALL_INTENSITY_BINS_JKG = [50, 100, 150, 200, 300, 400, np.inf]  # szczytowe CAPE w oknie ze śniegiem


def snow_density_ratio(t2m_c):
    """Przelicznik gęstości śniegu (snow:liquid ratio) zależny od temperatury —
    UŻYWANY TYLKO do przeliczenia już-zamarzniętej części opadu (wg CPOFP) na
    grubość śniegu. Sama decyzja 'czy to w ogóle śnieg' pochodzi teraz z CPOFP
    (procent opadu zamarzniętego, prosto z mikrofizyki modelu), nie z naszego
    dawnego, sztywnego progu T2m. Do skalibrowania w przyszłości."""
    return xr.where(t2m_c <= -10, 15.0,
           xr.where(t2m_c <= -5, 12.0,
           xr.where(t2m_c <= 0, 10.0, 7.0)))


def find_latest_run():
    """Szuka najnowszego przebiegu GEFS, który faktycznie już jest dostępny na AWS —
    sprawdzane na dwóch członkach (1 i 30), bo synchronizacja bywa rozłożona w czasie."""
    now = datetime.now(timezone.utc)
    candidate = now.replace(minute=0, second=0, microsecond=0)
    candidate -= timedelta(hours=candidate.hour % 6)
    for i in range(8):
        test_time = candidate - timedelta(hours=6 * i)
        try:
            H1 = Herbie(test_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                        member=1, fxx=6, priority=["aws"], verbose=False)
            H30 = Herbie(test_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                         member=30, fxx=6, priority=["aws"], verbose=False)
            if H1.grib is not None and H30.grib is not None:
                return test_time
        except Exception:
            continue
    raise RuntimeError("Nie znaleziono żadnego dostępnego przebiegu GEFS w ostatnich 48h")


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
    matrix_np = np.array(CESTOF_MATRIX)
    level_idx = np.zeros(intensity_idx.shape, dtype=int)
    has_signal = intensity_idx >= 0
    level_idx[has_signal] = matrix_np[prob_idx[has_signal], intensity_idx[has_signal]]
    return level_idx


def classify_hazard(stacked, intensity_bins, lats, lons, direction="ge"):
    """Serce systemu CESTOF: łączy prawdopodobieństwo i intensywność w jeden poziom.

    stacked: xr.DataArray (member, lat, lon)
    intensity_bins: 7 granic (rosnąco) definiujących 6 przedziałów intensywności
    direction="ge": więcej/wyżej = gorzej (opad, śnieg, ICE, BLIZZARD)
    direction="le": mniej/niżej = gorzej (mróz — ujemne temperatury)

    WAŻNE: wygładzanie (zagęszczanie siatki) dzieje się TUTAJ, na CIĄGŁYCH wielkościach
    (mediana, prawdopodobieństwo) — PRZED klasyfikacją na poziomy CESTOF, nie po niej.
    Uśrednianie już-skategoryzowanych poziomów (SLIGHT/MODERATE/...) nie miałoby
    dobrej interpretacji fizycznej — to tylko liczby porządkowe, nie ciągła skala.

    Zwraca:
      level_idx_native (lista list) — do zapisu w JSON / podglądu surowej siatki
      median_native (lista list) — zdiagnozowana intensywność, do JSON
      level_idx_smooth, lats_smooth, lons_smooth — wygładzona wersja, do polygonów
    """
    values = np.asarray(stacked.values)  # (member, lat, lon)

    if direction == "le":
        work = -values
        bins = [-b for b in intensity_bins]
    else:
        work = values
        bins = list(intensity_bins)

    median = np.median(work, axis=0)  # (lat, lon), w przestrzeni "work" (nie realnych jednostek)

    intensity_idx = _bucket_by_bins(median, bins)
    lower_bound_per_point = np.array(bins)[np.clip(intensity_idx, 0, 5)]
    prob = (work >= lower_bound_per_point[None, :, :]).mean(axis=0) * 100

    # --- wersja natywna (do JSON / podglądu surowej siatki) ---
    level_idx_native = _apply_matrix(intensity_idx, _bucket_prob(prob))
    real_median = np.median(values, axis=0)

    # --- wygładzanie: zagęszczamy medianę i prawdopodobieństwo, DOPIERO PÓŹNIEJ klasyfikujemy ---
    median_smooth = ndimage_zoom(median, POLYGON_SMOOTHING_FACTOR, order=3, mode="nearest")
    prob_smooth = np.clip(ndimage_zoom(prob, POLYGON_SMOOTHING_FACTOR, order=3, mode="nearest"), 0, 100)
    lats_smooth = np.linspace(lats[0], lats[-1], median_smooth.shape[0])
    lons_smooth = np.linspace(lons[0], lons[-1], median_smooth.shape[1])

    intensity_idx_smooth = _bucket_by_bins(median_smooth, bins)
    level_idx_smooth = _apply_matrix(intensity_idx_smooth, _bucket_prob(prob_smooth))

    return level_idx_native.tolist(), np.round(real_median, 1).tolist(), level_idx_smooth, lats_smooth, lons_smooth


def combine_general_risk(snow_idx, cold_idx, ice_idx, blizzard_idx, squall_idx):
    """GENERAL WINTER RISK — celowo NIE prosta suma: bazowy poziom to NAJGROŹNIEJSZY
    z pięciu hazardów w danym punkcie, ale jeśli co najmniej DWA jednocześnie
    osiągają ENHANCED (indeks >=2) lub wyżej, całość podbijamy o jeden poziom."""
    arrs = [np.array(x) for x in (snow_idx, cold_idx, ice_idx, blizzard_idx, squall_idx)]
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
    icing_precip_member_grids = [[] for _ in DAY_WINDOWS]
    blizzard_gust_member_grids = [[] for _ in DAY_WINDOWS]
    squall_cape_member_grids = [[] for _ in DAY_WINDOWS]
    failed = []
    lats = lons = None

    for m in MEMBERS:
        try:
            for day_idx, day_info in enumerate(DAY_WINDOWS):
                precip_total = None
                snow_total = None
                min_t2m = None
                icing_precip_total = None
                blizzard_max_gust = None
                squall_max_cape = None
                for start, end in day_info["windows"]:
                    fxx = end

                    H_p = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                                 member=m, fxx=fxx, priority=["aws"], verbose=False)
                    ds_p = H_p.xarray(f":APCP:surface:{start}-{end} hour acc", remove_grib=True)
                    precip_window = crop_to_region(ds_p["tp"])

                    H_t = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                                 member=m, fxx=fxx, priority=["aws"], verbose=False)
                    ds_t = H_t.xarray(":TMP:2 m above ground:", remove_grib=True)
                    t2m_window_c = crop_to_region(ds_t["t2m"]) - 273.15

                    # --- SNOW: CPOFP (procent opadu zamarzniętego, z mikrofizyki modelu) ---
                    H_cpofp = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                                     member=m, fxx=fxx, priority=["aws"], verbose=False)
                    ds_cpofp = H_cpofp.xarray(":CPOFP:surface:", remove_grib=True)
                    cpofp_window = crop_to_region(ds_cpofp[list(ds_cpofp.data_vars)[0]])
                    frozen_fraction = xr.where(cpofp_window >= 0, cpofp_window / 100.0, 0.0)
                    frozen_fraction = xr.where(frozen_fraction > 1, 1.0, frozen_fraction)
                    ratio = snow_density_ratio(t2m_window_c)
                    snow_window_cm = precip_window * frozen_fraction / 10.0 * ratio

                    precip_total = precip_window if precip_total is None else precip_total + precip_window
                    snow_total = snow_window_cm if snow_total is None else snow_total + snow_window_cm
                    min_t2m = t2m_window_c if min_t2m is None else xr.where(t2m_window_c < min_t2m, t2m_window_c, min_t2m)

                    # --- ICE: CFRZR (kategoryczna flaga marznącego deszczu WPROST z modelu) ---
                    H_cfrzr = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                                     member=m, fxx=fxx, priority=["aws"], verbose=False)
                    ds_cfrzr = H_cfrzr.xarray(":CFRZR:surface:", remove_grib=True)
                    cfrzr_window = crop_to_region(ds_cfrzr[list(ds_cfrzr.data_vars)[0]])
                    icing_precip_window = xr.where(cfrzr_window >= 0.5, precip_window, 0.0)
                    icing_precip_total = icing_precip_window if icing_precip_total is None \
                        else icing_precip_total + icing_precip_window

                    # --- BLIZZARD: GUST + VIS + śnieg ŚWIEŻY LUB JUŻ LEŻĄCY (SNOD) ---
                    H_g = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                                 member=m, fxx=fxx, priority=["aws"], verbose=False)
                    ds_g = H_g.xarray(":GUST:surface:", remove_grib=True)
                    gust_window = crop_to_region(ds_g[list(ds_g.data_vars)[0]])

                    H_vis = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                                   member=m, fxx=fxx, priority=["aws"], verbose=False)
                    ds_vis = H_vis.xarray(":VIS:surface:", remove_grib=True)
                    vis_window = crop_to_region(ds_vis[list(ds_vis.data_vars)[0]])  # metry

                    H_snod = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                                    member=m, fxx=fxx, priority=["aws"], verbose=False)
                    ds_snod = H_snod.xarray(":SNOD:surface:", remove_grib=True)
                    snod_window_cm = crop_to_region(ds_snod[list(ds_snod.data_vars)[0]]) * 100.0  # m -> cm

                    snow_available = (snow_window_cm >= MIN_FRESH_SNOW_FOR_BLIZZARD_CM) | \
                                      (snod_window_cm >= MIN_SNOW_DEPTH_FOR_GROUND_BLIZZARD_CM)
                    blizzard_condition = (gust_window >= BLIZZARD_GUST_THRESHOLD_MS) & \
                                         (vis_window <= BLIZZARD_VIS_THRESHOLD_M) & \
                                         snow_available
                    gust_during_blizzard = xr.where(blizzard_condition, gust_window, 0.0)
                    blizzard_max_gust = gust_during_blizzard if blizzard_max_gust is None else \
                        xr.where(gust_during_blizzard > blizzard_max_gust, gust_during_blizzard, blizzard_max_gust)

                    # --- SNOW SQUALLS: CAPE + aktywny, w większości zamarznięty opad ---
                    H_cape = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                                    member=m, fxx=fxx, priority=["aws"], verbose=False)
                    ds_cape = H_cape.xarray(":CAPE:surface:", remove_grib=True)
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
                precip_member_grids[day_idx].append(precip_total)
                snow_member_grids[day_idx].append(snow_total)
                cold_member_grids[day_idx].append(min_t2m)
                icing_precip_member_grids[day_idx].append(icing_precip_total)
                blizzard_gust_member_grids[day_idx].append(blizzard_max_gust)
                squall_cape_member_grids[day_idx].append(squall_max_cape)
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
        stacked_icing_precip = xr.concat(icing_precip_member_grids[day_idx], dim="member")
        stacked_blizzard_gust = xr.concat(blizzard_gust_member_grids[day_idx], dim="member")
        stacked_squall_cape = xr.concat(squall_cape_member_grids[day_idx], dim="member")

        precip_level, precip_median, precip_smooth, lats_s, lons_s = classify_hazard(stacked_precip, PRECIP_INTENSITY_BINS_MM, lats, lons)
        snow_level, snow_median, snow_smooth, _, _ = classify_hazard(stacked_snow, SNOW_INTENSITY_BINS_CM, lats, lons)
        cold_level, cold_median, cold_smooth, _, _ = classify_hazard(stacked_cold, COLD_INTENSITY_BINS_C, lats, lons, direction="le")
        ice_level, ice_median, ice_smooth, _, _ = classify_hazard(stacked_icing_precip, ICE_INTENSITY_BINS_MM, lats, lons)
        blizzard_level, blizzard_median, blizzard_smooth, _, _ = classify_hazard(stacked_blizzard_gust, BLIZZARD_INTENSITY_BINS_MS, lats, lons)
        squall_level, squall_median, squall_smooth, _, _ = classify_hazard(stacked_squall_cape, SQUALL_INTENSITY_BINS_JKG, lats, lons)

        # combine_general_risk liczymy na WYGŁADZONYCH siatkach (ten sam kształt dla
        # wszystkich pięciu, bo ten sam współczynnik zagęszczenia i ta sama siatka natywna)
        general_level = combine_general_risk(snow_level, cold_level, ice_level, blizzard_level, squall_level)
        general_smooth = combine_general_risk(snow_smooth, cold_smooth, ice_smooth, blizzard_smooth, squall_smooth)

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
                            "wody, mm/24h) - styl CESTOF, nie osobne progi.",
                    "level_grid": precip_level,
                    "median_intensity": precip_median,
                    "areas": grid_to_polygons(lats_s, lons_s, precip_smooth, country_mask),
                },
                "snow_24h_cm": {
                    "note": "Poziom zagrozenia z macierzy prawdopodobienstwo x intensywnosc (grubosc "
                            "sniegu, cm/24h). Snieg liczony jako CPOFP (procent opadu zamarznietego, "
                            "z mikrofizyki modelu) razy przelicznik gestosci zalezny od temperatury - "
                            "plynne przejscie, nie sztywny prog temperatury jak wczesniej.",
                    "level_grid": snow_level,
                    "median_intensity": snow_median,
                    "areas": grid_to_polygons(lats_s, lons_s, snow_smooth, country_mask),
                },
                "cold_min_t2m_c": {
                    "note": "Poziom zagrozenia z macierzy prawdopodobienstwo x intensywnosc (minimum "
                            "T2m z 4 odczytow co 6h w ciagu doby - przyblizenie, nie prawdziwe "
                            "ciagle minimum).",
                    "level_grid": cold_level,
                    "median_intensity": cold_median,
                    "areas": grid_to_polygons(lats_s, lons_s, cold_smooth, country_mask),
                },
                "ice_freezing_rain": {
                    "note": "Poziom zagrozenia z macierzy prawdopodobienstwo x intensywnosc. "
                            "Intensywnosc = suma opadu (mm) w oknach, gdzie CFRZR (kategoryczna "
                            "flaga marznacego deszczu WPROST z modelu) wskazala marznacy deszcz - "
                            "model sam analizuje caly profil pionowy, nie tylko dwa punkty jak "
                            "nasz dawny test T2m/T850.",
                    "level_grid": ice_level,
                    "median_intensity": ice_median,
                    "areas": grid_to_polygons(lats_s, lons_s, ice_smooth, country_mask),
                },
                "blizzard": {
                    "note": "Poziom zagrozenia z macierzy prawdopodobienstwo x intensywnosc. "
                            "Intensywnosc = szczytowy poryw wiatru (m/s, GUST) w oknach gdzie "
                            f"jednoczesnie GUST >= {BLIZZARD_GUST_THRESHOLD_MS} m/s, widzialnosc "
                            f"(VIS) <= {BLIZZARD_VIS_THRESHOLD_M}m, i snieg ŚWIEŻY "
                            f"(>= {MIN_FRESH_SNOW_FOR_BLIZZARD_CM}cm) LUB JUZ LEZACY na ziemi "
                            f"(SNOD >= {MIN_SNOW_DEPTH_FOR_GROUND_BLIZZARD_CM}cm) - to drugie "
                            "obejmuje tzw. ground blizzard (wiatr wzbijajacy stary snieg bez "
                            "nowych opadow), czego wczesniej nie wykrywalismy.",
                    "level_grid": blizzard_level,
                    "median_intensity": blizzard_median,
                    "areas": grid_to_polygons(lats_s, lons_s, blizzard_smooth, country_mask),
                },
                "snow_squalls": {
                    "note": "NOWY hazard - poziom zagrozenia z macierzy prawdopodobienstwo x "
                            "intensywnosc. Nagle, gwaltowne opady sniegu o niemal burzowym "
                            "charakterze. Intensywnosc = szczytowe CAPE (J/kg) w oknach gdzie "
                            f"jednoczesnie CAPE >= {SQUALL_CAPE_THRESHOLD_JKG} J/kg, opad w "
                            f"wiekszosci zamarzniety (CPOFP >= 50%) i opad >= "
                            f"{MIN_PRECIP_FOR_SQUALL_MM}mm.",
                    "level_grid": squall_level,
                    "median_intensity": squall_median,
                    "areas": grid_to_polygons(lats_s, lons_s, squall_smooth, country_mask),
                },
                "general_winter_risk": {
                    "note": "Polaczenie SNOW+COLD+ICE+BLIZZARD+SNOW_SQUALLS w jeden wskaznik - NIE "
                            "prosta suma. Bazowy poziom to najgrozniejszy z pieciu hazardow w danym "
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
        "days": days_out,
    }

    with open("swwf.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nZapisano swwf.json ({len(precip_member_grids[0])}/{len(MEMBERS)} członków użytych, "
          f"{len(DAY_WINDOWS)} doby)")


if __name__ == "__main__":
    main()
