"""
SWWF — test krok 4: suma opadu 24h dla WSZYSTKICH 30 członków,
policzenie realnego prawdopodobieństwa przekroczenia progu.

To jest pierwsza wersja bliska prawdziwemu SWWF — jeszcze nie liczy
grubości śniegu (to osobny krok: trzeba przeliczyć mm wody na cm
śniegu, co zależy od temperatury), tylko sam opad (mm wody).
"""

from datetime import datetime, timedelta, timezone
from herbie import Herbie
import numpy as np

target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d 00:00")

LAT, LON = 52.23, 21.01
LON_360 = LON % 360

windows = [(0, 6), (6, 12), (12, 18), (18, 24)]
members = list(range(1, 31))

print(f"Przebieg: {target_date} UTC, punkt: Warszawa ({LAT}, {LON})")
print(f"Liczę sumę opadu z 24h dla {len(members)} członków (4 okna 6h każdy = {len(members)*4} pobrań)\n")

totals = []
failed = []

for m in members:
    try:
        member_total = 0.0
        for start, end in windows:
            fxx = end
            search = f":APCP:surface:{start}-{end} hour acc"
            H = Herbie(target_date, model="gefs", product="atmos.5", member=m, fxx=fxx, verbose=False)
            ds = H.xarray(search, remove_grib=True)
            point = ds.sel(latitude=LAT, longitude=LON_360, method="nearest")
            member_total += float(point["tp"].values)
        totals.append(member_total)
        print(f"  człon {m:>2}: {member_total:6.1f} mm")
    except Exception as e:
        failed.append(m)
        print(f"  człon {m:>2}: BŁĄD ({e})")

print(f"\nUdało się: {len(totals)}/{len(members)} członków")
if failed:
    print(f"Nieudane: {failed}")

if totals:
    totals = np.array(totals)
    print(f"\nŚrednia: {totals.mean():.1f} mm")
    print(f"Rozrzut: {totals.min():.1f} - {totals.max():.1f} mm")

    for threshold in [1, 5, 10, 20]:
        count = int((totals >= threshold).sum())
        pct = 100 * count / len(totals)
        print(f"P(opad >= {threshold:>2}mm / 24h): {count}/{len(totals)} członków = {pct:.0f}%")

    print("\nUWAGA: to opad w mm wody, NIE grubość śniegu w cm — przeliczenie zależy od")
    print("temperatury i jest osobnym krokiem, którego jeszcze nie zrobiliśmy.")
