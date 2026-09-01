"""
SWWF — test krok 3a: PODGLĄD, nie jeszcze wyciąganie danych.

Zanim zaczniemy liczyć opad ze wszystkich 30 członków, sprawdzamy
najpierw, JAKIE dokładnie pola opadu są w pliku GEFS — bywa ich
kilka naraz (np. suma z ostatnich 6h i osobno suma "od startu"),
a wzięcie niewłaściwego dałoby błędny wynik albo błąd odczytu.
Ten skrypt tylko WYPISUJE listę dostępnych pól, nic nie liczy.
"""

from datetime import datetime, timedelta, timezone
from herbie import Herbie

target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d 00:00")
FXX = 24

print(f"Przebieg: {target_date} UTC, prognoza +{FXX}h, człon 1\n")

H = Herbie(target_date, model="gefs", product="atmos.5", member=1, fxx=FXX, verbose=False)

print("Wszystkie pola zawierające 'APCP' (opad skumulowany) w tym pliku:\n")
inv = H.inventory(searchString=":APCP:")
print(inv.to_string())

print("\n\nDla porównania, wszystkie pola zawierające 'PRATE' (natężenie opadu) w tym pliku:\n")
try:
    inv2 = H.inventory(searchString=":PRATE:")
    print(inv2.to_string())
except Exception as e:
    print(f"(brak / błąd: {e})")
