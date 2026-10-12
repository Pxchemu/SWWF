#!/usr/bin/env python3
"""
Ocena SWWF (GEFS) na obserwacjach IMGW — trafienia, fałszywe alarmy, przeoczenia, wiarygodność.

Czyta pliki hindcast (hindcast_points.py: surowe pola GEFS dla stacji, przebiegi 00Z) i dobowe dane
synop IMGW (fetch_obs_imgw.py), buduje z nich prognozy dobowe SWWF na różne sposoby i porównuje je
z obserwacjami, osobno dla wyprzedzenia 0, 1 i 2 doby. Nic nie zmienia w produkcji — to narzędzie
do DECYZJI (które progi/metody dają mniej przeoczeń bez narastania fałszywych alarmów).

Użycie:
    python calibrate_swwf.py                                  # domyślnie hindcast_v2/ + najnowszy obs/*.csv.gz
    python calibrate_swwf.py --hindcast hindcast --obs obs/imgw_dobowe_2020-11-01_2026-03-31_mc-1-2-3-11-12.csv.gz
    python calibrate_swwf.py --out reports/calibration_report.md

Wynik: raport tekstowy (stdout + plik). Wymaga tylko numpy.

Konwencje (ustalone empirycznie na pilocie, patrz plan projektu):
  - opad/śnieg: doba IMGW D = 06 UTC D -> 06 UTC D+1  (okna 6 h od +6 h przebiegu 00Z)
  - temperatura: doba kalendarzowa 00-24 UTC (TMIN)
  - wyprzedzenie k = ile dób przed dniem D wystartował przebieg 00Z (k=0 -> przebieg z dnia D)
  - pomijamy stacje górskie (flaga `gory` w stations_imgw.csv) i niepełne przebiegi (<30 członków)
"""
import argparse
import csv
import glob
import gzip
import json
import os
import sys
from datetime import date, datetime, timedelta

import numpy as np

OBS_COLS = ("NSP POST ROK MC DZ TMAX WTMAX TMIN WTMIN STD WSTD TMNG WTMNG SMDB WSMDB ROOP PKSN WPKSN RWSN WRWSN "
            "USL WUSL DESZ WDESZ SNEG WSNEG DISN WDISN GRAD WGRAD MGLA WMGLA ZMGL WZMGL SADZ WSADZ GOLO WGOLO "
            "ZMNI WZMNI ZMWS WZMWS ZMET WZMET FF10 WFF10 FF15 WFF15 BRZA WBRZA ROSA WROSA SZRO WSZRO DZPS WDZPS "
            "DZBL WDZBL SGR IZD WIZD IZG WIZG AKTN WAKTN").split()
assert len(OBS_COLS) == 65
NUMERIC = ("TMAX", "TMIN", "STD", "SMDB", "PKSN", "SNEG", "GOLO", "ZMNI", "ZMWS", "FF10", "FF15")
GUST_BLIZZARD_MS = 15.5
COLD_AIR_BIAS_PROD = -1.0          # korekta produkcyjna z generate_swwf.py (COLD_AIR_BIAS_C)
VIS_BLIZZARD_M = 400.0
OUT = []
SKIP = set()          # sekcje pomijane przez --skip (ice, blizzard)
MODEL = "GEFS"        # podpis modelu w raporcie (GEFS / IFS ENS / GEFS+IFS)
NO_WIND = False       # True dla IFS i zespołu połączonego: IFS nie ma wiatru ani wilgotności w tym hindcaście


def say(text=""):
    print(text, flush=True)
    OUT.append(text)


# ----------------------------------------------------------------------------- dane
def load_obs(path):
    """Obserwacje IMGW. Puste pole ze statusem 9 = brak zjawiska -> 0; status 8 / brak statusu -> brak danych (NaN)."""
    obs = {}
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:
        for r in csv.reader(f):
            if len(r) != len(OBS_COLS) + 1:
                continue
            d = dict(zip(["src"] + OBS_COLS, r))
            rec = {}
            for k in NUMERIC:
                raw = d[k].strip()
                if raw != "":
                    try:
                        rec[k] = float(raw)
                        continue
                    except ValueError:
                        pass
                st = d.get("W" + k, "").strip()
                rec[k] = 0.0 if st == "9" and k not in ("TMAX", "TMIN", "STD") else np.nan
            rec["ROOP"] = d["ROOP"].strip()
            obs[(d["NSP"], date(int(d["ROK"]), int(d["MC"]), int(d["DZ"])))] = rec
    return obs


def load_runs(directory, min_members=30):
    runs = {}
    for p in sorted(glob.glob(os.path.join(directory, "*.json.gz"))):
        d = json.load(gzip.open(p, "rt", encoding="utf-8"))
        stamp = datetime.strptime(d["run"], "%Y-%m-%dT%H:00Z")
        if stamp.hour != 0 or len(d["members"]) < min_members:
            continue
        arr = {k: np.array(v, dtype=float) for k, v in d["data"].items()}     # [członek, stacja, okno]; None -> nan
        runs[stamp.date()] = dict(arr=arr, stations=d["stations"], nwin=len(d["windows"]))
    return runs


def pool_runs(runs_a, runs_b, wa, wb):
    """Łączy członków dwóch modeli w jeden zespół (tylko przebiegi wspólne, stacje wspólne po kodzie).
    wa / wb = ile razy powtórzyć członków modelu A / B: 5:3 przy 30 i 51 członkach daje ~równą wagę modeli
    (150 vs 153 członków), 1:1 = zwykłe złączenie (IFS ~63% wagi). Pola, których model nie ma, są NaN w jego części."""
    out = {}
    for d in sorted(set(runs_a) & set(runs_b)):
        A_, B_ = runs_a[d], runs_b[d]
        codes_b = {st["code"]: i for i, st in enumerate(B_["stations"])}
        keep = [(i, codes_b[st["code"]]) for i, st in enumerate(A_["stations"]) if st["code"] in codes_b]
        if not keep or A_["nwin"] != B_["nwin"]:
            continue
        ia = [i for i, _ in keep]; ib = [j for _, j in keep]
        arr = {}
        for k in sorted(set(A_["arr"]) | set(B_["arr"])):
            ma = A_["arr"][k].shape[0] if k in A_["arr"] else next(iter(A_["arr"].values())).shape[0]
            mb = B_["arr"][k].shape[0] if k in B_["arr"] else next(iter(B_["arr"].values())).shape[0]
            pa = A_["arr"][k][:, ia, :].astype(np.float32) if k in A_["arr"] else np.full((ma, len(ia), A_["nwin"]), np.nan, np.float32)
            pb = B_["arr"][k][:, ib, :].astype(np.float32) if k in B_["arr"] else np.full((mb, len(ib), B_["nwin"]), np.nan, np.float32)
            arr[k] = np.concatenate([np.tile(pa, (wa, 1, 1)), np.tile(pb, (wb, 1, 1))], axis=0)
        out[d] = dict(arr=arr, stations=[A_["stations"][i] for i in ia], nwin=A_["nwin"])
    return out


def day_windows(shift_h, k, nwin):
    a = (24 * k + shift_h) // 6
    return list(range(a, a + 4)) if a + 4 <= nwin else None


# ----------------------------------------------------------------------------- fizyka
def wind_chill(t, wind_ms):
    kmh = wind_ms * 3.6
    wc = 13.12 + 0.6215 * t - 11.37 * np.power(np.maximum(kmh, 1e-6), 0.16) + 0.3965 * t * np.power(np.maximum(kmh, 1e-6), 0.16)
    return np.where((t <= 10) & (kmh > 4.8), wc, t)


def wet_bulb(t, rh):
    """Temperatura mokrego termometru (Stull 2011), t w °C, rh w %."""
    rh = np.clip(rh, 5, 99)
    return (t * np.arctan(0.151977 * np.sqrt(rh + 8.313659)) + np.arctan(t + rh) - np.arctan(rh - 1.676331)
            + 0.00391838 * np.power(rh, 1.5) * np.arctan(0.023101 * rh) - 4.686035)


