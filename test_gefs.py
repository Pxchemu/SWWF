"""
SWWF — test krok 5: siatka nad całą Polską zamiast jednego punktu.

Zamiast wyciągać jedną liczbę (Warszawa) z każdego pliku, przycinamy
całą siatkę do obszaru Polski i liczymy prawdopodobieństwo osobno
dla KAŻDEGO punktu siatki — to jest podstawa do rysowania map/polygonów.
"""

from datetime import datetime, timedelta, timezone
from herbie import Herbie
import numpy as np
import xarray as xr

target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d 00:00")

# ramka wokół Polski, z niewielkim zapasem na brzegach
LAT_MIN, LAT_MAX = 48.5, 55.5
LON_MIN, LON_MAX = 13.5, 24.5
LON_MIN_360, LON_MAX_360 = LON_MIN % 360, LON_MAX % 360

windows = [(0, 6), (6, 12), (12, 18), (18, 24)]
members = list(range(1, 31))


def crop_to_poland(da):
    lat = da.latitude
    # siatki GFS/GEFS bywają malejące (od 90 do -90) — obsługujemy oba warianty
    if float(lat[0]) > float(lat[-1]):
        lat_slice = slice(LAT_MAX, LAT_MIN)
    else:
        lat_slice = slice(LAT_MIN, LAT_MAX)
    return da.sel(latitude=lat_slice, longitude=slice(LON_MIN_360, LON_MAX_360))


print(f"Przebieg: {target_date} UTC — siatka nad Polską ({LAT_MIN}-{LAT_MAX}N, {LON_MIN}-{LON_MAX}E)\n")

# --- najpierw sprawdzamy przycinanie na JEDNYM pliku, zanim odpalimy pełną pętlę ---
print("Sprawdzam przycinanie na jednym pliku (człon 1, okno 0-6h)...")
H_check = Herbie(target_date, model="gefs", product="atmos.5", member=1, fxx=6, verbose=False)
ds_check = H_check.xarray(":APCP:surface:0-6 hour acc", remove_grib=True)
cropped_check = crop_to_poland(ds_check["tp"])
print(f"Kształt przed przycięciem: {ds_check['tp'].shape}")
print(f"Kształt PO przycięciu:     {cropped_check.shape}")
if cropped_check.size == 0:
    print("\n!!! PRZYCINANIE NIE DZIAŁA — siatka jest pusta. Przerywam, żeby nie tracić czasu na 120 pobrań.")
    raise SystemExit(1)
print("Wygląda dobrze — kontynuuję z pełną pętlą.\n")

# --- pełna pętla po wszystkich członkach ---
member_grids = []
failed = []

for m in members:
    try:
        total = None
        for start, end in windows:
            fxx = end
            search = f":APCP:surface:{start}-{end} hour acc"
            H = Herbie(target_date, model="gefs", product="atmos.5", member=m, fxx=fxx, verbose=False)
            ds = H.xarray(search, remove_grib=True)
            cropped = crop_to_poland(ds["tp"])
            total = cropped if total is None else total + cropped
        member_grids.append(total)
        print(f"  człon {m:>2}: OK (min {float(total.min()):.1f} mm, maks {float(total.max()):.1f} mm)")
    except Exception as e:
        failed.append(m)
        print(f"  człon {m:>2}: BŁĄD ({e})")

print(f"\nUdało się: {len(member_grids)}/{len(members)} członków")
if failed:
    print(f"Nieudane: {failed}")

if member_grids:
    stacked = xr.concat(member_grids, dim="member")
    print(f"\nKształt po złączeniu wszystkich członków: {stacked.shape}  (człon, lat, lon)")

    for threshold in [1, 5, 10, 20]:
        prob = (stacked >= threshold).mean(dim="member") * 100
        print(f"P(opad >= {threshold:>2}mm) nad Polską: od {float(prob.min()):.0f}% do {float(prob.max()):.0f}%")

    # punkt kontrolny — Warszawa, do porównania z poprzednim testem (na jednym punkcie, wyszło tam 13%)
    lat_check, lon_check = 52.23, 21.01 % 360
    check = stacked.sel(latitude=lat_check, longitude=lon_check, method="nearest")
    prob_check = float((check >= 5).mean(dim="member")) * 100
    print(f"\nKontrola (Warszawa): P(opad >=5mm) = {prob_check:.0f}% — powinno być zbliżone do wcześniejszego testu (13%)")
