"""
Hindcast IFS ENS (ECMWF) dla stacji IMGW — ten sam format co `hindcast_points.py` (GEFS), żeby `calibrate_swwf.py`
mógł porównać oba modele na tych samych dniach i tych samych obserwacjach.

Źródło: replika AWS S3 (ecmwf-forecasts), historia od 2024-03 (51 członków: kontrolny + 50; zmienne mn2t3, mx2t3, 10fg,
mucape, ptype dopiero od ok. 2024-11-15 — wcześniej te pola są po prostu puste). Tylko przebiegi 00 i 12Z.

Pobieramy wyłącznie potrzebne wiadomości GRIB zapytaniami HTTP Range (indeks `.index`), jak w archive_ecmwf_ens.py.
Domyślnie tylko 2t i tp (minimum do porównania z GEFS); IFS_EXTRAS=1 dokłada 2d, 10u, 10v, mn2t3, mx2t3, 10fg, mucape, ptype.

Użycie (zwykle przez workflow hindcast-ifs.yml):
    python hindcast_ifs.py extract "2025-01-15 00" 0 16 hindcast_chunks     # przebieg, członkowie od-do (0 = kontrolny)
    python hindcast_points.py merge hindcast_chunks hindcast_ifs            # scalenie (to samo narzędzie co GEFS)

Mapowanie na pola hindcastu GEFS (okna 6 h: 0-6, ..., 72-78 h; "połowa" = start + 3 h):
    apcp       = tp(koniec) - tp(start)      [mm]   (tp = suma od startu)
    t_end/mid  = 2t(koniec | połowa) - 273.15 [°C]
    u10/v10    = 10u/10v (koniec | połowa)
    rh         = z 2t i 2d (wzór Magnusa) [%]
    gust       = 10fg (maks. porywy z 3 h przed krokiem) — tylko od 2024-11
    cape_end   = mucape (koniec)                — tylko od 2024-11
    brak w IFS: cpofp_end, cfrzr_end, vis_end, snod_end (puste)
Dodatkowe pola (nowe, calibrate_swwf.py ich jeszcze nie używa): tmin3_end/mid (mn2t3), tmax3_end/mid (mx2t3), ptype_end/mid.

Wymaga: pip install eccodes requests
"""
import gzip
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import archive_ecmwf_ens as A                      # http_get, file_url, index_url, read_points, BASES
import hindcast_points as H                        # FIELDS, WINDOWS, load_stations

STEPS = list(range(0, 79, 3))                      # 27 kroków: 0..78 h co 3 h
STEPS_3H = set(range(3, 79, 3))                     # końce i połowy okien 6 h
STEPS_6H = set(range(6, 79, 6))                     # tylko końce okien
# Pliki ECMWF są GLOBALNE (pole 0,25° na cały świat, ok. 0,7-1,4 MB na wiadomość) i nie da się pobrać samego fragmentu
# Europy — dlatego liczba parametrów decyduje o czasie. Minimum do porównania z GEFS to 2t i tp.
BASE_PARAMS = ("2t", "tp")
EXTRA_PARAMS = ("2d", "10u", "10v", "mn2t3", "mx2t3", "10fg", "mucape", "ptype")
ESSENTIAL = ("apcp", "t_end")
WORKERS = int(os.environ.get("IFS_WORKERS", "4"))   # S3 ECMWF dławi (503 SlowDown) przy zbyt wielu równoległych zapytaniach
RETRY_ROUNDS = 4                                       # ile razy ponawiamy nieudane wiadomości po głównym przebiegu

FIELDS = dict(H.FIELDS)
FIELDS.update({
    "tmin3_end": "minimum T2m z 3 h przed końcem okna [°C] (mn2t3; od 2024-11)",
    "tmin3_mid": "minimum T2m z 3 h przed połową okna [°C]",
    "tmax3_end": "maksimum T2m z 3 h przed końcem okna [°C] (mx2t3; od 2024-11)",
    "tmax3_mid": "maksimum T2m z 3 h przed połową okna [°C]",
    "ptype_end": "typ opadu ECMWF na końcu okna (kod: 0 brak, 1 deszcz, 3 marznący deszcz, 5 śnieg, 6 mokry śnieg, 7 deszcz ze śniegiem, 8 granulki lodu; od 2024-11)",
    "ptype_mid": "typ opadu ECMWF w połowie okna",
})


def parse_run(text):
    run = datetime.strptime(text.strip(), "%Y-%m-%d %H").replace(tzinfo=timezone.utc)
    if run.hour not in (0, 12):
        sys.exit("Tylko przebiegi 00 i 12Z.")
    return run


def pick_base(run):
    """Pierwsze źródło mające przebieg (AWS ma historię, portal tylko ostatnie doby)."""
    for base in A.BASES:
        st, raw = A.http_get(A.index_url(base, run, STEPS[-1]), attempts=12, timeout=60)
        if raw is not None:
            return base
    return None