def clipf(x):
    return np.clip(x, 0.0, 1.0)


def phase_variants(have_rh):
    """Funkcje (te, tm, cp, rhe, rhm) -> frakcja opadu zamarzniętego (0..1) w oknie."""
    v = {
        "A dawna: CPOFP (gdy ważny), inaczej T końca okna (1@0C->0@2C)":
            lambda te, tm, cp, rhe, rhm: np.where(np.isfinite(cp) & (cp >= 0), np.minimum(cp / 100, 1), clipf((2.0 - te) / 2.0)),
        "D obecna (produkcja): T = zimniejsza z 2 próbek (1@1C->0@3C)":
            lambda te, tm, cp, rhe, rhm: clipf((3.0 - np.minimum(te, tm)) / 2.0),
        "G: CPOFP (gdy ważny), inaczej D":
            lambda te, tm, cp, rhe, rhm: np.where(np.isfinite(cp) & (cp >= 0), np.minimum(cp / 100, 1), clipf((3.0 - np.minimum(te, tm)) / 2.0)),
    }
    if have_rh:
        def tw(te, tm, rhe, rhm):
            return np.minimum(wet_bulb(te, np.nan_to_num(rhe, nan=80.0)), wet_bulb(tm, np.nan_to_num(rhm, nan=80.0)))
        v["W0: mokry termometr, zimniejsza z 2 próbek (1@0C->0@2C)"] = lambda te, tm, cp, rhe, rhm: clipf((2.0 - tw(te, tm, rhe, rhm)) / 2.0)
        v["W1: mokry termometr (1@0.5C->0@2.5C)"] = lambda te, tm, cp, rhe, rhm: clipf((2.5 - tw(te, tm, rhe, rhm)) / 2.0)
        v["W2: mokry termometr (1@1C->0@3C)"] = lambda te, tm, cp, rhe, rhm: clipf((3.0 - tw(te, tm, rhe, rhm)) / 2.0)
    return v


# ----------------------------------------------------------------------------- statystyki
def contingency(pf, ev, pthr):
    f = pf >= pthr
    h = int((f & ev).sum()); fa = int((f & ~ev).sum()); m = int((~f & ev).sum())
    pod = h / max(h + m, 1); far = fa / max(h + fa, 1); csi = h / max(h + fa + m, 1)
    return h, fa, m, pod, far, csi


def cont_line(pf, ev, pthrs=(0.1, 0.3, 0.5)):
    parts = []
    for p in pthrs:
        h, fa, m, pod, far, csi = contingency(pf, ev, p)
        parts.append(f"P>={int(p*100)}%: traf. {h}, fałsz. {fa}, przegap. {m} (POD {pod:.2f}, FAR {far:.2f}, CSI {csi:.2f})")
    return " | ".join(parts)


def reliability(pf, ev):
    out = []
    for lo, hi, label in ((0, 1e-9, "0"), (1e-9, 0.2, "0-20%"), (0.2, 0.4, "20-40%"), (0.4, 0.6, "40-60%"), (0.6, 0.8, "60-80%"), (0.8, 1.01, "80-100%")):
        sel = (pf <= 0) if label == "0" else ((pf >= lo) & (pf < hi))
        if sel.sum():
            out.append(f"P={label}: n={int(sel.sum())}, zaszło {ev[sel].mean() * 100:.0f}%")
    return " | ".join(out)


# ----------------------------------------------------------------------------- zbiór stacjodni
class Sample:
    """Wektory per-stacjodzień: obserwacje + wielkości członków."""
    def __init__(self):
        self.o, self.m, self.meta = [], {}, []

    def add(self, o, member_vals, meta=None):
        self.o.append(o)
        self.meta.append(meta)
        for k, v in member_vals.items():
            self.m.setdefault(k, []).append(v)

    def finalize(self):
        self.M = {k: np.array(v) for k, v in self.m.items()}
        self.n = len(self.o)
        return self

    def obs(self, key):
        return np.array([x[key] for x in self.o], dtype=float)

    def roop(self):
        return np.array([x["ROOP"] for x in self.o])


def build_sample(runs, obs, k, shift, extra):
    s = Sample()
    for R in sorted(runs):
        info = runs[R]
        w = day_windows(shift, k, info["nwin"])
        if w is None:
            continue
        D = R + timedelta(days=k)
        A = info["arr"]
        vals = extra(A, w)
        for i, st in enumerate(info["stations"]):
            if st.get("flag") == "gory":
                continue
            o = obs.get((st["code"], D))
            if o is None:
                continue
            s.add(o, {key: v[:, i] if v.ndim == 2 else v for key, v in vals.items()},
                  (R, D, st.get("code"), st.get("name", st.get("code")), st.get("lat"), st.get("lon")))
    return s.finalize()


# ----------------------------------------------------------------------------- sekcje raportu
def section_alignment(runs, obs):
    say("## 0. Kontrola okna doby IMGW (k=0)")
    mount = set()
    for label, field, tfun in (("opad SMDB", "SMDB", "precip"), ("TMIN", "TMIN", "tmin")):
        res = []
        for shift in (0, 6, 12, 18):
            xs, ys = [], []
            for R in sorted(runs):
                info = runs[R]; w = day_windows(shift, 0, info["nwin"])
                if w is None:
                    continue
                A = info["arr"]
                if tfun == "precip":
                    val = A["apcp"][:, :, w].sum(axis=2)
                else:
                    val = np.minimum(np.nanmin(A["t_end"][:, :, w], axis=2), np.nanmin(A["t_mid"][:, :, w], axis=2))
                for i, st in enumerate(info["stations"]):
                    if st.get("flag") == "gory":
                        continue
                    o = obs.get((st["code"], R))
                    if o is None or not np.isfinite(o[field]):
                        continue
                    xs.append(np.nanmean(val[:, i])); ys.append(o[field])
            xs, ys = np.array(xs), np.array(ys)
            if len(xs) > 20:
                c = np.corrcoef(np.sqrt(xs), np.sqrt(ys))[0, 1] if tfun == "precip" else np.corrcoef(xs, ys)[0, 1]
                res.append(f"start {shift:2d} UTC: r={c:.3f}")
        say(f"- {label}: " + " | ".join(res) + "  (najwyższe r = okno zgodne z IMGW)")
    say()


def section_precip(runs, obs):
    say("## 1. Opad dobowy (okno 06->06 UTC)")
    for k in (0, 1, 2):
        s = build_sample(runs, obs, k, 6, lambda A, w: dict(P=A["apcp"][:, :, w].sum(axis=2)))
        if s.n == 0:
            continue
        O = s.obs("SMDB"); ok = np.isfinite(O); P = s.M["P"][ok]; O = O[ok]
        mean = P.mean(axis=1); wet = O >= 1
        say(f"### wyprzedzenie k={k}: n={len(O)} stacjodni, mokrych (>=1 mm) {int(wet.sum())}")
        say(f"- średnia obs {O.mean():.2f} mm, {MODEL} {mean.mean():.2f} mm; korelacja sqrt = {np.corrcoef(np.sqrt(mean), np.sqrt(O))[0,1]:.3f}")
        if wet.sum():
            say(f"- dni mokre: {MODEL}/obs = {mean[wet].mean() / O[wet].mean():.2f}; obs > max zespołu: {((O > P.max(axis=1)) & wet).sum() / wet.sum() * 100:.1f}% dni mokrych")
        for thr in (1, 5, 10):
            say(f"- P(opad>={thr} mm): " + reliability((P >= thr).mean(axis=1), O >= thr))
    say()


