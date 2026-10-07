"""
Archiwizacja deterministycznego ICON-EU (DWD) dla wybranych punktów (stacje IMGW + miasta).

Po co: DWD trzyma w otwartych danych tylko NAJNOWSZY przebieg każdej godziny (w katalogu 00/
jest teraz tylko dzisiejszy przebieg 00Z, wczorajszy już nie istnieje). Nie da się więc odtworzyć
starych prognoz ICON-EU wstecz — historia powstaje tylko, jeśli ją zapisujemy na bieżąco. Ten
skrypt co przebieg (00/06/12/18Z) zapisuje prognozę ICON-EU dla naszych punktów do repo, żeby
po sezonie można było porównać ICON-EU i GEFS z obserwacjami IMGW (i zdecydować, czy ICON-EU
dokładać jako drugie źródło).

Użycie:
    python archive_icon_eu.py                  # przebieg wyliczony z aktualnego czasu
    python archive_icon_eu.py "2026-10-06 00"  # konkretny przebieg (UTC; tylko z ostatniej doby!)

Wynik: icon_archive/{RRRR-MM-DD}_{GG}z.json.gz — jedna paczka na przebieg. Struktura:
    {"model", "run", "steps": [0,3,...,72], "units": {zmienna: jednostka},
     "points": [{id, name, lat, lon, grid_lat, grid_lon, dist_km}],
     "data": {zmienna: [[wartość dla kroku 0, 3, ...] dla punktu 0, ... punktu 1, ...]},
     "missing": ["zmienna@krok", ...]}
Wartości są SUROWE (K, kg/m2 = mm, m, m/s). Pola opadowe (tot_prec, snow_gsp, snow_con) to
SUMY OD STARTU przebiegu — dobowy opad = różnica między krokami. null = brak pliku/wartości.

Zmienne: t_2m, tmin_2m, tmax_2m, tot_prec (opad całkowity), snow_gsp + snow_con (opad śniegu,
równoważnik wodny: wielkoskalowy + konwekcyjny), h_snow (wysokość pokrywy), u_10m, v_10m,
vmax_10m (porywy). Znaczenie tmin/tmax/vmax (okno uśredniania) sprawdzimy przy weryfikacji —
dlatego zapisujemy surowe wartości.

Wymaga: pip install eccodes requests
"""
import bz2
import gzip
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

import requests

BASE = "https://opendata.dwd.de/weather/nwp/icon-eu/grib"
FILE_FMT = "icon-eu_europe_regular-lat-lon_single-level_{stamp}_{step:03d}_{VAR}.grib2.bz2"
HEADERS = {"User-Agent": "SWWF-archive/1.0 (research; GitHub Actions)"}

VARS = {  # zmienna (nazwa katalogu DWD) -> jednostka surowych wartości
    "t_2m": "K",
    "tmin_2m": "K",
    "tmax_2m": "K",
    "tot_prec": "kg/m2 (suma od startu)",
    "snow_gsp": "kg/m2 (suma od startu)",
    "snow_con": "kg/m2 (suma od startu)",
    "h_snow": "m",
    "u_10m": "m/s",
    "v_10m": "m/s",
    "vmax_10m": "m/s",
}
ESSENTIAL = ("t_2m", "tot_prec")        # bez tych dwóch paczka jest bezwartościowa
STEPS = list(range(0, 73, 3))           # 0..72 h co 3 h (opady są sumami — wystarczy)
WORKERS = 8
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon_archive")

