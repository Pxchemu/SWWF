"""
SWWF — test: czy GEFS (atmos.25) publikuje TMP/GUST co 3h (nie tylko co 6h)?
Jeśli tak, możemy dwa razy gęściej próbkować minimum dla COLD, bez ruszania
reszty hazardów (które i tak agregują po 6h oknach).
"""

from datetime import datetime, timedelta, timezone
from herbie import Herbie

target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d 00:00")

print(f"Przebieg: {target_date} UTC, człon 1, produkt atmos.25\n")

for fxx in [3, 6, 9, 12]:
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