def section_snow(runs, obs):
    have_rh = (not NO_WIND) and all("rh_end" in r["arr"] and np.isfinite(r["arr"]["rh_end"]).any() for r in runs.values())
    variants = phase_variants(have_rh)
    say("## 2. Śnieg — metody rozpoznawania fazy opadu (okno 06->06 UTC)")
    say("Zdarzenie obserwowane: opad rodzaju S (śnieg) o sumie >= X mm. Prognoza: P(opad zamarznięty >= X mm) wg metody. "
        "Kolumna 'deszcz->śnieg' = odsetek dni z obserwowanym DESZCZEM >=3 mm, w których metoda daje P(śnieg>=3 mm) >= 30% (fałszywy śnieg).")
    if not have_rh:
        say("(brak pól wilgotności w danych albo zespół z IFS (IFS nie ma wilgotności) — warianty z mokrym termometrem pominięte)")
    def extra(A, w):
        ap = A["apcp"][:, :, w]; te = A["t_end"][:, :, w]; tm = A["t_mid"][:, :, w]
        cp = A["cpofp_end"][:, :, w] if "cpofp_end" in A else np.full_like(ap, np.nan)
        rhe = A["rh_end"][:, :, w] if have_rh else np.full_like(ap, np.nan)
        rhm = A["rh_mid"][:, :, w] if have_rh else np.full_like(ap, np.nan)
        d = {"precip": ap.sum(axis=2)}
        for name, fn in variants.items():
            d[name] = (ap * fn(te, tm, cp, rhe, rhm)).sum(axis=2)
        return d
    for k in (0, 1, 2):
        s = build_sample(runs, obs, k, 6, extra)
        if s.n == 0:
            continue
        O = s.obs("SMDB"); T = s.roop(); ok = np.isfinite(O)
        snow = np.where(T == "S", O, 0.0)
        rain = (T == "W") & (O >= 3)
        say(f"### wyprzedzenie k={k}: n={int(ok.sum())}; obs śnieg >=1 mm: {int((snow[ok] >= 1).sum())}, >=3 mm: {int((snow[ok] >= 3).sum())}, >=5 mm: {int((snow[ok] >= 5).sum())}; deszcz >=3 mm: {int(rain[ok].sum())}")
        say("| metoda | POD (3 mm) | FAR (3 mm) | CSI (3 mm) | POD (1 mm) | FAR (1 mm) | deszcz->śnieg |")
        say("|---|---|---|---|---|---|---|")
        for name in variants:
            SW = s.M[name]
            row = []
            for thr in (3, 1):
                _, _, _, pod, far, csi = contingency((SW[ok] >= thr).mean(axis=1), snow[ok] >= thr, 0.3)
                row.append((pod, far, csi))
            pr = (SW[ok & rain] >= 3).mean(axis=1) if (ok & rain).sum() else np.array([0.0])
            say(f"| {name} | {row[0][0]:.2f} | {row[0][1]:.2f} | {row[0][2]:.2f} | {row[1][0]:.2f} | {row[1][1]:.2f} | {(pr >= 0.3).mean() * 100:.0f}% |")
        best = next(n for n in variants if n.startswith('D'))
        say(f"- wiarygodność P(śnieg>=3 mm), metoda '{best[:1]}' (produkcyjna): " + reliability((s.M[best][ok] >= 3).mean(axis=1), snow[ok] >= 3))
    say()


def section_cold(runs, obs):
    have_uv = (not NO_WIND) and all("u10_end" in r["arr"] and np.isfinite(r["arr"]["u10_end"]).any() for r in runs.values())
    say("## 3. Mróz — temperatura powietrza vs odczuwalna (okno doby kalendarzowej 00-24 UTC; obserwacja = TMIN powietrza)")
    say("Uwaga: IMGW mierzy tylko temperaturę powietrza, więc odczuwalnej NIE da się zweryfikować wprost; poniżej sprawdzamy, jak daleko od powietrza jest każda wersja i czy 'odczuwalna' nie robi fałszywych alarmów względem realnego mrozu.")
    def extra(A, w):
        te = A["t_end"][:, :, w]; tm = A["t_mid"][:, :, w]
        d = {"air": np.minimum(np.nanmin(te, axis=2), np.nanmin(tm, axis=2))}
        if not NO_WIND:
            ge = A["gust_end"][:, :, w]; gm = A["gust_mid"][:, :, w]
            d["feels_gust"] = np.minimum(np.nanmin(wind_chill(te, ge), axis=2), np.nanmin(wind_chill(tm, gm), axis=2))
        if have_uv:
            we = np.hypot(A["u10_end"][:, :, w], A["v10_end"][:, :, w]); wm = np.hypot(A["u10_mid"][:, :, w], A["v10_mid"][:, :, w])
            d["feels_mean"] = np.minimum(np.nanmin(wind_chill(te, we), axis=2), np.nanmin(wind_chill(tm, wm), axis=2))
        return d
    for k in (0, 1, 2):
        s = build_sample(runs, obs, k, 0, extra)
        if s.n == 0:
            continue
        TM = s.obs("TMIN"); ok = np.isfinite(TM); TM = TM[ok]
        air = s.M["air"][ok]
        say(f"### wyprzedzenie k={k}: n={len(TM)}")
        say(f"- prognoza min. T powietrza: błąd średni {np.mean(air.mean(axis=1) - TM):+.2f} C, MAE {np.mean(abs(air.mean(axis=1) - TM)):.2f} C; "
            f"w mroźnych dniach (obs <= -10 C): błąd {np.mean(air.mean(axis=1)[TM <= -10] - TM[TM <= -10]):+.2f} C" if (TM <= -10).any() else
            f"- prognoza min. T powietrza: błąd średni {np.mean(air.mean(axis=1) - TM):+.2f} C, MAE {np.mean(abs(air.mean(axis=1) - TM)):.2f} C")
        for key, label in (("feels_gust", "odczuwalna z PORYWÓW (dawna wersja hazardu; produkcja używa T powietrza)"), ("feels_mean", "odczuwalna z wiatru ŚREDNIEGO")):
            if key in s.M:
                say(f"- {label}: chłodniejsza od powietrza średnio o {np.mean(air.mean(axis=1) - s.M[key][ok].mean(axis=1)):.1f} C")
        for thr in (-5, -10, -15, -20):
            ev = TM <= thr
            if ev.sum() < 5:
                continue
            say(f"- próg {thr} C (obs zdarzeń {int(ev.sum())}), powietrze: " + cont_line((air <= thr).mean(axis=1), ev, (0.3,)))
    say()


def section_ice(runs, obs):
    say("## 4. Gołoledź — opad w warunkach marznących (CFRZR >= 0.5) vs obserwowane godziny gołoledzi (GOLO)")
    def extra(A, w):
        ap = A["apcp"][:, :, w]; cf = A["cfrzr_end"][:, :, w]
        return {"ice": np.where(np.nan_to_num(cf, nan=0.0) >= 0.5, ap, 0.0).sum(axis=2)}
    for k in (0, 1, 2):
        s = build_sample(runs, obs, k, 6, extra)
        if s.n == 0:
            continue
        G = s.obs("GOLO"); ok = np.isfinite(G); ev = G[ok] >= 1
        if ev.sum() < 5:
            say(f"- k={k}: za mało zdarzeń gołoledzi w próbie ({int(ev.sum())})")
            continue
        for thr in (0.1, 1.0):
            say(f"- k={k}, obs GOLO>=1 h: {int(ev.sum())} zdarzeń z {int(ok.sum())}; prognoza P(opad marznący >= {thr} mm): " + cont_line((s.M['ice'][ok] >= thr).mean(axis=1), ev, (0.1, 0.3)))
    say()


