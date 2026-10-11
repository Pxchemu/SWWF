"""
Wybór przebiegów do hindcastu IFS ENS vs GEFS: dni ze zdarzeniami (śnieg, mróz, silny opad wg obserwacji IMGW)
i dni spokojne, z zim 2024/25 i 2025/26 (IFS ENS ma na AWS pełny zestaw zmiennych od 2024-11-15).

Dla każdego wybranego dnia D bierze przebiegi 00Z z D, D-1, D-2 (wyprzedzenie 1-3 doby), więc raport kalibracji
może liczyć k=0/1/2. Te same listy daje się podać zarówno hindcast.yml (GEFS), jak i hindcast-ifs.yml (IFS ENS).

Użycie:  python pick_hindcast_days.py [--per-batch 40] [--max-event 12] [--quiet 15] [--obs plik.csv.gz]
Wynik: lista przebiegów w paczkach, gotowa do wklejenia w pole "runs" workflow (po przecinku).
Nic nie zapisuje; wybór jest deterministyczny (ziarno 1).
"""
import argparse
import glob
import os
import random
import sys
from collections import defaultdict
from datetime import date, timedelta

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import calibrate_swwf as C

SEASONS = [(date(2024, 11, 17), date(2025, 3, 31)), (date(2025, 11, 1), date(2026, 3, 31))]
FIRST_RUN = date(2024, 11, 15)          # od tego dnia IFS ENS ma na AWS komplet zmiennych


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--obs", default=None)
    ap.add_argument("--per-batch", type=int, default=40, help="ile przebiegów w jednej paczce (jedno uruchomienie workflow)")
    ap.add_argument("--max-event", type=int, default=12, help="maks. dni na typ zdarzenia (śnieg / mróz / opad)")
    ap.add_argument("--quiet", type=int, default=15, help="ile dni spokojnych dołożyć")
    a = ap.parse_args()
    path = a.obs
    if path is None:
        found = sorted(glob.glob(os.path.join(HERE, "obs", "imgw_dobowe_*.csv.gz")), key=os.path.getmtime)
        if not found:
            sys.exit("Brak obserwacji: podaj --obs albo uruchom fetch_obs_imgw.py")
        path = found[-1]
    obs = C.load_obs(path)
    cnt = defaultdict(lambda: defaultdict(int))
    for (code, d), r in obs.items():
        if r["ROOP"] == "S" and r["SMDB"] == r["SMDB"] and r["SMDB"] >= 3:
            cnt[d]["snow"] += 1
        if r["TMIN"] == r["TMIN"] and r["TMIN"] <= -10:
            cnt[d]["cold10"] += 1
        if r["TMIN"] == r["TMIN"] and r["TMIN"] <= -15:
            cnt[d]["cold15"] += 1
        if r["SMDB"] == r["SMDB"] and r["SMDB"] >= 10:
            cnt[d]["rain10"] += 1
        cnt[d]["n"] += 1
    days = [d for d in sorted(cnt) if any(s <= d <= e for s, e in SEASONS) and cnt[d]["n"] >= 40]
    if not days:
        sys.exit("Obserwacje nie pokrywają zim 2024/25 i 2025/26.")
    chosen, reasons = {}, defaultdict(list)

    def top(key, thr, n):
        cand = sorted((d for d in days if cnt[d][key] >= thr), key=lambda d: -cnt[d][key])
        picked = []
        for d in cand:                                     # nie bierzemy sąsiednich dni z tego samego epizodu
            if all(abs((d - p).days) > 1 for p in picked):
                picked.append(d)
            if len(picked) >= n:
                break
        return picked

    for key, thr, label in (("snow", 5, "śnieg>=3 mm"), ("cold10", 5, "mróz<=-10"), ("cold15", 3, "mróz<=-15"), ("rain10", 5, "opad>=10 mm")):
        for d in top(key, thr, a.max_event):
            chosen[d] = True
            reasons[d].append(f"{label} ({cnt[d][key]} st.)")
    rng = random.Random(1)
    quiet = [d for d in days if cnt[d]["snow"] <= 1 and cnt[d]["cold10"] <= 1 and cnt[d]["rain10"] <= 1 and d not in chosen]
    for d in rng.sample(quiet, min(a.quiet, len(quiet))):
        chosen[d] = True
        reasons[d].append("spokojny")
    runs = set()
    for d in chosen:
        for k in (0, 1, 2):
            r = d - timedelta(days=k)
            if r >= FIRST_RUN:
                runs.add(r)
    runs = sorted(runs)
    print(f"Dni docelowe: {len(chosen)} (zdarzenia {sum(1 for d in chosen if reasons[d][0] != 'spokojny')}, spokojne "
          f"{sum(1 for d in chosen if reasons[d][0] == 'spokojny')}); przebiegów 00Z: {len(runs)}\n")
    for d in sorted(chosen):
        print(f"  {d}: {', '.join(reasons[d])}")
    print()
    for i in range(0, len(runs), a.per_batch):
        batch = runs[i:i + a.per_batch]
        print(f"=== PACZKA {i // a.per_batch + 1} ({len(batch)} przebiegów) ===")
        print(",".join(f"{r:%Y-%m-%d} 00" for r in batch))
        print()


if __name__ == "__main__":
    main()
