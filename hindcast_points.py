"""
Historyczna ekstrakcja GEFS dla stacji IMGW — surowy materiał do KALIBRACJI SWWF na obserwacjach.

Dla jednego przebiegu GEFS (30 członków) zapisuje, dla każdej stacji z `stations_imgw.csv`,
w każdym oknie 6 h (0-6, 6-12, ... 72-78 h) SUROWE pola, z których SWWF liczy swoje hazardy:
opad (APCP), T2m, porywy, wiatr 10 m (U, V) i wilgotność 2 m (na końcu i w połowie okna),
CPOFP, CFRZR, VIS, SNOD, CAPE. (Wiatr średni i wilgotność pozwalają policzyć standardowy
wind chill oraz temperaturę mokrego termometru jako lepszą decyzję deszcz/śnieg.)
Dzięki temu poziomy zagrożenia, progi, przelicznik śniegu i okno doby (06-06 UTC vs 00-24 UTC)
można zmieniać OFFLINE, bez ponownego pobierania — tylko raz pobieramy dane.

Użycie (zwykle przez workflow hindcast.yml):
    python hindcast_points.py extract "2021-01-03 00" 1 10      # przebieg, członkowie od-do (włącznie)
    python hindcast_points.py merge hindcast_chunks/ hindcast_v2/  # scala kawałki w jeden plik na przebieg

Wynik extract: {outdir}/chunk_{RRRR-MM-DD_GG}_m{od}-{do}.json.gz
Wynik merge:   hindcast_v2/{RRRR-MM-DD_GGz}.json.gz — struktura (v2: 13 okien do 78 h + wiatr i wilgotność; starsze pliki w hindcast/ mają 12 okien):
    {"run", "windows": [[0,6],...], "stations": [{code,name,lat,lon,grid_lat,grid_lon,flag}],
     "members": [1..30], "fields": {pole: opis},
     "data": {pole: [członek][stacja][okno] (lub null)}, "missing": {...}}
Jednostki: apcp mm (suma okna), t_end/t_mid °C, gust_* i u10/v10 m/s, rh_* %, cpofp_end % (-50 = brak),
cfrzr_end 0/1, vis_end m, snod_end m, cape_end J/kg.

Wymaga: pip install herbie-data (jak generate_swwf.py).
"""
import csv
import glob
import gzip
import json
import os
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
STATIONS_CSV = os.path.join(HERE, "stations_imgw.csv")
WINDOWS = [(s, s + 6) for s in range(0, 78, 6)]      # 13 okien 6 h = 78 h (okno 06-06 UTC doby +2 potrzebuje 72-78 h)
ESSENTIAL = ("apcp", "t_end")                         # bez nich członek się nie liczy
FIELDS = {
    "apcp": "opad w oknie [mm]",
    "t_end": "T2m na końcu okna [°C]",
    "t_mid": "T2m w połowie okna [°C]",
    "gust_end": "porywy na końcu okna [m/s]",
    "gust_mid": "porywy w połowie okna [m/s]",
    "cpofp_end": "CPOFP na końcu okna [%] (-50 = brak opadu w tej chwili)",
    "cfrzr_end": "CFRZR na końcu okna (0/1)",
    "vis_end": "widzialność na końcu okna [m]",
    "snod_end": "wysokość pokrywy śnieżnej (model) [m]",
    "cape_end": "CAPE na końcu okna [J/kg]",
    "u10_end": "składowa U wiatru 10 m na końcu okna [m/s]",
    "v10_end": "składowa V wiatru 10 m na końcu okna [m/s]",
    "u10_mid": "składowa U wiatru 10 m w połowie okna [m/s]",
    "v10_mid": "składowa V wiatru 10 m w połowie okna [m/s]",
    "rh_end": "wilgotność względna 2 m na końcu okna [%]",
    "rh_mid": "wilgotność względna 2 m w połowie okna [%]",
}


def load_stations():
    with open(STATIONS_CSV, encoding="utf-8") as f:
        return [dict(code=r["code"], name=r["name"], lat=float(r["lat"]), lon=float(r["lon"]),
                     flag=r.get("flag", "")) for r in csv.DictReader(f)]


def parse_run(text):
    return datetime.strptime(text.strip(), "%Y-%m-%d %H").replace(tzinfo=timezone.utc)


def retry(fn, attempts=3, base_sleep=2):
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:
            last = e
            if i < attempts - 1:
                time.sleep(base_sleep * (i + 1))
    raise last


