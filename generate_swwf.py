"""
SWWF — generowanie swwf.json.

Znajduje najnowszy DOSTĘPNY przebieg GEFS (nie zawsze najnowszy w ogóle —
dane pojawiają się na AWS z opóźnieniem, więc sprawdzamy kolejne wstecz,
aż trafimy na taki, który już jest — i to na DWÓCH członkach naraz, nie
tylko pierwszym, bo synchronizacja na AWS bywa rozłożona w czasie), liczy
prawdopodobieństwo:
  - opadu (mm wody) — jak dotychczas
  - ŚNIEGU (cm) — dla każdego okna 6h sprawdzamy T2m; jeśli jest wystarczająco
    zimno, opad z tego okna liczymy jako śnieg, z przelicznikiem zależnym
    od temperatury (zimniej = bardziej puchaty, mniej wody na cm)
  - MROZU — minimum T2m z 4 odczytów w ciągu doby
  - MARZNĄCEGO DESZCZU (ICE) — klasyczny układ "warm nose": zimna powierzchnia
    (T2m) + cieplejsza warstwa nad nią (T850, z osobnego, rzadszego produktu,
    interpolowana na naszą siatkę) + realny opad
  - ZAMIECI (BLIZZARD) — poryw wiatru (GUST) + świeży śnieg w tym samym oknie
    (brak realnej pokrywy śniegu w danych — pomija "ground blizzard", patrz sekcja 9 planu)

dla siatki punktów nad Europą Środkową (Niemcy, Polska, Czechy, Słowacja —
siatka 0.25°), zapisuje jako swwf.json.

UWAGA: przelicznik opad->śnieg (funkcja snow_ratio) to celowo uproszczona
tabela robocza — do skalibrowania danymi z weryfikacji (patrz plan projektu,
sekcja 4 i 8).

UWAGA 2: produkt 0.25° (atmos.25) JEST w pełni dostępny na AWS dla wszystkich
30 członków (zweryfikowane bezpośrednim testem, priority=["aws"]) — wcześniejsza
nieudana próba wynikała z tego, że sprawdzaliśmy gotowość przebiegu tylko na
członku 1, a synchronizacja pozostałych członków na AWS bywa opóźniona
względem niego. Stąd sprawdzanie na dwóch członkach (1 i 30) w find_latest_run(),
oraz priority=["aws"] wszędzie, żeby nigdy po cichu nie spadać na NOMADS.
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

LAT_MIN, LAT_MAX = 46.8, 55.5   # Niemcy/Polska/Czechy/Słowacja
LON_MIN, LON_MAX = 5.5, 24.5
LON_MIN_360, LON_MAX_360 = LON_MIN % 360, LON_MAX % 360

WINDOWS = [(0, 6), (6, 12), (12, 18), (18, 24)]
MEMBERS = list(range(1, 31))
THRESHOLDS_MM = [1, 5, 10, 20]      # progi dla samego opadu (mm wody)
SNOW_THRESHOLDS_CM = [5, 10, 20]    # progi dla śniegu (cm) — zgodnie z dokumentem planu
COLD_THRESHOLDS_C = [-15, -10, -5]  # progi dla mrozu — im niższa liczba, tym rzadziej przekraczana
ICE_THRESHOLDS = [1]                # ICE jest z natury tak/nie (0 albo 1) — jeden "próg" wystarcza

# ICE (marznący deszcz): klasyczny układ to zimna powierzchnia + ciepła warstwa nad nią + padający
# opad — krople topnieją/formują się w ciepłej warstwie w górze, po czym zamarzają przy kontakcie
# z zimną powierzchnią. Progi robocze, do skalibrowania.
SURFACE_FREEZE_THRESHOLD_C = -0.5   # T2m poniżej tego = powierzchnia realnie zamarznięta
WARM_NOSE_THRESHOLD_C = 0.5         # T850 powyżej tego = wyraźna ciepła warstwa w górze ("warm nose")
MIN_PRECIP_FOR_ICE_MM = 0.1         # musi w ogóle coś padać, żeby liczyć to jako marznący deszcz

BLIZZARD_THRESHOLDS = [1]           # tak jak ICE, z natury tak/nie
# klasyczna definicja zamieci (NWS): utrzymujący się wiatr LUB częste porywy >=35mph (~15.5 m/s)
# razem z padającym/unoszonym śniegiem. Używamy GUST (poryw), bo to dokładnie ta zmienna,
# na której opiera się definicja - nie średni wiatr.
BLIZZARD_GUST_THRESHOLD_MS = 15.5
# brakuje nam realnej pokrywy śnieżnej na ziemi (patrz sekcja 9 dokumentu planu) - jako namiastkę
# "śniegu dostępnego do unoszenia" używamy własnego, już liczonego świeżego opadu śniegu w tym
# oknie (to pomija "ground blizzard" - sam wiatr unoszący STARY śnieg bez nowych opadów)
MIN_FRESH_SNOW_FOR_BLIZZARD_CM = 0.5

# próg temperatury, powyżej którego opad w danym oknie liczymy jako deszcz, nie śnieg
# (lekko powyżej 0°C, bo mokry termometr chłodzi spadające krople/płatki)
SNOW_TEMP_THRESHOLD_C = 1.0

# poziomy zagrożenia z dokumentu planu (sekcja 3) — progi robocze, do skalibrowania później
LEVEL_BOUNDS = [0, 20, 40, 60, 80, 100]
LEVEL_COLORS = ['#ffffff', '#fde047', '#fb923c', '#ef4444', '#a855f7']
LEVEL_NAMES = ['NONE', 'SLIGHT', 'ENHANCED', 'MODERATE', 'HIGH']


def snow_ratio(t2m_c):
    """Bardzo uproszczony przelicznik opad wody -> grubość śniegu (snow:liquid ratio),
    zależny od temperatury. Klasyczne 10:1 w okolicach 0°C, więcej gdy mroźniej
    (suchszy, bardziej puchaty śnieg), mniej gdy blisko granicy topnienia.
    Do skalibrowania w przyszłości."""
    return xr.where(t2m_c <= -10, 15.0,
           xr.where(t2m_c <= -5, 12.0,
           xr.where(t2m_c <= 0, 10.0, 7.0)))


def find_latest_run():
    """Szuka najnowszego przebiegu GEFS, który faktycznie już jest dostępny na AWS —
    próbuje kolejno wstecz (00/06/12/18Z), bo świeżo wystartowany przebieg
    bywa widoczny na AWS dopiero po kilku godzinach. Sprawdzamy GOTOWOŚĆ na dwóch
    członkach (1 i 30, nie tylko pierwszym) — synchronizacja na AWS bywa rozłożona
    w czasie między członkami, więc sam pierwszy potrafi być gotowy wcześniej niż reszta."""
    now = datetime.now(timezone.utc)
    candidate = now.replace(minute=0, second=0, microsecond=0)
    candidate -= timedelta(hours=candidate.hour % 6)
    for i in range(8):  # sprawdź do 48h wstecz
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
    na docelową, gęstszą siatkę 0.25° używaną przez resztę zmiennych (opad, T2m)."""
    H = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.5",
               member=member, fxx=fxx, priority=["aws"], verbose=False)
    ds = H.xarray(":TMP:850 mb:", remove_grib=True)
    # nie zakładamy z góry dokładnej nazwy zmiennej w cfgrib (dla poziomów ciśnienia bywa
    # inna niż "t2m") — bierzemy po prostu jedyną zmienną, jaka jest w tym pliku
    da = ds[list(ds.data_vars)[0]]
    t850 = crop_to_region(da) - 273.15  # Kelwiny -> stopnie C
    return t850.interp(latitude=target_lat, longitude=target_lon)


