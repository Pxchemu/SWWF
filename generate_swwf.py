"""
SWWF — generowanie swwf.json.

Znajduje najnowszy DOSTĘPNY przebieg GEFS (sprawdzane na dwóch członkach — 1 i 30 —
bo synchronizacja na AWS bywa rozłożona w czasie), liczy dla każdego hazardu:
  - OPAD (mm), ŚNIEG (cm), MRÓZ (°C), MARZNĄCY DESZCZ (ICE), ZAMIEĆ (BLIZZARD)
  - oraz połączone GENERAL WINTER RISK

POZIOM ZAGROŻENIA — styl CESTOF/ESTOFEX (macierz prawdopodobieństwo × intensywność):
zamiast osobno klasyfikować kilka niezależnych progów po samym prawdopodobieństwie
(co ignorowało, że np. 20cm śniegu to dużo poważniejsza sytuacja niż 5cm przy tej
samej szansie wystąpienia), każdy punkt siatki dostaje JEDEN wynik: mediana z ensemble
wyznacza "diagnozowaną" intensywność (1-6), a prawdopodobieństwo osiągnięcia co
najmniej tej intensywności trafia w wiersz macierzy — przecięcie obu daje ostateczny
poziom NONE/SLIGHT/ENHANCED/MODERATE/HIGH/EXTREME.

Dla ICE i BLIZZARD (z natury zdarzenia tak/nie) intensywność budujemy z fizycznie
powiązanych składników: dla ICE to ilość opadu, który spadł w warunkach marznących
(realny wyznacznik grubości oblodzenia), dla BLIZZARD to szczytowy poryw wiatru
w oknach, gdzie warunki zamieci wystąpiły.

UWAGA: przelicznik opad->śnieg (funkcja snow_ratio), progi ICE/BLIZZARD i sama
macierz CESTOF_MATRIX to celowo uproszczone wartości robocze — do skalibrowania
danymi z weryfikacji (patrz plan projektu, sekcja 4, 8 i 9).

UWAGA 2: produkt 0.25° (atmos.25) JEST w pełni dostępny na AWS dla wszystkich
30 członków — priority=["aws"] wymuszone wszędzie, żeby nigdy po cichu nie
spadać na zawodny NOMADS. T850 (potrzebna do ICE) nie jest w atmos.25 — pobierana
osobno z pełnego atmos.5 (0.5°) i interpolowana na naszą gęstszą siatkę.

UWAGA 3: polygony są wygładzane (interpolacja siatki x4 przed konturowaniem),
przycinane do lądu (Natural Earth, żeby nie kolorować morza) i filtrowane
z drobnych skrawków na granicach (prawdopodobne artefakty interpolacji, nie
realne obszary zagrożenia) — patrz grid_to_polygons().
"""

from datetime import datetime, timedelta, timezone
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
from shapely.geometry import shape as shapely_shape, box as shapely_box, mapping as shapely_mapping
from shapely.ops import unary_union

LAT_MIN, LAT_MAX = 46.8, 55.5   # Niemcy/Polska/Czechy/Słowacja
LON_MIN, LON_MAX = 5.5, 24.5
LON_MIN_360, LON_MAX_360 = LON_MIN % 360, LON_MAX % 360

# granice lądu (Natural Earth, domena publiczna) — do przycinania hazardów tylko do lądu,
# żeby nie kolorować morza (Bałtyk itd.) tam gdzie opad/śnieg nas nie interesuje
LAND_GEOJSON_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_land.geojson"

# o ile zagęszczamy siatkę przed konturowaniem, żeby granice polygonów były gładkie,
# nie kanciaste (jak dotychczas, bezpośrednio z siatki 0.25°)
POLYGON_SMOOTHING_FACTOR = 4
# minimalna powierzchnia polygonu (w stopniach²), poniżej której traktujemy go jako
# artefakt interpolacji/szum na granicy, nie realny obszar zagrożenia
MIN_POLYGON_AREA_DEG2 = 0.03

WINDOWS = [(0, 6), (6, 12), (12, 18), (18, 24)]
MEMBERS = list(range(1, 31))

# próg temperatury, powyżej którego opad w danym oknie liczymy jako deszcz, nie śnieg
SNOW_TEMP_THRESHOLD_C = 1.0

