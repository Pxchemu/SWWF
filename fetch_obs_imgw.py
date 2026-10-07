"""
Pobiera DOBOWE dane synoptyczne IMGW (obserwacje stacji) dla wielu lat i stacji naraz i zapisuje
je do repo — do weryfikacji i kalibracji SWWF na obserwacjach (opad dobowy, rodzaj opadu,
pokrywa śnieżna, godziny opadu śniegu, temperatury, godziny silnego wiatru).

Użycie:
    python fetch_obs_imgw.py 2020-11-01 2026-03-31 ALL 11,12,1,2,3
    python fetch_obs_imgw.py 2025-12-28 2025-12-31 WARSZAWA

Argumenty:
    1. data początkowa RRRR-MM-DD, 2. data końcowa (włącznie) — zakres MOŻE obejmować kilka lat,
    3. stacje: ALL (wszystkie dostępne) albo fragmenty nazw po przecinku (wielkość liter bez
       znaczenia), np. "WARSZAWA,KRAKÓW",
    4. (opcjonalnie) miesiące po przecinku, np. 11,12,1,2,3 = tylko sezon zimowy.

Wynik (folder obs/):
    obs/imgw_dobowe_{od}_{do}[_mc-...].csv.gz   — surowe wiersze stacji (kolumna 1 = plik źródłowy)
    obs/imgw_stacje_{od}_{do}.txt               — lista stacji: kod, nazwa, liczba dni, pierwszy/ostatni dzień
    obs/imgw_dobowe_format_{rok}.txt            — opis kolumn z IMGW danego roku (jeśli znaleziony; format bywał zmieniany)
    obs/imgw_kolumny_{od}_{do}.txt              — ile kolumn mają wiersze w poszczególnych latach (kontrola spójności)

Struktura katalogów IMGW bywa zmieniana, więc skrypt NIE zakłada nazw plików: czyta listing
katalogu każdego roku, pobiera archiwa zip i szuka w nich wierszy (pliki s_d_*.csv; pliki s_d_t_*
mają inny układ kolumn i są pomijane). Lata bez katalogu są pomijane z komunikatem.
Dane IMGW są jawne (https://danepubliczne.imgw.pl), bez logowania.
"""
import csv
import gzip
import io
import os
import re
import sys
import time
import zipfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import requests

BASE = "https://danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/dane_meteorologiczne/dobowe/synop/"
HEADERS = {"User-Agent": "SWWF-verification/1.0 (research; GitHub Actions)"}
MAX_ZIPS_PER_YEAR = 400
WORKERS = 6


def http_get(url, binary=False, attempts=3):
    """Pobiera URL; 404 -> None; inne błędy ponawia."""
    last = None
    for i in range(attempts):
        try:
            r = requests.get(url, headers=HEADERS, timeout=120, allow_redirects=True)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.content if binary else r.content.decode("cp1250", errors="replace")
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"{url}: {last}")


def list_links(index_html):
    """Wszystkie odnośniki z listingu katalogu (bez sortowania i nadrzędnych)."""
    links = re.findall(r'href="([^"?#][^"]*)"', index_html, flags=re.IGNORECASE)
    return [l for l in links if not l.startswith(("/", "http", "..", "?"))]


def parse_date(text):
    y, m, d = (int(x) for x in text.split("-"))
    return date(y, m, d)


def is_data_member(name):
    base = os.path.basename(name).lower()
    return base.endswith(".csv") and base.startswith("s_d_") and not base.startswith("s_d_t_")


def rows_from_zip(content, name_filters, d0, d1, months):
    """Wiersze z plików s_d_*.csv w archiwum: pasujące stacje, daty z zakresu, miesiące.

    Zwraca (wiersze, zbiór pominiętych plików o innym układzie).
    """
    out = []
    skipped = set()
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        for member in zf.namelist():
            if not member.lower().endswith(".csv"):
                continue
            if not is_data_member(member):
                skipped.add(member)
                continue
            text = zf.read(member).decode("cp1250", errors="replace")
            for row in csv.reader(io.StringIO(text)):
                if len(row) < 6:
                    continue
                station = row[1].strip().strip('"').upper()
                if name_filters and not any(f in station for f in name_filters):
                    continue
                try:
                    day = date(int(row[2]), int(row[3]), int(row[4]))
                except ValueError:
                    continue
                if not (d0 <= day <= d1):
                    continue
                if months and day.month not in months:
                    continue
                out.append([member] + [c.strip().strip('"') for c in row])
    return out, skipped


