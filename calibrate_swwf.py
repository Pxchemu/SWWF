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


def load_runs(directory):
    runs = {}
    for p in sorted(glob.glob(os.path.join(directory, "*.json.gz"))):
        d = json.load(gzip.open(p, "rt", encoding="utf-8"))
        stamp = datetime.strptime(d["run"], "%Y-%m-%dT%H:00Z")
        if stamp.hour != 0 or len(d["members"]) != 30:
            continue
        arr = {k: np.array(v, dtype=float) for k, v in d["data"].items()}     # [członek, stacja, okno]; None -> nan
        runs[stamp.date()] = dict(arr=arr, stations=d["stations"], nwin=len(d["windows"]))
    return runs


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
        say(f"- średnia obs {O.mean():.2f} mm, GEFS {mean.mean():.2f} mm; korelacja sqrt = {np.corrcoef(np.sqrt(mean), np.sqrt(O))[0,1]:.3f}")
        if wet.sum():
            say(f"- dni mokre: GEFS/obs = {mean[wet].mean() / O[wet].mean():.2f}; obs > max zespołu: {((O > P.max(axis=1)) & wet).sum() / wet.sum() * 100:.1f}% dni mokrych")
        for thr in (1, 5, 10):
            say(f"- P(opad>={thr} mm): " + reliability((P >= thr).mean(axis=1), O >= thr))
    say()


def section_snow(runs, obs):
    have_rh = all("rh_end" in r["arr"] and np.isfinite(r["arr"]["rh_end"]).any() for r in runs.values())
    variants = phase_variants(have_rh)
    say("## 2. Śnieg — metody rozpoznawania fazy opadu (okno 06->06 UTC)")
    say("Zdarzenie obserwowane: opad rodzaju S (śnieg) o sumie >= X mm. Prognoza: P(opad zamarznięty >= X mm) wg metody. "
        "Kolumna 'deszcz->śnieg' = odsetek dni z obserwowanym DESZCZEM >=3 mm, w których metoda daje P(śnieg>=3 mm) >= 30% (fałszywy śnieg).")
    if not have_rh:
        say("(brak pól wilgotności w danych — warianty z mokrym termometrem pominięte; użyj hindcast_v2/)")
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
    have_uv = all("u10_end" in r["arr"] and np.isfinite(r["arr"]["u10_end"]).any() for r in runs.values())
    say("## 3. Mróz — temperatura powietrza vs odczuwalna (okno doby kalendarzowej 00-24 UTC; obserwacja = TMIN powietrza)")
    say("Uwaga: IMGW mierzy tylko temperaturę powietrza, więc odczuwalnej NIE da się zweryfikować wprost; poniżej sprawdzamy, jak daleko od powietrza jest każda wersja i czy 'odczuwalna' nie robi fałszywych alarmów względem realnego mrozu.")
    def extra(A, w):
        te = A["t_end"][:, :, w]; tm = A["t_mid"][:, :, w]
        ge = A["gust_end"][:, :, w]; gm = A["gust_mid"][:, :, w]
        d = {"air": np.minimum(np.nanmin(te, axis=2), np.nanmin(tm, axis=2)),
             "feels_gust": np.minimum(np.nanmin(wind_chill(te, ge), axis=2), np.nanmin(wind_chill(tm, gm), axis=2))}
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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hindcast", default="hindcast_v2")
    ap.add_argument("--obs", default=None)
    ap.add_argument("--out", default="reports/calibration_report.md")
    a = ap.parse_args()
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
    runs = load_runs(hd)
    if not runs:
        sys.exit(f"Brak pełnych przebiegów 00Z w {hd}")
    obs = load_obs(obs_path)
    say(f"# Kalibracja SWWF na obserwacjach IMGW — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    say(f"hindcast: {hd} ({len(runs)} przebiegów 00Z z 30 członkami, okien na przebieg: {sorted({r['nwin'] for r in runs.values()})}); obs: {os.path.basename(obs_path)} ({len(obs)} stacjodni)")
    say("Próba jest dobrana pod zdarzenia i dni spokojne (nie klimatologiczna) — FAR i odsetki zdarzeń z sekcji 1-5 dotyczą próby mieszanej; "
        "sekcja 6 rozdziela doby bez zdarzenia i ze zdarzeniem.")
    say()
    section_alignment(runs, obs)
    section_precip(runs, obs)
    section_snow(runs, obs)
    section_cold(runs, obs)
    section_ice(runs, obs)
    section_blizzard(runs, obs)
    section_quiet(runs, obs)
    section_cold_bias(runs, obs)
    section_snow_cal(runs, obs)
    out = a.out if os.path.isabs(a.out) else os.path.join(here, a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT) + "\n")
    print(f"\nZapisano raport: {out}")


if __name__ == "__main__":
    main()
