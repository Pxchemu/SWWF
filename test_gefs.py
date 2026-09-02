"""
SWWF — test: czy produkt atmos.25 (0.25°) dla GEFS jest FAKTYCZNIE dostępny
na AWS dla wszystkich 30 członków i obu potrzebnych zmiennych (opad, temperatura)?

Wymuszamy priority=["aws"], żeby Herbie NIE mógł po cichu przełączyć się na
NOMADS — jeśli czegoś nie ma na AWS, dostaniemy tu jawny "BRAK", zamiast
mylącego "czasem działa, czasem nie" (bo czasem akurat NOMADS odpowiedział).
"""

from datetime import datetime, timedelta, timezone
from herbie import Herbie

target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d 00:00")
FXX = 6

print(f"Przebieg: {target_date} UTC, tylko AWS (priority=['aws'])\n")

def check(member, search):
    try:
        H = Herbie(target_date, model="gefs", product="atmos.25", member=member, fxx=FXX,
                   priority=["aws"], verbose=False)
        if H.grib is None:
            return False
        H.xarray(search, remove_grib=True)
        return True
    except Exception:
        return False

precip_results = []
temp_results = []

for m in range(1, 31):
    ok_p = check(m, ":APCP:surface:0-6 hour acc")
    ok_t = check(m, ":TMP:2 m above ground:")
    precip_results.append(ok_p)
    temp_results.append(ok_t)
    print(f"  człon {m:>2}: opad={'OK  ' if ok_p else 'BRAK'}   temperatura={'OK' if ok_t else 'BRAK'}")

print(f"\nOpad (APCP) dostępny na AWS dla: {sum(precip_results)}/30 członków")
print(f"Temperatura (TMP) dostępna na AWS dla: {sum(temp_results)}/30 członków")

if sum(precip_results) == 30 and sum(temp_results) == 30:
    print("\n>>> WSZYSTKO jest na AWS — atmos.25 nadaje się do produkcji <<<")
else:
    print("\n>>> BRAKI na AWS — atmos.25 NIE nadaje się do niezawodnej automatyzacji <<<")
