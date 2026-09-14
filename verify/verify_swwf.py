"""
SWWF — verify_swwf.py

Porównuje wczorajszą, zarchiwizowaną prognozę SWWF (opad) z rzeczywistym,
zmierzonym opadem z GPM IMERG (NASA/JAXA, produkt GPM_3IMERGDE — Early Run,
dobowa suma, 0.1°, ~4h opóźnienia).

To pierwsza wersja weryfikacji — na razie tylko OPAD (precip_24h_mm). Inne
hazardy (śnieg, mróz itd.) nie mają prostego jedno-do-jednego odpowiednika
w IMERG (IMERG mierzy tylko opad wody, nie rozróżnia deszczu od śniegu ani
nie mierzy temperatury/wiatru) — do przemyślenia osobno w przyszłości.

WYMAGA: zmiennych środowiskowych EARTHDATA_USERNAME i EARTHDATA_PASSWORD
(konto NASA Earthdata, z zatwierdzoną aplikacją "NASA GESDISC DATA ARCHIVE").

UWAGA: to pierwsza wersja tego skryptu, nie testowana na żywych danych NASA
(inne środowisko sieciowe niż to, w którym pisany był ten kod) — pierwsze
uruchomienie może wymagać poprawek, dokładnie tak jak przy budowie GEFS.
"""

import os
import json
import glob
from datetime import datetime, timedelta, timezone

import numpy as np
import xarray as xr
import earthaccess
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import geojsoncontour
import requests
from shapely.geometry import shape as shapely_shape, mapping as shapely_mapping
from shapely.ops import unary_union

LAT_MIN, LAT_MAX = 46.8, 55.5
LON_MIN, LON_MAX = 5.5, 24.5

COUNTRIES_GEOJSON_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_0_countries.geojson"
TARGET_COUNTRY_ISO3 = {"DEU", "POL", "CZE", "SVK"}
MIN_POLYGON_AREA_DEG2 = 0.03
MATRIX_LEVEL_NAMES = ["NONE", "SLIGHT", "ENHANCED", "MODERATE", "HIGH", "EXTREME"]
MATRIX_LEVEL_COLORS = ["#ffffff", "#22c55e", "#fde047", "#fb923c", "#ef4444", "#c026d3"]


def build_country_mask():
    """Ta sama maska co w generate_swwf.py — Niemcy/Polska/Czechy/Słowacja, wycina
    morze i sąsiednie kraje jednym krokiem."""
    resp = requests.get(COUNTRIES_GEOJSON_URL, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    relevant = [shapely_shape(f["geometry"]) for f in data["features"]
                if f["properties"].get("ISO_A3") in TARGET_COUNTRY_ISO3]
    return unary_union(relevant)


def level_grid_to_polygons(lats, lons, level_idx_grid, country_mask):
    """Uproszczona wersja grid_to_polygons z generate_swwf.py — bez wygładzania
    Chaikina (niepotrzebne dla tego, pomocniczego widoku weryfikacji). Zamienia
    ARCHIWALNĄ siatkę poziomów (już-skategoryzowaną, z wczorajszej prognozy) na
    polygony GeoJSON, przycięte do naszych 4 krajów."""
    arr = np.array(level_idx_grid, dtype=float)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    try:
        bounds = [i - 0.5 for i in range(len(MATRIX_LEVEL_NAMES) + 1)]
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
        geom = geom.intersection(country_mask)
        if geom.is_empty:
            continue

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


def find_yesterdays_00z_archive():
    """Szuka wczorajszego archiwum przebiegu 00z — to jedyny przebieg, którego
    Dzień 1 pokrywa się DOKŁADNIE z pełną dobą kalendarzową (00:00-24:00 UTC),
    więc tylko ten nadaje się do czystego porównania z dobową sumą IMERG."""
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    path = f"archive/{yesterday}_00z.json"
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Brak archiwum {path} — albo przebieg 00z nie był jeszcze gotowy "
            f"tego dnia (find_latest_run cofnął się na inny przebieg), albo "
            f"archiwizacja nie działała jeszcze wtedy. Nie ma z czym porównać."
        )
    with open(path, encoding="utf-8") as f:
        return yesterday, json.load(f)


