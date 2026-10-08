"""
Archiwizacja zespołu IFS ENS (ECMWF, otwarte dane) dla wybranych punktów (stacje IMGW + miasta).

Po co: ECMWF trzyma w otwartych danych tylko OSTATNIE ~12 przebiegów (2-3 doby), a pełne archiwum jest
płatne. Historii nie da się odtworzyć wstecz, więc — tak jak przy ICON-EU — zapisujemy ją na bieżąco.
Po sezonie można porównać GEFS, IFS ENS i ICON-EU z obserwacjami IMGW i zdecydować o drugim źródle.

Dane: ECMWF Open Data (licencja CC-BY-4.0 — przy publicznym użyciu podać ECMWF jako źródło).
Plik `...-{krok}h-enfo-ef.grib2` zawiera wszystkie pola i WSZYSTKICH członków (kontrolny + 50 zaburzonych),
a obok leży `.index` (JSON na linię z przesunięciem i długością każdej wiadomości GRIB). Pobieramy tylko
potrzebne wiadomości zapytaniami HTTP Range, więc nie ściągamy całych plików.

Użycie:
    python archive_ecmwf_ens.py                  # przebieg wyliczony z aktualnego czasu (00 lub 12Z)
    python archive_ecmwf_ens.py "2026-10-08 00"  # konkretny przebieg (UTC; tylko z ostatnich 2-3 dób!)
    ECMWF_TEST=1 python archive_ecmwf_ens.py     # test: 3 kroki, 3 członków, nic nie trafia do archiwum;
                                                 # drukuje ilość pobranych danych i oszacowanie pełnego przebiegu

Wynik: ecmwf_archive/{RRRR-MM-DD}_{GG}z.json.gz — jedna paczka na przebieg:
    {"model", "run", "steps": [0,3,...,72], "members": [0,1,...,50] (0 = kontrolny), "units", "scale",
     "points": [{id, name, lat, lon, grid_lat, grid_lon, dist_km}],
     "data": {zmienna: [punkt][członek][krok]}  # liczby CAŁKOWITE = wartość * scale; null = brak,
     "missing": [...]}
Zmienne: t_2m (K, scale 100), tot_prec (mm = kg/m2, SUMA OD STARTU, scale 100), snow (mm w.e., SUMA OD STARTU,
scale 100). Dobowy opad = różnica między krokami.

Wymaga: pip install eccodes requests
"""
import gzip
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

import requests

# źródła w kolejności prób: replika w chmurze AWS, potem portal ECMWF (strona zaleca chmurę przy kłopotach z portalem)
BASES = [b for b in (os.environ.get("ECMWF_BASE", "").strip(),
                     "https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com",
                     "https://data.ecmwf.int/forecasts") if b]
HEADERS = {"User-Agent": "SWWF-archive/1.0 (research; GitHub Actions)"}

# param ECMWF -> (nazwa w archiwum, jednostka źródłowa -> mnożnik do mm/K, scale zapisu)
PARAMS = {
    "2t": ("t_2m", 1.0, 100),          # K
    "tp": ("tot_prec", 1000.0, 100),   # m -> mm
    "sf": ("snow", 1000.0, 100),       # m w.e. -> mm
}
ESSENTIAL = ("2t", "tp")
TEST = os.environ.get("ECMWF_TEST", "").strip() not in ("", "0")
STEPS = [0, 6] if TEST else list(range(0, 73, 3))
MEMBERS_LIMIT = 3 if TEST else 51
WORKERS = int(os.environ.get("ECMWF_WORKERS", "16"))
MAX_MISSING_FRACTION = 0.02
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecmwf_archive_test" if TEST else "ecmwf_archive")

try:                                    # te same punkty co w archiwum ICON-EU (łatwe porównanie)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from archive_icon_eu import POINTS
except Exception:
    POINTS = [("WARSZAWA", "Warszawa-Okęcie", 52.17, 20.97), ("KRAKOW", "Kraków-Balice", 50.08, 19.80),
              ("GDANSK", "Gdańsk-Rębiechowo", 54.38, 18.47), ("WROCLAW", "Wrocław-Strachowice", 51.10, 16.89)]

STATS = {"bytes": 0, "requests": 0}


