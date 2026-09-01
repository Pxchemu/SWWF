"""
SWWF — test krok 1: sprawdzenie, czy da się w ogóle pobrać i odczytać
jeden plik GEFS (jeden member, jedna zmienna, jedna godzina prognozy).

Nie liczy jeszcze niczego meteorologicznego — to tylko test całego łańcucha:
pobranie z AWS -> parsowanie GRIB2 -> odczyt konkretnej wartości.
"""

from datetime import datetime, timedelta, timezone
from herbie import Herbie

# Bierzemy wczorajszy przebieg o 00Z — na pewno już dostępny na AWS
# (GEFS pojawia się na AWS z opóźnieniem kilku godzin po starcie modelu)
target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d 00:00")

print(f"Szukam przebiegu GEFS z: {target_date} UTC")

H = Herbie(
    target_date,
    model="gefs",       # Global Ensemble Forecast System
    product="atmos.5",  # siatka 0.5 stopnia — dostępna dla wszystkich 30 członków
    member=1,            # pojedynczy człon ensemble (1-30); "mean"/"avg" = średnia z całego ensemble
    fxx=24,               # prognoza na +24h
)

print(f"Znaleziono plik? {H.grib is not None}")
print(f"Źródło: {H.SOURCES.get(H.grib_source) if hasattr(H, 'SOURCES') else H.grib_source}")

# pobiera TYLKO fragment pliku odpowiadający T2m (nie cały plik GRIB2 — ten trik
# z .idx / byte-range to właśnie to, o czym mowa w dokumencie planu)
ds = H.xarray(":TMP:2 m above ground:")

print("\n--- Wynik ---")
print(ds)

t2m_celsius = float(ds["t2m"].mean()) - 273.15
print(f"\nŚrednia T2m (cały globalny obszar siatki): {t2m_celsius:.1f}°C")
print("\nJeśli widzisz sensowną liczbę powyżej (nie błąd) — cały łańcuch działa.")
