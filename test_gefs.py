"""
SWWF — test: czy da się użyć gęstszej siatki (0.25 stopnia zamiast 0.5)?

GEFS ma osobny produkt "atmos.25" z dwukrotnie gęstszą siatką,
dostępny podobno dla każdego członka osobno (nie tylko dla średniej).
Sprawdzamy to na jednym pliku, zanim przerobimy na to cały skrypt produkcyjny.
"""

from datetime import datetime, timedelta, timezone
from herbie import Herbie

target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d 00:00")

print(f"Przebieg: {target_date} UTC, człon 1, produkt atmos.25 (0.25°)\n")

H = Herbie(target_date, model="gefs", product="atmos.25", member=1, fxx=6, verbose=False)
print(f"Znaleziono plik? {H.grib is not None}")

print("\nWszystkie pola APCP dostępne w tym pliku (0.25°):")
inv = H.inventory(search=":APCP:")
print(inv.to_string())

ds = H.xarray(":APCP:surface:0-6 hour acc", remove_grib=True)
print(f"\nKształt siatki (globalnie): {ds['tp'].shape}")
print(f"Dla porównania: przy 0.5° było to (361, 720)")

LAT_MIN, LAT_MAX = 48.5, 55.5
LON_MIN_360, LON_MAX_360 = 13.5 % 360, 24.5 % 360
lat = ds["tp"].latitude
lat_slice = slice(LAT_MAX, LAT_MIN) if float(lat[0]) > float(lat[-1]) else slice(LAT_MIN, LAT_MAX)
cropped = ds["tp"].sel(latitude=lat_slice, longitude=slice(LON_MIN_360, LON_MAX_360))
print(f"\nKształt PO przycięciu do Polski: {cropped.shape}")
print(f"Dla porównania: przy 0.5° było to (15, 23)")
print(f"\nWartości: min {float(cropped.min()):.2f} mm, maks {float(cropped.max()):.2f} mm")