def parse_run(argv):
    if len(argv) > 1 and argv[1].strip():
        text = argv[1].strip()
        run = None
        for fmt in ("%Y-%m-%d %H", "%Y-%m-%d %H:%M"):
            try:
                run = datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
                break
            except ValueError:
                pass
        if run is None or run.hour not in (0, 12):
            sys.exit('Zły przebieg. Oczekiwany: "RRRR-MM-DD GG" (UTC), GG = 00 lub 12.')
        return run
    # dane ENS pojawiają się na serwerze ok. 7-8 h po czasie nominalnym
    t = datetime.now(timezone.utc) - timedelta(hours=8)
    return t.replace(hour=t.hour // 12 * 12, minute=0, second=0, microsecond=0)


def file_url(base, run, step):
    stamp = run.strftime("%Y%m%d%H") + "0000"
    return f"{base}/{run:%Y%m%d}/{run:%H}z/ifs/0p25/enfo/{stamp}-{step}h-enfo-ef.grib2"


def http_get(url, headers=None, attempts=4, timeout=120):
    """Zwraca (status, bytes). 404/403 -> (status, None) bez ponawiania; inne błędy ponawia."""
    last = None
    for i in range(attempts):
        try:
            r = requests.get(url, headers={**HEADERS, **(headers or {})}, timeout=timeout)
            STATS["requests"] += 1
            if r.status_code in (403, 404):
                return r.status_code, None
            r.raise_for_status()
            STATS["bytes"] += len(r.content)
            return r.status_code, r.content
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"{url}: {last}")


def pick_base(run):
    """Pierwsze źródło, które ma indeks ostatniego kroku (przebieg kompletny)."""
    for base in BASES:
        try:
            _status, raw = http_get(file_url(base, run, STEPS[-1]) + ".index", attempts=1, timeout=30)
        except Exception:
            continue
        if raw is not None:
            return base
    return None


def wait_for_run(run, minutes):
    deadline = time.time() + minutes * 60
    while True:
        base = pick_base(run)
        if base:
            return base
        if time.time() >= deadline:
            return None
        print("  przebieg jeszcze niekompletny na serwerze ECMWF — czekam 3 min...", flush=True)
        time.sleep(180)