# ICE: klasyczny układ "warm nose" — zimna powierzchnia + ciepła warstwa nad nią + opad
SURFACE_FREEZE_THRESHOLD_C = -0.5
WARM_NOSE_THRESHOLD_C = 0.5
MIN_PRECIP_FOR_ICE_MM = 0.1

# BLIZZARD: klasyczna definicja (NWS) — poryw wiatru >=35mph (~15.5 m/s) + śnieg
BLIZZARD_GUST_THRESHOLD_MS = 15.5
MIN_FRESH_SNOW_FOR_BLIZZARD_CM = 0.5

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
ICE_INTENSITY_BINS_MM = [0.1, 1, 2, 4, 6, 10, np.inf]           # mm opadu w warunkach marznących
BLIZZARD_INTENSITY_BINS_MS = [15.5, 18, 21, 24, 28, 33, np.inf]  # szczytowy poryw, m/s


def snow_ratio(t2m_c):
    """Bardzo uproszczony przelicznik opad wody -> grubość śniegu (snow:liquid ratio),
    zależny od temperatury. Do skalibrowania w przyszłości."""
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


def fetch_t850_interpolated(run_time, member, fxx, target_lat, target_lon):
    """Pobiera T850 z PEŁNEGO produktu atmos.5 (0.5° — atmos.25 go nie ma) i interpoluje
    na docelową, gęstszą siatkę 0.25° używaną przez resztę zmiennych."""
    H = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.5",
               member=member, fxx=fxx, priority=["aws"], verbose=False)
    ds = H.xarray(":TMP:850 mb:", remove_grib=True)
    da = ds[list(ds.data_vars)[0]]
    t850 = crop_to_region(da) - 273.15
    return t850.interp(latitude=target_lat, longitude=target_lon)


