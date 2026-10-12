"""
IFS ENS (ECMWF, otwarte dane) dla produkcji SWWF — pola na CAŁYM obszarze SWWF (nie w punktach stacji).

Używane przez generate_swwf.py (SWWF_IFS = shadow / on). Pobiera dla jednego przebiegu:
  - 2t (T2m, K) co 3 h: kroki 3, 6, ..., 72  (koniec i połowa okien 6 h)
  - tp (opad skumulowany od startu, m) co 6 h: kroki 6, 12, ..., 72
dla wszystkich 51 członków (kontrolny + 50 zaburzonych), przycięte do tego samego prostokąta co GEFS.

Pliki ECMWF są GLOBALNE i nie da się pobrać fragmentu — pobieramy całe wiadomości GRIB pojedynczymi
zapytaniami HTTP Range według indeksu (36 wiadomości na członka, ok. 1840 na przebieg, 1,5-2,5 GB),
z przełączaniem AWS <-> lustro Google i ponawianiem (logika w archive_ecmwf_ens.http_get).
Dekodowanie: eccodes; z każdej wiadomości zostaje tylko wycinek obszaru SWWF (float32).

Licencja danych: CC-BY-4.0 — przy publicznym użyciu podać ECMWF jako źródło.

Interfejs:
    data = load_ifs(run_utc, region=(lat_min, lat_max, lon_min360, lon_max360), wait_minutes=45)
    -> None (brak/niekompletne dane) albo słownik:
       {"lat": ndarray malejące, "lon": ndarray rosnące (0-360), "members": {nr: {"t": {krok: °C 2D},
        "tp": {krok: mm skumulowane 2D}}}, "stats": {...}}
"""
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import archive_ecmwf_ens as A                      # http_get, file_url, index_url, BASES, STATS

STEPS_T = list(range(3, 73, 3))                    # 24 kroki: koniec i połowa okien 6 h
STEPS_TP = list(range(6, 73, 6))                   # 12 kroków: granice okien 6 h
LAST_STEP = STEPS_T[-1]
WORKERS = int(os.environ.get("IFS_WORKERS", "8"))
MIN_COMPLETE_MEMBERS = int(os.environ.get("IFS_MIN_MEMBERS", "25"))    # poniżej — IFS nie jest używany
RETRY_ROUNDS = 3


def wait_for_base(run, wait_minutes, log=print):
    """Pierwsze źródło mające indeks ostatniego potrzebnego kroku (72 h); czeka do wait_minutes."""
    deadline = time.time() + wait_minutes * 60
    first = True
    while True:
        for base in A.BASES:
            try:
                st, raw = A.http_get(A.index_url(base, run, LAST_STEP), attempts=2, timeout=30)
            except Exception:
                st, raw = None, None
            if raw is not None:
                return base
        if time.time() >= deadline:
            return None
        if first:
            log(f"IFS: przebieg {run:%Y-%m-%d %Hz} jeszcze niedostępny — czekam (do {wait_minutes} min)...")
            first = False
        time.sleep(120)


