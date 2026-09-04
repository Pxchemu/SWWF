"""
SWWF — test: czy rozszerzone zmienne (kategoryczny typ opadu, procent opadu
zamarzniętego, pokrywa śniegu, CAPE, widzialność), o których rozmawialiśmy
przy okazji Open-Meteo, są dostępne bezpośrednio w GEFS? Jeśli tak — nie
potrzebujemy w ogóle innego źródła dla tych ulepszeń.

Sprawdzamy najpierw w atmos.25 (którego już używamy w produkcji), a jeśli
czegoś tam brakuje, sprawdzamy też w pełnym atmos.5 (tak jak przy T850).
"""

from datetime import datetime, timedelta, timezone
from herbie import Herbie

target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d 00:00")

WANTED = ["CRAIN", "CFRZR", "CICEP", "CSNOW", "CPOFP", "SNOD", "WEASD", "CAPE", "CIN", "VIS"]

for product in ["atmos.25", "atmos.5"]:
    print(f"\n{'='*60}")
    print(f"PRODUKT: {product}")
    print('='*60)
    H = Herbie(target_date, model="gefs", product=product, member=1, fxx=6,
               priority=["aws"], verbose=False)
    for var in WANTED:
        try:
            inv = H.inventory(search=f":{var}:")
            if len(inv):
                row = inv.iloc[0]
                print(f"  {var:8s} -> JEST  (poziom: {row['level']}, opis: {row.get('phenomenon_description', row.get('?', ''))})")
            else:
                print(f"  {var:8s} -> brak")
        except Exception as e:
            print(f"  {var:8s} -> błąd sprawdzania ({e})")
