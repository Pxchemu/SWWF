"""
Jednorazowa sonda: jak daleko wstecz ECMWF trzyma przebiegi IFS ENS (0.25 st.) w replice AWS S3 / portalu,
i jakie zmienne zawieraja starsze przebiegi (2t, tp, sf, mn2t3, mx2t3, 10fg, mucape, ptype, sd, 10u, 10v).
Jesli historia istnieje, mozna zrobic hindcast IFS ENS na tych samych dniach co GEFS (kalibracja na prawdziwych danych).

Uzycie:  python probe_ecmwf_history.py            (daty: 1. i 15. dzien miesiaca od 2024-01, przebiegi 00Z i 12Z)
         python probe_ecmwf_history.py 2025-01-15 (jedna data)
Wynik tylko na ekran (nic nie zapisuje do repo).
"""
import json
import sys
import time
from datetime import date, datetime, timedelta

import requests

BASES = ["https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com", "https://storage.googleapis.com/ecmwf-open-data", "https://data.ecmwf.int/forecasts"]


def label(base):
    return "aws-s3" if "s3" in base else ("google" if "googleapis" in base else "ecmwf.int")
WANT = ["2t", "tp", "sf", "mn2t3", "mx2t3", "10fg", "mucape", "ptype", "sd", "10u", "10v", "msl", "tcwv"]
HEADERS = {"User-Agent": "SWWF-probe/1.0 (research; GitHub Actions)"}


def url(base, d, hh, step=72):
    return f"{base}/{d:%Y%m%d}/{hh:02d}z/ifs/0p25/enfo/{d:%Y%m%d}{hh:02d}0000-{step}h-enfo-ef.index"


def get(u, attempts=4):
    for i in range(attempts):
        try:
            r = requests.get(u, headers=HEADERS, timeout=60)
            if r.status_code in (403, 404):
                return r.status_code, None
            r.raise_for_status()
            return r.status_code, r.content
        except Exception as e:
            err = f"{type(e).__name__}"
            time.sleep(3 * (i + 1))
    return err, None


def main():
    if len(sys.argv) > 1 and sys.argv[1].strip():
        days = [datetime.strptime(x.strip(), "%Y-%m-%d").date() for x in sys.argv[1].split(",") if x.strip()]
    else:
        days, d = [], date(2024, 1, 1)
        today = date.today()
        while d < today:
            days.append(d)
            days.append(d.replace(day=15))
            d = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
    print(f"{'data':<12}{'przebieg':<9}{'zrodlo':<11}{'status':<8} zmienne (brak) / czlonkowie")
    first_ok = None
    for d in days:
        if d >= date.today():
            continue
        for hh in (0, 12):
            line, found = None, False
            for base in BASES:
                st, raw = get(url(base, d, hh))
                if raw is not None:
                    found = True
                    members = set()
                    params = set()
                    for ln in raw.decode("utf-8").splitlines():
                        if not ln.strip():
                            continue
                        j = json.loads(ln)
                        if j.get("levtype") == "sfc":
                            params.add(j.get("param"))
                            members.add((j.get("type"), j.get("number")))
                    miss = [w for w in WANT if w not in params]
                    print(f"{d}  {hh:02d}Z      {label(base):<11}{st!s:<8} brak: {miss or '-'} | czlonkow: {len(members)}", flush=True)
                    first_ok = first_ok or (d, hh)
                    continue
                line = f"{d}  {hh:02d}Z      {label(base):<11}{st!s:<8}"
                print(line, flush=True)
            if not found:
                pass
    print("\nNajstarszy dostepny przebieg z listy:", first_ok)


if __name__ == "__main__":
    main()