def read_index(base, run, step):
    """[(param, członek, offset, długość)] dla kroku; członek 0 = kontrolny (type cf). None gdy brak indeksu."""
    import json
    st, raw = A.http_get(A.index_url(base, run, step), attempts=8)
    if raw is None:
        return None
    want = {"2t"} | ({"tp"} if step in STEPS_TP else set())
    out = []
    for line in raw.decode("utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        if d.get("levtype") != "sfc" or d.get("param") not in want:
            continue
        if d.get("type") == "cf":
            member = 0
        elif d.get("type") == "pf":
            member = int(d.get("number"))
        else:
            continue
        out.append((d["param"], member, int(d["_offset"]), int(d["_length"])))
    return out


def decode_region(raw, region):
    """Wiadomość GRIB -> (lat malejące, lon rosnące 0-360, pole float32 (lat, lon) z NaN za brak danych),
    przycięte do region = (lat_min, lat_max, lon_min360, lon_max360) włącznie z granicami."""
    import eccodes
    lat_min, lat_max, lon_min, lon_max = region
    gid = eccodes.codes_new_from_message(raw)
    try:
        ni = int(eccodes.codes_get(gid, "Ni"))
        nj = int(eccodes.codes_get(gid, "Nj"))
        la1 = float(eccodes.codes_get(gid, "latitudeOfFirstGridPointInDegrees"))
        la2 = float(eccodes.codes_get(gid, "latitudeOfLastGridPointInDegrees"))
        lo1 = float(eccodes.codes_get(gid, "longitudeOfFirstGridPointInDegrees"))
        lo2 = float(eccodes.codes_get(gid, "longitudeOfLastGridPointInDegrees"))
        if int(eccodes.codes_get(gid, "jPointsAreConsecutive")) != 0:
            raise ValueError("nieobsługiwany układ siatki (jPointsAreConsecutive=1)")
        try:
            missing = float(eccodes.codes_get(gid, "missingValue"))
        except Exception:
            missing = 9999.0
        values = eccodes.codes_get_values(gid)
    finally:
        eccodes.codes_release(gid)
    if values.size != ni * nj:
        raise ValueError(f"liczba wartości {values.size} != {ni}x{nj}")
    lats = np.linspace(la1, la2, nj)                 # kolejność skanowania (zwykle od północy)
    lons = np.linspace(lo1, lo2, ni) % 360.0
    field = values.reshape(nj, ni).astype(np.float32)
    field[(np.abs(field - missing) < 1e-6) | ~np.isfinite(field) | (np.abs(field) > 1e8)] = np.nan
    if lats[0] < lats[-1]:                           # ujednolicenie: lat malejące
        lats, field = lats[::-1], field[::-1]
    lon_order = np.argsort(lons)
    lons, field = lons[lon_order], field[:, lon_order]
    eps = 1e-6
    li = np.where((lats >= lat_min - eps) & (lats <= lat_max + eps))[0]
    lj = np.where((lons >= lon_min - eps) & (lons <= lon_max + eps))[0]
    if li.size == 0 or lj.size == 0:
        raise ValueError("wycinek obszaru pusty")
    return lats[li], lons[lj], np.ascontiguousarray(field[np.ix_(li, lj)])


def fetch_field(base, run, step, offset, length, region):
    """(lat, lon, pole, None) albo (None, None, None, powód)."""
    try:
        st, raw = A.http_get(A.file_url(base, run, step),
                             headers={"Range": f"bytes={offset}-{offset + length - 1}"}, attempts=10)
    except Exception as e:
        return None, None, None, f"sieć: {str(e)[-100:]}"
    if raw is None or len(raw) != length:
        return None, None, None, f"HTTP {st} / długość"
    if raw[:4] != b"GRIB" or raw[-4:] != b"7777":
        return None, None, None, "GRIB: zły początek/koniec wiadomości"
    try:
        lat, lon, field = decode_region(raw, region)
    except Exception as e:
        return None, None, None, f"GRIB: {type(e).__name__}: {str(e)[:80]}"
    return lat, lon, field, None


def load_ifs(run, region, wait_minutes=45, log=print):
    t0 = time.time()
    b0, r0, g0 = A.STATS["bytes"], A.STATS["requests"], A.STATS["google_ok"]
    base = wait_for_base(run, wait_minutes, log)
    if base is None:
        log(f"IFS: brak przebiegu {run:%Y-%m-%d %Hz} po {wait_minutes} min — pomijam IFS.")
        return None
    t_avail = time.time() - t0

    steps = sorted(set(STEPS_T) | set(STEPS_TP))
    index = {}
    with ThreadPoolExecutor(max_workers=min(WORKERS, 8)) as ex:
        futs = {ex.submit(read_index, base, run, s): s for s in steps}
        for f in as_completed(futs):
            try:
                index[futs[f]] = f.result()
            except Exception as e:
                index[futs[f]] = None
                log(f"IFS: indeks kroku {futs[f]} h: {str(e)[-100:]}")
    if any(index.get(s) is None for s in steps):
        log("IFS: brak indeksu dla części kroków — pomijam IFS.")
        return None

    todo = [(p, m, s, off, ln) for s in steps for (p, m, off, ln) in index[s]]
    total = len(todo)
    store = {}                                        # (param, członek, krok) -> pole
    grid = {}
    bad = {}

    def run_pass(items):
        failed = []
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futs = {ex.submit(fetch_field, base, run, s, off, ln, region): (p, m, s, off, ln)
                    for (p, m, s, off, ln) in items}
            for f in as_completed(futs):
                p, m, s, off, ln = futs[f]
                lat, lon, field, why = f.result()
                if field is None:
                    bad[(p, m, s)] = why
                    failed.append((p, m, s, off, ln))
                    continue
                if not grid:
                    grid["lat"], grid["lon"] = lat, lon
                if lat.shape != grid["lat"].shape or lon.shape != grid["lon"].shape or \
                        not np.allclose(lat, grid["lat"], atol=1e-4) or not np.allclose(lon, grid["lon"], atol=1e-4):
                    bad[(p, m, s)] = "siatka różni się od pierwszej wiadomości"
                    failed.append((p, m, s, off, ln))
                    continue
                store[(p, m, s)] = field
        return failed

    pending = todo
    for rnd in range(1 + RETRY_ROUNDS):
        pending = run_pass(pending)
        if not pending:
            break
        log(f"IFS: runda {rnd + 1}: {len(pending)} z {total} wiadomości nieudanych"
            f"{' — ponawiam' if rnd < RETRY_ROUNDS else ''}")
        if rnd < RETRY_ROUNDS:
            time.sleep(15)

    members = {}
    all_members = sorted({m for (_, m, _, _, _) in todo})
    for m in all_members:
        t = {s: store[("2t", m, s)] for s in STEPS_T if ("2t", m, s) in store}
        tp = {s: store[("tp", m, s)] for s in STEPS_TP if ("tp", m, s) in store}
        if len(t) == len(STEPS_T) and len(tp) == len(STEPS_TP):
            members[m] = {"t": {s: (a - 273.15).astype(np.float32) for s, a in t.items()},
                          "tp": {s: (a * 1000.0).astype(np.float32) for s, a in tp.items()}}
    stats = {"base": base.split("/")[2], "run": run.strftime("%Y-%m-%d %H"),
             "messages_total": total, "messages_failed": len(pending),
             "members_total": len(all_members), "members_complete": len(members),
             "seconds_wait": round(t_avail, 1), "seconds_total": round(time.time() - t0, 1),
             "mb": round((A.STATS["bytes"] - b0) / 1e6, 1), "requests": A.STATS["requests"] - r0,
             "google_ok": A.STATS["google_ok"] - g0}
    log("IFS: " + ", ".join(f"{k}={v}" for k, v in stats.items()))
    if bad and pending:
        why = {}
        for k in pending:
            why.setdefault(bad.get(k[:3], "?"), 0)
            why[bad.get(k[:3], "?")] += 1
        log("IFS: powody niepowodzeń: " + "; ".join(f"{w} ×{n}" for w, n in why.items()))
    if len(members) < MIN_COMPLETE_MEMBERS:
        log(f"IFS: kompletnych członków {len(members)} < {MIN_COMPLETE_MEMBERS} — pomijam IFS.")
        return None
    return {"lat": grid["lat"], "lon": grid["lon"], "members": members, "stats": stats}