def grid_to_polygons(lats, lons, grid_2d):
    """Zamienia siatkę liczb (% prawdopodobieństwa) na gotowe polygony GeoJSON,
    pogrupowane wg poziomów zagrożenia SLIGHT/ENHANCED/MODERATE/HIGH."""
    arr = np.array(grid_2d, dtype=float)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    try:
        cs = ax.contourf(lons, lats, arr, levels=LEVEL_BOUNDS, colors=LEVEL_COLORS)
        geojson_str = geojsoncontour.contourf_to_geojson(contourf=cs, ndigits=3, fill_opacity=0.45)
    finally:
        plt.close(fig)

    data = json.loads(geojson_str)
    features_out = []
    for feature in data.get("features", []):
        title = feature["properties"].get("title", "")
        try:
            lower_bound = float(title.split("-")[0].strip())
        except (ValueError, IndexError):
            lower_bound = 0
        idx = 0
        for i in range(len(LEVEL_BOUNDS) - 1):
            if abs(LEVEL_BOUNDS[i] - lower_bound) < 0.5:
                idx = i
                break
        level_name = LEVEL_NAMES[idx]
        if level_name == "NONE":
            continue
        feature["properties"]["level"] = level_name
        features_out.append(feature)

    return {"type": "FeatureCollection", "features": features_out}


