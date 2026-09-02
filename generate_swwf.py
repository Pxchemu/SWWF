"""
SWWF — generowanie swwf.json.

Znajduje najnowszy DOSTĘPNY przebieg GEFS (nie zawsze najnowszy w ogóle —
dane pojawiają się na AWS z opóźnieniem, więc sprawdzamy kolejne wstecz,
aż trafimy na taki, który już jest), liczy prawdopodobieństwo opadu
>= różnych progów dla siatki punktów nad Europą Środkową (Niemcy, Polska,
Czechy, Słowacja — siatka 0.25°), zapisuje jako swwf.json.

UWAGA: na razie tylko opad (mm wody), NIE przeliczenie na śnieg (cm) —
to świadomie odłożone na później (patrz plan projektu, sekcja 4).
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
THRESHOLDS_MM = [1, 5, 10, 20]

# poziomy zagrożenia z dokumentu planu (sekcja 3) — progi robocze, do skalibrowania później
LEVEL_BOUNDS = [0, 20, 40, 60, 80, 100]
LEVEL_COLORS = ['#ffffff', '#fde047', '#fb923c', '#ef4444', '#a855f7']
LEVEL_NAMES = ['NONE', 'SLIGHT', 'ENHANCED', 'MODERATE', 'HIGH']


def find_latest_run():
    """Szuka najnowszego przebiegu GEFS, który faktycznie już jest dostępny na AWS —
    próbuje kolejno wstecz (00/06/12/18Z), bo świeżo wystartowany przebieg
    bywa widoczny na AWS dopiero po kilku godzinach."""
    now = datetime.now(timezone.utc)
    candidate = now.replace(minute=0, second=0, microsecond=0)
    candidate -= timedelta(hours=candidate.hour % 6)
    for i in range(8):  # sprawdź do 48h wstecz
        test_time = candidate - timedelta(hours=6 * i)
        try:
            H = Herbie(test_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                       member=1, fxx=6, verbose=False)
            if H.grib is not None:
                return test_time
        except Exception:
            continue
    raise RuntimeError("Nie znaleziono żadnego dostępnego przebiegu GEFS w ostatnich 48h")


def crop_to_poland(da):
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
    # dopisujemy czytelną nazwę poziomu (SLIGHT/ENHANCED/...) do każdego polygonu na podstawie
    # jego dolnej granicy — i pomijamy poziom NONE (0-20%), bo nie ma sensu go rysować na mapie
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


def main():
    run_time = find_latest_run()
    print(f"Używam przebiegu: {run_time.isoformat()}")

    member_grids = []
    failed = []
    lats = lons = None

    for m in MEMBERS:
        try:
            total = None
            for start, end in WINDOWS:
                fxx = end
                search = f":APCP:surface:{start}-{end} hour acc"
                H = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                           member=m, fxx=fxx, verbose=False)
                ds = H.xarray(search, remove_grib=True)
                cropped = crop_to_poland(ds["tp"])
                total = cropped if total is None else total + cropped
            if lats is None:
                lats = [round(float(x), 3) for x in total.latitude.values]
                lons = [round(float(x) - 360 if float(x) > 180 else float(x), 3) for x in total.longitude.values]
            member_grids.append(total)
            print(f"  człon {m:>2}: OK")
        except Exception as e:
            failed.append(m)
            print(f"  człon {m:>2}: BŁĄD ({e})")

    if not member_grids:
        raise RuntimeError("Żaden człon się nie udał — przerywam bez zapisu pliku")

    stacked = xr.concat(member_grids, dim="member")

    thresholds_out = {}
    areas_out = {}
    for t in THRESHOLDS_MM:
        prob = (stacked >= t).mean(dim="member") * 100
        grid = np.round(prob.values, 0).astype(int).tolist()
        thresholds_out[str(t)] = grid
        areas_out[str(t)] = grid_to_polygons(lats, lons, grid)

    valid_from = run_time
    valid_to = run_time + timedelta(hours=24)

    result = {
        "issued": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model_run": run_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valid_from": valid_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valid_to": valid_to.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "members_used": len(member_grids),
        "members_failed": failed,
        "grid": {
            "lat": lats,
            "lon": lons,
        },
        "hazards": {
            "precip_24h_mm": {
                "note": "Prawdopodobienstwo (%) przekroczenia progu opadu w mm wody na 24h. "
                        "TO NIE JEST jeszcze grubosc sniegu w cm - przeliczenie planowane w kolejnym etapie.",
                "thresholds": thresholds_out,
                "areas": areas_out,
            }
        },
    }

    with open("swwf.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nZapisano swwf.json ({len(member_grids)}/{len(MEMBERS)} członków użytych)")


if __name__ == "__main__":
    main()