# (id, nazwa, szerokość, długość) — współrzędne przybliżone; siatka ICON-EU ma ~6 km, więc
# błąd rzędu kilku km nie ma znaczenia. Nazwy polskich stacji = nazwy z danych synop IMGW,
# żeby łatwo je było potem dopasować do obserwacji.
POINTS = [
    ("WARSZAWA", "Warszawa-Okęcie", 52.17, 20.97),
    ("KRAKOW", "Kraków-Balice", 50.08, 19.80),
    ("WROCLAW", "Wrocław-Strachowice", 51.10, 16.89),
    ("GDANSK", "Gdańsk-Rębiechowo", 54.38, 18.47),
    ("POZNAN", "Poznań-Ławica", 52.42, 16.83),
    ("KATOWICE", "Katowice-Muchowiec", 50.24, 19.03),
    ("LODZ", "Łódź-Lublinek", 51.72, 19.40),
    ("SZCZECIN", "Szczecin-Dąbie", 53.40, 14.62),
    ("LUBLIN", "Lublin-Radawiec", 51.22, 22.40),
    ("BIALYSTOK", "Białystok", 53.11, 23.16),
    ("SUWALKI", "Suwałki", 54.13, 22.95),
    ("RZESZOW", "Rzeszów-Jasionka", 50.11, 22.02),
    ("OLSZTYN", "Olsztyn", 53.77, 20.42),
    ("TORUN", "Toruń", 53.04, 18.60),
    ("KIELCE", "Kielce-Suków", 50.81, 20.69),
    ("OPOLE", "Opole", 50.63, 17.97),
    ("ZIELONA GORA", "Zielona Góra", 51.93, 15.53),
    ("KOLOBRZEG", "Kołobrzeg", 54.18, 15.58),
    ("KOSZALIN", "Koszalin", 54.20, 16.15),
    ("LEGNICA", "Legnica", 51.19, 16.20),
    ("BIELSKO-BIALA", "Bielsko-Biała", 49.81, 19.00),
    ("TERESPOL", "Terespol", 52.07, 23.62),
    ("SIEDLCE", "Siedlce", 52.18, 22.28),
    ("LESKO", "Lesko", 49.47, 22.34),
    ("JELENIA GORA", "Jelenia Góra", 50.90, 15.79),
    ("KLODZKO", "Kłodzko", 50.43, 16.65),
    ("USTKA", "Ustka", 54.58, 16.86),
    ("CHOJNICE", "Chojnice", 53.70, 17.53),
    ("GORZOW", "Gorzów Wielkopolski", 52.74, 15.28),
    ("LESZNO", "Leszno", 51.83, 16.53),
    ("SANDOMIERZ", "Sandomierz", 50.69, 21.72),
    ("ZAKOPANE", "Zakopane", 49.30, 19.96),
    ("KASPROWY WIERCH", "Kasprowy Wierch", 49.23, 19.98),
    ("SNIEZKA", "Śnieżka", 50.74, 15.74),
    ("BERLIN", "Berlin-Tegel", 52.56, 13.31),
    ("DRESDEN", "Drezno", 51.13, 13.77),
    ("MUENCHEN", "Monachium", 48.35, 11.81),
    ("HAMBURG", "Hamburg", 53.63, 10.00),
    ("FRANKFURT", "Frankfurt n. Menem", 50.03, 8.57),
    ("PRAHA", "Praga-Ruzyně", 50.10, 14.26),
    ("BRNO", "Brno-Tuřany", 49.15, 16.69),
    ("OSTRAVA", "Ostrawa-Mošnov", 49.69, 18.11),
    ("BRATISLAVA", "Bratysława", 48.17, 17.20),
    ("KOSICE", "Koszyce", 48.66, 21.22),
]


def parse_run(argv):
    """Przebieg z argumentu albo wyliczony: najnowszy 00/06/12/18Z, który już powinien być gotowy."""
    if len(argv) > 1 and argv[1].strip():
        text = argv[1].strip()
        for fmt in ("%Y-%m-%d %H", "%Y-%m-%d %H:%M"):
            try:
                run = datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
                break
            except ValueError:
                run = None
        if run is None or run.hour not in (0, 6, 12, 18):
            sys.exit('Zły przebieg. Oczekiwany: "RRRR-MM-DD GG" (UTC), GG = 00, 06, 12 lub 18.')
        return run
    # pliki danego przebiegu pojawiają się na serwerze ~2,5-3,5 h po jego czasie nominalnym
    t = datetime.now(timezone.utc) - timedelta(hours=3, minutes=30)
    return t.replace(hour=t.hour // 6 * 6, minute=0, second=0, microsecond=0)


def file_url(run, var, step):
    name = FILE_FMT.format(stamp=run.strftime("%Y%m%d%H"), step=step, VAR=var.upper())
    return f"{BASE}/{run:%H}/{var}/{name}"


def fetch_raw(url, attempts=4):
    """Pobiera i rozpakowuje plik GRIB2. 404 -> None (pliku nie ma); inne błędy: ponawia."""
    last = None
    for i in range(attempts):
        try:
            r = requests.get(url, headers=HEADERS, timeout=120)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return bz2.decompress(r.content)
        except Exception as e:  # sieć, zerwane połączenie, uszkodzone bz2
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"{url}: {last}")