def read_index(base, run, step):
    """Lista wiadomości do pobrania dla kroku: (param, członek, offset, długość)."""
    st, raw = http_get(file_url(base, run, step) + ".index")
    if raw is None:
        return None
    out = []
    for line in raw.decode("utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        if d.get("levtype") != "sfc" or d.get("param") not in PARAMS:
            continue
        if d.get("type") == "cf":
            member = 0
        elif d.get("type") == "pf":
            member = int(d.get("number"))
        else:
            continue
        if member >= MEMBERS_LIMIT:
            continue
        out.append((d["param"], member, int(d["_offset"]), int(d["_length"])))
    return out


def read_points(grib_bytes, points):
    import eccodes
    gid = eccodes.codes_new_from_message(grib_bytes)
    try:
        try:
            missing = float(eccodes.codes_get(gid, "missingValue"))
        except Exception:
            missing = 9999.0
        found = eccodes.codes_grib_find_nearest_multiple(gid, False, [p[2] for p in points], [p[3] for p in points])
    finally:
        eccodes.codes_release(gid)
    out = []
    for f in found:
        v = f["value"]
        ok = v is not None and v == v and abs(v - missing) > 1e-6 and abs(v) < 1e8
        out.append((float(v) if ok else None, f["lat"], f["lon"], f["distance"]))
    return out


def fetch_message(base, run, step, param, member, offset, length):
    url = file_url(base, run, step)
    st, raw = http_get(url, headers={"Range": f"bytes={offset}-{offset + length - 1}"})
    if raw is None or len(raw) != length:
        return None
    return read_points(raw, POINTS)


def main():
    t0 = time.time()
    run = parse_run(sys.argv)
    wait_minutes = float(os.environ.get("ECMWF_WAIT_MINUTES", "60"))
    out_path = os.path.join(OUT_DIR, f"{run:%Y-%m-%d_%H}z.json.gz")
    print(f"IFS ENS — przebieg {run:%Y-%m-%d %H}Z UTC, punktów: {len(POINTS)}, kroków: {len(STEPS)}, "
          f"członków: {MEMBERS_LIMIT}" + (" [TEST]" if TEST else ""))
    if not TEST and os.path.exists(out_path):
        print(f"Już zarchiwizowane: {out_path} — pomijam.")
        return
    base = wait_for_run(run, wait_minutes)
    if not base:
        sys.exit("Przebieg nie jest kompletny na serwerze ECMWF (albo został już usunięty — trzymają ~12 przebiegów). "
                 "Uruchom ponownie później.")
    print(f"Źródło: {base.split('/')[2]}")

    jobs, plan = [], {}
    for step in STEPS:
        idx = read_index(base, run, step)
        if idx is None:
            sys.exit(f"Brak indeksu kroku {step} h.")
        plan[step] = idx
        for param, member, off, ln in idx:
            jobs.append((step, param, member, off, ln))
    print(f"Wiadomości do pobrania: {len(jobs)}", flush=True)

    results = {}
    grid_info = None
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(fetch_message, base, run, s, p, m, o, l): (s, p, m) for s, p, m, o, l in jobs}
        for fut in as_completed(futs):
            key = futs[fut]
            vals = fut.result()
            if vals is not None:
                results[key] = [x[0] for x in vals]
                if grid_info is None:
                    grid_info = [(x[1], x[2], x[3]) for x in vals]
            done += 1
            if done % 500 == 0:
                print(f"  pobrano {done}/{len(jobs)}  ({STATS['bytes'] / 1e6:.0f} MB)", flush=True)

    members = list(range(MEMBERS_LIMIT))
    missing = []
    for step in STEPS:
        for param in PARAMS:
            if step == 0 and param in ("tp", "sf"):
                continue                # pola sum nie istnieją w kroku 0
            for m in members:
                if (step, param, m) not in results:
                    missing.append(f"{param}@{step}#{m}")
    total = sum(1 for s in STEPS for p in PARAMS for _ in members if not (s == 0 and p in ("tp", "sf")))
    for param in ESSENTIAL:
        lack = [x for x in missing if x.startswith(param + "@")]
        if len(lack) > MAX_MISSING_FRACTION * (total / len(PARAMS)):
            sys.exit(f"Za dużo brakujących wiadomości zmiennej {param} ({len(lack)}) — nie zapisuję niekompletnej paczki.")
    if grid_info is None:
        sys.exit("Brak jakichkolwiek danych.")

    data = {}
    for param, (name, mult, scale) in PARAMS.items():
        arr = []
        for pi in range(len(POINTS)):
            per_member = []
            for m in members:
                row = []
                for step in STEPS:
                    v = results.get((step, param, m))
                    x = None if v is None or v[pi] is None else int(round(v[pi] * mult * scale))
                    row.append(x)
                per_member.append(row)
            arr.append(per_member)
        data[name] = arr

    doc = {
        "model": "ifs-enfo-0p25",
        "source": "ECMWF Open Data (CC-BY-4.0)",
        "run": run.strftime("%Y-%m-%dT%H:00Z"),
        "archived_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "steps": STEPS,
        "members": members,
        "units": {"t_2m": "K", "tot_prec": "mm (suma od startu)", "snow": "mm w.e. (suma od startu)"},
        "scale": {name: scale for name, _mult, scale in PARAMS.values()},
        "points": [{"id": p[0], "name": p[1], "lat": p[2], "lon": p[3],
                    "grid_lat": round(g[0], 4), "grid_lon": round(g[1], 4), "dist_km": round(g[2], 2)}
                   for p, g in zip(POINTS, grid_info)],
        "data": data,
        "missing": sorted(missing)[:200],
        "n_missing": len(missing),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = out_path + ".tmp"
    with gzip.open(tmp, "wt", encoding="utf-8", compresslevel=9) as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, out_path)
    elapsed = time.time() - t0
    size_kb = os.path.getsize(out_path) / 1024
    print(f"Zapisano: {out_path} ({size_kb:.0f} KB), brakujących wiadomości: {len(missing)}")
    print(f"Pobrano {STATS['bytes'] / 1e6:.0f} MB w {STATS['requests']} zapytaniach, czas {elapsed:.0f} s")
    if TEST:
        full_msgs = 25 * len(PARAMS) * 51
        factor = full_msgs / max(len(jobs), 1)
        print(f"SZACUNEK pełnego przebiegu (25 kroków x 51 członków x {len(PARAMS)} pola): "
              f"~{STATS['bytes'] * factor / 1e9:.1f} GB, ~{elapsed * factor / 60:.0f} min "
              f"(czas bez czekania na serwer; plik wynikowy ok. {size_kb * 51 / MEMBERS_LIMIT * 25 / len(STEPS):.0f} KB)")


if __name__ == "__main__":
    main()
