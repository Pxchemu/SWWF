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

LAT_MIN, LAT_MAX = 46.8, 55.5
LON_MIN, LON_MAX = 5.5, 24.5
LON_MIN_360, LON_MAX_360 = LON_MIN % 360, LON_MAX % 360

WINDOWS = [(0, 6), (6, 12), (12, 18), (18, 24)]
MEMBERS = list(range(1, 31))
THRESHOLDS_MM = [1, 5, 10, 20]      # progi dla samego opadu (mm wody)
SNOW_THRESHOLDS_CM = [5, 10, 20]    # progi dla śniegu (cm) — zgodnie z dokumentem planu

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


def probabilities_and_areas(stacked, thresholds, lats, lons):
    thresholds_out = {}
    areas_out = {}
    for t in thresholds:
        prob = (stacked >= t).mean(dim="member") * 100
        grid = np.round(prob.values, 0).astype(int).tolist()
        thresholds_out[str(t)] = grid
        areas_out[str(t)] = grid_to_polygons(lats, lons, grid)
    return thresholds_out, areas_out


def main():
    run_time = find_latest_run()
    print(f"Używam przebiegu: {run_time.isoformat()}")

    precip_member_grids = []
    snow_member_grids = []
    failed = []
    lats = lons = None

    for m in MEMBERS:
        try:
            precip_total = None
            snow_total = None
            for start, end in WINDOWS:
                fxx = end

                # --- opad w tym oknie (jak dotychczas) ---
                H_p = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                             member=m, fxx=fxx, priority=["aws"], verbose=False)
                ds_p = H_p.xarray(f":APCP:surface:{start}-{end} hour acc", remove_grib=True)
                precip_window = crop_to_region(ds_p["tp"])

                # --- temperatura na koniec tego okna (NOWOŚĆ) ---
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

            if lats is None:
                lats = [round(float(x), 3) for x in precip_total.latitude.values]
                lons = [round(float(x) - 360 if float(x) > 180 else float(x), 3) for x in precip_total.longitude.values]
            precip_member_grids.append(precip_total)
            snow_member_grids.append(snow_total)
            print(f"  człon {m:>2}: OK")
        except Exception as e:
            failed.append(m)
            print(f"  człon {m:>2}: BŁĄD ({e})")

    if not precip_member_grids:
        raise RuntimeError("Żaden człon się nie udał — przerywam bez zapisu pliku")

    stacked_precip = xr.concat(precip_member_grids, dim="member")
    stacked_snow = xr.concat(snow_member_grids, dim="member")

    precip_thresholds_out, precip_areas_out = probabilities_and_areas(stacked_precip, THRESHOLDS_MM, lats, lons)
    snow_thresholds_out, snow_areas_out = probabilities_and_areas(stacked_snow, SNOW_THRESHOLDS_CM, lats, lons)

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
        },
    }

    with open("swwf.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nZapisano swwf.json ({len(precip_member_grids)}/{len(MEMBERS)} członków użytych)")


if __name__ == "__main__":
    main()