def section_blizzard(runs, obs):
    say("## 5. Zamieć (gwałtowny wiatr + widzialność) — UWAGA: to NIE jest produkcyjny hazard Snow Squalls (CAPE + opad zamarznięty, nieweryfikowalny obserwacjami IMGW); sekcja sprawdza wycofany hazard BLIZZARD")
    say("## 5 (opis). Zamieć — definicja SWWF (porywy >= 15.5 m/s, widzialność <= 400 m, śnieg świeży/leżący) vs obserwowane godziny zamieci śnieżnej (ZMNI+ZMWS)")
    say("Uwaga: przebiegi bez pola widzialności (GEFS 2021) nie mogą dać flagi wg definicji SWWF, więc są z tej oceny wyłączone; "
        "wariant 'bez VIS' (porywy + śnieg) działa na wszystkich.")
    def extra(A, w):
        g = A["gust_end"][:, :, w]; ap = A["apcp"][:, :, w]
        snod = np.nan_to_num(A["snod_end"][:, :, w], nan=0.0) * 100.0
        snow_ok = (ap >= 0.05) | (snod >= 5.0)              # opad (>= ~0.5 cm) albo leżący >= 5 cm
        vis_raw = A["vis_end"][:, :, w]
        has_vis = np.isfinite(vis_raw).any()
        flag_vis = (g >= GUST_BLIZZARD_MS) & (np.nan_to_num(vis_raw, nan=1e9) <= VIS_BLIZZARD_M) & snow_ok
        flag_novis = (g >= GUST_BLIZZARD_MS) & snow_ok
        gm = np.maximum(np.nan_to_num(g, nan=0.0), np.nan_to_num(A["gust_mid"][:, :, w], nan=0.0)).max(axis=2)
        return {"flag": flag_vis.any(axis=2).astype(float), "flag_novis": flag_novis.any(axis=2).astype(float),
                "gust": gm, "has_vis": np.array(has_vis)}
    for k in (0, 1):
        s = build_sample(runs, obs, k, 6, extra)
        if s.n == 0:
            continue
        Z = s.obs("ZMNI") + s.obs("ZMWS"); ok = np.isfinite(Z); ev = Z[ok] >= 1
        hv = s.M["has_vis"].astype(bool)
        if ev.sum() < 5:
            say(f"- k={k}: za mało zdarzeń zamieci w próbie ({int(ev.sum())})")
            continue
        say(f"- k={k}: obs zamieć >=1 h: {int(ev.sum())} z {int(ok.sum())} stacjodni")
        okv = ok & hv
        if (Z[okv] >= 1).sum() >= 3:
            say(f"    definicja SWWF z VIS (tylko przebiegi z VIS, {int(okv.sum())} stacjodni, {int((Z[okv] >= 1).sum())} zdarzeń): " + cont_line(s.M["flag"][okv].mean(axis=1), Z[okv] >= 1, (0.1, 0.3)))
        say("    bez VIS (porywy >= 15.5 m/s + śnieg): " + cont_line(s.M["flag_novis"][ok].mean(axis=1), ev, (0.1, 0.3, 0.5)))
        for gthr in (15.5, 20):
            say(f"    tylko porywy >= {gthr} m/s: " + cont_line((s.M["gust"][ok] >= gthr).mean(axis=1), ev, (0.3, 0.5)))
    say()


def section_quiet(runs, obs):
    """Fałszywe alarmy na dobach BEZ zdarzenia vs trafienia na dobach ZE zdarzeniem.
    Doba (przebieg, wyprzedzenie k) jest 'bez zdarzenia' dla danego hazardu, gdy zdarzenie zaszło na <= 1 stacji;
    'ze zdarzeniem' — gdy na >= 5 stacjach. Dzięki temu nie trzeba listy przebiegów: liczy się to, co faktycznie zaszło."""
    say("## 6. Fałszywe alarmy na dobach bez zdarzenia i trafienia na dobach ze zdarzeniem")
    say("Alarm = P(zdarzenia) >= 30% wg zespołu. Doba 'bez zdarzenia' = zdarzenie na <= 1 stacji (wtedy każdy alarm jest fałszywy); "
        "'ze zdarzeniem' = na >= 5 stacjach. 'doby z >=3 stacjami' = ile dób miało alarm na co najmniej 3 stacjach naraz "
        "(tyle widziałby użytkownik jako plamę na mapie).")
    def snow_extra(A, w):
        ap = A["apcp"][:, :, w]; te = A["t_end"][:, :, w]; tm = A["t_mid"][:, :, w]
        return {"v": (ap * clipf((3.0 - np.minimum(te, tm)) / 2.0)).sum(axis=2)}
    def cold_extra(A, w):
        return {"v": np.minimum(np.nanmin(A["t_end"][:, :, w], axis=2), np.nanmin(A["t_mid"][:, :, w], axis=2))}
    def precip_extra(A, w):
        return {"v": A["apcp"][:, :, w].sum(axis=2)}
    def blizz_extra(A, w):
        g = A["gust_end"][:, :, w]; ap = A["apcp"][:, :, w]
        snod = np.nan_to_num(A["snod_end"][:, :, w], nan=0.0) * 100.0
        return {"v": ((g >= GUST_BLIZZARD_MS) & ((ap >= 0.05) | (snod >= 5.0))).any(axis=2).astype(float)}
    def snow_obs(s):
        O = s.obs("SMDB"); return np.where(s.roop() == "S", O, 0.0)
    specs = [
        ("śnieg >= 3 mm", 6, snow_extra, snow_obs, lambda v: (v >= 3).mean(axis=1), lambda o: o >= 3),
        ("opad >= 10 mm", 6, precip_extra, lambda s: s.obs("SMDB"), lambda v: (v >= 10).mean(axis=1), lambda o: o >= 10),
        ("mróz TMIN <= -10 C", 0, cold_extra, lambda s: s.obs("TMIN"), lambda v: (v <= -10).mean(axis=1), lambda o: o <= -10),
        ("mróz TMIN <= -15 C", 0, cold_extra, lambda s: s.obs("TMIN"), lambda v: (v <= -15).mean(axis=1), lambda o: o <= -15),
        ("zamieć (porywy >= 15.5 m/s + śnieg, bez VIS)", 6, blizz_extra, lambda s: s.obs("ZMNI") + s.obs("ZMWS"),
         lambda v: v.mean(axis=1), lambda o: o >= 1),
    ]
    if "blizzard" in SKIP:
        specs = [sp for sp in specs if not sp[0].startswith("zamieć")]
    for k in (0, 1, 2):
        say(f"### wyprzedzenie k={k}")
        for name, shift, extra, obsfn, pfun, evfun in specs:
            fr = dict(days=0, sd=0, al=0, big=0)                 # doby bez zdarzenia
            ev_ = dict(days=0, ev=0, hit=0, fa=0)                # doby ze zdarzeniem
            for R in sorted(runs):
                s = build_sample({R: runs[R]}, obs, k, shift, extra)
                if s.n == 0:
                    continue
                o = obsfn(s); ok = np.isfinite(o)
                if not ok.any():
                    continue
                al = pfun(s.M["v"][ok]) >= 0.3; ev = evfun(o[ok]); nev = int(ev.sum())
                if nev <= 1:
                    fr["days"] += 1; fr["sd"] += int(ok.sum()); fr["al"] += int(al.sum()); fr["big"] += int(al.sum() >= 3)
                elif nev >= 5:
                    ev_["days"] += 1; ev_["ev"] += nev; ev_["hit"] += int((al & ev).sum()); ev_["fa"] += int((al & ~ev).sum())
            if fr["days"]:
                say(f"- {name}: doby bez zdarzenia: {fr['days']}, stacjodni {fr['sd']}, fałszywych alarmów {fr['al']} "
                    f"({fr['al'] / max(fr['sd'], 1) * 1000:.1f} na 1000 stacjodni); doby z >=3 stacjami: {fr['big']} z {fr['days']}")
            else:
                say(f"- {name}: brak dób bez zdarzenia w próbie")
            if ev_["days"]:
                say(f"    doby ze zdarzeniem: {ev_['days']}, zdarzeń {ev_['ev']}, trafionych {ev_['hit']} (POD {ev_['hit'] / max(ev_['ev'], 1):.2f}), "
                    f"fałszywych alarmów na tych dobach {ev_['fa']}")
    say()


