"""
SWWF — test: czy T850 (temperatura na 850hPa) jest dostępna w PEŁNYM
produkcie atmos.5 (0.5°) — skoro nie było jej w okrojonym atmos.25.
Sprawdzamy dokładną nazwę pola, zanim zbudujemy to na produkcji.
"""

from datetime import datetime, timedelta, timezone
from herbie import Herbie

target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d 00:00")

print(f"Przebieg: {target_date} UTC, człon 1, produkt atmos.5\n")

H = Herbie(target_date, model="gefs", product="atmos.5", member=1, fxx=6,
           priority=["aws"], verbose=False)

print("Wszystkie pola zawierające 'TMP' (temperatura, dowolny poziom) w tym pliku:\n")
inv = H.inventory(search=":TMP:")
print(inv.to_string())
