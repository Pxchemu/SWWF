"""
SWWF — test sanity-check: sprawdzenie, czy logika śniegu i mrozu w ogóle
DZIAŁA i daje sensowne, niezerowe wartości — na obszarze, gdzie mróz
i śnieg są gwarantowane przez cały rok (środek lądolodu Grenlandii),
zamiast czekać do zimy nad Europą.

To NIE dotyka generate_swwf.py ani prawdziwego swwf.json — czysto
jednorazowy test diagnostyczny na kilku członkach (nie wszystkich 30,
żeby było szybko).
"""

from datetime import datetime, timedelta, timezone
from herbie import Herbie
import numpy as np
import xarray as xr

# środek lądolodu Grenlandii — praktycznie gwarantowany mróz i śnieg cały rok
LAT_MIN, LAT_MAX = 70.0, 75.0
LON_MIN, LON_MAX = -45.0, -35.0
LON_MIN_360, LON_MAX_360 = LON_MIN % 360, LON_MAX % 360

WINDOWS = [(0, 6), (6, 12), (12, 18), (18, 24)]
TEST_MEMBERS = [1, 2, 3]  # tylko kilku, to sam sanity-check, nie pełna produkcja
SNOW_TEMP_THRESHOLD_C = 1.0


def snow_ratio(t2m_c):
    return xr.where(t2m_c <= -10, 15.0,
           xr.where(t2m_c <= -5, 12.0,
           xr.where(t2m_c <= 0, 10.0, 7.0)))


def find_latest_run():
    now = datetime.now(timezone.utc)
    candidate = now.replace(minute=0, second=0, microsecond=0)
    candidate -= timedelta(hours=candidate.hour % 6)
    for i in range(8):
        test_time = candidate - timedelta(hours=6 * i)
        try:
            H1 = Herbie(test_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                        member=1, fxx=6, priority=["aws"], verbose=False)
            H30 = Herbie(test_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                         member=30, fxx=6, priority=["aws"], verbose=False)
            if H1.grib is not None and H30.grib is not None:
                return test_time
        except Exception:
            continue
    raise RuntimeError("Nie znaleziono żadnego dostępnego przebiegu GEFS w ostatnich 48h")


def crop_to_region(da):
    lat = da.latitude
    lat_slice = slice(LAT_MAX, LAT_MIN) if float(lat[0]) > float(lat[-1]) else slice(LAT_MIN, LAT_MAX)
    return da.sel(latitude=lat_slice, longitude=slice(LON_MIN_360, LON_MAX_360))


run_time = find_latest_run()
print(f"Przebieg: {run_time.isoformat()}")
print(f"Obszar testowy: środek lądolodu Grenlandii ({LAT_MIN}-{LAT_MAX}N, {LON_MIN}-{LON_MAX}E)\n")

for m in TEST_MEMBERS:
    precip_total = None
    snow_total = None
    min_t2m = None
    for start, end in WINDOWS:
        fxx = end
        H_p = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                     member=m, fxx=fxx, priority=["aws"], verbose=False)
        ds_p = H_p.xarray(f":APCP:surface:{start}-{end} hour acc", remove_grib=True)
        precip_window = crop_to_region(ds_p["tp"])

        H_t = Herbie(run_time.strftime("%Y-%m-%d %H:%M"), model="gefs", product="atmos.25",
                     member=m, fxx=fxx, priority=["aws"], verbose=False)
        ds_t = H_t.xarray(":TMP:2 m above ground:", remove_grib=True)
        t2m_window_c = crop_to_region(ds_t["t2m"]) - 273.15

        is_snow = t2m_window_c <= SNOW_TEMP_THRESHOLD_C
        ratio = snow_ratio(t2m_window_c)
        snow_window_cm = xr.where(is_snow, precip_window / 10.0 * ratio, 0.0)

        precip_total = precip_window if precip_total is None else precip_total + precip_window
        snow_total = snow_window_cm if snow_total is None else snow_total + snow_window_cm
        min_t2m = t2m_window_c if min_t2m is None else xr.where(t2m_window_c < min_t2m, t2m_window_c, min_t2m)

    print(f"człon {m}:")
    print(f"  opad (mm):        min {float(precip_total.min()):.1f}  maks {float(precip_total.max()):.1f}")
    print(f"  śnieg (cm):       min {float(snow_total.min()):.1f}  maks {float(snow_total.max()):.1f}")
    print(f"  temperatura (C):  min {float(min_t2m.min()):.1f}  maks {float(min_t2m.max()):.1f}")
    print()

print("Jeśli widzisz temperatury wyraźnie poniżej zera i niezerowe wartości śniegu")
print("(nawet przy zerowym/niskim opadzie mm, bo mróz sam w sobie już potwierdza COLD)")
print("— cała logika snow_ratio + próg śniegu + minimum dobowe działa poprawnie.")