def section_cold_bias(runs, obs):
    """Skad bierze sie niedoszacowanie ogona zimna: zaleznosc bledu od prognozowanej temperatury, rozrzut zespolu,
    rozrzut miedzy stacjami (teren?) oraz prosta korekta oceniana krzyzowo (leave-one-run-out)."""
    say("## 7. Mróz — diagnoza niedoszacowania ogona zimna i test prostej korekty (TMIN, doba 00-24 UTC)")
    say("Błąd = obserwacja - prognoza (średnia zespołu min. T powietrza); UJEMNY = w rzeczywistości zimniej niż w prognozie (prognoza za ciepła). "
        "Przedziały wg PROGNOZY (wersja użyteczna do korekty; przedziały wg obserwacji zawyżają błąd przez regresję do średniej).")
    def extra(A, w):
        te = A["t_end"][:, :, w]; tm = A["t_mid"][:, :, w]
        return {"air": np.minimum(np.nanmin(te, axis=2), np.nanmin(tm, axis=2))}
    bins = [(-99, -15, "prog. < -15"), (-15, -10, "-15..-10"), (-10, -5, "-10..-5"), (-5, 0, "-5..0"), (0, 99, "> 0")]
    for k in (0, 1, 2):
        s = build_sample(runs, obs, k, 0, extra)
        if s.n == 0:
            continue
        TM = s.obs("TMIN"); ok = np.isfinite(TM)
        air = s.M["air"][ok]; TM = TM[ok]; meta = [m for m, g in zip(s.meta, ok) if g]
        mean = air.mean(axis=1); sd = air.std(axis=1); err = TM - mean
        say(f"### wyprzedzenie k={k}: n={len(TM)}")
        row = []
        for lo, hi, lab in bins:
            sel = (mean >= lo) & (mean < hi)
            if sel.sum() >= 10:
                row.append(f"{lab}: n={int(sel.sum())}, błąd {err[sel].mean():+.2f} C (mediana {np.median(err[sel]):+.2f})")
        say("- błąd wg przedziałów prognozy: " + " | ".join(row))
        cold = mean <= -5
        say(f"- rozrzut zespołu (średnie odch. std) {sd.mean():.2f} C vs RMSE średniej zespołu {np.sqrt(np.mean(err ** 2)):.2f} C; "
            f"dla prognoz <= -5 C: rozrzut {sd[cold].mean():.2f} C vs RMSE {np.sqrt(np.mean(err[cold] ** 2)):.2f} C")
        below = TM < air.min(axis=1)
        say(f"- obserwacja zimniejsza niż WSZYSTKIE 30 członków: {below.mean() * 100:.1f}% stacjodni (przy dobrze rozproszonym zespole ~3%); "
            f"dla prognoz <= -5 C: {below[cold].mean() * 100:.1f}%")
        # rozrzut miedzy stacjami (czy blad zalezy od stacji = teren)
        st = {}
        for e, m, c in zip(err, meta, cold):
            if c:
                st.setdefault(m[2], dict(name=m[3], lat=m[4], lon=m[5], e=[]))["e"].append(e)
        rows = [(np.mean(v["e"]), len(v["e"]), v["name"], v["lat"], v["lon"]) for v in st.values() if len(v["e"]) >= 8]
        if len(rows) >= 6:
            rows.sort()
            allm = np.array([r[0] for r in rows])
            say(f"- błąd na dniach z prognozą <= -5 C wg stacji (n stacji={len(rows)}): średnia {allm.mean():+.2f} C, "
                f"rozrzut między stacjami (std) {allm.std():.2f} C")
            say("    najmniejszy błąd: " + ", ".join(f"{r[2]} {r[0]:+.1f}" for r in rows[:5]))
            say("    największy błąd: " + ", ".join(f"{r[2]} {r[0]:+.1f}" for r in rows[-6:]))
            lats = np.array([r[3] for r in rows if r[3] is not None], dtype=float)
            lons = np.array([r[4] for r in rows if r[4] is not None], dtype=float)
            if len(lats) == len(rows):
                say(f"    korelacja błędu stacji z szerokością: {np.corrcoef(lats, allm)[0, 1]:+.2f}, z długością: {np.corrcoef(lons, allm)[0, 1]:+.2f}")
        # warianty korekty, oceniane leave-one-run-out (parametry z pozostałych przebiegów, ocena na pominiętym)
        runs_id = np.array([m[0].toordinal() for m in meta])
        shift = np.zeros_like(mean); sigma = np.full_like(mean, np.nan)
        for r in np.unique(runs_id):
            tr = (runs_id != r) & (mean <= 2)
            if tr.sum() < 100:
                continue
            bb, aa = np.polyfit(mean[tr], TM[tr], 1)
            te_ = (runs_id == r)
            shift[te_] = (aa + bb * mean[te_]) - mean[te_]
            sigma[te_] = np.std(TM[tr] - (aa + bb * mean[tr]))
        sigma = np.where(np.isfinite(sigma), sigma, np.nanmean(sigma))
        from math import erf
        ncdf = np.vectorize(lambda z: 0.5 * (1.0 + erf(z / 2 ** 0.5)))
        prod = air + COLD_AIR_BIAS_PROD
        lin = air + shift[:, None]
        res_sd = np.sqrt(np.maximum(sigma ** 2 - sd ** 2, 0.25))      # brakujący rozrzut (sigma całkowita - rozrzut zespołu)
        say(f"- korekta liniowa po prognozie: MAE {np.mean(abs(mean - TM)):.2f} -> {np.mean(abs(lin.mean(axis=1) - TM)):.2f} C; "
            f"błąd średni {np.mean(TM - mean):+.2f} -> {np.mean(TM - lin.mean(axis=1)):+.2f} C; "
            f"średnie przesunięcie dla prognoz <= -10 C: {shift[mean <= -10].mean() if (mean <= -10).any() else 0:+.2f} C "
            f"(produkcja: {COLD_AIR_BIAS_PROD:+.1f} C); sigma resztowa ok. {np.nanmean(sigma):.2f} C")
        # doby bez zdarzenia (<= 1 stacja z TMIN <= prog) -> fałszywe alarmy na 1000 stacjodni
        variants = (
            ("surowe (bez korekty)", lambda thr: (air <= thr).mean(axis=1)),
            (f"produkcja ({COLD_AIR_BIAS_PROD:+.1f} C)", lambda thr: (prod <= thr).mean(axis=1)),
            ("korekta liniowa (LORO)", lambda thr: (lin <= thr).mean(axis=1)),
            ("produkcja + wygładzenie rozrzutu (sigma z LORO)", lambda thr: ncdf((thr - prod) / res_sd[:, None]).mean(axis=1)),
            ("korekta liniowa + wygładzenie rozrzutu", lambda thr: ncdf((thr - lin) / res_sd[:, None]).mean(axis=1)),
        )
        for thr in (-5, -10, -15):
            ev = TM <= thr
            if ev.sum() < 5:
                continue
            nev = {r: int(ev[runs_id == r].sum()) for r in np.unique(runs_id)}
            free = np.array([nev[r] <= 1 for r in runs_id])
            say(f"- próg {thr} C, alarm przy P>=30%:")
            for name, fn in variants:
                p = fn(thr); h, fa, m, pod, far, csi = contingency(p, ev, 0.3)
                fa_free = int(((p >= 0.3) & ~ev & free).sum())
                say(f"    {name}: POD {pod:.2f}, FAR {far:.2f}, CSI {csi:.2f}, fałszywych {fa}; na dobach bez zdarzenia {fa_free / max(int(free.sum()), 1) * 1000:.1f} na 1000 stacjodni")
    say()


