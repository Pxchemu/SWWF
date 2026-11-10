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
Zestawy powstaja TYLKO z prognozy liczonej zespolem GEFS+IFS (pole "ensemble" w swwf.json); przy samym GEFS nic nie
generujemy (przy --send przychodzi krotka wiadomosc). --any-ensemble wylacza te kontrole (tylko podglad/testy).
Zmienne: TT_HAZARDS (domyslna lista), TT_MIN_LEVEL (domyslnie 1 = SLIGHT), TT_LOGO (domyslnie swwf_logo.png),
         TG_FONT_DIR (folder z IBMPlexSans-*.ttf, jak w skrypcie Telegrama).
"""
import argparse
import json
import math
import os
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
# strefa bezpieczna (widok feedu z opisem): gora ~190 px, dol do ~1500 px (kropki karuzeli ~1540, opis od ~1600),
# prawo do 930 px (kolumna ikon TikToka: serce, komentarze, zakladka, udostepnij zaczyna sie ~950 px), lewo 80 px
SX0, SX1, SY0, SY1 = 80, 930, 190, 1500
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
WD_LONG = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MON = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
MON_FULL = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# miasta na mapie (mniej niz w Telegramie - ekran telefonu jest maly)
CITIES_TT = {"Warszawa", "Kraków", "Gdańsk", "Wrocław", "Poznań", "Szczecin", "Lublin", "Białystok", "Łódź",
             "Katowice", "Berlin", "Hamburg", "Kolonia", "Frankfurt", "Monachium", "Drezno", "Praga", "Brno",
             "Bratysława", "Olsztyn", "Hanower", "Rzeszów"}
# przesuniecia podpisow (w stopniach) tylko dla map TikToka - tam podpisy sa wieksze niz w Telegramie, wiec ciasne pary
# (Katowice/Krakow/Rzeszow, Olsztyn/Gdansk) trzeba rozsunac; brak wpisu = przesuniecie z swwf_telegram.CITIES
TT_OFFSETS = {"Katowice": (-1.45, 0.12), "Kraków": (-0.05, -0.4), "Rzeszów": (0.1, -0.4), "Olsztyn": (0.14, 0.12)}

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
    """Bez liczb (czlonkow, godzin) - nie tlumaczymy szczegolow wlasnego generowania prognozy."""
    return "two leading global ensemble forecast systems (NOAA GEFS + ECMWF IFS)"


def ensemble_ok(swwf: dict) -> bool:
    """Slideshowy robimy tylko z zespolu GEFS+IFS."""
    kind = swwf.get("ensemble") or ""
    return "GEFS" in kind and "IFS" in kind


def attribution(swwf: dict) -> str:
    return "Contains modified ECMWF data (CC BY 4.0)"


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
              f"How it works: we combine {models_text(swwf)} → chance × severity → 5 hazard levels (swipe to the last "
              f"slide).",
              "",
              "⚠️ Not an official warning. This is our own model-based calculation and it can be wrong, "
              "especially for local snow amounts and at longer lead times. Always follow your national weather "
              "service (IMGW, DWD, ČHMÚ, SHMÚ)."]
    lines.append(attribution(swwf) + ".")
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

    def width(self, s, size, weight="normal"):
        """Szerokosc napisu w px (do centrowania, dopasowania i ukladania obok siebie bez nachodzenia)."""
        weight = {"bold": "semibold", "semibold": "medium", "medium": "normal"}.get(weight, weight)
        t = self.ax.text(0, 0, s, fontsize=size * PT, fontweight=weight, alpha=0)
        w = t.get_window_extent(self.fig.canvas.get_renderer()).width
        t.remove()
        return w

    def fit(self, s, size, maxw, weight="normal", minsize=18):
        """Najwiekszy rozmiar <= size, przy ktorym napis miesci sie w maxw px."""
        while size > minsize and self.width(s, size, weight) > maxw:
            size -= 1
        return size

    def ctext(self, x, cy, s, size, color=TXT, weight="normal", ha="center", **kw):
        """Tekst WIELKIMI/cyframi wysrodkowany optycznie w pionie wzgledem cy (kotwica = linia bazowa, bo va=center
        liczy tez miejsce na ogonki liter i napis wyglada na uniesiony)."""
        return self.text(x, cy + 0.35 * size, s, size, color, weight, ha=ha, va="baseline", **kw)

    def wrap_px(self, s, size, maxw, weight="normal"):
        """Zawijanie wg szerokosci w px (a nie liczby znakow) - krój ma zmienna szerokosc liter."""
        lines, cur = [], ""
        for w in s.split(" "):          # tylko zwykla spacja - twarde spacje (\u00a0) trzymaja zwroty razem
            t = (cur + " " + w).strip()
            if cur and self.width(t, size, weight) > maxw:
                lines.append(cur)
                cur = w
            else:
                cur = t
        if cur:
            lines.append(cur)
        return lines

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


def header(cv: Canvas, swwf: dict, logo_path: str, right: str, days=None):
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
    pcy, ph = SY0 + 30, 44                   # mala pigulka w jednej linii z napisem SWWF, wyraznie nad podpisem
    if days:                                  # znacznik wydania prognozy: "ISSUED 8 NOV 2026 · 08:00 CET"
        lab, val = "ISSUED", days
        sz, pad, gap = 18, 18, 9
        w1, w2 = cv.width(lab, sz, "medium"), cv.width(val, sz, "bold")
        pw = pad * 2 + w1 + gap + w2
        if SX1 - pw < x + tw + 40:            # za wąsko obok napisu SWWF -> bez słowa ISSUED
            lab, w1, gap = "", 0, 0
            pw = pad * 2 + w2
        cv.rrect(SX1 - pw, pcy - ph / 2, pw, ph, ph / 2, CARD, ec=LINE, lw=2)
        x0 = SX1 - pw + pad
        if lab:
            cv.ctext(x0, pcy, lab, sz, FOOT, "medium", ha="left")
        cv.ctext(x0 + w1 + gap, pcy, val, sz, TXT, "bold", ha="left")
    elif right:
        sz, pad = 19, 22
        pw = pad * 2 + cv.width(right, sz, "bold")
        cv.rrect(SX1 - pw, pcy - ph / 2, pw, ph, ph / 2, CARD, ec=LINE, lw=2)
        cv.ctext(SX1 - pw / 2, pcy, right, sz, TXT, "bold")


def legend(cv: Canvas, swwf: dict, y: float, present: set):
    colors = swwf["level_colors"]
    seg = (SW - 5 * 8) / 6
    for i in range(6):
        x = SX0 + i * (seg + 8)
        on = i in present
        face = CARD if i == 0 else colors[i]
        cv.rrect(x, y, seg, 16, 8, face, ec=LINE if i == 0 else "none", lw=2, alpha=1.0 if on or i == 0 else 0.55)
        cv.ctext(x + seg / 2, y + 44, LEVELS_EN[i], 21, TXT if on else FOOT, "bold" if on else "medium")


def draw_map_card(cv: Canvas, swwf: dict, day: dict, hkey: str, geo_bg, admin1, x, y, w):
    names, colors = swwf["level_names"], swwf["level_colors"]
    ASP = 1.0 / 0.62
    h = w * ((st.LAT_MAX - st.LAT_MIN) * ASP) / (st.LON_MAX - st.LON_MIN)
    ax = cv.fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])
    ax.set_facecolor("none")                      # tlo rysujemy jako zaokraglony ksztalt (patrz nizej), nie prostokat osi
    ax.patch.set_alpha(0)
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
    ax.add_patch(PathPatch(clip, transform=ax.transData, fc="#12101a", ec="none", zorder=0.5))

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
        if name in TT_OFFSETS:
            dx, dy = TT_OFFSETS[name]
        ax.plot(lon, lat, "o", color=TXT, markersize=6.5, zorder=5, markeredgecolor="#0b0910", markeredgewidth=1.2,
                clip_path=cp)
        t = ax.text(lon + dx * 1.15, lat + dy * 1.1, st.CITY_EN.get(name, name), fontsize=22 * PT, fontweight="semibold",
                    color=TXT, zorder=6, path_effects=halo)
        t.set_clip_path(cp)
    ax.add_patch(PathPatch(clip, transform=ax.transData, fc="none", ec=LINE, lw=2.2 * PT, zorder=9, clip_on=False))
    return h


def issued_label(swwf: dict) -> str:
    """Data i godzina wygenerowania prognozy (godzina zaokraglona w dol), np. '8 NOV 2026 · 08:00 CET'."""
    dt = st.parse_iso(swwf.get("issued") or swwf["model_run"])
    return f"{dt.day} {MON[dt.month - 1]} {dt.year} · {dt:%H}:00 {tz_label(dt)}"


def forecast_slide(swwf, day, di, hkey, geo_bg, admin1, logo, out, guides):
    names, colors = swwf["level_names"], swwf["level_colors"]
    hz = HAZ[hkey]
    f_lg = np.nan_to_num(np.array(day["hazards"][hkey]["level_grid"], dtype=float), nan=0).astype(int)
    top = int(f_lg.max())
    present = {int(v) for v in np.unique(f_lg) if v > 0}
    cv = Canvas(colors[top] if top > 0 else "#3b6fe0", guides)
    header(cv, swwf, logo, "", days=issued_label(swwf))

    # tytul hazardu
    cv.text(SX0, 412, hz["title"], 108 if len(hz["title"]) <= 8 else 84, TXT, "bold")
    cv.text(SX0, 502, hz["sub"], 32, SUB, "medium")

    # data waznosci (najwazniejszy element, ale spokojniejszy rozmiar) + szczyt - obie grupy wysrodkowane w pionie
    dt0, dt1 = st.parse_iso(day["valid_from"]), st.parse_iso(day["valid_to"])
    by, bh = 548, 152
    mid = by + bh / 2
    cv.rrect(SX0, by, SW, bh, 30, CARD, ec=LINE, lw=2)
    cv.rrect(SX0, by, 14, bh, 7, colors[top] if top > 0 else SUB)
    nm = names[top] if top > 0 else "NONE"
    nsz = 52 if len(nm) <= 7 else 44
    rx = SX1 - 42
    peak_w = max(cv.width("PEAK LEVEL", 23, "semibold"), cv.width(nm, nsz, "bold"))
    lx = SX0 + 14 + 36
    date_s = f"{WD_LONG[dt0.weekday()]} {dt0.day} {MON[dt0.month - 1]}"
    dsz = cv.fit(date_s, 62, (rx - peak_w) - lx - 36, "bold", minsize=40)
    cv.ctext(lx, mid - 21, date_s, dsz, TXT, "bold", ha="left")
    cv.ctext(lx, mid + 30,
             f"{dt0:%H:%M} {WD_FULL[dt0.weekday()]} → {dt1:%H:%M} {WD_FULL[dt1.weekday()]} · {tz_label(dt0)}",
             25, SUB, "medium", ha="left")
    cv.ctext(rx, mid - 28, "PEAK LEVEL", 23, SUB, "semibold", ha="right")
    cv.ctext(rx, mid + 20, nm, nsz, colors[top] if top > 0 else SUB, "bold", ha="right")

    # mapa
    my = by + bh + 28
    mh = draw_map_card(cv, swwf, day, hkey, geo_bg, admin1, SX0, my, SW)
    ly = my + mh + 30
    legend(cv, swwf, ly, present or {0})

    # stopka (disclaimer) - mala, nadal w strefie bezpiecznej
    fy = ly + 92
    footer(cv, fy)
    cv.finish(out)
    return fy


def footer(cv, fy):
    cv.ctext(SX0, fy, "Own model analysis — not an official warning", 21, FOOT, "medium", ha="left")
    cv.ctext(SX1, fy, "MeteoPanel", 21, SUB, "bold", ha="right")


def explain_steps(swwf, hkey):
    """Z czego korzystamy - bez liczb (czlonkow, godzin, rozdzielczosci), zeby nie tlumaczyc szczegolow generowania."""
    if hkey == "snow_squalls":
        s1 = ("Many forecasts of the same day", "We use NOAA's GEFS ensemble: many runs from slightly different "
              "starting points. How much they disagree = uncertainty.")
    else:
        s1 = ("Many forecasts of the same day", "We combine two leading global ensemble forecast systems, NOAA GEFS "
              "and ECMWF IFS. How much their runs disagree = uncertainty.")
    s3 = ("Chance × severity = level", "Share of runs reaching each threshold\u00a0→\u00a0matrix\u00a0→\u00a0level. "
          "A small chance of a big event can still rank high.")
    if hkey == "snow_24h_cm":
        s2 = ("Fresh snow in every grid cell", "We estimate snowfall from forecast precipitation and air temperature.")
    elif hkey == "cold_min_t2m_c":
        s2 = ("Coldest air of the day", "We keep the lowest forecast air temperature of the 24-hour window in every "
              "grid cell.")
    elif hkey == "precip_24h_mm":
        s2 = ("24-hour precipitation total", "We add up forecast precipitation to millimetres of water for the day.")
    elif hkey == "snow_squalls":
        s2 = ("Squall ingredients", "Unstable air, mostly frozen precipitation and real precipitation at the same "
              "time. The instability sets the intensity.")
    else:
        s1 = ("Three hazards, three levels", "Snow, cold and snow squalls are each rated with the chance\u00a0×\u00a0severity "
              "matrix.")
        s2 = ("Take the worst", "In every cell, the general winter risk is the highest of those three levels.")
        s3 = ("Bump when they stack", "If two or more hazards reach ENHANCED or above in the same cell, the "
              "general level goes up by one step.")
    return [s1, s2, s3]


def how_slide(swwf, hkey, logo, out, guides):
    names, colors = swwf["level_names"], swwf["level_colors"]
    hz = HAZ[hkey]
    info = swwf["hazard_info"].get(hkey)
    cv = Canvas("#7c4dff", guides)
    header(cv, swwf, logo, "HOW IT WORKS")

    cv.text(SX0, 356, "HOW WE CALCULATE", 30, SUB, "semibold")
    cv.text(SX0, 436, hz["title"] if hkey != "general_winter_risk" else "WINTER RISK", 74 if len(hz["title"]) <= 8 else 60,
            TXT, "bold")

    # kroki
    y = 496
    steps = explain_steps(swwf, hkey)
    for i, (title, desc) in enumerate(steps, 1):
        cv.dot(SX0 + 27, y + 25, 27, TXT, z=9)
        cv.text(SX0 + 27, y + 26, str(i), 30, BG, "bold", ha="center")
        cv.text(SX0 + 78, y + 24, title, 34, TXT, "bold")
        lines = cv.wrap_px(desc, 27, SW - 78 - 6)
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
        rh = 38
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
        ey = gy + 6 * (rh + 6) + 26
        lead = "Example:"
        rest = f"{rows[pi]} of runs reach {fmt_b(bins[j])} →"
        lvl_s = names[lv]
        esz = 29
        while esz > 22 and (cv.width(lead, esz, "bold") + 14 + cv.width(rest, esz, "medium") + 18
                            + cv.width(lvl_s, esz + 2, "bold")) > SW:
            esz -= 1
        lw = cv.width(lead, esz, "bold")
        cv.ctext(SX0, ey, lead, esz, TXT, "bold", ha="left")
        cv.ctext(SX0 + lw + 14, ey, rest, esz, SUB, "medium", ha="left")
        cv.ctext(SX1, ey, lvl_s, esz + 2, colors[lv], "bold", ha="right")
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
    ly = min(end_y + 56, SY1 - 104)
    legend(cv, swwf, ly, set(range(6)))
    fy = ly + 92
    footer(cv, fy)
    cv.finish(out)
    return fy


def make_set(swwf, hkey, geo_bg, named, admin1, out_dir, logo, min_level, guides=False):
    names = swwf["level_names"]
    regions = Regions(swwf, named)
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
        forecast_slide(swwf, swwf["days"][i], i, hkey, geo_bg, admin1, logo, p, guides)
        paths.append(p)
    n += 1
    p = os.path.join(sub, f"slide_{n}_how.png")
    how_slide(swwf, hkey, logo, p, guides)
    paths.append(p)
    cap = build_caption(swwf, hkey, regions, used)
    with open(os.path.join(sub, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(cap)
    print(f"{hkey}: {len(paths)} slajdów -> {sub}")
    return sub, paths, cap


def tiktok_chats():
    """Odbiorcy zestawow TikTok: sekret TIKTOK_CHAT_IDS (np. tylko wlasciciel); gdy go nie ma - PIERWSZY numer z
    TG_CHAT_IDS (zwykle wlasciciel). Zestawy sa robocze (do wrzucenia na TikTok), wiec nie ida do wszystkich znajomych."""
    own = [c.strip() for c in os.environ.get("TIKTOK_CHAT_IDS", "").split(",") if c.strip()]
    if own:
        return own
    allc = [c.strip() for c in os.environ.get("TG_CHAT_IDS", "").split(",") if c.strip()]
    return allc[:1]


def send_documents(token, chat_id, paths, caption):
    """Slajdy jako DOKUMENTY (oryginalne PNG 1080x1920 - Telegram nie zmniejsza ich jak zdjec), album po <= 10."""
    ok, err = True, ""
    for n in range(0, len(paths), 10):
        chunk = paths[n:n + 10]
        media, files = [], {}
        for i, pth in enumerate(chunk):
            item = {"type": "document", "media": f"attach://d{i}"}
            if i == len(chunk) - 1 and n == 0 and caption:   # podpis na ostatnim: album sie zwija z podpisem pod spodem
                item["caption"] = caption
            media.append(item)
            files[f"d{i}"] = open(pth, "rb")
        try:
            if len(chunk) == 1:
                o, e = st.tg_call(token, "sendDocument", {"chat_id": chat_id, "caption": caption},
                                  {"document": files["d0"]})
            else:
                o, e = st.tg_call(token, "sendMediaGroup", {"chat_id": chat_id, "media": json.dumps(media)}, files)
        finally:
            for fh in files.values():
                fh.close()
        ok, err = ok and o, err or e
    return ok, err


def send_results(results, nothing_msg):
    token = os.environ.get("TG_TOKEN", "").strip()
    chats = tiktok_chats()
    if not token or not chats:
        print("Brak sekretu TG_TOKEN albo odbiorców (TIKTOK_CHAT_IDS / TG_CHAT_IDS) - nic nie wysyłam.")
        return 1
    all_ok = True
    for chat in chats:
        if not results:
            o, e = st.send_text(token, chat, nothing_msg)
            all_ok = all_ok and o
            print(f"Wiadomość: {'wysłano' if o else 'BŁĄD ' + e}")
            continue
        for hkey, (sub, paths, cap) in results:
            title = HAZ[hkey]["title"].title()
            o1, e1 = send_documents(token, chat, paths, f"🎬 TikTok · {title} · {len(paths)} slides (1080×1920 PNG)")
            o2, e2 = st.send_text(token, chat, cap[:4000])   # opis osobnym komunikatem - latwo skopiowac
            print(f"{hkey}: slajdy {'wysłano' if o1 else 'BŁĄD ' + e1}, opis {'wysłano' if o2 else 'BŁĄD ' + e2}")
            all_ok = all_ok and o1 and o2
    return 0 if all_ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--swwf", default=st.SWWF_JSON)
    ap.add_argument("--out-dir", default="tiktok")
    ap.add_argument("--hazards", default=os.environ.get("TT_HAZARDS", "").strip() or
                    "general_winter_risk,snow_24h_cm,cold_min_t2m_c,precip_24h_mm")
    ap.add_argument("--min-level", type=int, default=int(os.environ.get("TT_MIN_LEVEL", "").strip() or "1"))
    ap.add_argument("--logo", default=os.environ.get("TT_LOGO", "").strip() or "swwf_logo.png")
    ap.add_argument("--guides", action="store_true", help="narysuj strefę bezpieczną (tylko podgląd)")
    ap.add_argument("--any-ensemble", action="store_true",
                    help="nie wymagaj zespolu GEFS+IFS (tylko podglad/testy)")
    ap.add_argument("--send", action="store_true", help="wyślij zestawy na Telegram (TG_TOKEN + TIKTOK_CHAT_IDS)")
    args = ap.parse_args()
    with open(args.swwf, encoding="utf-8") as f:
        swwf = json.load(f)
    if not args.any_ensemble and not ensemble_ok(swwf):
        kind = swwf.get("ensemble") or "brak informacji"
        run = st.parse_iso(swwf["model_run"])
        msg = (f"🎬 TikTok: prognoza z przebiegu {run:%d.%m %H:%M} nie jest liczona zespołem GEFS+IFS (skład: {kind}) "
               f"— slajdów nie generuję.")
        print(msg)
        return send_results([], msg) if args.send else 0
    st.setup_fonts()
    geo_bg, named = load_geo()
    admin1 = st.load_admin1()
    results = []
    for hkey in [k.strip() for k in args.hazards.split(",") if k.strip()]:
        if hkey not in HAZ or hkey not in swwf["days"][0]["hazards"]:
            print(f"Pomijam nieznany hazard: {hkey}")
            continue
        r = make_set(swwf, hkey, geo_bg, named, admin1, args.out_dir, args.logo, args.min_level, args.guides)
        if r:
            results.append((hkey, r))
    if args.send:
        run = st.parse_iso(swwf["model_run"])
        return send_results(results, f"🎬 TikTok: w prognozie z przebiegu {run:%d.%m %H:%M} nie ma zagrożeń "
                                     f"na poziomie {swwf['level_names'][args.min_level]} lub wyższym — nie ma czego publikować.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
