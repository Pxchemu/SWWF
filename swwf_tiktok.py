#!/usr/bin/env python3
"""SWWF -> slideshow na TikTok (pionowe 1080x1920, angielski), osobno dla kazdego hazardu.

Zestaw na hazard:
  slide_1_day1.png, slide_2_day2.png, slide_3_day3.png - mapa prognozy na dobe (tylko doby, w ktorych hazard wystepuje)
  slide_N_how.png                                       - jak liczymy ten hazard (macierz prawdopodobienstwo x intensywnosc)
  caption.txt                                           - opis do wklejenia pod post (po angielsku, z disclaimerem)

Uklad: grafika wypelnia caly ekran 9:16 (tlo na calosc), ale cala tresc lezy w "strefie bezpiecznej" - z dala od
gornego paska TikToka (wyszukiwarka/status) i dolnego (opis, nazwa konta, muzyka) oraz od ikon po prawej.

Uzycie:
  python swwf_tiktok.py --swwf swwf.json --out-dir tiktok
  python swwf_tiktok.py --hazards snow_24h_cm,cold_min_t2m_c --guides   (--guides rysuje obrys strefy bezpiecznej - tylko do podgladu)
Zmienne: TT_HAZARDS (domyslna lista), TT_MIN_LEVEL (domyslnie 1 = SLIGHT), TT_LOGO (domyslnie swwf_logo.png),
         TG_FONT_DIR (folder z IBMPlexSans-*.ttf, jak w skrypcie Telegrama).
"""
import argparse
import json
import math
import os
import textwrap
import urllib.request
from datetime import datetime

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyBboxPatch, PathPatch, Rectangle  # noqa: E402
from matplotlib.path import Path  # noqa: E402
from shapely.geometry import Point, shape  # noqa: E402

import swwf_telegram as st  # noqa: E402  (mapa, miasta, czcionki)

W, H = 1080, 1920
# strefa bezpieczna: gora ~190 px (pasek TikToka), dol od ~1440 px (opis, konto, muzyka), boki 90 px (ikony po prawej)
SX0, SX1, SY0, SY1 = 90, 990, 190, 1440
SW = SX1 - SX0
PT = 0.72                       # px -> pt przy dpi=100

BG = "#0b0910"
CARD = "#15121f"
LINE = "#2f2b44"
TXT = "#f4f3f8"
SUB = "#b9b5cb"
FOOT = "#8e8aa3"

HAZ = {
    "snow_24h_cm": dict(title="SNOW", sub="Fresh snowfall in 24 h", unit="Fresh snow in 24 h (cm)", pre="≥", suf="",
                        word="snowfall"),
    "cold_min_t2m_c": dict(title="COLD", sub="Lowest air temperature in 24 h", unit="Lowest air temperature (°C)",
                           pre="≤", suf="", word="frost"),
    "snow_squalls": dict(title="SNOW SQUALLS", sub="Sudden, intense snow showers", unit="Peak instability, CAPE (J/kg)",
                         pre="≥", suf="", word="squalls"),
    "precip_24h_mm": dict(title="PRECIPITATION", sub="Total precipitation in 24 h", unit="Precipitation in 24 h (mm)",
                          pre="≥", suf="", word="precipitation"),
    "general_winter_risk": dict(title="WINTER RISK", sub="Combined winter-weather level", unit="", pre="", suf="",
                                word="winter weather"),
}
LEVELS_EN = ["NONE", "SLIGHT", "ENHANCED", "MODERATE", "HIGH", "EXTREME"]
LEVEL_WORD = ["no hazard", "low", "elevated", "significant", "high", "extreme"]
WD = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
WD_FULL = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MON = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
MON_FULL = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# miasta na mapie (mniej niz w Telegramie - ekran telefonu jest maly)
CITIES_TT = {"Warszawa", "Kraków", "Gdańsk", "Wrocław", "Poznań", "Szczecin", "Lublin", "Białystok", "Łódź",
             "Katowice", "Berlin", "Hamburg", "Kolonia", "Frankfurt", "Monachium", "Drezno", "Praga", "Brno",
             "Bratysława", "Wiedeń", "Hanower", "Rzeszów"}

COUNTRY_NAMES = {"DEU": "Germany", "POL": "Poland", "CZE": "Czechia", "SVK": "Slovakia"}