def section_snow_cal(runs, obs):
    """Śnieg: czy skalowanie ilości (mokry bias GEFS) i/lub próg alarmu P poprawia wynik; oceniane na dobach ze zdarzeniem i bez."""
    say("## 8. Śnieg — test skalowania ilości opadu zamarzniętego (wariant D) i progu alarmu")
    say("Skala f mnoży opad zamarznięty każdego członka (f=1,0 = obecna produkcja). Zdarzenie = obserwowany opad rodzaju S >= X mm (SMDB). "
        "Doby bez zdarzenia = zdarzenie na <= 1 stacji. Uwaga: to ilość WODY (mm), nie centymetry śniegu — przelicznik śnieg:woda jest osobną sprawą.")
    def extra(A, w):
        ap = A["apcp"][:, :, w]; te = A["t_end"][:, :, w]; tm = A["t_mid"][:, :, w]
        return {"v": (ap * clipf((3.0 - np.minimum(te, tm)) / 2.0)).sum(axis=2)}
    for k in (0, 1, 2):
        s = build_sample(runs, obs, k, 6, extra)
        if s.n == 0:
            continue
        O = s.obs("SMDB"); T = s.roop(); ok = np.isfinite(O)
        snow = np.where(T == "S", O, 0.0)[ok]; V = s.M["v"][ok]
        meta = [m for m, g in zip(s.meta, ok) if g]; rid = np.array([m[0].toordinal() for m in meta])
        mean = V.mean(axis=1)
        say(f"### wyprzedzenie k={k}: n={int(ok.sum())}")
        row = []
        for lo, hi, lab in ((0.5, 1, "0,5-1 mm"), (1, 3, "1-3 mm"), (3, 6, "3-6 mm"), (6, 999, ">6 mm")):
            sel = (mean >= lo) & (mean < hi)
            if sel.sum() >= 15:
                row.append(f"{lab}: n={int(sel.sum())}, obs/prog. = {snow[sel].mean() / mean[sel].mean():.2f}")
        say("- stosunek średniej obserwowanego śniegu (mm) do średniej prognozy wg przedziałów prognozy: " + " | ".join(row))
        for thr in (3, 5):
            ev = snow >= thr
            if ev.sum() < 10:
                continue
            nev = {r: int(ev[rid == r].sum()) for r in np.unique(rid)}
            free = np.array([nev[r] <= 1 for r in rid])
            say(f"- próg {thr} mm:")
            for f in (1.0, 0.9, 0.8, 0.7, 0.6):
                for pthr in (0.3, 0.5):
                    p = (V * f >= thr).mean(axis=1)
                    h, fa, m, pod, far, csi = contingency(p, ev, pthr)
                    ff = int(((p >= pthr) & ~ev & free).sum())
                    say(f"    f={f:.1f}, alarm przy P>={int(pthr * 100)}%: POD {pod:.2f}, FAR {far:.2f}, CSI {csi:.2f}, fałszywych {fa}; na dobach bez zdarzenia {ff / max(int(free.sum()), 1) * 1000:.1f} na 1000 stacjodni")
    say()


SNOW_RATIO_PROD = ((-99, -10, 15.0), (-10, -5, 12.0), (-5, 0.01, 10.0), (0.01, 99, 7.0))   # jak snow_density_ratio w generate_swwf.py


def section_snow_ratio(obs):
    """Przelicznik śnieg:woda (cm śniegu na 1 mm wody) z obserwacji: przyrost pokrywy PKSN (cm, 06 UTC D - 06 UTC D-1)
    do opadu dobowego SMDB (mm) w dobach z opadem rodzaju S. Niezależne od hindcastu (cała próbka obserwacji)."""
    say("## 9. Przelicznik śnieg:woda — przyrost pokrywy śnieżnej (PKSN) / opad dobowy (SMDB), doby z opadem śniegu")
    say("Doba D: ROOP = S, SMDB >= 2 mm, PKSN znane w D i D-1, przyrost > 0. Temperatura = (TMIN+TMAX)/2 doby. Wartość = cm śniegu na 1 mm wody "
        "(10 = klasyczne 10:1). Uwaga: przyrost pokrywy jest DOLNYM oszacowaniem (osiadanie, topnienie, zawianie), a niedoszacowanie "
        "opadu przez deszczomierz przy śniegu (wiatr) zawyża iloraz — wynik traktować jako rząd wielkości.")
    rows = []
    for (st, d), o in obs.items():
        if o.get("ROOP") != "S":
            continue
        sm, pk, tmin, tmax = o.get("SMDB"), o.get("PKSN"), o.get("TMIN"), o.get("TMAX")
        prev = obs.get((st, d - timedelta(days=1)))
        if prev is None or not all(np.isfinite(x) for x in (sm, pk, tmin, tmax, prev.get("PKSN", np.nan))):
            continue
        dpk = pk - prev["PKSN"]
        if sm >= 2 and dpk > 0:
            rows.append(((tmin + tmax) / 2.0, dpk / sm))
    if len(rows) < 30:
        say(f"- za mało dób do oceny (n={len(rows)})")
        say()
        return
    T = np.array([r[0] for r in rows]); R = np.array([r[1] for r in rows])
    say(f"- dób z przyrostem pokrywy: {len(R)}; mediana ilorazu {np.median(R):.1f} cm/mm (kwartyle {np.percentile(R, 25):.1f}-{np.percentile(R, 75):.1f})")
    for lo, hi, prod in SNOW_RATIO_PROD:
        sel = (T > lo) & (T <= hi)
        if sel.sum() >= 15:
            q = np.percentile(R[sel], [25, 50, 75])
            lab = ("T śr. < " + f"{hi:g}" if lo <= -99 else ("T śr. > 0" if hi >= 99 else f"T śr. {lo:g}..{hi:g}")).replace("0.01", "0")
            say(f"- {lab} C: n={int(sel.sum())}, mediana {q[1]:.1f} cm/mm (kwartyle {q[0]:.1f}-{q[2]:.1f}); produkcja używa {prod / 10:.1f} cm/mm ({prod:.0f}:1)")
    say()


def snow_ratio_prod(t):
    """Jak snow_density_ratio w generate_swwf.py (T na końcu okna)."""
    return np.where(t <= -10, 15.0, np.where(t <= -5, 12.0, np.where(t <= 0, 10.0, 7.0)))


def section_snow_cm(runs, obs):
    """Test koniec-do-końca: PROGNOZOWANE cm śniegu (dokładnie wzór produkcyjny: opad * frakcja zamarznięta / 10 * przelicznik)
    vs OBSERWOWANY przyrost pokrywy PKSN (cm) w dobie. To jest liczba, którą widzi użytkownik."""
    say("## 10. Śnieg w cm — prognoza produkcyjna vs przyrost pokrywy śnieżnej (PKSN D - PKSN D-1)")
    say("Prognoza = suma po 4 oknach: opad * frakcja zamarznięta (wariant D) / 10 * przelicznik (15/12/10/7 z T na końcu okna), skala g mnoży cm. "
        "Zdarzenie = przyrost pokrywy >= X cm. UWAGA: przyrost pokrywy to DOLNE oszacowanie świeżego śniegu (osiadanie, topnienie, zawianie), "
        "więc 'obs/prog.' < 1 częściowo wynika z samego pomiaru; interpretować porównawczo (czy g poprawia CSI), nie jako dokładny współczynnik.")
    def extra(A, w):
        ap = A["apcp"][:, :, w]; te = A["t_end"][:, :, w]; tm = A["t_mid"][:, :, w]
        fz = clipf((3.0 - np.minimum(te, tm)) / 2.0)
        return {"cm": (ap * fz / 10.0 * snow_ratio_prod(te)).sum(axis=2)}
    for k in (0, 1, 2):
        s = build_sample(runs, obs, k, 6, extra)
        if s.n == 0:
            continue
        dpk = np.full(s.n, np.nan)
        for i, m in enumerate(s.meta):
            pk = s.o[i].get("PKSN", np.nan); prev = obs.get((m[2], m[1] - timedelta(days=1)))
            if prev is not None and np.isfinite(pk) and np.isfinite(prev.get("PKSN", np.nan)):
                dpk[i] = pk - prev["PKSN"]
        ok = np.isfinite(dpk)
        if ok.sum() < 50:
            say(f"### wyprzedzenie k={k}: za mało dób z PKSN (n={int(ok.sum())})")
            continue
        V = s.M["cm"][ok]; O = np.maximum(dpk[ok], 0.0)
        rid = np.array([m[0].toordinal() for m, g in zip(s.meta, ok) if g])
        mean = V.mean(axis=1)
        say(f"### wyprzedzenie k={k}: n={int(ok.sum())}")
        row = []
        for lo, hi, lab in ((1, 3, "1-3 cm"), (3, 6, "3-6 cm"), (6, 10, "6-10 cm"), (10, 999, ">10 cm")):
            sel = (mean >= lo) & (mean < hi)
            if sel.sum() >= 15:
                row.append(f"{lab}: n={int(sel.sum())}, śr. prog. {mean[sel].mean():.1f} cm, śr. obs {O[sel].mean():.1f} cm (obs/prog. = {O[sel].mean() / mean[sel].mean():.2f})")
        say("- wg przedziałów prognozy (średnia zespołu): " + " | ".join(row))
        for thr in (5, 10):
            ev = O >= thr
            if ev.sum() < 10:
                continue
            nev = {r: int(ev[rid == r].sum()) for r in np.unique(rid)}
            free = np.array([nev[r] <= 1 for r in rid])
            say(f"- próg {thr} cm (zdarzeń {int(ev.sum())}):")
            for g in (1.0, 0.8, 0.6, 0.5):
                for pthr in (0.3, 0.5):
                    p = (V * g >= thr).mean(axis=1)
                    h, fa, m_, pod, far, csi = contingency(p, ev, pthr)
                    ff = int(((p >= pthr) & ~ev & free).sum())
                    say(f"    g={g:.1f}, alarm przy P>={int(pthr * 100)}%: POD {pod:.2f}, FAR {far:.2f}, CSI {csi:.2f}, fałszywych {fa}; na dobach bez zdarzenia {ff / max(int(free.sum()), 1) * 1000:.1f} na 1000 stacjodni")
    say()