def fetch_year(year, name_filters, d0, d1, months, out_dir):
    year_url = f"{BASE}{year}/"
    html = http_get(year_url)
    if html is None:
        print(f"[{year}] brak katalogu roku — pomijam", flush=True)
        return [], {}
    links = list_links(html)
    zips = [l for l in links if l.lower().endswith(".zip")]
    print(f"[{year}] archiwów zip: {len(zips)}", flush=True)
    if not zips:
        print(f"[{year}] brak archiwów zip (przykładowe odnośniki: {links[:8]})", flush=True)
        return [], {}

    for l in links:  # opis kolumn danego roku (jeśli jest) — format bywał zmieniany
        if "format" in l.lower() and l.lower().endswith(".txt"):
            txt = http_get(year_url + l)
            if txt:
                with open(os.path.join(out_dir, f"imgw_dobowe_format_{year}.txt"), "w", encoding="utf-8") as f:
                    f.write(txt)
            break

    rows, skipped_all = [], set()

    def one(z):
        try:
            content = http_get(year_url + z, binary=True)
            if content is None:
                return [], set()
            return rows_from_zip(content, name_filters, d0, d1, months)
        except Exception as e:
            print(f"  [{year}] pominięto {z}: {e}", flush=True)
            return [], set()

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for r, sk in ex.map(one, zips[:MAX_ZIPS_PER_YEAR]):
            rows += r
            skipped_all |= sk
    ncols = Counter(len(r) for r in rows)
    print(f"[{year}] wierszy: {len(rows)}; pominięte pliki (inny układ): {sorted(skipped_all)[:4]}"
          f"{'...' if len(skipped_all) > 4 else ''}", flush=True)
    return rows, dict(ncols)


def main():
    if len(sys.argv) < 4:
        sys.exit("Użycie: python fetch_obs_imgw.py RRRR-MM-DD RRRR-MM-DD ALL|FRAGMENT[,FRAGMENT2] [MIESIĄCE]")
    d0, d1 = parse_date(sys.argv[1]), parse_date(sys.argv[2])
    if d1 < d0:
        sys.exit("Data końcowa wcześniejsza niż początkowa.")
    arg = sys.argv[3].strip()
    name_filters = None if arg.upper() == "ALL" else [f.strip().upper() for f in arg.split(",") if f.strip()]
    months = None
    if len(sys.argv) > 4 and sys.argv[4].strip():
        months = {int(m) for m in sys.argv[4].split(",") if m.strip()}
        if not months <= set(range(1, 13)):
            sys.exit("Miesiące muszą być liczbami 1-12.")

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "obs")
    os.makedirs(out_dir, exist_ok=True)

    all_rows, cols_by_year = [], {}
    for year in range(d0.year, d1.year + 1):
        rows, ncols = fetch_year(year, name_filters, d0, d1, months, out_dir)
        all_rows += rows
        cols_by_year[year] = ncols
    print(f"\nŁącznie wierszy: {len(all_rows)}")
    if not all_rows:
        sys.exit("Brak wierszy — sprawdź filtr stacji, zakres dat i miesiące.")

    all_rows.sort(key=lambda r: (int(r[3]), int(r[4]), int(r[5]), r[2]))
    tag = f"{d0}_{d1}" + (f"_mc-{'-'.join(str(m) for m in sorted(months))}" if months else "")
    out_path = os.path.join(out_dir, f"imgw_dobowe_{tag}.csv.gz")
    with gzip.open(out_path, "wt", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(all_rows)
    print(f"Zapisano: {out_path} ({os.path.getsize(out_path) / 1024:.0f} KB)")

    # lista stacji (kod, nazwa, liczba dni, zakres) — do wyboru stacji i dopasowania do punktów ICON-EU
    st = defaultdict(list)
    for r in all_rows:
        st[(r[1], r[2])].append(date(int(r[3]), int(r[4]), int(r[5])))
    with open(os.path.join(out_dir, f"imgw_stacje_{d0}_{d1}.txt"), "w", encoding="utf-8") as f:
        f.write("kod\tnazwa\tdni\tpierwszy\tostatni\n")
        for (code, name), days in sorted(st.items(), key=lambda kv: kv[0][1]):
            f.write(f"{code}\t{name}\t{len(days)}\t{min(days)}\t{max(days)}\n")
    with open(os.path.join(out_dir, f"imgw_kolumny_{d0}_{d1}.txt"), "w", encoding="utf-8") as f:
        f.write("rok\tliczba kolumn (z kolumną pliku źródłowego) -> liczba wierszy\n")
        for y, nc in sorted(cols_by_year.items()):
            f.write(f"{y}\t{nc}\n")
    print(f"Stacji: {len(st)}")
    for y, nc in sorted(cols_by_year.items()):
        print(f"  {y}: kolumny -> wiersze {nc}")


if __name__ == "__main__":
    main()