def build_land_mask():
    """Pobiera granice lądu (Natural Earth) i buduje jedną geometrię (unię) tylko z tych
    fragmentów, które faktycznie przecinają nasz region — reszta świata nas nie interesuje,
    a to znacznie przyspiesza późniejsze przycinanie."""
    resp = requests.get(LAND_GEOJSON_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    region_box = shapely_box(LON_MIN, LAT_MIN, LON_MAX, LAT_MAX)
    relevant = [shapely_shape(f["geometry"]) for f in data["features"]
                if shapely_shape(f["geometry"]).intersects(region_box)]
    return unary_union(relevant)


def grid_to_polygons(lats, lons, level_idx_grid, land_mask=None):
    """Zamienia siatkę indeksów poziomu zagrożenia (0-5) na gotowe polygony GeoJSON:
    1) zagęszcza siatkę przed konturowaniem (gładkie granice zamiast kanciastych),
    2) przycina wynik do lądu (nie kolorujemy morza),
    3) odrzuca drobne, prawdopodobnie fałszywe skrawki na granicach."""
    arr = np.array(level_idx_grid, dtype=float)

    # --- 1) wygładzanie: zagęszczamy siatkę interpolacją, zanim policzymy kontury ---
    arr_smooth = ndimage_zoom(arr, POLYGON_SMOOTHING_FACTOR, order=3, mode="nearest")
    arr_smooth = np.clip(arr_smooth, 0, len(MATRIX_LEVEL_NAMES) - 1)
    lats_smooth = np.linspace(lats[0], lats[-1], arr_smooth.shape[0])
    lons_smooth = np.linspace(lons[0], lons[-1], arr_smooth.shape[1])

    fig = plt.figure()
    ax = fig.add_subplot(111)
    try:
        bounds = [i - 0.5 for i in range(len(MATRIX_LEVEL_NAMES) + 1)]  # -0.5 .. 5.5
        cs = ax.contourf(lons_smooth, lats_smooth, arr_smooth, levels=bounds, colors=MATRIX_LEVEL_COLORS)
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

        # --- 2) przycinamy do lądu (nie kolorujemy morza) ---
        if land_mask is not None:
            geom = geom.intersection(land_mask)
            if geom.is_empty:
                continue

        # --- 3) odrzucamy drobne skrawki (artefakty interpolacji na granicach) ---
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


def classify_hazard(stacked, intensity_bins, direction="ge"):
    """Serce systemu CESTOF: łączy prawdopodobieństwo i intensywność w jeden poziom.

    stacked: xr.DataArray (member, lat, lon)
    intensity_bins: 7 granic (rosnąco) definiujących 6 przedziałów intensywności
    direction="ge": więcej/wyżej = gorzej (opad, śnieg, ICE, BLIZZARD)
    direction="le": mniej/niżej = gorzej (mróz — ujemne temperatury)

    Zwraca: (level_idx_grid, median_grid) jako zwykłe listy list (do zapisu w JSON).
    """
    values = np.asarray(stacked.values)  # (member, lat, lon)
    n_lat, n_lon = values.shape[1], values.shape[2]

    if direction == "le":
        work = -values
        bins = [-b for b in intensity_bins]
    else:
        work = values
        bins = list(intensity_bins)

    median = np.median(work, axis=0)  # (lat, lon)

    # przedział intensywności zdiagnozowanej mediany: 0-5, albo -1 gdy poniżej najniższego progu
    intensity_idx = np.full((n_lat, n_lon), -1, dtype=int)
    for i in range(6):
        lo, hi = bins[i], bins[i + 1]
        mask = (median >= lo) if i == 5 else ((median >= lo) & (median < hi))
        intensity_idx[mask] = i

    # próg do porównania per punkt: dolna granica ZDIAGNOZOWANEGO przedziału (0 tam gdzie -1,
    # i tak nieużywane, bo tam wynik i tak będzie NONE)
    lower_bound_per_point = np.array(bins)[np.clip(intensity_idx, 0, 5)]
    prob = (work >= lower_bound_per_point[None, :, :]).mean(axis=0) * 100

    prob_idx = np.zeros((n_lat, n_lon), dtype=int)
    for i in range(6):
        lo, hi = MATRIX_PROB_BINS[i], MATRIX_PROB_BINS[i + 1]
        mask = (prob >= lo) if i == 5 else ((prob >= lo) & (prob < hi))
        prob_idx[mask] = i

    level_idx = np.zeros((n_lat, n_lon), dtype=int)
    matrix_np = np.array(CESTOF_MATRIX)
    has_signal = intensity_idx >= 0
    level_idx[has_signal] = matrix_np[prob_idx[has_signal], intensity_idx[has_signal]]
    # tam gdzie intensity_idx == -1 zostaje 0 (NONE) — nic nie robimy, już zainicjalizowane zerami

    real_median = np.median(values, axis=0)
    return level_idx.tolist(), np.round(real_median, 1).tolist()


def combine_general_risk(snow_idx, cold_idx, ice_idx, blizzard_idx):
    """GENERAL WINTER RISK — celowo NIE prosta suma: bazowy poziom to NAJGROŹNIEJSZY
    z czterech hazardów w danym punkcie, ale jeśli co najmniej DWA jednocześnie
    osiągają ENHANCED (indeks >=2) lub wyżej, całość podbijamy o jeden poziom."""
    arrs = [np.array(x) for x in (snow_idx, cold_idx, ice_idx, blizzard_idx)]
    max_idx = np.maximum.reduce(arrs)
    compound_count = sum((a >= 2).astype(int) for a in arrs)
    bump = (compound_count >= 2).astype(int)
    general_idx = np.minimum(max_idx + bump, len(MATRIX_LEVEL_NAMES) - 1)
    return general_idx.tolist()


def main():
    run_time = find_latest_run()
    print(f"Używam przebiegu: {run_time.isoformat()}")

    print("Pobieram granice lądu (Natural Earth)...")
    land_mask = build_land_mask()
    print(f"Maska lądu gotowa ({land_mask.geom_type})")

    precip_member_grids = []
    snow_member_grids = []
    cold_member_grids = []
    icing_precip_member_grids = []   # ile opadu spadło w warunkach marznących (intensywność ICE)
    blizzard_gust_member_grids = []  # szczytowy poryw w oknach z zamiecią (intensywność BLIZZARD)
    failed = []
    lats = lons = None

    for m in MEMBERS:
        try:
            precip_total = None
            snow_total = None
            min_t2m = None
            icing_precip_total = None
            blizzard_max_gust = None
            for start, end in WINDOWS:
                fxx = end

                H_p = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                             member=m, fxx=fxx, priority=["aws"], verbose=False)
                ds_p = H_p.xarray(f":APCP:surface:{start}-{end} hour acc", remove_grib=True)
                precip_window = crop_to_region(ds_p["tp"])

                H_t = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                             member=m, fxx=fxx, priority=["aws"], verbose=False)
                ds_t = H_t.xarray(":TMP:2 m above ground:", remove_grib=True)
                t2m_window_c = crop_to_region(ds_t["t2m"]) - 273.15

                is_snow = t2m_window_c <= SNOW_TEMP_THRESHOLD_C
                ratio = snow_ratio(t2m_window_c)
                snow_window_cm = xr.where(is_snow, precip_window / 10.0 * ratio, 0.0)

                precip_total = precip_window if precip_total is None else precip_total + precip_window
                snow_total = snow_window_cm if snow_total is None else snow_total + snow_window_cm
                min_t2m = t2m_window_c if min_t2m is None else xr.where(t2m_window_c < min_t2m, t2m_window_c, min_t2m)

                # --- ICE: T850 + intensywność = opad spadły w warunkach marznących ---
                t850_window_c = fetch_t850_interpolated(run_time, m, fxx, t2m_window_c.latitude, t2m_window_c.longitude)
                warm_nose = (t2m_window_c <= SURFACE_FREEZE_THRESHOLD_C) & \
                            (t850_window_c >= WARM_NOSE_THRESHOLD_C) & \
                            (precip_window >= MIN_PRECIP_FOR_ICE_MM)
                icing_precip_window = xr.where(warm_nose, precip_window, 0.0)
                icing_precip_total = icing_precip_window if icing_precip_total is None \
                    else icing_precip_total + icing_precip_window

                # --- BLIZZARD: GUST + intensywność = szczytowy poryw w oknach z zamiecią ---
                H_g = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                             member=m, fxx=fxx, priority=["aws"], verbose=False)
                ds_g = H_g.xarray(":GUST:surface:", remove_grib=True)
                gust_window = crop_to_region(ds_g[list(ds_g.data_vars)[0]])
                blizzard_condition = (gust_window >= BLIZZARD_GUST_THRESHOLD_MS) & \
                                     (snow_window_cm >= MIN_FRESH_SNOW_FOR_BLIZZARD_CM)
                gust_during_blizzard = xr.where(blizzard_condition, gust_window, 0.0)
                blizzard_max_gust = gust_during_blizzard if blizzard_max_gust is None else \
                    xr.where(gust_during_blizzard > blizzard_max_gust, gust_during_blizzard, blizzard_max_gust)

            if lats is None:
                lats = [round(float(x), 3) for x in precip_total.latitude.values]
                lons = [round(float(x) - 360 if float(x) > 180 else float(x), 3) for x in precip_total.longitude.values]
            precip_member_grids.append(precip_total)
            snow_member_grids.append(snow_total)
            cold_member_grids.append(min_t2m)
            icing_precip_member_grids.append(icing_precip_total)
            blizzard_gust_member_grids.append(blizzard_max_gust)
            print(f"  człon {m:>2}: OK")
        except Exception as e:
            failed.append(m)
            print(f"  człon {m:>2}: BŁĄD ({e})")

    if not precip_member_grids:
        raise RuntimeError("Żaden człon się nie udał — przerywam bez zapisu pliku")

    stacked_precip = xr.concat(precip_member_grids, dim="member")
    stacked_snow = xr.concat(snow_member_grids, dim="member")
    stacked_cold = xr.concat(cold_member_grids, dim="member")
    stacked_icing_precip = xr.concat(icing_precip_member_grids, dim="member")
    stacked_blizzard_gust = xr.concat(blizzard_gust_member_grids, dim="member")

    precip_level, precip_median = classify_hazard(stacked_precip, PRECIP_INTENSITY_BINS_MM)
    snow_level, snow_median = classify_hazard(stacked_snow, SNOW_INTENSITY_BINS_CM)
    cold_level, cold_median = classify_hazard(stacked_cold, COLD_INTENSITY_BINS_C, direction="le")
    ice_level, ice_median = classify_hazard(stacked_icing_precip, ICE_INTENSITY_BINS_MM)
    blizzard_level, blizzard_median = classify_hazard(stacked_blizzard_gust, BLIZZARD_INTENSITY_BINS_MS)

    general_level = combine_general_risk(snow_level, cold_level, ice_level, blizzard_level)

    valid_from = run_time
    valid_to = run_time + timedelta(hours=24)

    result = {
        "issued": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model_run": run_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valid_from": valid_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valid_to": valid_to.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "members_used": len(precip_member_grids),
        "members_failed": failed,
        "grid": {"lat": lats, "lon": lons},
        "level_names": MATRIX_LEVEL_NAMES,
        "level_colors": MATRIX_LEVEL_COLORS,
        "hazards": {
            "precip_24h_mm": {
                "note": "Poziom zagrozenia z macierzy prawdopodobienstwo x intensywnosc (opad "
                        "wody, mm/24h) - styl CESTOF, nie osobne progi.",
                "level_grid": precip_level,
                "median_intensity": precip_median,
                "areas": grid_to_polygons(lats, lons, precip_level, land_mask),
            },
            "snow_24h_cm": {
                "note": "Poziom zagrozenia z macierzy prawdopodobienstwo x intensywnosc (grubosc "
                        "sniegu, cm/24h). Snieg liczony tylko z opadu w oknach gdzie T2m <= "
                        f"{SNOW_TEMP_THRESHOLD_C}C, z przelicznikiem zaleznym od temperatury.",
                "level_grid": snow_level,
                "median_intensity": snow_median,
                "areas": grid_to_polygons(lats, lons, snow_level, land_mask),
            },
            "cold_min_t2m_c": {
                "note": "Poziom zagrozenia z macierzy prawdopodobienstwo x intensywnosc (minimum "
                        "T2m z 4 odczytow co 6h w ciagu doby - przyblizenie, nie prawdziwe "
                        "ciagle minimum).",
                "level_grid": cold_level,
                "median_intensity": cold_median,
                "areas": grid_to_polygons(lats, lons, cold_level, land_mask),
            },
            "ice_freezing_rain": {
                "note": "Poziom zagrozenia z macierzy prawdopodobienstwo x intensywnosc. "
                        "Intensywnosc = suma opadu (mm) ktory spadl w oknach z warunkami "
                        f"marznacymi (T2m <= {SURFACE_FREEZE_THRESHOLD_C}C, T850 >= "
                        f"{WARM_NOSE_THRESHOLD_C}C, opad >= {MIN_PRECIP_FOR_ICE_MM}mm) - realny "
                        "wyznacznik grubosci oblodzenia. T850 z osobnego, rzadszego produktu "
                        "(0.5 stopnia), interpolowana na nasza siatke.",
                "level_grid": ice_level,
                "median_intensity": ice_median,
                "areas": grid_to_polygons(lats, lons, ice_level, land_mask),
            },
            "blizzard": {
                "note": "Poziom zagrozenia z macierzy prawdopodobienstwo x intensywnosc. "
                        "Intensywnosc = szczytowy poryw wiatru (m/s, GUST) w oknach gdzie "
                        f"jednoczesnie GUST >= {BLIZZARD_GUST_THRESHOLD_MS} m/s i swiezy snieg "
                        f">= {MIN_FRESH_SNOW_FOR_BLIZZARD_CM}cm. UWAGA: brak realnej pokrywy "
                        "sniegu na ziemi w danych - to pomija tzw. ground blizzard.",
                "level_grid": blizzard_level,
                "median_intensity": blizzard_median,
                "areas": grid_to_polygons(lats, lons, blizzard_level, land_mask),
            },
            "general_winter_risk": {
                "note": "Polaczenie SNOW+COLD+ICE+BLIZZARD w jeden wskaznik - NIE prosta suma. "
                        "Bazowy poziom to najgrozniejszy z czterech hazardow w danym punkcie; "
                        "jesli co najmniej DWA hazardy jednoczesnie osiagaja ENHANCED lub wyzej, "
                        "calosc podbijana o jeden poziom.",
                "level_grid": general_level,
                "areas": grid_to_polygons(lats, lons, general_level, land_mask),
            },
        },
    }

    with open("swwf.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nZapisano swwf.json ({len(precip_member_grids)}/{len(MEMBERS)} członków użytych)")


if __name__ == "__main__":
    main()