def fetch_imerg_precip(target_date):
    """Pobiera dobową sumę opadu z GPM IMERG (Early Run) dla danego dnia,
    przycina do naszego regionu. Zwraca xr.DataArray (lat, lon) w mm."""
    auth = earthaccess.login(strategy="environment")
    if not auth.authenticated:
        raise RuntimeError(
            "Logowanie do NASA Earthdata nie powiodło się — sprawdź sekrety "
            "EARTHDATA_USERNAME/EARTHDATA_PASSWORD i czy aplikacja "
            "'NASA GESDISC DATA ARCHIVE' jest zatwierdzona na koncie."
        )

    results = earthaccess.search_data(
        short_name="GPM_3IMERGDE",
        version="07",
        temporal=(target_date, target_date),
    )
    if not results:
        raise RuntimeError(f"Brak wyników IMERG dla {target_date} — dane mogą jeszcze nie być gotowe.")

    files = earthaccess.download(results, "./imerg_tmp")
    ds = xr.open_dataset(files[0])

    # nazwa zmiennej z opadem bywa różna zależnie od dokładnej wersji produktu —
    # sprawdzamy kilka znanych wariantów, zamiast zakładać jedną z góry
    candidates = ["precipitation", "precipitationCal", "precip"]
    var_name = next((c for c in candidates if c in ds.data_vars), None)
    if var_name is None:
        raise RuntimeError(
            f"Nie znaleziono zmiennej opadu w pliku IMERG. Dostępne zmienne: "
            f"{list(ds.data_vars)} — trzeba dopisać właściwą nazwę do listy candidates."
        )

    precip = ds[var_name]
    if "time" in precip.dims:
        precip = precip.isel(time=0)

    # IMERG zwykle ma wymiary (lon, lat) w tej kolejności, nie (lat, lon) jak GEFS —
    # sprawdzamy i w razie potrzeby transponujemy
    if "lat" in precip.dims and "lon" in precip.dims:
        precip = precip.transpose("lat", "lon")

    precip = precip.sel(lat=slice(LAT_MIN, LAT_MAX), lon=slice(LON_MIN, LON_MAX))
    return precip


def main():
    print("Szukam wczorajszego archiwum (przebieg 00z)...")
    yesterday, archive = find_yesterdays_00z_archive()
    print(f"Znaleziono archiwum dla {yesterday}, przebieg {archive['model_run']}")

    forecast_precip = archive["hazards"]["precip_24h_mm"]["median_intensity"]
    forecast_level_grid = archive["hazards"]["precip_24h_mm"]["level_grid"]
    lats = archive["grid"]["lat"]
    lons = archive["grid"]["lon"]

    print("Generuję polygony wczorajszej prognozy (do nałożenia na mapę weryfikacji)...")
    country_mask = build_country_mask()
    forecast_areas = level_grid_to_polygons(lats, lons, forecast_level_grid, country_mask)

    print(f"Pobieram rzeczywisty opad IMERG dla {yesterday}...")
    imerg_precip = fetch_imerg_precip(yesterday)
    print(f"IMERG: zakres {float(imerg_precip.min()):.1f} - {float(imerg_precip.max()):.1f} mm")

    # przesiatkowanie IMERG (0.1°) na naszą siatkę (0.25°, z archiwum) — ta sama
    # metoda interpolacji, której już używaliśmy wcześniej (T850)
    imerg_regridded = imerg_precip.interp(lat=lats, lon=lons)
    actual_precip = np.round(imerg_regridded.values, 1)
    actual_precip = np.nan_to_num(actual_precip, nan=0.0).tolist()

    forecast_arr = np.array(forecast_precip)
    actual_arr = np.array(actual_precip)
    diff = actual_arr - forecast_arr

    result = {
        "date": yesterday,
        "model_run": archive["model_run"],
        "grid": {"lat": lats, "lon": lons},
        "precip_24h_mm": {
            "forecast": forecast_precip,
            "actual": actual_precip,
            "difference": np.round(diff, 1).tolist(),
            "forecast_areas": forecast_areas,
        },
        "summary": {
            "mean_bias_mm": round(float(np.mean(diff)), 2),
            "mean_absolute_error_mm": round(float(np.mean(np.abs(diff))), 2),
        },
    }

    os.makedirs("verification", exist_ok=True)
    out_path = f"verification/{yesterday}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # kopia pod stałą nazwą — frontend zawsze pyta o to samo, bez zgadywania
    # daty (unika problemów ze strefami czasowymi / brakującymi dniami)
    with open("verification/latest.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nZapisano {out_path} (i verification/latest.json)")
    print(f"Średnie odchylenie (bias): {result['summary']['mean_bias_mm']} mm")
    print(f"Średni błąd bezwzględny: {result['summary']['mean_absolute_error_mm']} mm")


if __name__ == "__main__":
    main()
