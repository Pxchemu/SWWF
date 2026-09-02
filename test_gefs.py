"""
SWWF — test: czy T850 (temperatura na poziomie 850hPa, potrzebna do ICE —
wykrywanie "warm nose" nad marznącą powierzchnią) jest w ogóle dostępna
w produkcie atmos.25 (0.25°, "Select Parms" — tylko ~35 najpopularniejszych
zmiennych)? Sprawdzamy to PRZED budowaniem tego w produkcji.
"""

from datetime import datetime, timedelta, timezone
from herbie import Herbie

target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d 00:00")

print(f"Przebieg: {target_date} UTC, człon 1, produkt atmos.25\n")

H = Herbie(target_date, model="gefs", product="atmos.25", member=1, fxx=6,
           priority=["aws"], verbose=False)

print("Wszystkie pola zawierające 'TMP' (temperatura, dowolny poziom) w tym pliku:\n")
inv = H.inventory(search=":TMP:")
print(inv.to_string())
