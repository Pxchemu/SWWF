"""
SWWF — test: czy GEFS (atmos.25) publikuje TMP/GUST co 3h również dla DALSZYCH
godzin prognozy (Dzień 2/3), nie tylko dla pierwszych 12h, które już sprawdziliśmy?
Sprawdzamy punkty w połowie okien: 27, 33, 39, 45 (Dzień 2), 51, 57, 63, 69 (Dzień 3).
"""

from datetime import datetime, timedelta, timezone
from herbie import Herbie

target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d 00:00")

print(f"Przebieg: {target_date} UTC, człon 1, produkt atmos.25\n")

for fxx in [24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 63, 66, 69, 72]:
    print(f"--- fxx={fxx} ---")
    try:
        H = Herbie(target_date, model="gefs", product="atmos.25", member=1, fxx=fxx,
                   priority=["aws"], verbose=False)
        inv_t = H.inventory(search=":TMP:2 m above ground:")
        inv_g = H.inventory(search=":GUST:surface:")
        print(f"  TMP 2m:  {'JEST' if len(inv_t) else 'brak'}")
        print(f"  GUST:    {'JEST' if len(inv_g) else 'brak'}")
    except Exception as e:
        print(f"  błąd: {e}")
    print()
