"""
Backtest SWWF — przelicza prognozę dla wskazanego, HISTORYCZNEGO przebiegu GEFS
(zamiast najnowszego), bez dotykania produkcyjnego swwf.json ani archive/.

Użycie:
    python backtest_swwf.py "2025-12-30 00:00"     (czas UTC; przebiegi GEFS: 00, 06, 12, 18)

Wynik trafia do osobnego folderu:
    backtest/2025-12-30_00z/swwf.json
    backtest/2025-12-30_00z/archive/2025-12-30_00z.json

Działa przez wywołanie PRODUKCYJNEGO generate_swwf.py (ta sama klasyfikacja, te same progi),
z podmienioną jedynie funkcją wyboru przebiegu i zmienionym folderem zapisu — dzięki temu
backtest sprawdza dokładnie ten kod, który działa na żywo, a nie jego kopię.
"""
import os
import sys
from datetime import datetime, timezone


def parse_run_time(text):
    try:
        dt = datetime.strptime(text.strip(), "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
    except ValueError:
        sys.exit(f'Zły format daty: "{text}". Oczekiwany: "RRRR-MM-DD GG:00", np. "2025-12-30 00:00" (UTC).')
    if dt.minute != 0 or dt.hour not in (0, 6, 12, 18):
        sys.exit("GEFS ma przebiegi tylko o 00:00, 06:00, 12:00 i 18:00 UTC.")
    return dt


def ensure_run_available(gen, run_time):
    """Szybka kontrola przed 30-minutowym przeliczeniem: czy ten przebieg w ogóle jest na AWS
    (sprawdzamy członków 1 i 30 na najdalszej potrzebnej godzinie — tak samo jak find_latest_run)."""
    max_fxx = gen.DAY_WINDOWS[-1]["windows"][-1][1]
    stamp = run_time.strftime("%Y-%m-%d %H:%M")
    for member in (1, 30):
        try:
            h = gen.Herbie(stamp, model="gefs", product="atmos.25", member=member, fxx=max_fxx,
                           priority=["aws"], verbose=False)
            ok = h.grib is not None
        except Exception as e:
            sys.exit(f"Przebieg {stamp} UTC niedostępny na AWS (członek {member}, fxx={max_fxx}): {e}")
        if not ok:
            sys.exit(f"Przebieg {stamp} UTC niedostępny na AWS (członek {member}, fxx={max_fxx}) — "
                     "archiwum GEFS może nie sięgać tak daleko wstecz albo przebieg ma braki.")
    print(f"Przebieg {stamp} UTC dostępny na AWS (członkowie 1 i 30, fxx={max_fxx}).")


def main():
    if len(sys.argv) != 2:
        sys.exit('Użycie: python backtest_swwf.py "RRRR-MM-DD GG:00"   (czas UTC)')
    run_time = parse_run_time(sys.argv[1])

    repo_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, repo_root)
    import generate_swwf as gen

    ensure_run_available(gen, run_time)

    # main() w generate_swwf.py woła find_latest_run() (globalna nazwa modułu) — podmieniamy ją
    gen.find_latest_run = lambda: run_time

    # generate_swwf.py zapisuje do ścieżek względnych (swwf.json, archive/) — wchodząc do
    # osobnego folderu nie nadpisujemy produkcyjnej prognozy
    out_dir = os.path.join(repo_root, "backtest", run_time.strftime("%Y-%m-%d_%Hz"))
    os.makedirs(out_dir, exist_ok=True)
    os.chdir(out_dir)
    print(f"Backtest: przebieg {run_time.isoformat()}, wynik w {out_dir}")
    gen.main()


if __name__ == "__main__":
    main()