def make_sampler(stations):
    """Zwraca funkcję: DataArray -> lista wartości w punktach stacji (najbliższy węzeł siatki)."""
    import xarray as xr
    lats = xr.DataArray([s["lat"] for s in stations], dims="s")
    lons = xr.DataArray([s["lon"] % 360 for s in stations], dims="s")

    def sample(da):
        da = da.squeeze(drop=True)
        pts = da.sel(latitude=lats, longitude=lons, method="nearest")
        vals = [float(v) for v in pts.values]
        grid = [(float(a), float(b)) for a, b in zip(pts["latitude"].values, pts["longitude"].values)]
        return vals, grid
    return sample


def extract(run, m_from, m_to, outdir):
    from herbie import Herbie
    stations = load_stations()
    sample = make_sampler(stations)
    stamp = run.strftime("%Y-%m-%d %H:%M")
    herbie_cache = {}

    def herbie(member, fxx):
        key = (member, fxx)
        if key not in herbie_cache:
            herbie_cache.clear()  # trzymamy tylko ostatnie dwa-trzy obiekty, nie całą historię
            herbie_cache[key] = Herbie(stamp, model="gefs", product="atmos.25", member=member,
                                       fxx=fxx, priority=["aws"], verbose=False)
        return herbie_cache[key]

    def get(member, fxx, search, attempts=3, base_sleep=2):
        H = herbie(member, fxx)

        def go():
            ds = H.xarray(search, remove_grib=True)
            if isinstance(ds, list):
                ds = ds[0]
            return ds[list(ds.data_vars)[0]]
        return retry(go, attempts, base_sleep)

    grid_info = None
    members_out, missing = [], {}
    data = {k: [] for k in FIELDS}
    apcp_windowed = True      # czy GEFS podaje okna "6-12 hour acc"; jeśli nie, przełączamy na sumy 0-end
    consecutive_fail = {}     # pole opcjonalne -> ile razy z rzędu go zabrakło (bezpiecznik)
    DISABLE_AFTER = 3         # po tylu porażkach z rzędu pole pomijamy do końca (nie tracimy czasu na ponowienia)

    for m in range(m_from, m_to + 1):
        per_field = {k: [[None] * len(WINDOWS) for _ in stations] for k in FIELDS}
        prev_cum = None   # skumulowany opad 0-start (gdy GEFS podaje sumy narastające zamiast okien)
        member_ok = True
        try:
            for w, (start, end) in enumerate(WINDOWS):
                def put(field, vals):
                    for s, v in enumerate(vals):
                        # NaN -> None
                        per_field[field][s][w] = None if v != v else round(v, 3)

                # --- opad: okno start-end; gdy go brak w pliku — różnica sum narastających 0-end ---
                vals = g = None
                if apcp_windowed:
                    try:
                        vals, g = sample(get(m, end, f":APCP:surface:{start}-{end} hour acc", attempts=2, base_sleep=1))
                    except Exception:
                        apcp_windowed = False
                        print("  uwaga: brak okien APCP 'start-end hour acc' — liczę z sum 0-end", flush=True)
                if vals is None:
                    cum_end, g = sample(get(m, end, f":APCP:surface:0-{end} hour acc"))
                    if start == 0:
                        vals = cum_end
                    else:
                        cum_start, _ = sample(get(m, start, f":APCP:surface:0-{start} hour acc"))
                        vals = [a - b for a, b in zip(cum_end, cum_start)]
                if grid_info is None:
                    grid_info = g
                put("apcp", vals)
                t_end, _ = sample(get(m, end, ":TMP:2 m above ground:"))
                put("t_end", [v - 273.15 for v in t_end])

                # --- pola opcjonalne (brak w starszych przebiegach nie przerywa członka) ---
                def optional(field, fxx, search, conv=lambda v: v):
                    if consecutive_fail.get(field, 0) >= DISABLE_AFTER:
                        missing[field] = missing.get(field, 0) + 1
                        return
                    try:
                        vals, _ = sample(get(m, fxx, search, attempts=2, base_sleep=1))
                        put(field, [conv(v) for v in vals])
                        consecutive_fail[field] = 0
                    except Exception:
                        consecutive_fail[field] = consecutive_fail.get(field, 0) + 1
                        missing[field] = missing.get(field, 0) + 1

                mid = start + 3
                optional("t_mid", mid, ":TMP:2 m above ground:", lambda v: v - 273.15)
                optional("gust_end", end, ":GUST:surface:")
                optional("gust_mid", mid, ":GUST:surface:")
                optional("cpofp_end", end, ":CPOFP:surface:")
                optional("cfrzr_end", end, ":CFRZR:surface:")
                optional("vis_end", end, ":VIS:surface:")
                optional("snod_end", end, ":SNOD:surface:")
                optional("cape_end", end, ":CAPE:surface:")
                optional("u10_end", end, ":UGRD:10 m above ground:")
                optional("v10_end", end, ":VGRD:10 m above ground:")
                optional("u10_mid", mid, ":UGRD:10 m above ground:")
                optional("v10_mid", mid, ":VGRD:10 m above ground:")
                optional("rh_end", end, ":RH:2 m above ground:")
                optional("rh_mid", mid, ":RH:2 m above ground:")
        except Exception as e:
            member_ok = False
            print(f"  człon {m:>2}: BŁĄD ({e})", flush=True)
        if member_ok:
            members_out.append(m)
            for k in FIELDS:
                data[k].append(per_field[k])
            print(f"  człon {m:>2}: ok", flush=True)

    if not members_out:
        sys.exit("Żaden człon się nie udał — nie zapisuję pliku.")
    for s, (glat, glon) in zip(stations, grid_info):
        s["grid_lat"] = round(glat, 3)
        s["grid_lon"] = round(glon - 360 if glon > 180 else glon, 3)
    doc = {
        "run": run.strftime("%Y-%m-%dT%H:00Z"),
        "windows": [list(w) for w in WINDOWS],
        "stations": stations,
        "members": members_out,
        "fields": FIELDS,
        "data": data,
        "missing": missing,
    }
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"chunk_{run:%Y-%m-%d_%H}_m{m_from}-{m_to}.json.gz")
    with gzip.open(path, "wt", encoding="utf-8", compresslevel=9) as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Zapisano: {path} (członków: {len(members_out)}, braki pól opcjonalnych: {missing})")


