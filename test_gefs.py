"""
SWWF — test: czy wiatr (10m, potrzebny do BLIZZARD) jest dostępny
w produkcie atmos.25? Sprawdzamy dokładne nazwy pól (UGRD/VGRD czy
może gotowy WIND) przed budową na produkcji.
"""

from datetime import datetime, timedelta, timezone
from herbie import Herbie

target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d 00:00")

print(f"Przebieg: {target_date} UTC, człon 1, produkt atmos.25\n")

H = Herbie(target_date, model="gefs", product="atmos.25", member=1, fxx=6,
           priority=["aws"], verbose=False)

for keyword in ["UGRD", "VGRD", "WIND", "GUST"]:
    print(f"--- Pola zawierające '{keyword}' ---")
    try:
        inv = H.inventory(search=f":{keyword}:")
        print(inv.to_string() if len(inv) else "(brak)")
    except Exception as e:
        print(f"(błąd / brak: {e})")
    print()