# ----------------------------------------------------------------------------- dane pomocnicze
def load_geo():
    """(lista geometrii tla, {iso3: geometria}) z jednego pobrania Natural Earth 50m."""
    req = urllib.request.Request(st.COUNTRIES_URL, headers={"User-Agent": "meteopanel-swwf"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode())
    bg, named = [], {}
    for f in data["features"]:
        try:
            g = shape(f["geometry"])
        except Exception:
            continue
        minx, miny, maxx, maxy = g.bounds
        if maxx < st.LON_MIN - 2 or minx > st.LON_MAX + 2 or maxy < st.LAT_MIN - 2 or miny > st.LAT_MAX + 2:
            continue
        bg.append(g)
        p = f["properties"]
        iso = p.get("ADM0_A3") or p.get("ISO_A3") or ""
        if iso in COUNTRY_NAMES:
            named[iso] = g
    return bg, named


def tz_label(dt: datetime) -> str:
    off = dt.utcoffset().total_seconds() / 3600 if dt.utcoffset() else 1
    return "CEST" if off >= 2 else "CET"


def fmt_amount(hkey: str, v: float) -> str:
    if hkey == "snow_24h_cm":
        v = max(v, 1.0)
        v = round(v) if v < 10 else int(5 * round(v / 5))
        return f"{v} cm"
    if hkey == "cold_min_t2m_c":
        return f"{round(v)} °C".replace("-", "−")
    if hkey == "precip_24h_mm":
        v = round(v) if v < 20 else int(5 * round(v / 5))
        return f"{v} mm"
    if hkey == "snow_squalls":
        return f"{int(10 * round(v / 10))} J/kg"
    return ""


def models_text(swwf: dict) -> str:
    info = (swwf.get("ensemble_info") or {}).get("models") or []
    n = swwf.get("members_used") or sum(m.get("members", 0) for m in info) or 30
    if info:
        parts = [f"{m['members']} {m['provider'].split('/')[0]} {m['name']}" for m in info]
        return f"{n} forecast runs ({' + '.join(parts)})"
    return f"{n} forecast runs (NOAA GEFS)"


def attribution(swwf: dict) -> str:
    kind = swwf.get("ensemble") or "GEFS"
    return "Contains modified ECMWF data (CC BY 4.0)" if "IFS" in kind else ""


# ----------------------------------------------------------------------------- tekst opisowy (EN)
class Regions:
    """Opis obszaru slowami: kraje DE/PL/CZ/SK, udzial pol siatki i kierunek (north/south/east/west/central)."""

    def __init__(self, swwf: dict, named: dict):
        lat = np.array(swwf["grid"]["lat"], dtype=float)
        lon = np.array(swwf["grid"]["lon"], dtype=float)
        self.lat, self.lon = lat, lon
        self.cells = {}
        for iso, g in named.items():
            m = np.zeros((len(lat), len(lon)), dtype=bool)
            gp = g.buffer(0)
            minx, miny, maxx, maxy = gp.bounds
            for i, la in enumerate(lat):
                if la < miny - 0.01 or la > maxy + 0.01:
                    continue
                for j, lo in enumerate(lon):
                    if minx - 0.01 <= lo <= maxx + 0.01 and gp.contains(Point(lo, la)):
                        m[i, j] = True
            self.cells[iso] = m

    def describe(self, mask: np.ndarray) -> str:
        """np. 'most of Poland, the southern part of Czechia and isolated areas of Germany and Slovakia'."""
        out, iso_names = [], []
        for iso in ("POL", "DEU", "CZE", "SVK"):
            cm = self.cells.get(iso)
            if cm is None or cm.sum() == 0:
                continue
            hit = mask & cm
            n, tot = int(hit.sum()), int(cm.sum())
            if n < 2:
                continue
            frac = n / tot
            name = COUNTRY_NAMES[iso]
            if frac >= 0.95:
                out.append((frac, f"the whole of {name}"))
            elif frac >= 0.7:
                out.append((frac, f"most of {name}"))
            elif frac < 0.12:
                iso_names.append(name)
            else:
                ii, jj = np.where(cm)
                la0, la1, lo0, lo1 = self.lat[ii].min(), self.lat[ii].max(), self.lon[jj].min(), self.lon[jj].max()
                hi, hj = np.where(hit)
                v = (self.lat[hi].mean() - la0) / max(la1 - la0, 1e-6)
                u = (self.lon[hj].mean() - lo0) / max(lo1 - lo0, 1e-6)
                ns = "northern" if v > 0.62 else ("southern" if v < 0.38 else "")
                ew = "eastern" if u > 0.62 else ("western" if u < 0.38 else "")
                if ns and ew:
                    out.append((frac, f"the {ns[:-4]}-{ew} part of {name}"))
                elif ns or ew:
                    out.append((frac, f"the {ns or ew} part of {name}"))
                else:
                    out.append((frac, f"central {name}"))
        out.sort(key=lambda t: -t[0])
        parts = [t[1] for t in out]
        if iso_names:
            parts.append("isolated areas of " + _join(iso_names))
        return _join(parts)


def _join(parts):
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def day_facts(swwf: dict, day: dict, hkey: str, regions: Regions) -> dict:
    names = swwf["level_names"]
    h = day["hazards"][hkey]
    lg = np.array(h["level_grid"], dtype=float)
    lg = np.nan_to_num(lg, nan=0).astype(int)
    top = int(lg.max()) if lg.size else 0
    mi = np.array(h.get("median_intensity") or [], dtype=float)
    peak = None
    if top > 0 and mi.shape == lg.shape:
        sel = mi[lg == top]
        if sel.size:
            peak = float(np.nanmin(sel)) if hkey == "cold_min_t2m_c" else float(np.nanmax(sel))
    share = float((lg >= 1).sum()) / lg.size
    return dict(top=top, top_name=names[top], grid=lg, peak=peak, share=share)


def day_sentence(swwf: dict, day: dict, hkey: str, regions: Regions) -> str:
    f = day_facts(swwf, day, hkey, regions)
    dt = st.parse_iso(day["valid_from"])
    when = f"{WD_FULL[dt.weekday()]} {dt.day} {MON_FULL[dt.month - 1]}"
    top = f["top"]
    if top == 0:
        return f"{when}: no hazard areas."
    lvl = f["top_name"]
    amount = fmt_amount(hkey, f["peak"]) if f["peak"] is not None else ""
    if hkey == "snow_24h_cm":
        what = f"model-estimated snowfall up to about {amount} locally" if amount else "snowfall possible"
    elif hkey == "cold_min_t2m_c":
        what = f"lows down to about {amount} locally" if amount else "frost possible"
    elif hkey == "precip_24h_mm":
        what = f"up to about {amount} of precipitation locally" if amount else "precipitation possible"
    elif hkey == "snow_squalls":
        what = f"short, intense snow showers (peak CAPE about {amount})" if amount else "snow squalls possible"
    else:
        what = "snow, cold or snow squalls"
    word = LEVEL_WORD[top]
    lvl_txt = lvl if word.upper() == lvl else f"{lvl} ({word})"
    where_top = regions.describe(f["grid"] >= top)
    if top == 1:
        s = f"{when}: only a low-level signal (SLIGHT) — {what}"
        if where_top:
            s += f", over {where_top}"
        return s + "."
    s = f"{when}: highest level {lvl_txt} — {what}."
    if where_top:
        s += f" Peak level in {where_top}."
    if top >= 3:
        w2 = regions.describe(f["grid"] >= 2)
        if w2:
            s += f" ENHANCED or higher: {w2}."
    return s


def build_caption(swwf: dict, hkey: str, regions: Regions, days_used: list) -> str:
    hz = HAZ[hkey]
    emoji = {"snow_24h_cm": "❄️", "cold_min_t2m_c": "🥶", "snow_squalls": "🌨️", "precip_24h_mm": "🌧️",
             "general_winter_risk": "⚠️"}.get(hkey, "❄️")
    lines = [f"{emoji} {hz['title'].title()} forecast for Central Europe (Germany · Poland · Czechia · Slovakia)", ""]
    for i in days_used:
        lines.append("📅 " + day_sentence(swwf, swwf["days"][i], hkey, regions))
    lines += ["",
              f"How it works: {models_text(swwf)} → chance × severity → 5 hazard levels (swipe to the last slide).",
              "",
              "⚠️ Not an official warning. This is our own model-based calculation and it can be wrong, "
              "especially for local snow amounts and at longer lead times. Always follow your national weather "
              "service (IMGW, DWD, ČHMÚ, SHMÚ)."]
    a = attribution(swwf)
    if a:
        lines.append(a + ".")
    lines += ["", f"#weather #{hz['title'].lower().replace(' ', '')} #forecast #europe #poland #germany "
                  f"#czechia #slovakia #winter #meteorology"]
    return "\n".join(lines)


# ----------------------------------------------------------------------------- rysowanie
class Canvas:
    def __init__(self, glow_hex: str, guides: bool = False):
        plt.rcParams["font.family"] = st.setup_fonts()[0]
        self.fig = plt.figure(figsize=(W / 100, H / 100), dpi=100, facecolor=BG)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, W)
        self.ax.set_ylim(H, 0)
        self.ax.axis("off")
        self._background(glow_hex)
        self.guides = guides

    def _background(self, glow_hex):
        ny, nx = 480, 270
        yy, xx = np.mgrid[0:ny, 0:nx]
        X, Y = xx / nx * W, yy / ny * H
        base = np.array(matplotlib.colors.to_rgb(BG))
        img = np.tile(base, (ny, nx, 1))

        def add(col, cx, cy, rad, a):
            d = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) / rad
            w = np.clip(1 - d, 0, 1) ** 2 * a
            c = np.array(matplotlib.colors.to_rgb(col))
            for k in range(3):
                img[:, :, k] = img[:, :, k] * (1 - w) + c[k] * w

        add(glow_hex, 880, 520, 980, 0.30)       # kolor poziomu zagrozenia
        add("#3b6fe0", 120, 1700, 1000, 0.20)    # akcent z logo (niebieski/fiolet)
        add("#7c4dff", 1000, 1850, 800, 0.16)
        self.ax.imshow(img, extent=[0, W, H, 0], interpolation="bilinear", zorder=0, aspect="auto")

    # ---- prymitywy (wspolrzedne w px od lewej-gornej)
    def text(self, x, y, s, size, color=TXT, weight="normal", ha="left", va="center", **kw):
        kw.setdefault("zorder", 10)
        weight = {"bold": "semibold", "semibold": "medium", "medium": "normal"}.get(weight, weight)  # lżejszy krój
        return self.ax.text(x, y, s, fontsize=size * PT, color=color, fontweight=weight, ha=ha, va=va, **kw)

    def spaced(self, x, y, s, size, color, weight="normal", gap=0.0, **kw):
        """Tekst z rozstrzeleniem liter (gap w px) - jak podpis pod SWWF na stronie. Zwraca szerokość w px."""
        r = self.fig.canvas.get_renderer()
        cx = x
        for ch in s:
            t = self.text(cx, y, ch, size, color, weight, **kw)
            if ch == " ":
                w = self.text(0, 0, "a a", size, color, weight, alpha=0).get_window_extent(r).width - \
                    self.text(0, 0, "aa", size, color, weight, alpha=0).get_window_extent(r).width
            else:
                w = t.get_window_extent(r).width
            cx += w + gap
        return cx - x - gap

    def rrect(self, x, y, w, h, r, fc, ec="none", lw=0, alpha=1.0, z=5):
        p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw * PT,
                           alpha=alpha, zorder=z)
        self.ax.add_patch(p)
        return p

    def dot(self, x, y, r, color, z=11):
        self.ax.add_patch(plt.Circle((x, y), r, fc=color, ec="none", zorder=z))

    def finish(self, path):
        if self.guides:
            self.ax.add_patch(Rectangle((SX0, SY0), SW, SY1 - SY0, fc="none", ec="#ff3b6b", lw=2.2, ls=(0, (6, 4)),
                                        zorder=50))
            self.ax.add_patch(Rectangle((0, 0), W, SY0, fc="#ff3b6b", alpha=0.10, ec="none", zorder=49))
            self.ax.add_patch(Rectangle((0, SY1), W, H - SY1, fc="#ff3b6b", alpha=0.10, ec="none", zorder=49))
            self.ax.add_patch(Rectangle((SX1, 880), W - SX1, 700, fc="#ff3b6b", alpha=0.10, ec="none", zorder=49))
            self.text(W / 2, 100, "TikTok top bar", 30, "#ff8aa5", "semibold", ha="center", zorder=51)
            self.text(W / 2, 1700, "TikTok caption / buttons zone", 34, "#ff8aa5", "semibold", ha="center")
        self.fig.savefig(path, facecolor=BG, dpi=100)
        plt.close(self.fig)


