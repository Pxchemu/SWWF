"""
Diagnostyka punktowa SWWF — rozbija prognozę dla JEDNEGO punktu (np. Warszawy) na
poszczególnych członków zespołu GEFS i na składniki obliczeń śniegu i mrozu.

Po co: swwf.json zawiera tylko mediany i prawdopodobieństwa — nie widać z nich, DLACZEGO
śnieg wyszedł np. 10x niższy niż w rzeczywistości. Ten skrypt pokazuje, czy winny jest
sam model (mało opadu u wszystkich członków), przelicznik opad->śnieg (ratio), czy sposób
użycia CPOFP (próbkowany chwilowo na końcu okna 6h, a nie uśredniony po całym oknie).

Użycie:
    python diagnose_point.py "2025-12-30 00:00" 52.23 21.01 Warszawa 2

Argumenty: przebieg (UTC), szerokość, długość, nazwa (do nazwy pliku), liczba dób (1-3).
Wynik: backtest/{RRRR-MM-DD_GGz}/diag_{nazwa}.json oraz .txt (to samo co w logu).

Korzysta z TYCH SAMYCH funkcji co generate_swwf.py (crop_to_region, wind_chill_c,
snow_density_ratio, DAY_WINDOWS), więc diagnozuje dokładnie produkcyjny kod.
"""
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np