def read_points(grib_bytes, points):
    """Wartości z najbliższych węzłów siatki dla wszystkich punktów naraz.

    Zwraca listę (wartość|None, szer. węzła, dł. węzła, odległość km) w kolejności punktów.
    """
    import eccodes
    gid = eccodes.codes_new_from_message(grib_bytes)
    try:
        try:
            missing = float(eccodes.codes_get(gid, "missingValue"))
        except Exception:
            missing = 9999.0
        found = eccodes.codes_grib_find_nearest_multiple(
            gid, False, [p[2] for p in points], [p[3] for p in points])
    finally:
        eccodes.codes_release(gid)
    out = []
    for f in found:
        v = f["value"]
        ok = v is not None and v == v and abs(v - missing) > 1e-6 and abs(v) < 1e8
        out.append((float(v) if ok else None, f["lat"], f["lon"], f["distance"]))
    return out


def wait_for_run(run, minutes):
    """Czeka aż pojawi się ostatni krok T_2M i TOT_PREC (przebieg bywa publikowany z opóźnieniem)."""
    probes = [file_url(run, v, STEPS[-1]) for v in ESSENTIAL]
    deadline = time.time() + minutes * 60
    while True:
        try:
            ok = all(requests.head(u, headers=HEADERS, timeout=30).status_code == 200 for u in probes)
        except Exception:
            ok = False
        if ok:
            return True
        if time.time() >= deadline:
            return False
        print("  przebieg jeszcze niekompletny na serwerze DWD — czekam 3 min...", flush=True)
        time.sleep(180)


def main():
    run = parse_run(sys.argv)
    wait_minutes = float(os.environ.get("ICON_WAIT_MINUTES", "60"))
    out_path = os.path.join(OUT_DIR, f"{run:%Y-%m-%d_%H}z.json.gz")
    print(f"ICON-EU — przebieg {run:%Y-%m-%d %H}Z UTC, punktów: {len(POINTS)}, kroków: {len(STEPS)}, "
          f"zmiennych: {len(VARS)}")
    if os.path.exists(out_path):
        print(f"Już zarchiwizowane: {out_path} — pomijam.")
        return
    if not wait_for_run(run, wait_minutes):
        sys.exit("Przebieg nie jest kompletny na serwerze DWD (albo już został nadpisany nowszym). "
                 "Uruchom ponownie później; starszych niż ~1 doba przebiegów nie da się pobrać.")

    jobs = [(v, s) for v in VARS for s in STEPS]
    results = {}      # (zmienna, krok) -> lista wartości po punktach
    grid_info = None  # (lat, lon, dystans) węzłów — z pierwszego udanego pliku
    missing = []

    def work(job):
        v, s = job
        raw = fetch_raw(file_url(run, v, s))
        return job, raw

    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = [ex.submit(work, j) for j in jobs]
        for fut in as_completed(futures):
            job, raw = fut.result()      # błąd sieci po ponowieniach przerywa całość (nic nie zapisujemy)
            v, s = job
            if raw is None:
                missing.append(f"{v}@{s}")
            else:
                vals = read_points(raw, POINTS)
                results[job] = [x[0] for x in vals]
                if grid_info is None:
                    grid_info = [(x[1], x[2], x[3]) for x in vals]
            done += 1
            if done % 50 == 0:
                print(f"  pobrano {done}/{len(jobs)}", flush=True)

    # kontrola kompletności: kroki podstawowych zmiennych muszą być (krok 0 bywa pominięty dla pól sum)
    for v in ESSENTIAL:
        lacking = [s for s in STEPS if (v, s) not in results and s != 0]
        if lacking:
            sys.exit(f"Brakuje kroków {lacking} zmiennej {v} — nie zapisuję niekompletnej paczki.")
    if grid_info is None:
        sys.exit("Brak jakichkolwiek danych.")

    data = {}
    for v in VARS:
        data[v] = []
        for p in range(len(POINTS)):
            row = []
            for s in STEPS:
                val = results.get((v, s))
                x = None if val is None else val[p]
                row.append(None if x is None else round(x, 4))
            data[v].append(row)

    doc = {
        "model": "icon-eu",
        "run": run.strftime("%Y-%m-%dT%H:00Z"),
        "archived_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "steps": STEPS,
        "units": VARS,
        "points": [
            {"id": p[0], "name": p[1], "lat": p[2], "lon": p[3],
             "grid_lat": round(g[0], 4), "grid_lon": round(g[1], 4), "dist_km": round(g[2], 2)}
            for p, g in zip(POINTS, grid_info)
        ],
        "data": data,
        "missing": sorted(missing),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = out_path + ".tmp"
    with gzip.open(tmp, "wt", encoding="utf-8", compresslevel=9) as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, out_path)
    print(f"Zapisano: {out_path} ({os.path.getsize(out_path) / 1024:.0f} KB), "
          f"brakujących plików: {len(missing)}" + (f" — {sorted(missing)[:10]}" if missing else ""))


if __name__ == "__main__":
    main()
