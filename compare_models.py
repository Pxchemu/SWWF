#!/usr/bin/env python3
"""
Porównanie modeli PARAMI na tych samych stacjodniach (CRPS, Brier z sekcji 8 raportu kalibracji).

Wejście: pliki .npz z calibrate_swwf.py --scores-out (po jednym na model/zespół), np.
    reports/scores_hindcast_v2_gefs_wspolne.npz        (GEFS)
    reports/scores_hindcast_ifs_ifs_wspolne.npz        (IFS ENS)
    reports/scores_hindcast_v2_pool_5_3.npz            (zespół połączony 5:3)
    reports/scores_hindcast_v2_pool_1_1.npz            (zespół połączony 1:1)
Dla każdej oceny bierze stacjodni wspólne dla wszystkich plików i liczy różnicę średnich A - B (ujemna = A lepszy)
z 95% przedziałem ufności z bootstrapu po DNIACH (przebiegach), bo stacje tego samego dnia są ze sobą skorelowane.
Wynik: tabela w stdout i w pliku .md.

Użycie:
    python compare_models.py --files a.npz b.npz c.npz d.npz --labels GEFS IFS pool_5_3 pool_1_1 --out reports/porownanie_modeli.md
Pary: każdy zespół/model od 3. wzwyż vs model 1 i 2, oraz model 2 vs 1.
"""
import argparse
import os
import sys

import numpy as np


def load(path):
    z = np.load(path, allow_pickle=False)
    out = {}
    for k in z.files:
        if k.endswith("__keys"):
            n = k[:-6]
            out[n] = (z[k].astype(str), z[n + "__vals"].astype(np.float64))
    return out


def boot_ci(day_sum, day_cnt, nboot=4000, seed=1):
    rng = np.random.default_rng(seed)
    nd = len(day_sum)
    idx = rng.integers(0, nd, size=(nboot, nd))
    m = day_sum[idx].sum(axis=1) / np.maximum(day_cnt[idx].sum(axis=1), 1)
    return np.percentile(m, [2.5, 97.5])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--labels", nargs="+", default=None)
    ap.add_argument("--out", default="reports/porownanie_modeli.md")
    a = ap.parse_args()
    labels = a.labels or [os.path.basename(f).replace("scores_", "").replace(".npz", "") for f in a.files]
    if len(labels) != len(a.files):
        sys.exit("Liczba --labels musi równać się liczbie --files")
    data = [load(f) for f in a.files]
    names = [n for n in data[0] if all(n in d for d in data[1:])]
    if not names:
        sys.exit("Brak wspólnych ocen w plikach")
    n = len(data)
    pairs = [(j, i) for j in range(2, n) for i in (0, 1)] + ([(1, 0)] if n >= 2 else [])
    OUT = []

    def say(t=""):
        print(t, flush=True)
        OUT.append(t)

    say("# Porównanie modeli parami (CRPS / Brier, niższe = lepiej)")
    say("Różnica = średnia(A) - średnia(B) na wspólnych stacjodniach; ujemna = A lepszy. 95% CI z bootstrapu po dniach. "
        "Pogrubiona nazwa w kolumnie „lepszy” = różnica istotna (CI nie obejmuje 0), „—” = bez rozstrzygnięcia. Brier zdarzeń rzadkich jest zdominowany przez dni bez zdarzenia — "
        "czytaj razem z POD/CSI i fałszywymi alarmami z raportów.")
    say()
    say("Liczba wspólnych stacjodni wg oceny: " + ", ".join(f"{nm}={len(set.intersection(*[set(d[nm][0]) for d in data]))}" for nm in names[:3]) + " ...")
    say()
    tally = {}
    for j, i in pairs:
        A_, B_ = labels[j], labels[i]
        say(f"## {A_} vs {B_}")
        say("| ocena | n | " + A_ + " | " + B_ + " | różnica | 95% CI | lepszy |")
        say("|---|---|---|---|---|---|---|")
        wins_a = wins_b = 0
        for nm in names:
            ka, va = data[j][nm]; kb, vb = data[i][nm]
            common = np.intersect1d(ka, kb)
            if len(common) < 30:
                continue
            da = dict(zip(ka, va)); db = dict(zip(kb, vb))
            xa = np.array([da[c] for c in common]); xb = np.array([db[c] for c in common])
            days = np.array([c.split("|")[0] for c in common])
            ud, inv = np.unique(days, return_inverse=True)
            diff = xa - xb
            ds = np.bincount(inv, weights=diff, minlength=len(ud)); dc = np.bincount(inv, minlength=len(ud)).astype(float)
            lo, hi = boot_ci(ds, dc)
            md = diff.mean()
            who = f"**{A_}**" if hi < 0 else (f"**{B_}**" if lo > 0 else "—")
            wins_a += hi < 0; wins_b += lo > 0
            say(f"| {nm} | {len(common)} | {xa.mean():.4f} | {xb.mean():.4f} | {md:+.4f} | [{lo:+.4f}, {hi:+.4f}] | {who} |")
        say(f"- istotnie lepszy {A_}: {wins_a} ocen, istotnie lepszy {B_}: {wins_b} ocen, bez rozstrzygnięcia: {len(names) - wins_a - wins_b}")
        say()
    out = a.out
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT) + "\n")
    print(f"Zapisano: {out}")


if __name__ == "__main__":
    main()