def parse_args():
    if len(sys.argv) < 5:
        sys.exit('Użycie: python diagnose_point.py "RRRR-MM-DD GG:00" LAT LON NAZWA [LICZBA_DOB]')
    try:
        run_time = datetime.strptime(sys.argv[1].strip(), "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
    except ValueError:
        sys.exit('Zły format daty. Oczekiwany: "RRRR-MM-DD GG:00" (UTC).')
    lat, lon = float(sys.argv[2]), float(sys.argv[3])
    name = "".join(c for c in sys.argv[4] if c.isalnum() or c in "-_") or "punkt"
    days = int(sys.argv[5]) if len(sys.argv) > 5 else 2
    return run_time, lat, lon, name, max(1, min(3, days))


def point_value(da, lat, lon):
    """Wartość z najbliższego punktu siatki (po przycięciu do regionu, tak jak w produkcji)."""
    return float(da.sel(latitude=lat, longitude=lon % 360, method="nearest").values)


def main():
    run_time, lat, lon, name, n_days = parse_args()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import generate_swwf as gen

    stamp = run_time.strftime("%Y-%m-%d %H:%M")
    day_windows = gen.DAY_WINDOWS[:n_days]

    def fetch(member, fxx, search, var=None):
        h = gen.Herbie(stamp, model="gefs", product="atmos.25", member=member, fxx=fxx,
                       priority=["aws"], verbose=False)
        ds = gen.xarray_with_retry(h, search)
        da = ds[var] if var else ds[list(ds.data_vars)[0]]
        return gen.crop_to_region(da)

    records = []   # jeden rekord = (członek, doba)
    failed = []
    for m in gen.MEMBERS:
        try:
            per_day = []
            for day_info in day_windows:
                precip_total = snow_current = snow_fallback = 0.0
                precip_cpofp_ok = precip_cpofp_missing = 0.0
                t_end_list, cpofp_list, ratio_list, feels_list = [], [], [], []
                for start, end in day_info["windows"]:
                    p = point_value(fetch(m, end, f":APCP:surface:{start}-{end} hour acc", "tp"), lat, lon)
                    t_end = point_value(fetch(m, end, ":TMP:2 m above ground:", "t2m"), lat, lon) - 273.15
                    gust_end = point_value(fetch(m, end, ":GUST:surface:"), lat, lon)
                    cpofp = point_value(fetch(m, end, ":CPOFP:surface:"), lat, lon)
                    mid = start + 3
                    t_mid = point_value(fetch(m, mid, ":TMP:2 m above ground:", "t2m"), lat, lon) - 273.15
                    gust_mid = point_value(fetch(m, mid, ":GUST:surface:"), lat, lon)

                    cpofp_valid = cpofp >= 0
                    ff = min(cpofp / 100.0, 1.0) if cpofp_valid else 0.0
                    ratio = float(gen.snow_density_ratio(gen.xr.DataArray(t_end)))
                    # hipotetyczny wariant: gdy CPOFP brak (brak opadu w CHWILI końca okna), ale w
                    # oknie opad był — frakcja z temperatury (1 poniżej 0C, liniowo do 0 przy +2C)
                    ff_alt = ff if cpofp_valid else float(np.clip((2.0 - t_end) / 2.0, 0.0, 1.0))

                    precip_total += p
                    snow_current += p * ff / 10.0 * ratio
                    snow_fallback += p * ff_alt / 10.0 * ratio
                    if cpofp_valid:
                        precip_cpofp_ok += p
                    else:
                        precip_cpofp_missing += p
                    t_end_list.append(t_end)
                    cpofp_list.append(cpofp)
                    ratio_list.append(ratio)
                    for t, g in ((t_end, gust_end), (t_mid, gust_mid)):
                        feels_list.append(float(gen.wind_chill_c(gen.xr.DataArray(t), gen.xr.DataArray(g))))
                per_day.append({
                    "member": m,
                    "precip_mm": round(precip_total, 2),
                    "snow_cm_current": round(snow_current, 2),
                    "snow_cm_if_cpofp_fallback": round(snow_fallback, 2),
                    "precip_mm_in_windows_cpofp_ok": round(precip_cpofp_ok, 2),
                    "precip_mm_in_windows_cpofp_missing": round(precip_cpofp_missing, 2),
                    "t2m_end_c": [round(t, 1) for t in t_end_list],
                    "cpofp_end": [round(c, 1) for c in cpofp_list],
                    "snow_ratio_used": ratio_list,
                    "min_feels_like_c": round(min(feels_list), 1),
                })
            records.append(per_day)
            print(f"  człon {m:>2}: ok", flush=True)
        except Exception as e:
            failed.append(m)
            print(f"  człon {m:>2}: BŁĄD ({e})", flush=True)

    if not records:
        sys.exit("Żaden człon się nie udał")

    lines = []
    out = lines.append
    out(f"DIAGNOSTYKA PUNKTOWA — {name} ({lat}, {lon}), przebieg {stamp} UTC, "
        f"członków: {len(records)}/{len(gen.MEMBERS)}" + (f", nieudane: {failed}" if failed else ""))
    for d, day_info in enumerate(day_windows):
        rows = [r[d] for r in records]
        out("")
        out(f"=== {day_info['label']} ===")

        def q(key):
            v = np.array([r[key] for r in rows], dtype=float)
            return (f"min {v.min():6.2f} | p10 {np.percentile(v,10):6.2f} | p25 {np.percentile(v,25):6.2f} | "
                    f"mediana {np.median(v):6.2f} | p75 {np.percentile(v,75):6.2f} | "
                    f"p90 {np.percentile(v,90):6.2f} | max {v.max():6.2f}")
        out(f"opad [mm]                       {q('precip_mm')}")
        out(f"śnieg obecna metoda [cm]        {q('snow_cm_current')}")
        out(f"śnieg z fallbackiem CPOFP [cm]  {q('snow_cm_if_cpofp_fallback')}")
        out(f"min odczuwalna [C]              {q('min_feels_like_c')}")
        tot = sum(r["precip_mm"] for r in rows)
        miss = sum(r["precip_mm_in_windows_cpofp_missing"] for r in rows)
        out(f"opad w oknach BEZ ważnego CPOFP (wyzerowany w śniegu): {miss / tot * 100 if tot else 0:.1f}% całego opadu")
        for thr in (1, 5, 10, 20):
            n_cur = sum(r["snow_cm_current"] >= thr for r in rows)
            n_alt = sum(r["snow_cm_if_cpofp_fallback"] >= thr for r in rows)
            out(f"  członków ze śniegiem >= {thr:>2} cm: obecna metoda {n_cur:>2}/{len(rows)} | z fallbackiem {n_alt:>2}/{len(rows)}")
        out("  członek | opad mm | śnieg cm (obecny) | śnieg cm (fallback) | CPOFP na końcach okien | T2m na końcach okien")
        for r in sorted(rows, key=lambda x: -x["precip_mm"]):
            out(f"  {r['member']:>7} | {r['precip_mm']:7.2f} | {r['snow_cm_current']:17.2f} | "
                f"{r['snow_cm_if_cpofp_fallback']:19.2f} | {r['cpofp_end']} | {r['t2m_end_c']}")

    text = "\n".join(lines)
    print("\n" + text)

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backtest", run_time.strftime("%Y-%m-%d_%Hz"))
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"diag_{name}.txt"), "w", encoding="utf-8") as f:
        f.write(text + "\n")
    with open(os.path.join(out_dir, f"diag_{name}.json"), "w", encoding="utf-8") as f:
        json.dump({"run": stamp, "lat": lat, "lon": lon, "name": name, "failed": failed,
                   "days": [[r[d] for r in records] for d in range(len(day_windows))]},
                  f, ensure_ascii=False)
    print(f"\nZapisano: {out_dir}/diag_{name}.txt oraz .json")


if __name__ == "__main__":
    main()