def read_index(base, run, step, params):
    """[(param, członek, offset, długość)] dla kroku; członek 0 = kontrolny (type cf)."""
    st, raw = A.http_get(A.index_url(base, run, step), attempts=14)
    if raw is None:
        return None
    out = []
    for line in raw.decode("utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        if d.get("levtype") != "sfc" or d.get("param") not in params:
            continue
        if d.get("type") == "cf":
            member = 0
        elif d.get("type") == "pf":
            member = int(d.get("number"))
        else:
            continue
        out.append((d["param"], member, int(d["_offset"]), int(d["_length"])))
    return out


def fetch(base, run, step, offset, length, points):
    try:
        st, raw = A.http_get(A.file_url(base, run, step), headers={"Range": f"bytes={offset}-{offset + length - 1}"}, attempts=10)
    except Exception as e:
        return None, f"siec: {str(e)[-100:]}"
    if raw is None or len(raw) != length:
        return None, f"HTTP {st} / dlugosc"
    if raw[:4] != b"GRIB" or raw[-4:] != b"7777":          # zle przesuniecie (np. inny plik na lustrze) - odrzuc
        return None, "GRIB: zly poczatek/koniec wiadomosci"
    try:
        return A.read_points(raw, points), None
    except Exception as e:
        return None, f"GRIB: {type(e).__name__}: {str(e)[:80]}"


def needed_steps(param):
    """Które kroki są naprawdę używane: tp tylko na granicach okien 6 h (6, 12, ... 78 h; reszta to ~30% zbędnych
    pobrań), cape (mucape) tylko na końcach okien, pozostałe pola także w połowie okna (3, 6, 9, ... 78 h)."""
    if param in ("tp", "mucape"):
        return STEPS_6H
    return STEPS_3H


def rh_from(t_k, td_k):
    if t_k is None or td_k is None:
        return None
    t, td = t_k - 273.15, td_k - 273.15
    rh = 100.0 * math.exp(17.625 * td / (243.04 + td)) / math.exp(17.625 * t / (243.04 + t))
    return max(0.0, min(100.0, rh))


def r3(v):
    return None if v is None or v != v else round(v, 3)


def extract(run, m_from, m_to, outdir, extras=False):
    stations = H.load_stations()
    points = [(s["code"], s["name"], s["lat"], s["lon"]) for s in stations]
    params = set(BASE_PARAMS) | (set(EXTRA_PARAMS) if extras else set())
    base = pick_base(run)
    if not base:
        sys.exit(f"Przebieg {run:%Y-%m-%d %H}Z niedostępny na żadnym źródle (zbyt stary albo jeszcze nie opublikowany).")
    print(f"IFS ENS {run:%Y-%m-%d %H}Z, źródło: {base.split('/')[2]}, stacji: {len(stations)}, "
          f"członkowie {m_from}-{m_to}, parametry: {sorted(params)}", flush=True)

    t0 = time.time()
    jobs, present = [], set()
    steps = [st for st in STEPS if st > 0]                 # krok 0 nie jest używany (opad okna 0-6 h = tp(6 h) - 0)
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:     # indeksy (po kilka MB każdy) równolegle, nie po kolei
        indexes = list(ex.map(lambda st: read_index(base, run, st, params), steps))
    for step, idx in zip(steps, indexes):
        if idx is None:
            sys.exit(f"Brak indeksu kroku {step} h — przebieg niekompletny.")
        for param, member, off, ln in idx:
            present.add(param)
            if m_from <= member <= m_to and step in needed_steps(param):
                jobs.append((step, param, member, off, ln))
    print(f"Wiadomości do pobrania: {len(jobs)}; dostępne parametry: {sorted(present)}", flush=True)
    for need in ("2t", "tp"):
        if need not in present:
            sys.exit(f"W indeksie brak wymaganego parametru {need}.")

    vals, fails, grid_info, done = {}, {}, None, 0

    def run_pass(todo, workers, label):
        """Pobiera listę wiadomości; zwraca słownik nieudanych {klucz: powód}."""
        nonlocal grid_info, done
        bad, n = {}, 0
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(fetch, base, run, s, o, l, points): (s, p, m, o, l) for s, p, m, o, l in todo}
            for fut in as_completed(futs):
                s_, p_, m_, o_, l_ = futs[fut]
                res, why = fut.result()
                if res is None:
                    bad[(s_, p_, m_, o_, l_)] = why
                else:
                    vals[(s_, p_, m_)] = [x[0] for x in res]
                    if grid_info is None:
                        grid_info = [(x[1], x[2], x[3]) for x in res]
                n += 1
                done += 1
                if done % 500 == 0:
                    print(f"  {label}: {n}/{len(todo)}  ({A.STATS['bytes'] / 1e6:.0f} MB, {time.time() - t0:.0f} s)", flush=True)
        return bad

    pending = run_pass(jobs, WORKERS, "pobrano")
    for rnd in range(1, RETRY_ROUNDS + 1):
        if not pending:
            break
        print(f"Nieudane wiadomości: {len(pending)} (np. {next(iter(pending.values()))}); runda ponowień {rnd}/{RETRY_ROUNDS} "
              f"za {30 * rnd} s, wątków: {max(1, WORKERS // 2)}", flush=True)
        time.sleep(30 * rnd)
        pending = run_pass(list(pending), max(1, WORKERS // 2), f"ponowienie {rnd}")
    fails = pending
    if fails:
        print(f"Niepowodzenia pobierania po {RETRY_ROUNDS} rundach ponowień: {len(fails)} (pierwsze 5):")
        for k, why in list(fails.items())[:5]:
            print(f"  krok {k[0]} h, {k[1]}, członek {k[2]}: {why}")
        # lepiej nie zapisać nic niż zapisać dziurawy kawałek (brakujących członków nikt by nie zauważył);
        # ponów to zadanie przyciskiem "Re-run failed jobs" — scalanie dopisze brakujące
        sys.exit("Kawałek niekompletny — nie zapisuję pliku. Uruchom ponownie nieudane zadania.")
    if grid_info is None:
        sys.exit("Brak jakichkolwiek danych.")

    def get(param, step, member, s, mult=1.0, add=0.0):
        v = vals.get((step, param, member))
        if v is None or v[s] is None:
            return None
        return v[s] * mult + add

    members_out, data, missing = [], {k: [] for k in FIELDS}, {}
    members = sorted({m for (_, _, m) in vals})
    for m in members:
        per = {k: [[None] * len(H.WINDOWS) for _ in stations] for k in FIELDS}
        for si in range(len(stations)):
            for w, (start, end) in enumerate(H.WINDOWS):
                mid = start + 3
                tp_end = get("tp", end, m, si, 1000.0)
                tp_start = 0.0 if start == 0 else get("tp", start, m, si, 1000.0)
                per["apcp"][si][w] = r3(max(tp_end - tp_start, 0.0)) if tp_end is not None and tp_start is not None else None
                per["t_end"][si][w] = r3(get("2t", end, m, si, 1.0, -273.15))
                per["t_mid"][si][w] = r3(get("2t", mid, m, si, 1.0, -273.15))
                for tag, st_ in (("end", end), ("mid", mid)):
                    per[f"u10_{tag}"][si][w] = r3(get("10u", st_, m, si))
                    per[f"v10_{tag}"][si][w] = r3(get("10v", st_, m, si))
                    per[f"rh_{tag}"][si][w] = r3(rh_from(get("2t", st_, m, si), get("2d", st_, m, si)))
                    per[f"gust_{tag}"][si][w] = r3(get("10fg", st_, m, si))
                    per[f"tmin3_{tag}"][si][w] = r3(get("mn2t3", st_, m, si, 1.0, -273.15))
                    per[f"tmax3_{tag}"][si][w] = r3(get("mx2t3", st_, m, si, 1.0, -273.15))
                    per[f"ptype_{tag}"][si][w] = r3(get("ptype", st_, m, si))
                per["cape_end"][si][w] = r3(get("mucape", end, m, si))
        bad = [k for k in ESSENTIAL if any(x is None for row in per[k] for x in row)]
        if bad:
            print(f"  członek {m:>2}: pominięty (braki w {bad})", flush=True)
            continue
        members_out.append(m)
        for k in FIELDS:
            data[k].append(per[k])
    if not members_out:
        sys.exit("Żaden członek nie jest kompletny — nie zapisuję pliku.")
    for k in FIELDS:                                       # ile pól pustych (diagnostyka: np. przebieg sprzed 2024-11)
        n = sum(1 for mi in range(len(members_out)) for row in data[k][mi] for x in row if x is None)
        if n:
            missing[k] = n

    for s, g in zip(stations, grid_info):
        s["grid_lat"] = round(g[0], 3)
        s["grid_lon"] = round(g[1], 3)
    doc = {"run": run.strftime("%Y-%m-%dT%H:00Z"), "model": "ifs-enfo-0p25", "windows": [list(w) for w in H.WINDOWS],
           "stations": stations, "members": members_out, "fields": FIELDS, "data": data, "missing": missing}
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"chunk_{run:%Y-%m-%d_%H}_m{m_from}-{m_to}.json.gz")
    with gzip.open(path, "wt", encoding="utf-8", compresslevel=9) as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Zapisano: {path} (członków: {len(members_out)}, puste pola: {missing})", flush=True)
    print(f"Czas: {time.time() - t0:.0f} s, pobrano {A.STATS['bytes'] / 1e6:.0f} MB w {A.STATS['requests']} zapytaniach, w tym nieudanych (ponowionych): {A.STATS['retries']}, z lustra Google: {A.STATS['google_ok']}", flush=True)


def main():
    if len(sys.argv) < 5 or sys.argv[1] != "extract":
        sys.exit(__doc__)
    run = parse_run(sys.argv[2])
    outdir = sys.argv[5] if len(sys.argv) > 5 else os.path.join(HERE, "hindcast_chunks")
    extras = os.environ.get("IFS_EXTRAS", "0").strip() not in ("0", "false", "")
    extract(run, int(sys.argv[3]), int(sys.argv[4]), outdir, extras)


if __name__ == "__main__":
    main()