def header(cv: Canvas, swwf: dict, logo_path: str, right: str, days=None, cur=0):
    y = SY0 + 46
    x = SX0
    if logo_path and os.path.exists(logo_path):
        try:
            import matplotlib.image as mpimg
            im = mpimg.imread(logo_path)
            cv.ax.imshow(im, extent=[SX0, SX0 + 92, SY0 + 94, SY0 - 2], zorder=9, interpolation="bilinear")
            x = SX0 + 92 + 22
        except Exception as e:
            print(f"Bez logo ({type(e).__name__})")
    t = cv.text(x, SY0 + 36, "SWWF", 64, TXT, "bold")
    tw = t.get_window_extent(cv.fig.canvas.get_renderer()).width
    bw = (tw - 2 * 8) / 3
    for k, col in enumerate(("#9fd3ff", "#2f80e0", "#8b5cf6")):      # trzy kreski pod napisem, jak na stronie
        cv.rrect(x + k * (bw + 8), SY0 + 69, bw, 6, 3, col)
    cv.spaced(x, SY0 + 91, "SEVERE WINTER WEATHER FORECAST", 19, SUB, "medium", gap=2.2)
    if days:
        pw, ph, gap = 104, 52, 10
        px0 = SX1 - len(days) * pw - (len(days) - 1) * gap
        for k, label in enumerate(days):
            on = k == cur
            xx = px0 + k * (pw + gap)
            cv.rrect(xx, y - ph / 2 - 2, pw, ph, 27, TXT if on else CARD, ec=TXT if on else LINE, lw=2)
            cv.text(xx + pw / 2, y - 2, label, 25, BG if on else SUB, "bold", ha="center")
    elif right:
        pw = 20 + len(right) * 17
        cv.rrect(SX1 - pw, y - 28, pw, 56, 28, CARD, ec=LINE, lw=2)
        cv.text(SX1 - pw / 2, y, right, 27, TXT, "bold", ha="center")