def merge(chunks_dir, out_dir):
    """Scala kawałki (różni członkowie tego samego przebiegu) w jeden plik na przebieg.

    Jeśli plik przebiegu już istnieje (np. ponowiono tylko nieudane kawałki), jego członkowie
    zostają zachowane, a nowe kawałki dopisują się lub nadpisują tych samych członków.
    """
    files = sorted(glob.glob(os.path.join(chunks_dir, "**", "chunk_*.json.gz"), recursive=True))
    if not files:
        sys.exit("Brak plików chunk_*.json.gz do scalenia.")
    by_run = {}
    for p in files:
        d = json.load(gzip.open(p, "rt", encoding="utf-8"))
        by_run.setdefault(d["run"], []).append(d)
    os.makedirs(out_dir, exist_ok=True)
    for run, docs in sorted(by_run.items()):
        stamp = datetime.strptime(run, "%Y-%m-%dT%H:00Z")
        path = os.path.join(out_dir, f"{stamp:%Y-%m-%d_%H}z.json.gz")
        if os.path.exists(path):   # istniejący plik = najstarsze źródło, nowe kawałki go nadpisują
            docs = [json.load(gzip.open(path, "rt", encoding="utf-8"))] + docs
        base = docs[-1]
        per_member = {}            # członek -> {pole: [stacja][okno]}
        for d in docs:
            for i, m in enumerate(d["members"]):
                per_member[m] = {k: d["data"][k][i] for k in d["fields"]}
        members = sorted(per_member)
        merged = {k: base[k] for k in ("run", "windows", "stations", "fields")}
        merged["members"] = members
        merged["data"] = {k: [per_member[m][k] for m in members] for k in base["fields"]}
        miss = {}
        for d in docs:
            for k, v in d["missing"].items():
                miss[k] = miss.get(k, 0) + v
        merged["missing"] = miss
        with gzip.open(path, "wt", encoding="utf-8", compresslevel=9) as f:
            json.dump(merged, f, ensure_ascii=False, separators=(",", ":"))
        print(f"{run}: członków {len(members)}/30 -> {path} ({os.path.getsize(path) / 1024:.0f} KB)")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("extract", "merge"):
        sys.exit(__doc__)
    if sys.argv[1] == "extract":
        if len(sys.argv) < 5:
            sys.exit('Użycie: python hindcast_points.py extract "RRRR-MM-DD GG" OD DO [KATALOG]')
        run = parse_run(sys.argv[2])
        outdir = sys.argv[5] if len(sys.argv) > 5 else os.path.join(HERE, "hindcast_chunks")
        extract(run, int(sys.argv[3]), int(sys.argv[4]), outdir)
    else:
        if len(sys.argv) < 4:
            sys.exit("Użycie: python hindcast_points.py merge KATALOG_KAWAŁKÓW KATALOG_WYJŚCIOWY")
        merge(sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    main()