# sigma całkowita (RMSE po korekcie liniowej) z sekcji 7 raportu dla wyprzedzenia k=0/1/2 — te same stałe trafią do generatora
COLD_SIGMA_TOTAL_BY_K = {0: 2.35, 1: 2.59, 2: 2.78}


def section_cold_spread(runs, obs):
    """Mróz: wygładzenie rozrzutu DOKŁADNIE jak w planowanym kodzie produkcyjnym. P(T <= próg) = średnia po członkach z
    Phi((próg - (T_czł + korekta)) / s), gdzie s = w * sqrt(max(sigma_całk(k)^2 - rozrzut_zespołu^2, 0.25)).
    Oceniamy kilka progów P (produkcyjna macierz zaczyna się od ok. 10%) i kilka wag w (0 = bez wygładzenia = produkcja)."""
    say("## 11. Mróz — test wygładzenia rozrzutu odtwarzający planowaną zmianę produkcyjną (stałe sigma wg wyprzedzenia)")
    say(f"Sigma całkowita wg wyprzedzenia: {COLD_SIGMA_TOTAL_BY_K}. Środek = temperatura członka + korekta produkcyjna {COLD_AIR_BIAS_PROD:+.1f} C. "
        "w = waga wygładzenia (0 = obecna produkcja). Doby bez zdarzenia = zdarzenie (TMIN <= próg) na <= 1 stacji. "
        "'fałsz. bez zdarz.' = fałszywe alarmy na 1000 stacjodni z tych dób.")
    from math import erf
    ncdf = np.vectorize(lambda z: 0.5 * (1.0 + erf(z / 2 ** 0.5)))
    def extra(A, w):
        te = A["t_end"][:, :, w]; tm = A["t_mid"][:, :, w]
        return {"air": np.minimum(np.nanmin(te, axis=2), np.nanmin(tm, axis=2))}
    weights = (0.0, 0.5, 0.75, 1.0)
    pthrs = (0.1, 0.2, 0.3, 0.5)
    for k in (0, 1, 2):
        s = build_sample(runs, obs, k, 0, extra)
        if s.n == 0:
            continue
        TM = s.obs("TMIN"); ok = np.isfinite(TM)
        air = s.M["air"][ok]; TM = TM[ok]; meta = [m for m, g in zip(s.meta, ok) if g]
        runs_id = np.array([m[0].toordinal() for m in meta])
        sd = air.std(axis=1)
        centre = air + COLD_AIR_BIAS_PROD
        base_s = np.sqrt(np.maximum(COLD_SIGMA_TOTAL_BY_K[k] ** 2 - sd ** 2, 0.25))
        say(f"### wyprzedzenie k={k}: n={len(TM)}, sigma całkowita {COLD_SIGMA_TOTAL_BY_K[k]:.2f} C, średni dodany rozrzut {base_s.mean():.2f} C")
        for thr in (-5, -10, -15):
            ev = TM <= thr
            if ev.sum() < 5:
                continue
            nev = {r: int(ev[runs_id == r].sum()) for r in np.unique(runs_id)}
            free = np.array([nev[r] <= 1 for r in runs_id]); nfree = max(int(free.sum()), 1)
            say(f"- próg {thr} C (zdarzeń {int(ev.sum())}):")
            for wgt in weights:
                if wgt == 0.0:
                    p = (centre <= thr).mean(axis=1)
                else:
                    p = ncdf((thr - centre) / (wgt * base_s)[:, None]).mean(axis=1)
                parts = []
                for pt in pthrs:
                    h, fa, m_, pod, far, csi = contingency(p, ev, pt)
                    ff = int(((p >= pt) & ~ev & free).sum())
                    parts.append(f"P>={int(pt * 100)}%: POD {pod:.2f} FAR {far:.2f} CSI {csi:.2f} fałsz. bez zdarz. {ff / nfree * 1000:.1f}")
                say(f"    w={wgt:.2f}{' (produkcja)' if wgt == 0.0 else ''}: " + " | ".join(parts))
    say()



# ----------------------------------------------------------------------------- oceny probabilistyczne (do porównania modeli)
def crps_ens(X, y):
    """CRPS zespołu: X [próbki, członkowie], y [próbki]. CRPS = E|X-y| - 0.5 E|X-X'| (dokładnie, przez sortowanie)."""
    X = np.sort(X, axis=1)
    n = X.shape[1]
    w = 2 * np.arange(1, n + 1) - n - 1
    return np.mean(np.abs(X - y[:, None]), axis=1) - (X * w).sum(axis=1) / (n * n)