def probabilities_and_areas(stacked, thresholds, lats, lons, direction="ge"):
    """direction="ge": prawdopodobieństwo, że wartość >= progu (opad, śnieg — im więcej, tym gorzej)
    direction="le": prawdopodobieństwo, że wartość <= progu (mróz — im niżej, tym gorzej)"""
    thresholds_out = {}
    areas_out = {}
    for t in thresholds:
        if direction == "le":
            prob = (stacked <= t).mean(dim="member") * 100
        else:
            prob = (stacked >= t).mean(dim="member") * 100
        grid = np.round(prob.values, 0).astype(int).tolist()
        thresholds_out[str(t)] = grid
        areas_out[str(t)] = grid_to_polygons(lats, lons, grid)
    return thresholds_out, areas_out


def level_index(prob_grid_list):
    """Zamienia siatkę procentów (0-100, jako zwykła lista list) na siatkę indeksów
    poziomu zagrożenia: 0=NONE, 1=SLIGHT, 2=ENHANCED, 3=MODERATE, 4=HIGH."""
    arr = np.array(prob_grid_list, dtype=float)
    idx = np.zeros_like(arr, dtype=int)
    for i in range(len(LEVEL_BOUNDS) - 1):
        lo, hi = LEVEL_BOUNDS[i], LEVEL_BOUNDS[i + 1]
        mask = (arr >= lo) & (arr <= hi) if hi == 100 else (arr >= lo) & (arr < hi)
        idx[mask] = i
    return idx


def combine_general_risk(snow_idx, cold_idx, ice_idx, blizzard_idx):
    """GENERAL WINTER RISK — celowo NIE prosta suma (patrz dokument planu, sekcja 2/6):
    bazowy poziom to NAJGROŹNIEJSZY z czterech hazardów w danym punkcie, ale jeśli co
    najmniej DWA hazardy jednocześnie osiągają ENHANCED lub wyżej, całość podbijamy
    o jeden poziom (kombinacja zagrożeń jest gorsza niż którekolwiek z osobna)."""
    max_idx = np.maximum.reduce([snow_idx, cold_idx, ice_idx, blizzard_idx])
    compound_count = ((snow_idx >= 2).astype(int) + (cold_idx >= 2).astype(int) +
                       (ice_idx >= 2).astype(int) + (blizzard_idx >= 2).astype(int))
    bump = (compound_count >= 2).astype(int)
    general_idx = np.minimum(max_idx + bump, len(LEVEL_NAMES) - 1)
    # przeliczamy indeks z powrotem na "procent" tak, żeby trafiał w te same przedziały
    # LEVEL_BOUNDS (0/20/40/60/80/100) i dało się użyć TEJ SAMEJ funkcji grid_to_polygons
    # bez pisania jej drugi raz — 0→0%, 1→25%, 2→50%, 3→75%, 4→100%, każdy trafia w środek
    # właściwego przedziału swojego poziomu
    return (general_idx * 25).tolist()


