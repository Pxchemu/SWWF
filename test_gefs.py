"""
SWWF — test krok 3b: suma opadu z 24 godzin, dla JEDNEGO członka.

Odkryliśmy w kroku 3a, że GEFS ma tylko sumy 6-godzinne (0-6h, 6-12h,
12-18h, 18-24h), nie jedną sumę "od startu". Żeby dostać opad z całej
doby, trzeba pobrać wszystkie cztery kawałki i je zsumować.

Na razie tylko JEDEN członek (żeby sprawdzić, czy sumowanie w ogóle
działa i daje sensowną liczbę) — pętlę po 30 członkach zrobimy
w następnym kroku, jak to już będzie działać poprawnie.
"""

from datetime import datetime, timedelta, timezone
from herbie import Herbie

target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d 00:00")
MEMBER = 1

LAT, LON = 52.23, 21.01
LON_360 = LON % 360

# cztery 6-godzinne okna składające się na pełną dobę (0-24h)
windows = [(0, 6), (6, 12), (12, 18), (18, 24)]

print(f"Przebieg: {target_date} UTC, człon {MEMBER}, punkt: Warszawa ({LAT}, {LON})\n")

total_mm = 0.0
for start, end in windows:
    fxx = end  # plik z danym oknem jest pod prognozą kończącą się na "end" godzinie
    search = f":APCP:surface:{start}-{end} hour acc"
    H = Herbie(target_date, model="gefs", product="atmos.5", member=MEMBER, fxx=fxx, verbose=False)
    ds = H.xarray(search, remove_grib=True)
    point = ds.sel(latitude=LAT, longitude=LON_360, method="nearest")
    # APCP jest w kg/m^2, co dla wody odpowiada 1:1 milimetrom opadu
    mm = float(point["tp"].values) if "tp" in point else float(list(point.data_vars.values())[0].values)
    print(f"  okno {start:>2}-{end}h: {mm:6.2f} mm")
    total_mm += mm

print(f"\n>>> SUMA opadu z 24h (0-24h) nad Warszawą: {total_mm:.1f} mm <<<")
print("\nJeśli to sensowna liczba (0-50mm w normalnych warunkach, nie coś jak 5000 albo ujemne)")
print("— sumowanie działa poprawnie i możemy to rozbudować na wszystkie 30 członków.")