def section_scores(runs, obs, store):
    """Oceny, które NIE zależą od wyboru progu alarmu (mniej szumu niż POD/CSI na kilkudziesięciu zdarzeniach):
    CRPS (ciągłe: TMIN, opad doby) i Brier (zdarzenia). Niższe = lepiej. Wektory per stacjodzień trafiają do `store`
    (--scores-out), a compare_models.py porównuje modele PARAMI na tych samych stacjodniach z przedziałem ufności."""
    say("## 8. Oceny probabilistyczne (CRPS, Brier — niższe = lepiej; wektory zapisane do porównania modeli parami)")
    def cold_extra(A, w):
        return {"v": np.minimum(np.nanmin(A["t_end"][:, :, w], axis=2), np.nanmin(A["t_mid"][:, :, w], axis=2))}
    def precip_extra(A, w):
        return {"v": A["apcp"][:, :, w].sum(axis=2)}
    def snow_extra(A, w):
        ap = A["apcp"][:, :, w]; te = A["t_end"][:, :, w]; tm = A["t_mid"][:, :, w]
        return {"v": (ap * clipf((3.0 - np.minimum(te, tm)) / 2.0)).sum(axis=2)}
    def put(name, s_, ok, vals):
        keys = np.array([f"{m[0]}|{m[2]}" for m in s_.meta])[ok]
        store[name + "__keys"] = keys.astype("S")                 # bajty zamiast unicode: 4x mniejszy plik
        store[name + "__vals"] = np.asarray(vals, dtype=np.float32)
        say(f"- {name}: n={len(vals)}, średnia {np.mean(vals):.4f}")
    for k in (0, 1, 2):
        say(f"### wyprzedzenie k={k}")
        s0 = build_sample(runs, obs, k, 0, cold_extra)
        if s0.n:
            TM = s0.obs("TMIN"); ok = np.isfinite(TM) & np.isfinite(s0.M["v"]).all(axis=1)
            X = s0.M["v"][ok]; y = TM[ok]
            put(f"tmin_crps_k{k}", s0, ok, crps_ens(X, y))
            for thr in (-5, -10, -15):
                if (y <= thr).sum() >= 5:
                    put(f"tmin_le{abs(thr)}_brier_k{k}", s0, ok, ((X <= thr).mean(axis=1) - (y <= thr)) ** 2)
        s1 = build_sample(runs, obs, k, 6, precip_extra)
        if s1.n:
            O = s1.obs("SMDB"); ok = np.isfinite(O) & np.isfinite(s1.M["v"]).all(axis=1)
            X = s1.M["v"][ok]; y = O[ok]
            put(f"precip_crps_k{k}", s1, ok, crps_ens(X, y))
            for thr in (1, 5, 10):
                if (y >= thr).sum() >= 5:
                    put(f"precip_ge{thr}_brier_k{k}", s1, ok, ((X >= thr).mean(axis=1) - (y >= thr)) ** 2)
        s2 = build_sample(runs, obs, k, 6, snow_extra)
        if s2.n:
            O = s2.obs("SMDB"); ok = np.isfinite(O) & np.isfinite(s2.M["v"]).all(axis=1)
            y = np.where(s2.roop() == "S", O, 0.0)[ok]; X = s2.M["v"][ok]
            for thr in (1, 3):
                if (y >= thr).sum() >= 5:
                    put(f"snow_ge{thr}_brier_k{k}", s2, ok, ((X >= thr).mean(axis=1) - (y >= thr)) ** 2)
    say()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hindcast", default="hindcast_v2")
    ap.add_argument("--obs", default=None)
    ap.add_argument("--out", default="reports/calibration_report.md")
    ap.add_argument("--min-members", type=int, default=30,
                    help="minimalna liczba członków w przebiegu (GEFS: 30; IFS ENS: 50)")
    ap.add_argument("--common-with", default=None,
                    help="katalog drugiego hindcastu: liczy tylko przebiegi (daty), które są w obu — porównanie GEFS vs IFS na tych samych dniach")
    ap.add_argument("--pool-with", default=None,
                    help="katalog drugiego hindcastu (np. hindcast_ifs): łączy członków obu modeli w jeden zespół i liczy raport "
                         "dla zespołu połączonego (tylko przebiegi wspólne)")
    ap.add_argument("--pool-weights", default="5:3",
                    help="powtórzenia członków A:B przy łączeniu; 5:3 = ~równa waga modeli przy 30 (GEFS) i 51 (IFS) członkach, 1:1 = zwykłe złączenie")
    ap.add_argument("--pool-min-members", type=int, default=50, help="minimalna liczba członków drugiego modelu")
    ap.add_argument("--common-min-members", type=int, default=None,
                    help="minimalna liczba członków w drugim folderze przy --common-with (domyślnie 50 gdy nazwa folderu zawiera 'ifs', inaczej 30) — "
                         "dzięki temu raporty GEFS, IFS i zespołu liczą dokładnie te same daty")
    ap.add_argument("--scores-out", default=None,
                    help="plik .npz z wektorami ocen per stacjodzień (sekcja 8) do porównania modeli parami (compare_models.py)")
    ap.add_argument("--skip", default="",
                    help="sekcje do pominięcia, po przecinku: ice, blizzard (np. dla IFS, który nie ma CFRZR/VIS)")
    a = ap.parse_args()
    skip = {x.strip() for x in a.skip.split(",") if x.strip()}
    SKIP.update(skip)
    here = os.path.dirname(os.path.abspath(__file__))
    hd = a.hindcast if os.path.isabs(a.hindcast) else os.path.join(here, a.hindcast)
    obs_path = a.obs
    if obs_path is None:
        found = sorted(glob.glob(os.path.join(here, "obs", "imgw_dobowe_*.csv.gz")), key=os.path.getmtime)
        if not found:
            sys.exit("Brak obserwacji: podaj --obs albo uruchom fetch_obs_imgw.py")
        obs_path = found[-1]
    elif not os.path.isabs(obs_path):
        obs_path = os.path.join(here, obs_path)
    runs = load_runs(hd, a.min_members)
    if not runs:
        sys.exit(f"Brak pełnych przebiegów 00Z (>= {a.min_members} członków) w {hd}")
    if a.common_with:
        other_dir = a.common_with if os.path.isabs(a.common_with) else os.path.join(here, a.common_with)
        cmin = a.common_min_members if a.common_min_members is not None else (50 if "ifs" in os.path.basename(other_dir.rstrip("/")).lower() else 30)
        other = load_runs(other_dir, cmin)
        runs = {k: v for k, v in runs.items() if k in other}
        if not runs:
            sys.exit(f"Brak wspólnych przebiegów z {other_dir}")
    pool_info = None
    if a.pool_with:
        pdir = a.pool_with if os.path.isabs(a.pool_with) else os.path.join(here, a.pool_with)
        runs_b = load_runs(pdir, a.pool_min_members)
        wa, wb = (int(x) for x in a.pool_weights.split(":"))
        runs = pool_runs(runs, runs_b, wa, wb)
        if not runs:
            sys.exit(f"Brak wspólnych kompletnych przebiegów z {pdir}")
        n_any = next(iter(runs.values()))["arr"]["apcp"].shape[0]
        pool_info = f"zespół POŁĄCZONY: {os.path.basename(hd)} x{wa} + {os.path.basename(pdir)} x{wb} = {n_any} członków (waga modeli ~ {wa}*A : {wb}*B)"
    global MODEL, NO_WIND
    if a.pool_with:
        MODEL, NO_WIND = "GEFS+IFS", True
    elif "ifs" in os.path.basename(hd.rstrip("/")).lower():
        MODEL, NO_WIND = "IFS ENS", True
    n_members = sorted({len(json.load(gzip.open(p, "rt", encoding="utf-8"))["members"])
                        for p in sorted(glob.glob(os.path.join(hd, "*.json.gz")))[:3]})
    obs = load_obs(obs_path)
    say(f"# Kalibracja SWWF na obserwacjach IMGW — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    say(f"hindcast: {hd} ({len(runs)} przebiegów 00Z z {'/'.join(map(str, n_members))} członkami, okien na przebieg: {sorted({r['nwin'] for r in runs.values()})}); obs: {os.path.basename(obs_path)} ({len(obs)} stacjodni)")
    if pool_info:
        say(pool_info)
    say("Próba jest dobrana pod zdarzenia i dni spokojne (nie klimatologiczna) — FAR i odsetki zdarzeń z sekcji 1-5 dotyczą próby mieszanej; "
        "sekcja 6 rozdziela doby bez zdarzenia i ze zdarzeniem.")
    say()
    section_alignment(runs, obs)
    section_precip(runs, obs)
    section_snow(runs, obs)
    section_cold(runs, obs)
    if "ice" not in skip:
        section_ice(runs, obs)
    if "blizzard" not in skip:
        section_blizzard(runs, obs)
    section_quiet(runs, obs)
    section_cold_bias(runs, obs)
    section_snow_cal(runs, obs)
    section_snow_ratio(obs)
    section_snow_cm(runs, obs)
    section_cold_spread(runs, obs)
    store = {}
    section_scores(runs, obs, store)
    if a.scores_out and store:
        sp = a.scores_out if os.path.isabs(a.scores_out) else os.path.join(here, a.scores_out)
        os.makedirs(os.path.dirname(sp), exist_ok=True)
        np.savez_compressed(sp, **store)
        print(f"Zapisano wektory ocen: {sp}")
    out = a.out if os.path.isabs(a.out) else os.path.join(here, a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT) + "\n")
    print(f"\nZapisano raport: {out}")


if __name__ == "__main__":
    main()