def main():
    run_time = find_latest_run()
    print(f"Używam przebiegu: {run_time.isoformat()}")

    precip_member_grids = []
    snow_member_grids = []
    cold_member_grids = []
    ice_member_grids = []
    blizzard_member_grids = []
    failed = []
    lats = lons = None

    for m in MEMBERS:
        try:
            precip_total = None
            snow_total = None
            min_t2m = None
            ice_any = None
            blizzard_any = None
            for start, end in WINDOWS:
                fxx = end

                # --- opad w tym oknie (jak dotychczas) ---
                H_p = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                             member=m, fxx=fxx, priority=["aws"], verbose=False)
                ds_p = H_p.xarray(f":APCP:surface:{start}-{end} hour acc", remove_grib=True)
                precip_window = crop_to_region(ds_p["tp"])

                # --- temperatura na koniec tego okna ---
                H_t = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                             member=m, fxx=fxx, priority=["aws"], verbose=False)
                ds_t = H_t.xarray(":TMP:2 m above ground:", remove_grib=True)
                t2m_window_c = crop_to_region(ds_t["t2m"]) - 273.15  # Kelwiny -> stopnie C

                # opad w tym oknie liczy się jako śnieg tylko tam, gdzie jest dość zimno;
                # przelicznik (snow:liquid ratio) zależy od temperatury w danym punkcie
                is_snow = t2m_window_c <= SNOW_TEMP_THRESHOLD_C
                ratio = snow_ratio(t2m_window_c)
                snow_window_cm = xr.where(is_snow, precip_window / 10.0 * ratio, 0.0)

                precip_total = precip_window if precip_total is None else precip_total + precip_window
                snow_total = snow_window_cm if snow_total is None else snow_total + snow_window_cm
                # COLD: interesuje nas NAJNIŻSZA temperatura osiągnięta w ciągu doby
                # (z 4 odczytów co 6h — przybliżenie, nie prawdziwe minimum ciągłe)
                min_t2m = t2m_window_c if min_t2m is None else xr.where(t2m_window_c < min_t2m, t2m_window_c, min_t2m)

                # --- ICE: T850 z osobnego, pełnego produktu + interpolacja na naszą siatkę ---
                t850_window_c = fetch_t850_interpolated(run_time, m, fxx, t2m_window_c.latitude, t2m_window_c.longitude)
                warm_nose = (t2m_window_c <= SURFACE_FREEZE_THRESHOLD_C) & \
                            (t850_window_c >= WARM_NOSE_THRESHOLD_C) & \
                            (precip_window >= MIN_PRECIP_FOR_ICE_MM)
                ice_window = xr.where(warm_nose, 1, 0)
                # w ciągu doby wystarczy, że warunek na marznący deszcz wystąpił w KTÓRYMKOLWIEK
                # z 4 okien — stąd maksimum (logiczne "LUB"), nie suma
                ice_any = ice_window if ice_any is None else xr.where(ice_window > ice_any, ice_window, ice_any)

                # --- BLIZZARD: poryw wiatru (GUST) + świeży śnieg w tym samym oknie ---
                H_g = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                             member=m, fxx=fxx, priority=["aws"], verbose=False)
                ds_g = H_g.xarray(":GUST:surface:", remove_grib=True)
                gust_window = crop_to_region(ds_g[list(ds_g.data_vars)[0]])
                blizzard_condition = (gust_window >= BLIZZARD_GUST_THRESHOLD_MS) & \
                                     (snow_window_cm >= MIN_FRESH_SNOW_FOR_BLIZZARD_CM)
                blizzard_window = xr.where(blizzard_condition, 1, 0)
                blizzard_any = blizzard_window if blizzard_any is None else \
                    xr.where(blizzard_window > blizzard_any, blizzard_window, blizzard_any)

            if lats is None:
                lats = [round(float(x), 3) for x in precip_total.latitude.values]
                lons = [round(float(x) - 360 if float(x) > 180 else float(x), 3) for x in precip_total.longitude.values]
            precip_member_grids.append(precip_total)
            snow_member_grids.append(snow_total)
            cold_member_grids.append(min_t2m)
            ice_member_grids.append(ice_any)
            blizzard_member_grids.append(blizzard_any)
            print(f"  człon {m:>2}: OK")
        except Exception as e:
            failed.append(m)
            print(f"  człon {m:>2}: BŁĄD ({e})")

    if not precip_member_grids:
        raise RuntimeError("Żaden człon się nie udał — przerywam bez zapisu pliku")

    stacked_precip = xr.concat(precip_member_grids, dim="member")
    stacked_snow = xr.concat(snow_member_grids, dim="member")
    stacked_cold = xr.concat(cold_member_grids, dim="member")
    stacked_ice = xr.concat(ice_member_grids, dim="member")
    stacked_blizzard = xr.concat(blizzard_member_grids, dim="member")

    precip_thresholds_out, precip_areas_out = probabilities_and_areas(stacked_precip, THRESHOLDS_MM, lats, lons)
    snow_thresholds_out, snow_areas_out = probabilities_and_areas(stacked_snow, SNOW_THRESHOLDS_CM, lats, lons)
    cold_thresholds_out, cold_areas_out = probabilities_and_areas(stacked_cold, COLD_THRESHOLDS_C, lats, lons, direction="le")
    ice_thresholds_out, ice_areas_out = probabilities_and_areas(stacked_ice, ICE_THRESHOLDS, lats, lons)
    blizzard_thresholds_out, blizzard_areas_out = probabilities_and_areas(stacked_blizzard, BLIZZARD_THRESHOLDS, lats, lons)

    # --- GENERAL WINTER RISK: łączymy cztery hazardy po jednym reprezentatywnym progu każdy ---
    snow_idx = level_index(snow_thresholds_out[str(SNOW_THRESHOLDS_CM[1])])    # 10cm — środkowy próg
    cold_idx = level_index(cold_thresholds_out[str(COLD_THRESHOLDS_C[1])])     # -10C — środkowy próg
    ice_idx = level_index(ice_thresholds_out[str(ICE_THRESHOLDS[0])])
    blizzard_idx = level_index(blizzard_thresholds_out[str(BLIZZARD_THRESHOLDS[0])])
    general_grid = combine_general_risk(snow_idx, cold_idx, ice_idx, blizzard_idx)
    general_thresholds_out = {"risk": general_grid}
    general_areas_out = {"risk": grid_to_polygons(lats, lons, general_grid)}

    valid_from = run_time
    valid_to = run_time + timedelta(hours=24)

    result = {
        "issued": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model_run": run_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valid_from": valid_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valid_to": valid_to.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "members_used": len(precip_member_grids),
        "members_failed": failed,
        "grid": {
            "lat": lats,
            "lon": lons,
        },
        "hazards": {
            "precip_24h_mm": {
                "note": "Prawdopodobienstwo (%) przekroczenia progu opadu w mm wody na 24h "
                        "(niezaleznie od tego czy to snieg czy deszcz).",
                "thresholds": precip_thresholds_out,
                "areas": precip_areas_out,
            },
            "snow_24h_cm": {
                "note": "Prawdopodobienstwo (%) przekroczenia progu grubosci SNIEGU (cm) na 24h. "
                        "Liczone tylko z opadu w oknach czasowych gdzie T2m <= "
                        f"{SNOW_TEMP_THRESHOLD_C}C, z przelicznikiem opad->snieg zaleznym "
                        "od temperatury (uproszczona tabela robocza, do kalibracji).",
                "thresholds": snow_thresholds_out,
                "areas": snow_areas_out,
            },
            "cold_min_t2m_c": {
                "note": "Prawdopodobienstwo (%), ze temperatura 2m spadnie ponizej progu (stopnie C) "
                        "w ciagu najblizszych 24h. Liczone jako minimum z 4 odczytow co 6h "
                        "(przyblizenie, nie prawdziwe ciagle minimum).",
                "thresholds": cold_thresholds_out,
                "areas": cold_areas_out,
            },
            "ice_freezing_rain": {
                "note": "Prawdopodobienstwo (%) wystapienia marznacego deszczu (T2m <= "
                        f"{SURFACE_FREEZE_THRESHOLD_C}C, T850 >= {WARM_NOSE_THRESHOLD_C}C - "
                        "cieplejsza warstwa nad zamarznieta powierzchnia - i realny opad) "
                        "w KTORYMKOLWIEK z 4 okien 6h w ciagu doby. T850 pochodzi z osobnego, "
                        "rzadszego produktu (0.5 stopnia) i jest interpolowane na siatke "
                        "reszty zmiennych (0.25 stopnia).",
                "thresholds": ice_thresholds_out,
                "areas": ice_areas_out,
            },
            "blizzard": {
                "note": "Prawdopodobienstwo (%) wystapienia warunkow zamieci: poryw wiatru (GUST) "
                        f">= {BLIZZARD_GUST_THRESHOLD_MS} m/s razem ze swiezym sniegiem "
                        f"(>= {MIN_FRESH_SNOW_FOR_BLIZZARD_CM}cm) w tym samym oknie 6h, w "
                        "KTORYMKOLWIEK z 4 okien w ciagu doby. UWAGA: brak realnej pokrywy "
                        "sniegu na ziemi w danych - to pomija tzw. ground blizzard (sam wiatr "
                        "unoszacy STARY snieg bez nowych opadow).",
                "thresholds": blizzard_thresholds_out,
                "areas": blizzard_areas_out,
            },
            "general_winter_risk": {
                "note": "Polaczenie SNOW+COLD+ICE+BLIZZARD w jeden wskaznik - NIE prosta suma. "
                        "Bazowy poziom to najgrozniejszy z czterech hazardow w danym punkcie; "
                        "jesli co najmniej DWA hazardy jednoczesnie osiagaja ENHANCED lub wyzej, "
                        "calosc podbijana o jeden poziom. Wartosc w 'thresholds' to nie procent "
                        "prawdopodobienstwa jak w innych hazardach, tylko poziom zagrozenia "
                        "zakodowany jako 0/25/50/75/100 (odpowiednio NONE/SLIGHT/ENHANCED/"
                        "MODERATE/HIGH) - do odczytu przez te same granice co reszta (LEVEL_BOUNDS).",
                "thresholds": general_thresholds_out,
                "areas": general_areas_out,
            },
        },
    }

    with open("swwf.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nZapisano swwf.json ({len(precip_member_grids)}/{len(MEMBERS)} członków użytych)")


if __name__ == "__main__":
    main()