def legend(cv: Canvas, swwf: dict, y: float, present: set):
    colors = swwf["level_colors"]
    seg = (SW - 5 * 8) / 6
    for i in range(6):
        x = SX0 + i * (seg + 8)
        on = i in present
        face = CARD if i == 0 else colors[i]
        cv.rrect(x, y, seg, 16, 8, face, ec=LINE if i == 0 else "none", lw=2, alpha=1.0 if on or i == 0 else 0.55)
        cv.text(x + 2, y + 44, LEVELS_EN[i], 23, TXT if on else FOOT, "bold" if on else "medium")


def draw_map_card(cv: Canvas, swwf: dict, day: dict, hkey: str, geo_bg, admin1, x, y, w):
    names, colors = swwf["level_names"], swwf["level_colors"]
    ASP = 1.0 / 0.62
    h = w * ((st.LAT_MAX - st.LAT_MIN) * ASP) / (st.LON_MAX - st.LON_MIN)
    ax = cv.fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])
    ax.set_facecolor("#12101a")
    ax.set_xlim(st.LON_MIN, st.LON_MAX)
    ax.set_ylim(st.LAT_MIN, st.LAT_MAX)
    ax.set_aspect(ASP, adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    r_px = 34
    rx = r_px / w * (st.LON_MAX - st.LON_MIN)
    ry = r_px / h * (st.LAT_MAX - st.LAT_MIN)
    clip = Path(st.rounded_rect_xy(st.LON_MIN, st.LAT_MIN, st.LON_MAX, st.LAT_MAX, rx, ry))
    cp = PathPatch(clip, transform=ax.transData, fc="none", ec="none")
    ax.add_patch(cp)

    def add(p, z):
        p.set_zorder(z)
        p.set_clip_path(cp)
        ax.add_patch(p)

    th = st.THEMES["dark"]
    feats = (day["hazards"][hkey].get("areas") or {}).get("features") or []
    feats = sorted(feats, key=lambda f: st.level_index(f["properties"].get("level", ""), names))
    for g in geo_bg:
        for p in st.geom_patches(g, facecolor=th["land"], edgecolor="none"):
            add(p, 1)
    for g in admin1:
        for p in st.geom_patches(g, facecolor="none", edgecolor=th["admin"], linewidth=0.5):
            add(p, 3.5)
    for f in feats:
        lvl = st.level_index(f["properties"].get("level", ""), names)
        for p in st.geom_patches(shape(f["geometry"]), facecolor=colors[lvl], edgecolor="#f4f3f8", linewidth=1.1,
                                 alpha=0.82):
            add(p, 3)
    for g in geo_bg:
        for p in st.geom_patches(g, facecolor="none", edgecolor=th["border"], linewidth=1.3):
            add(p, 4)
    halo = [pe.withStroke(linewidth=4.2, foreground="#0b0910")]
    for name, lat, lon, dx, dy in st.CITIES:
        if name not in CITIES_TT:
            continue
        ax.plot(lon, lat, "o", color=TXT, markersize=6.5, zorder=5, markeredgecolor="#0b0910", markeredgewidth=1.2,
                clip_path=cp)
        t = ax.text(lon + dx * 1.15, lat + dy * 1.1, st.CITY_EN.get(name, name), fontsize=22 * PT, fontweight="semibold",
                    color=TXT, zorder=6, path_effects=halo)
        t.set_clip_path(cp)
    ax.add_patch(PathPatch(clip, transform=ax.transData, fc="none", ec=LINE, lw=2.2 * PT, zorder=9))
    return h


def forecast_slide(swwf, day, di, hkey, geo_bg, admin1, logo, out, guides, ndays_total, day_labels):
    names, colors = swwf["level_names"], swwf["level_colors"]
    hz = HAZ[hkey]
    f_lg = np.nan_to_num(np.array(day["hazards"][hkey]["level_grid"], dtype=float), nan=0).astype(int)
    top = int(f_lg.max())
    present = {int(v) for v in np.unique(f_lg) if v > 0}
    cv = Canvas(colors[top] if top > 0 else "#3b6fe0", guides)
    header(cv, swwf, logo, "", days=day_labels, cur=di)

    # tytul hazardu
    cv.text(SX0, 358, hz["title"], 118 if len(hz["title"]) <= 8 else 92, TXT, "bold")
    cv.text(SX0, 442, hz["sub"], 32, SUB, "medium")

    # data (najwazniejszy element) + szczyt
    dt0, dt1 = st.parse_iso(day["valid_from"]), st.parse_iso(day["valid_to"])
    by, bh = 480, 168
    cv.rrect(SX0, by, SW, bh, 30, CARD, ec=LINE, lw=2)
    cv.rrect(SX0, by, 14, bh, 7, colors[top] if top > 0 else SUB)
    cv.text(SX0 + 46, by + 60, f"{WD[dt0.weekday()]} {dt0.day} {MON[dt0.month - 1]}", 92, TXT, "bold")
    cv.text(SX0 + 46, by + 126,
            f"{dt0:%H:%M} {WD_FULL[dt0.weekday()]} → {dt1:%H:%M} {WD_FULL[dt1.weekday()]} · {tz_label(dt0)}",
            27, SUB, "medium")
    cx = SX1 - 34
    cv.text(cx, by + 58, "PEAK LEVEL", 25, SUB, "semibold", ha="right")
    nm = names[top] if top > 0 else "NONE"
    cv.text(cx, by + 112, nm, 56 if len(nm) <= 7 else 48, colors[top] if top > 0 else SUB, "bold", ha="right")

    # mapa
    my = by + bh + 26
    mh = draw_map_card(cv, swwf, day, hkey, geo_bg, admin1, SX0, my, SW)
    ly = my + mh + 24
    legend(cv, swwf, ly, present or {0})

    # stopka (disclaimer) - nadal w strefie bezpiecznej
    fy = ly + 82
    cv.text(SX0, fy, "Own model analysis — not an official warning", 27, TXT, "semibold")
    cv.text(SX1, fy, "MeteoPanel", 27, SUB, "bold", ha="right")
    cv.finish(out)
    return fy


def wrap(s, width):
    return textwrap.wrap(s, width=width, break_long_words=False)


def explain_steps(swwf, hkey):
    models = models_text(swwf)
    if hkey == "snow_squalls":
        models = "30 forecast runs (30 NOAA GEFS)"
    n = models.split(" forecast")[0]
    who = models.split("(")[-1].rstrip(")")
    s1 = ("Many forecasts of the same day", f"{n} runs from slightly different starting points: {who}. "
          f"Their spread = uncertainty.")
    s3 = ("Chance × severity = level", "Share of runs reaching each threshold → matrix → level. "
          "A small chance of a big event can still rank high.")
    if hkey == "snow_24h_cm":
        s2 = ("Fresh snow in every ~25 km cell", "Precipitation × share falling as snow (from air temperature) × "
              "snow density (colder = fluffier).")
    elif hkey == "cold_min_t2m_c":
        s2 = ("Coldest air of the day", "Air temperature every 3 hours in each run; we keep the lowest reading "
              "of the 24 h window in every ~25 km cell.")
    elif hkey == "precip_24h_mm":
        s2 = ("24-hour precipitation total", "Each run gives precipitation in 6-hour steps; we add them up to "
              "millimetres of water for the day.")
    elif hkey == "snow_squalls":
        s2 = ("Squall ingredients", "Unstable air (CAPE), mostly frozen precipitation and real precipitation at "
              "the same time. Peak CAPE sets the intensity.")
    else:
        s1 = ("Three hazards, three levels", "Snow, cold and snow squalls are each rated with the chance × severity "
              "matrix, using the whole forecast ensemble.")
        s2 = ("Take the worst", "In every cell, the general winter risk is the highest of those three levels.")
        s3 = ("Bump when they stack", "If two or more hazards reach ENHANCED or above in the same cell, the "
              "general level goes up by one step.")
    return [s1, s2, s3]


def how_slide(swwf, hkey, logo, out, guides, day_labels):
    names, colors = swwf["level_names"], swwf["level_colors"]
    hz = HAZ[hkey]
    info = swwf["hazard_info"].get(hkey)
    cv = Canvas("#7c4dff", guides)
    header(cv, swwf, logo, "HOW IT WORKS")

    cv.text(SX0, 324, "HOW WE CALCULATE", 30, SUB, "semibold")
    cv.text(SX0, 384, hz["title"] if hkey != "general_winter_risk" else "WINTER RISK", 78 if len(hz["title"]) <= 8 else 66,
            TXT, "bold")

    # kroki
    y = 450
    steps = explain_steps(swwf, hkey)
    for i, (title, desc) in enumerate(steps, 1):
        cv.dot(SX0 + 27, y + 25, 27, TXT, z=9)
        cv.text(SX0 + 27, y + 26, str(i), 30, BG, "bold", ha="center")
        cv.text(SX0 + 78, y + 24, title, 34, TXT, "bold")
        lines = wrap(desc, 56)
        for k, ln in enumerate(lines):
            cv.text(SX0 + 78, y + 64 + k * 32, ln, 27, SUB, "normal")
        y += 64 + 32 * len(lines) + 14

    # macierz / lancuch
    matrix = swwf.get("swwf_matrix")
    if info and matrix and hkey != "general_winter_risk":
        bins = info["intensity_bins"][:6]
        pl = swwf["swwf_prob_bin_labels"]
        lo = [p.replace(">", "") for p in pl]
        rows = []
        for i in range(6):
            if i == 0:
                rows.append("<5%")
            elif i == 5:
                rows.append(f"≥{lo[5]}%")
            else:
                rows.append(f"{lo[i]}–{lo[i + 1]}%")
        pre = hz["pre"]

        def fmt_b(v):
            s = f"{v:g}".replace("-", "−")
            return f"{pre}{s}"

        cv.text(SX0, y + 14, hz["unit"], 27, TXT, "semibold")
        y += 40
        lab_w = 190
        gx0 = SX0 + lab_w
        cw = (SX1 - gx0 - 5 * 6) / 6
        rh = 44
        for j, b in enumerate(bins):
            cv.text(gx0 + j * (cw + 6) + cw / 2, y + 16, fmt_b(b), 25, SUB, "bold", ha="center")
        gy = y + 40
        order = [5, 4, 3, 2, 1, 0]
        for r, pi in enumerate(order):
            ry = gy + r * (rh + 6)
            cv.text(gx0 - 14, ry + rh / 2, rows[pi], 25, SUB, "bold", ha="right")
            for j in range(6):
                lv = matrix[pi][j]
                face = CARD if lv == 0 else colors[lv]
                cv.rrect(gx0 + j * (cw + 6), ry, cw, rh, 10, face, ec=LINE if lv == 0 else "none", lw=2, alpha=0.96)
        # opis osi pionowej
        cv.text(SX0 + 14, gy + 3 * (rh + 6) - 3, "SHARE OF RUNS", 22, FOOT, "bold", ha="center", rotation=90)
        # przyklad
        pi, j = 3, 3
        lv = matrix[pi][j]
        rr = order.index(pi)
        ex_x, ex_y = gx0 + j * (cw + 6), gy + rr * (rh + 6)
        cv.ax.add_patch(FancyBboxPatch((ex_x - 3, ex_y - 3), cw + 6, rh + 6, boxstyle="round,pad=0,rounding_size=12",
                                       fc="none", ec=TXT, lw=4.2 * PT, zorder=12))
        ey = gy + 6 * (rh + 6) + 18
        cv.text(SX0, ey, "Example:", 29, TXT, "bold")
        cv.text(SX0 + 140, ey,
                f"{rows[pi]} of runs reach {fmt_b(bins[j])} → ", 29, SUB, "medium")
        cv.text(SX1, ey, names[lv], 31, colors[lv], "bold", ha="right")
        end_y = ey
    else:
        # hazard bez macierzy (ogolne ryzyko): trzy karty "SNOW + COLD + SQUALLS -> MAX"
        y += 6
        cw = (SW - 2 * 70) / 3
        for k, nm in enumerate(["SNOW", "COLD", "SQUALLS"]):
            x0 = SX0 + k * (cw + 70)
            cv.rrect(x0, y, cw, 110, 22, CARD, ec=LINE, lw=2)
            cv.text(x0 + cw / 2, y + 55, nm, 30, TXT, "bold", ha="center")
            if k < 2:
                cv.text(x0 + cw + 35, y + 53, "+", 46, SUB, "bold", ha="center")
        cv.text(SX0 + SW / 2, y + 160, "↓  highest level  (+1 if two reach ENHANCED)", 30, SUB, "semibold", ha="center")
        end_y = y + 160

    # legenda poziomow + disclaimer
    ly = min(end_y + 50, SY1 - 104)
    legend(cv, swwf, ly, set(range(6)))
    fy = ly + 90
    cv.text(SX0, fy, "Own model analysis — not an official warning", 27, TXT, "semibold")
    cv.text(SX1, fy, "MeteoPanel", 27, SUB, "bold", ha="right")
    cv.finish(out)
    return fy


def make_set(swwf, hkey, geo_bg, named, admin1, out_dir, logo, min_level, guides=False):
    names = swwf["level_names"]
    regions = Regions(swwf, named)
    day_labels = [f"DAY {i + 1}" for i in range(len(swwf["days"]))]
    used = []
    for i, day in enumerate(swwf["days"]):
        h = day["hazards"].get(hkey)
        if h and st.max_level(h, names) >= min_level:
            used.append(i)
    if not used:
        print(f"{hkey}: brak zagrożenia >= {names[min_level]} w żadnej dobie — pomijam zestaw.")
        return None
    run = st.parse_iso(swwf["model_run"])
    sub = os.path.join(out_dir, f"{run:%Y-%m-%d_%Hz}_{hkey}")
    os.makedirs(sub, exist_ok=True)
    paths = []
    n = 0
    for i in used:
        n += 1
        p = os.path.join(sub, f"slide_{n}_day{i + 1}.png")
        forecast_slide(swwf, swwf["days"][i], i, hkey, geo_bg, admin1, logo, p, guides, len(swwf["days"]), day_labels)
        paths.append(p)
    n += 1
    p = os.path.join(sub, f"slide_{n}_how.png")
    how_slide(swwf, hkey, logo, p, guides, day_labels)
    paths.append(p)
    cap = build_caption(swwf, hkey, regions, used)
    with open(os.path.join(sub, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(cap)
    print(f"{hkey}: {len(paths)} slajdów -> {sub}")
    return sub, paths, cap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--swwf", default=st.SWWF_JSON)
    ap.add_argument("--out-dir", default="tiktok")
    ap.add_argument("--hazards", default=os.environ.get("TT_HAZARDS", "").strip() or
                    "general_winter_risk,snow_24h_cm,cold_min_t2m_c,precip_24h_mm")
    ap.add_argument("--min-level", type=int, default=int(os.environ.get("TT_MIN_LEVEL", "").strip() or "1"))
    ap.add_argument("--logo", default=os.environ.get("TT_LOGO", "").strip() or "swwf_logo.png")
    ap.add_argument("--guides", action="store_true", help="narysuj strefę bezpieczną (tylko podgląd)")
    args = ap.parse_args()
    with open(args.swwf, encoding="utf-8") as f:
        swwf = json.load(f)
    st.setup_fonts()
    geo_bg, named = load_geo()
    admin1 = st.load_admin1()
    for hkey in [k.strip() for k in args.hazards.split(",") if k.strip()]:
        if hkey not in HAZ or hkey not in swwf["days"][0]["hazards"]:
            print(f"Pomijam nieznany hazard: {hkey}")
            continue
        make_set(swwf, hkey, geo_bg, named, admin1, args.out_dir, args.logo, args.min_level, args.guides)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
