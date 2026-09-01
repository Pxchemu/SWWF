"""
SWWF — test krok 2: pętla po wszystkich członkach ensemble GEFS,
odczyt T2m nad Warszawą dla każdego, policzenie prostego procentu.

To jest pierwsza "prawdziwa" operacja SWWF: nie pojedynczy człon,
tylko statystyka po całym zestawie — dokładnie to, co odróżnia ten
moduł od zwykłego pobierania gotowych danych (jak reszta MeteoPanelu).
"""

from datetime import datetime, timedelta, timezone
from herbie import Herbie
import numpy as np

target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d 00:00")
FXX = 24  # prognoza na +24h

# współrzędne Warszawy — tu sprawdzamy przykładowy próg
LAT, LON = 52.23, 21.01
LON_360 = LON % 360  # siatka GEFS używa zakresu 0-360, nie -180/180

print(f"Przebieg: {target_date} UTC, prognoza +{FXX}h, punkt: Warszawa ({LAT}, {LON})\n")

members = list(range(1, 31))  # 30 "perturbowanych" członków (gep01..gep30)
results = []
failed = []

for m in members:
    try:
        H = Herbie(target_date, model="gefs", product="atmos.5", member=m, fxx=FXX, verbose=False)
        ds = H.xarray(":TMP:2 m above ground:", remove_grib=True)
        point = ds.sel(latitude=LAT, longitude=LON_360, method="nearest")
        t2m_c = float(point["t2m"].values) - 273.15
        results.append(t2m_c)
        print(f"  człon {m:>2}: {t2m_c:6.1f}°C")
    except Exception as e:
        failed.append(m)
        print(f"  człon {m:>2}: BŁĄD ({e})")

print(f"\nUdało się: {len(results)}/{len(members)} członków")
if failed:
    print(f"Nieudane: {failed}")

if results:
    results = np.array(results)
    below_zero = int((results < 0).sum())
    pct = 100 * below_zero / len(results)
    print(f"\nŚrednia T2m nad Warszawą: {results.mean():.1f}°C")
    print(f"Rozrzut (min-max): {results.min():.1f}°C do {results.max():.1f}°C")
    print(f"\n>>> {below_zero}/{len(results)} członków ({pct:.0f}%) pokazuje T2m < 0°C <<<")
    print("To jest dokładnie ten typ liczby, którą SWWF będzie pokazywał jako prawdopodobieństwo zagrożenia.")
else:
    print("\nŻaden człon się nie udał — coś jest nie tak z połączeniem albo dostępnością danych.")
