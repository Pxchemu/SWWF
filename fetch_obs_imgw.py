"""
Pobiera DOBOWE dane synoptyczne IMGW (obserwacje stacji) dla wybranych stacji i dni i zapisuje
je do repo — żeby można było porównać prognozę SWWF z tym, co faktycznie wystąpiło
(opad dobowy, wysokość pokrywy śnieżnej, temperatury).

Użycie:
    python fetch_obs_imgw.py 2025-12-28 2025-12-31 WARSZAWA

Argumenty: data początkowa, data końcowa (obie włącznie, ten sam rok kalendarzowy), fragment nazwy
stacji (wielkość liter bez znaczenia; można podać kilka po przecinku, np. "WARSZAWA,LEGIONOWO").

Wynik (folder obs/):
    obs/imgw_dobowe_{od}_{do}.csv     — surowe wiersze stacji z zakresu dat (kolumna 1 = plik źródłowy)
    obs/imgw_dobowe_format.txt        — opis kolumn z IMGW (jeśli udało się go znaleźć)
    obs/imgw_dobowe_index_{rok}.txt   — lista plików znaleziona w katalogu roku (do diagnozy)

Struktura katalogów IMGW bywa zmieniana, więc skrypt NIE zakłada nazw plików — czyta listing
katalogu roku, pobiera wszystkie archiwa zip z tego roku i szuka w nich wierszy stacji.
Dane IMGW są jawne (https://danepubliczne.imgw.pl), bez logowania.
"""
import csv
import io
import os
import re
import sys
import zipfile
from datetime import date

import requests

BASE = "https://danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/dane_meteorologiczne/dobowe/synop/"
HEADERS = {"User-Agent": "SWWF-verification/1.0 (research; GitHub Actions)"}
MAX_ZIPS = 300


def http_get(url, binary=False):
    r = requests.get(url, headers=HEADERS, timeout=120, allow_redirects=True)
    r.raise_for_status()
    return r.content if binary else r.content.decode("cp1250", errors="replace")


def list_links(index_html):
    """Wszystkie odnośniki z listingu katalogu (bez sortowania i nadrzędnych)."""
    links = re.findall(r'href="([^"?#][^"]*)"', index_html, flags=re.IGNORECASE)
    return [l for l in links if not l.startswith(("/", "http", "..", "?"))]


def parse_date(text):
    y, m, d = (int(x) for x in text.split("-"))
    return date(y, m, d)


def rows_from_zip(content, name_filters, d0, d1):
    """Wiersze z plików csv w archiwum, dla stacji pasujących do filtrów i dat z zakresu."""
    out = []
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        for member in zf.namelist():
            if not member.lower().endswith(".csv"):
                continue
            text = zf.read(member).decode("cp1250", errors="replace")
            for row in csv.reader(io.StringIO(text)):
                if len(row) < 6:
                    continue
                station = row[1].strip().strip('"').upper()
                if not any(f in station for f in name_filters):
                    continue
                try:
                    day = date(int(row[2]), int(row[3]), int(row[4]))
                except ValueError:
                    continue
                if d0 <= day <= d1:
                    out.append([member] + [c.strip().strip('"') for c in row])
    return out


def main():
    if len(sys.argv) < 4:
        sys.exit("Użycie: python fetch_obs_imgw.py RRRR-MM-DD RRRR-MM-DD FRAGMENT_NAZWY[,FRAGMENT2]")
    d0, d1 = parse_date(sys.argv[1]), parse_date(sys.argv[2])
    if d0.year != d1.year or d1 < d0:
        sys.exit("Zakres musi mieścić się w jednym roku kalendarzowym (od <= do).")
    name_filters = [f.strip().upper() for f in sys.argv[3].split(",") if f.strip()]

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "obs")
    os.makedirs(out_dir, exist_ok=True)

    year_url = f"{BASE}{d0.year}/"
    print(f"Listing katalogu: {year_url}")
    index_html = http_get(year_url)
    links = list_links(index_html)
    zips = [l for l in links if l.lower().endswith(".zip")]
    with open(os.path.join(out_dir, f"imgw_dobowe_index_{d0.year}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(links) + "\n")
    print(f"Znaleziono odnośników: {len(links)}, w tym archiwów zip: {len(zips)}")
    print("Przykłady:", links[:12])
    if not zips:
        sys.exit("Brak archiwów zip w katalogu roku — zobacz obs/imgw_dobowe_index_*.txt (struktura mogła się zmienić).")

    # opis kolumn: plik z "format" w nazwie, w katalogu roku albo nadrzędnym (synop/)
    format_text = None
    for url, candidates in ((year_url, links), (BASE, list_links(http_get(BASE)))):
        for l in candidates:
            if "format" in l.lower() and l.lower().endswith(".txt"):
                format_text = http_get(url + l)
                print(f"Opis kolumn: {url + l}")
                break
        if format_text:
            break
    if format_text:
        with open(os.path.join(out_dir, "imgw_dobowe_format.txt"), "w", encoding="utf-8") as f:
            f.write(format_text)
        print("----- opis kolumn -----")
        print(format_text)
        print("-----------------------")
    else:
        print("Nie znaleziono pliku z opisem kolumn (nazwa zawierająca 'format').")

    rows = []
    for n, z in enumerate(zips[:MAX_ZIPS]):
        try:
            rows += rows_from_zip(http_get(year_url + z, binary=True), name_filters, d0, d1)
        except Exception as e:
            print(f"  pominięto {z}: {e}")
    print(f"\nZnaleziono wierszy dla {name_filters} w {d0}..{d1}: {len(rows)}")
    if not rows:
        sys.exit("Brak wierszy — sprawdź filtr nazwy stacji i zakres dat.")

    rows.sort(key=lambda r: (r[2], int(r[3]), int(r[4]), int(r[5])))
    out_path = os.path.join(out_dir, f"imgw_dobowe_{d0}_{d1}.csv")
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)
    for r in rows:
        print(",".join(r))
    print(f"\nZapisano: {out_path}")


if __name__ == "__main__":
    main()
