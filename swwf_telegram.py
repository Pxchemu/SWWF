#!/usr/bin/env python3
"""SWWF -> Telegram: rysuje mape kazdego dnia prognozy (z legenda z boku) i wysyla album
+ krotkie podsumowanie do odbiorcow.

Wejscie:  swwf.json (wynik generate_swwf.py)
Stan:     telegram_state.json (tylko sygnatura ostatnio wyslanej prognozy - bez sekretow)

Sekrety (tylko GitHub Actions secrets, nigdy w repo ani w logach):
  TG_TOKEN, TG_CHAT_IDS (po przecinku)
Ustawienia (zwykle zmienne srodowiskowe):
  TG_HAZARD     klucz hazardu na mapie, domyslnie general_winter_risk
                (do testow w sezonie bez zimy: precip_24h_mm)
  TG_MIN_LEVEL  najnizszy poziom, ktory liczy sie jako "jest sygnal" przy decyzji,
                czy wysylac (0..5; domyslnie 2 = ENHANCED). Mapy pokazuja wszystkie poziomy.
  TG_THEME      dark (domyslnie) albo light
  TG_FORCE      "1" = wyslij niezaleznie od zmian
  TG_LINK       opcjonalny link do strony, dopisywany na koncu wiadomosci

Uzycie lokalne bez wysylania:
  python swwf_telegram.py --dry-run --out-dir mapy
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.request
from datetime import datetime

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import PathPatch, Rectangle  # noqa: E402
from matplotlib.path import Path  # noqa: E402
from shapely.geometry import shape  # noqa: E402

SWWF_JSON = "swwf.json"
STATE_FILE = "telegram_state.json"
COUNTRIES_URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
                 "master/geojson/ne_50m_admin_0_countries.geojson")

# zakres mapy (Polska + sasiedzi, jak siatka SWWF)
LON_MIN, LON_MAX = 5.5, 24.5
LAT_MIN, LAT_MAX = 47.0, 55.5

ADMIN1_URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
              "master/geojson/ne_10m_admin_1_states_provinces.geojson")
ADMIN1_ISO3 = {"POL", "DEU", "CZE", "SVK", "AUT"}  # wojewodztwa, landy, kraje CZ/SK/AT

# (nazwa, szerokosc, dlugosc, przesuniecie etykiety dx, dy w stopniach)
CITIES = [
    # Polska
    ("Warszawa", 52.23, 21.01, 0.12, 0.07), ("Kraków", 50.06, 19.94, 0.12, 0.07),
    ("Gdańsk", 54.35, 18.65, 0.12, 0.07), ("Wrocław", 51.11, 17.04, 0.12, 0.07),
    ("Poznań", 52.41, 16.93, 0.12, 0.07), ("Szczecin", 53.43, 14.55, 0.12, 0.07),
    ("Lublin", 51.25, 22.57, 0.12, 0.07), ("Białystok", 53.13, 23.16, -1.0, 0.1),
    ("Łódź", 51.76, 19.46, 0.12, 0.07), ("Rzeszów", 50.04, 22.00, 0.12, 0.07),
    ("Katowice", 50.26, 19.02, -1.2, -0.06), ("Olsztyn", 53.78, 20.48, 0.12, 0.07),
    ("Bydgoszcz", 53.12, 18.01, -0.2, 0.12), ("Opole", 50.67, 17.93, -0.9, 0.08),
    ("Zielona Góra", 51.94, 15.51, 0.12, 0.07), ("Kielce", 50.87, 20.63, 0.12, 0.07),
    # Niemcy (zachod i srodek tez)
    ("Berlin", 52.52, 13.40, 0.12, 0.07), ("Hamburg", 53.55, 9.99, 0.12, 0.07),
    ("Brema", 53.08, 8.80, -0.9, 0.1), ("Hanower", 52.37, 9.74, 0.12, 0.07),
    ("Kolonia", 50.94, 6.96, 0.12, 0.07), ("Düsseldorf", 51.23, 6.77, -0.3, 0.12),
    ("Dortmund", 51.51, 7.47, 0.12, 0.07), ("Frankfurt", 50.11, 8.68, 0.12, 0.07),
    ("Stuttgart", 48.78, 9.18, 0.12, 0.07), ("Monachium", 48.14, 11.58, 0.12, 0.07),
    ("Norymberga", 49.45, 11.08, 0.12, 0.07), ("Lipsk", 51.34, 12.37, 0.12, 0.07),
    ("Drezno", 51.05, 13.74, 0.12, 0.07), ("Magdeburg", 52.13, 11.63, 0.12, 0.07),
    ("Saarbrücken", 49.24, 7.00, 0.12, 0.07), ("Fryburg", 47.99, 7.85, 0.12, 0.07),
    # Czechy, Slowacja, Austria
    ("Praga", 50.08, 14.44, 0.12, 0.07), ("Brno", 49.20, 16.61, 0.12, 0.07),
    ("Ostrawa", 49.82, 18.26, -0.2, -0.24), ("Bratysława", 48.15, 17.11, 0.12, -0.22),
    ("Koszyce", 48.72, 21.26, 0.12, 0.07), ("Wiedeń", 48.21, 16.37, -0.95, 0.1),
]

# motywy kolorystyczne (TG_THEME=dark|light, domyslnie dark) — paleta ze strony MeteoPanel
THEMES = {
    "dark": dict(fig="#0b0910", sea="#12101a", land="#1d1a2b", border="#6d6890", admin="#34304a",
                 text="#f4f3f8", sub="#c9c5d6", foot="#9b97ad", city="#f4f3f8", halo="#0b0910",
                 poly_edge="#f4f3f8", frame="#3a3650", none_swatch="#1d1a2b", poly_alpha=0.80,
                 pill_on="#f4f3f8", pill_on_text="#0b0910", pill_off="#14111c"),
    "light": dict(fig="#f4f3f8", sea="#dfe6f2", land="#fbfaff", border="#7a7596", admin="#cfcbe0",
                  text="#14111c", sub="#4a4660", foot="#6b6783", city="#14111c", halo="#ffffff",
                  poly_edge="#14111c", frame="#b9b4cc", none_swatch="#ffffff", poly_alpha=0.78,
                  pill_on="#14111c", pill_on_text="#f4f3f8", pill_off="#ffffff"),
}

HAZARD_TITLES = {
    "general_winter_risk": "Ogólne ryzyko zimowe",
    "snow_24h_cm": "Śnieg",
    "cold_min_t2m_c": "Mróz",
    "snow_squalls": "Szkwały śnieżne",
    "precip_24h_mm": "Opady (suma 24 h)",
}
SIGNAL_HAZARDS = ["snow_24h_cm", "cold_min_t2m_c", "snow_squalls", "general_winter_risk"]
EMOJI = ["⬜", "🟩", "🟨", "🟧", "🟥", "🟪"]
WEEKDAYS = ["pn", "wt", "śr", "czw", "pt", "sob", "niedz"]
LEVEL_DESC = ["brak zagrożenia", "niewielkie", "podwyższone", "umiarkowane", "wysokie", "ekstremalne"]

# --- wersje językowe map (PL domyślnie jak dotąd; EN dla odbiorców angielskojęzycznych)
WEEKDAYS_EN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
CITY_EN = {"Warszawa": "Warsaw", "Kraków": "Krakow", "Gdańsk": "Gdansk", "Wrocław": "Wroclaw", "Poznań": "Poznan",
           "Szczecin": "Szczecin", "Lublin": "Lublin", "Białystok": "Bialystok", "Łódź": "Lodz", "Rzeszów": "Rzeszow",
           "Katowice": "Katowice", "Olsztyn": "Olsztyn", "Bydgoszcz": "Bydgoszcz", "Opole": "Opole",
           "Zielona Góra": "Zielona Gora", "Kielce": "Kielce", "Berlin": "Berlin", "Hamburg": "Hamburg",
           "Brema": "Bremen", "Hanower": "Hanover", "Kolonia": "Cologne", "Düsseldorf": "Dusseldorf",
           "Dortmund": "Dortmund", "Frankfurt": "Frankfurt", "Stuttgart": "Stuttgart", "Monachium": "Munich",
           "Norymberga": "Nuremberg", "Lipsk": "Leipzig", "Drezno": "Dresden", "Magdeburg": "Magdeburg",
           "Saarbrücken": "Saarbrucken", "Fryburg": "Freiburg", "Praga": "Prague", "Brno": "Brno",
           "Ostrawa": "Ostrava", "Bratysława": "Bratislava", "Koszyce": "Kosice", "Wiedeń": "Vienna"}
TEXTS = {
    "pl": dict(day="Dzień", valid="ważne", tz="czas polski", wd=WEEKDAYS, top="Najwyższy poziom",
               none="Brak obszarów zagrożenia", levels=LEVEL_DESC,
               foot1="Własna analiza zespołu GEFS (30 członków) · przebieg {run}, wydano {issued}",
               foot2="Poziom wynika z macierzy: prawdopodobieństwo × intensywność. To nie jest oficjalne ostrzeżenie IMGW.",
               titles=None),
    "en": dict(day="Day", valid="valid", tz="Central European time", wd=WEEKDAYS_EN, top="Highest level",
               none="No hazard areas",
               levels=["no hazard", "low", "elevated", "significant", "high", "extreme"],
               foot1="Own analysis of a 30-member GEFS ensemble · run {run}, issued {issued}",
               foot2="Level comes from a matrix: probability × intensity. This is not an official warning.",
               titles={"general_winter_risk": "General winter risk", "snow_24h_cm": "Snow",
                       "cold_min_t2m_c": "Cold", "snow_squalls": "Snow squalls",
                       "precip_24h_mm": "Precipitation (24 h)"}),
}


# ----------------------------------------------------------------------------- pomocnicze
def parse_iso(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")


def fmt_day_range(a: str, b: str, lang: str = "pl") -> str:
    da, db = parse_iso(a), parse_iso(b)
    wd = TEXTS[lang]["wd"]
    return (f"{wd[da.weekday()]} {da:%d.%m} {da:%H:%M} → "
            f"{wd[db.weekday()]} {db:%d.%m} {db:%H:%M}")


def level_index(name: str, names: list) -> int:
    try:
        return names.index(name)
    except ValueError:
        return 0


def max_level(hazard: dict, names: list) -> int:
    feats = (hazard.get("areas") or {}).get("features") or []
    return max([level_index(f["properties"].get("level", ""), names) for f in feats] or [0])


def geom_patches(geom, **kw):
    polys = [geom] if geom.geom_type == "Polygon" else list(getattr(geom, "geoms", []))
    for p in polys:
        if p.is_empty or p.geom_type != "Polygon":
            continue
        verts, codes = [], []
        for ring in [p.exterior, *p.interiors]:
            xy = list(ring.coords)
            verts += xy
            codes += [Path.MOVETO] + [Path.LINETO] * (len(xy) - 2) + [Path.CLOSEPOLY]
        yield PathPatch(Path(verts, codes), **kw)


def load_countries():
    req = urllib.request.Request(COUNTRIES_URL, headers={"User-Agent": "meteopanel-swwf"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode())
    out = []
    for f in data["features"]:
        try:
            g = shape(f["geometry"])
        except Exception:
            continue
        minx, miny, maxx, maxy = g.bounds
        if maxx < LON_MIN - 2 or minx > LON_MAX + 2 or maxy < LAT_MIN - 2 or miny > LAT_MAX + 2:
            continue
        out.append(g)
    return out


def load_admin1():
    """Granice wojewodztw / landow (Natural Earth 10m, ok. 40 MB — tylko wybrane kraje)."""
    try:
        req = urllib.request.Request(ADMIN1_URL, headers={"User-Agent": "meteopanel-swwf"})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        print(f"Bez granic województw/landów ({type(e).__name__}) — rysuję tylko państwa.")
        return []
    out = []
    for f in data["features"]:
        if f["properties"].get("adm0_a3") not in ADMIN1_ISO3:
            continue
        try:
            g = shape(f["geometry"]).simplify(0.01)
        except Exception:
            continue
        out.append(g)
    return out


# ----------------------------------------------------------------------------- czcionki i logo
def setup_fonts():
    """Inter (tekst) + Archivo (naglowki) — te same, co na stronie. Szuka plikow TTF z npm
    (@expo-google-fonts/*, instalowane w workflow) albo w TG_FONT_DIR; bez nich zostaje DejaVu."""
    import glob
    from matplotlib import font_manager as fm
    roots = [os.environ.get("TG_FONT_DIR", "").strip(), "node_modules", "fonts/node_modules"]
    found = 0
    for root in [r for r in roots if r]:
        for fam in ("inter", "archivo"):
            for f in glob.glob(os.path.join(root, "**", "@expo-google-fonts", fam, "*", "*.ttf"), recursive=True) + \
                     glob.glob(os.path.join(root, "@expo-google-fonts", fam, "*", "*.ttf")) + \
                     glob.glob(os.path.join(root, "*.ttf")):
                base = os.path.basename(f)
                if any(x in base for x in ("Italic", "Condensed", "Expanded", "Narrow")):
                    continue
                try:
                    fm.fontManager.addfont(f)
                    found += 1
                except Exception:
                    pass
    names = {f.name for f in fm.fontManager.ttflist}
    body = "Inter" if "Inter" in names else "DejaVu Sans"
    head = "Archivo" if "Archivo" in names else body
    print(f"Czcionki: tekst={body}, nagłówki={head} (plików: {found})")
    return body, head


def rounded_rect_xy(x0, y0, x1, y1, rx, ry, n=10):
    """Zaokraglony prostokat w ukladzie danych (rx, ry = promien w jednostkach osi x i y)."""
    import numpy as np
    pts = []
    for cx, cy, a0 in ((x1 - rx, y1 - ry, 0), (x0 + rx, y1 - ry, 90), (x0 + rx, y0 + ry, 180), (x1 - rx, y0 + ry, 270)):
        for t in np.linspace(a0, a0 + 90, n):
            pts.append((cx + rx * np.cos(np.radians(t)), cy + ry * np.sin(np.radians(t))))
    return pts


# ----------------------------------------------------------------------------- rysowanie mapy
def render_map(day: dict, hazard_key: str, swwf: dict, countries, admin1, path: str, theme: str = "dark",
               lang: str = "pl"):
    from matplotlib.patches import FancyBboxPatch
    th = THEMES.get(theme, THEMES["dark"])
    T = TEXTS.get(lang, TEXTS["pl"])
    body, head = setup_fonts()
    plt.rcParams["font.family"] = body
    names = swwf["level_names"]
    colors = swwf["level_colors"]
    hazard = day["hazards"][hazard_key]
    title = (T["titles"] or HAZARD_TITLES).get(hazard_key, hazard_key)
    feats = (hazard.get("areas") or {}).get("features") or []
    feats = sorted(feats, key=lambda f: level_index(f["properties"].get("level", ""), names))
    present = {level_index(f["properties"].get("level", ""), names) for f in feats}
    top = max(present) if present else 0

    FW, FH = 10.0, 9.7
    fig = plt.figure(figsize=(FW, FH), dpi=150, facecolor=th["fig"])

    def fx(inch):
        return inch / FW

    def fy(inch):
        return inch / FH

    M = 0.42                                   # margines boczny (cale)
    MAP_W = FW - 2 * M
    ASPECT = 1.0 / 0.62                        # cos(~51.5 st.)
    MAP_H = MAP_W * ((LAT_MAX - LAT_MIN) * ASPECT) / (LON_MAX - LON_MIN)
    map_y = 1.66                               # dol mapy (cale od dolu): miejsce na legende i stopke

    # ---- naglowek
    logo_path = os.environ.get("TG_LOGO", "swwf_logo.png")
    hx = M
    if os.path.exists(logo_path):
        try:
            import matplotlib.image as mpimg
            lax = fig.add_axes([fx(M), fy(FH - 0.30 - 0.78), fx(0.78), fy(0.78)])
            lax.imshow(mpimg.imread(logo_path))
            lax.axis("off")
            hx = M + 0.78 + 0.22
        except Exception as e:
            print(f"Bez logo ({type(e).__name__})")
    fig.text(fx(hx), fy(FH - 0.30 - 0.20), title, fontsize=21, fontweight="bold", family=head,
             va="center", color=th["text"])
    fig.text(fx(hx), fy(FH - 0.30 - 0.58),
             f"{day['label'].replace('Dzień', T['day'])}  ·  {T['valid']} {fmt_day_range(day['valid_from'], day['valid_to'], lang)} ({T['tz']})",
             fontsize=10.5, color=th["sub"], va="center")

    # ---- zakladki dni (jak na stronie): aktywny dzien wypelniony
    ndays = len(swwf["days"])
    cur = next((i for i, d in enumerate(swwf["days"]) if d["label"] == day["label"]), 0)
    pill_w, pill_h, gap = 0.80, 0.30, 0.08
    px = FW - M - ndays * pill_w - (ndays - 1) * gap
    py = FH - 0.30 - 0.50
    for i, d in enumerate(swwf["days"]):
        x = px + i * (pill_w + gap)
        active = i == cur
        pax = fig.add_axes([fx(x), fy(py), fx(pill_w), fy(pill_h)])
        pax.axis("off")
        pax.set_xlim(0, 1)
        pax.set_ylim(0, 1)
        pax.add_patch(FancyBboxPatch((0.02, 0.04), 0.96, 0.92, boxstyle="round,pad=0,rounding_size=0.28",
                                     fc=th["pill_on"] if active else th["pill_off"],
                                     ec=th["pill_on"] if active else th["frame"], lw=0.8,
                                     mutation_aspect=pill_h / pill_w))
        pax.text(0.5, 0.5, d["label"].replace("Dzień", T["day"]), ha="center", va="center", fontsize=9, fontweight="semibold",
                 color=th["pill_on_text"] if active else th["sub"])

    # ---- mapa
    ax = fig.add_axes([fx(M), fy(map_y), fx(MAP_W), fy(MAP_H)])
    ax.set_facecolor(th["sea"])
    ax.set_xlim(LON_MIN, LON_MAX)
    ax.set_ylim(LAT_MIN, LAT_MAX)
    ax.set_aspect(ASPECT, adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

    # zaokraglone rogi karty mapy: promien ~0.16 cala, w jednostkach danych
    r_in = 0.16
    rx = r_in / MAP_W * (LON_MAX - LON_MIN)
    ry = r_in / MAP_H * (LAT_MAX - LAT_MIN)
    clip = Path(rounded_rect_xy(LON_MIN, LAT_MIN, LON_MAX, LAT_MAX, rx, ry))
    clip_patch = PathPatch(clip, transform=ax.transData, fc="none", ec="none")
    ax.add_patch(clip_patch)

    def add(p, z):
        p.set_zorder(z)
        p.set_clip_path(clip_patch)
        ax.add_patch(p)

    for g in countries:
        for p in geom_patches(g, facecolor=th["land"], edgecolor="none"):
            add(p, 1)
    for g in admin1:
        for p in geom_patches(g, facecolor="none", edgecolor=th["admin"], linewidth=0.45):
            add(p, 3.5)
    for f in feats:
        lvl = level_index(f["properties"].get("level", ""), names)
        for p in geom_patches(shape(f["geometry"]), facecolor=colors[lvl], edgecolor=th["poly_edge"],
                              linewidth=0.8, alpha=th["poly_alpha"]):
            add(p, 3)
    for g in countries:
        for p in geom_patches(g, facecolor="none", edgecolor=th["border"], linewidth=0.9):
            add(p, 4)

    halo = [pe.withStroke(linewidth=2.2, foreground=th["halo"])]
    for name, lat, lon, dx, dy in CITIES:
        ax.plot(lon, lat, "o", color=th["city"], markersize=2.6, zorder=5, markeredgecolor=th["halo"],
                markeredgewidth=0.6, clip_path=clip_patch)
        t = ax.text(lon + dx, lat + dy, CITY_EN.get(name, name) if lang == "en" else name, fontsize=7.4, fontweight="medium", color=th["city"], zorder=6,
                    path_effects=halo)
        t.set_clip_path(clip_patch)

    # ramka karty mapy (na wierzchu, ta sama zaokraglona krawedz)
    ax.add_patch(PathPatch(clip, transform=ax.transData, fc="none", ec=th["frame"], lw=1.2, zorder=9))

    # plakietka na mapie: najwyzszy poziom (albo brak zagrozen)
    bx, by = LON_MIN + 0.45, LAT_MIN + 0.30
    if feats:
        label = f"{T['top']}  {names[top]}"
        dot = colors[top]
    else:
        label = T["none"]
        dot = th["sub"]
    ax.annotate("       " + label, xy=(bx, by), xytext=(0, 0), textcoords="offset points", fontsize=9.5,
                fontweight="semibold", color=th["text"], va="center", ha="left", zorder=8, annotation_clip=False,
                bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.8", fc=th["fig"], ec=th["frame"], lw=0.9,
                          alpha=0.95))
    from matplotlib.transforms import offset_copy
    ax.plot([bx], [by], "o", color=dot, markersize=7.5, zorder=8.5, markeredgecolor=th["fig"],
            markeredgewidth=0.8, transform=offset_copy(ax.transData, fig=fig, x=7.5, y=0, units="points"))

    # ---- legenda: poziome segmenty, jak na stronie
    LG_H = 0.62
    lg = fig.add_axes([fx(M), fy(map_y - 0.20 - LG_H), fx(MAP_W), fy(LG_H)])
    lg.set_xlim(0, 6)
    lg.set_ylim(0, 1)
    lg.axis("off")
    for k, i in enumerate(range(len(names))):
        x0 = k + 0.0
        face = th["none_swatch"] if i == 0 else colors[i]
        on = (i in present) or (i == 0 and not feats)
        lg.add_patch(FancyBboxPatch((x0 + 0.02, 0.70), 0.94, 0.20, boxstyle="round,pad=0,rounding_size=0.05",
                                    fc=face, ec=th["poly_edge"] if i == 0 else "none", lw=0.6,
                                    alpha=1.0 if on else 0.7, mutation_aspect=LG_H * 0.20 / (MAP_W / 6)))
        lg.text(x0 + 0.02, 0.50, names[i], fontsize=9, fontweight="bold" if on else "medium",
                color=th["text"] if on else th["sub"], va="center")
        lg.text(x0 + 0.02, 0.22, T["levels"][i], fontsize=7.6, color=th["sub"] if on else th["foot"], va="center")

    # ---- stopka
    run = parse_iso(swwf["model_run"])
    issued = parse_iso(swwf["issued"])
    fig.text(fx(M), fy(0.36),
             T["foot1"].format(run=f"{run:%d.%m %H:%M}", issued=f"{issued:%d.%m %H:%M}") + "\n" + T["foot2"],
             fontsize=7.4, color=th["foot"], va="center", linespacing=1.5)
    fig.text(FW and fx(FW - M), fy(0.36), "MeteoPanel", fontsize=10.5, fontweight="bold", family=head,
             ha="right", va="center", color=th["sub"])
    fig.savefig(path, facecolor=th["fig"])
    plt.close(fig)


# ----------------------------------------------------------------------------- tekst
def build_text(swwf: dict, hazard_key: str) -> str:
    names = swwf["level_names"]
    run = parse_iso(swwf["model_run"])
    issued = parse_iso(swwf["issued"])
    lines = [f"❄️ SWWF — nowa prognoza",
             f"Przebieg GEFS: {WEEKDAYS[run.weekday()]} {run:%d.%m %H:%M} · wydano {issued:%H:%M}",
             f"Na mapach: {HAZARD_TITLES.get(hazard_key, hazard_key)}", ""]
    keys = list(SIGNAL_HAZARDS)
    if hazard_key == "precip_24h_mm":
        keys = ["precip_24h_mm"]
    for day in swwf["days"]:
        lines.append(f"{day['label']} ({fmt_day_range(day['valid_from'], day['valid_to'])})")
        any_line = False
        for k in keys:
            lvl = max_level(day["hazards"].get(k, {}), names)
            if lvl > 0:
                lines.append(f"  {EMOJI[lvl]} {HAZARD_TITLES[k]}: {names[lvl]}")
                any_line = True
        if not any_line:
            lines.append("  ⬜ brak zagrożeń")
        lines.append("")
    lines.append("Własna analiza zespołu GEFS, nie oficjalne ostrzeżenie IMGW.")
    link = os.environ.get("TG_LINK", "").strip()
    if link:
        lines.append(link)
    return "\n".join(lines)


# ----------------------------------------------------------------------------- decyzja o wysylce
def signature(swwf: dict, min_level: int):
    names = swwf["level_names"]
    sig = {}
    for i, day in enumerate(swwf["days"]):
        for k in SIGNAL_HAZARDS:
            lvl = max_level(day["hazards"].get(k, {}), names)
            sig[f"{i}:{k}"] = lvl if lvl >= min_level else 0
    has_signal = any(v > 0 for v in sig.values())
    digest = hashlib.sha256(json.dumps(sig, sort_keys=True).encode()).hexdigest()[:16]
    return digest, has_signal, sig


def read_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def write_state(digest, has_signal):
    state = read_state()
    state.update({"signature": digest, "has_signal": has_signal})
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)


# ----------------------------------------------------------------------------- Telegram
def tg_call(token: str, method: str, data=None, files=None):
    """Zwraca (ok, opis_bledu). Nigdy nie drukuje URL (zawiera token)."""
    import requests
    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/{method}", data=data, files=files, timeout=90)
        try:
            body = r.json()
        except Exception:
            body = {}
        if r.status_code == 200 and body.get("ok"):
            return True, ""
        return False, f"HTTP {r.status_code}: {body.get('description', '')}"
    except Exception as e:  # tresc wyjatku moze zawierac URL z tokenem
        return False, type(e).__name__


def send_album(token, chat_id, image_paths, caption):
    media, files = [], {}
    for i, p in enumerate(image_paths):
        item = {"type": "photo", "media": f"attach://p{i}"}
        if i == 0 and caption:
            item["caption"] = caption
        media.append(item)
        files[f"p{i}"] = open(p, "rb")
    try:
        return tg_call(token, "sendMediaGroup", {"chat_id": chat_id, "media": json.dumps(media)}, files)
    finally:
        for fh in files.values():
            fh.close()


def send_text(token, chat_id, text):
    return tg_call(token, "sendMessage", {"chat_id": chat_id, "text": text,
                                          "disable_web_page_preview": "true"})


# ----------------------------------------------------------------------------- main
def main_changes(args) -> int:
    """TRYB STARY (TG_MODE=changes): wysyłka po zmianie poziomów zagrożeń, jedna mapa wybranego hazardu."""
    hazard_key = os.environ.get("TG_HAZARD", "").strip() or "general_winter_risk"
    try:
        min_level = int(os.environ.get("TG_MIN_LEVEL", "").strip() or "2")
    except ValueError:
        min_level = 2
    force = os.environ.get("TG_FORCE", "").strip() in ("1", "true", "True")

    with open(args.swwf, encoding="utf-8") as f:
        swwf = json.load(f)
    if hazard_key not in swwf["days"][0]["hazards"]:
        print(f"Nieznany hazard: {hazard_key}")
        return 1

    digest, has_signal, _ = signature(swwf, min_level)
    old = read_state()
    changed = digest != old.get("signature")
    print(f"Sygnatura {digest} (poprzednia {old.get('signature')}), sygnal: {has_signal}, "
          f"zmiana: {changed}, force: {force}")

    ended = old.get("has_signal") and not has_signal
    if not args.dry_run and not force:
        if not changed or not (has_signal or ended):
            print("Bez zmian poziomu zagrożeń — nic nie wysyłam.")
            return 0

    token = os.environ.get("TG_TOKEN", "").strip()
    chats = [c.strip() for c in os.environ.get("TG_CHAT_IDS", "").split(",") if c.strip()]
    if not args.dry_run and (not token or not chats):
        print("Brak sekretów TG_TOKEN / TG_CHAT_IDS.")
        return 1

    text = build_text(swwf, hazard_key)
    print(text)

    paths = []
    if has_signal or force or args.dry_run:
        os.makedirs(args.out_dir, exist_ok=True)
        countries = load_countries()
        admin1 = load_admin1()
        theme = os.environ.get("TG_THEME", "").strip() or "dark"
        for i, day in enumerate(swwf["days"]):
            p = os.path.join(args.out_dir, f"swwf_dzien{i + 1}.png")
            render_map(day, hazard_key, swwf, countries, admin1, p, theme)
            paths.append(p)
        print(f"Narysowano {len(paths)} map w {args.out_dir}/")

    if args.dry_run:
        return 0

    caption = text if len(text) <= 1000 else text[:997] + "..."
    ok_count = 0
    for i, chat in enumerate(chats, 1):
        if paths:
            ok, err = send_album(token, chat, paths, caption)
            if ok and len(text) > 1000:
                ok, err = send_text(token, chat, text)
        else:
            ok, err = send_text(token, chat, "✅ SWWF: zagrożenia z poprzedniej prognozy ustąpiły.\n\n" + text)
        print(f"Odbiorca {i}/{len(chats)}: {'wysłano' if ok else 'BŁĄD ' + err}")
        ok_count += ok

    if ok_count:
        write_state(digest, has_signal)
    print(f"Dotarło do {ok_count} z {len(chats)} odbiorców.")
    return 0 if ok_count == len(chats) else 1


# ----------------------------------------------------------------------------- tryb poranny
MORNING_HAZARDS = ["general_winter_risk", "precip_24h_mm"]   # mapy: zimowe razem + opad
MORNING_CAPTION = {"pl": "🗺 Mapy SWWF — dni, w których prognozowane jest zagrożenie",
                   "en": "🗺 SWWF maps — days with a forecast hazard"}


def morning_map_list(swwf: dict, min_level: int):
    """[(numer_doby, klucz_hazardu)] tylko tam, gdzie na mapie jest obszar o poziomie >= min_level."""
    names = swwf["level_names"]
    out = []
    for i, day in enumerate(swwf["days"]):
        for k in MORNING_HAZARDS:
            h = day["hazards"].get(k)
            if h and max_level(h, names) >= min_level:
                out.append((i, k))
    return out


def split_text(text: str, limit: int = 4000):
    """Dzieli długi tekst na części <= limit znaków, po pustych liniach."""
    if len(text) <= limit:
        return [text]
    parts, cur = [], ""
    for block in text.split("\n\n"):
        if cur and len(cur) + 2 + len(block) > limit:
            parts.append(cur)
            cur = block
        else:
            cur = f"{cur}\n\n{block}" if cur else block
    if cur:
        parts.append(cur)
    return parts


def send_maps(token, chat_id, image_paths, caption):
    """1 zdjęcie -> sendPhoto (album wymaga >= 2), więcej -> albumy po <= 10."""
    if len(image_paths) == 1:
        with open(image_paths[0], "rb") as fh:
            return tg_call(token, "sendPhoto", {"chat_id": chat_id, "caption": caption}, {"photo": fh})
    ok, err = True, ""
    for n in range(0, len(image_paths), 10):
        chunk = image_paths[n:n + 10]
        if len(chunk) == 1:
            with open(chunk[0], "rb") as fh:
                o, e = tg_call(token, "sendPhoto", {"chat_id": chat_id}, {"photo": fh})
        else:
            o, e = send_album(token, chat_id, chunk, caption if n == 0 else "")
        ok, err = ok and o, err or e
    return ok, err


def main_morning(args) -> int:
    """Depesza poranna: raz dziennie, po pierwszej nowej prognozie danego dnia (data wydania wg czasu polskiego).

    Tekst: PL do TG_CHAT_IDS, EN do TG_CHAT_IDS_EN. Mapy tylko dla dób/hazardów, na których coś jest."""
    import swwf_airmet as AM
    force = os.environ.get("TG_FORCE", "").strip() in ("1", "true", "True")
    try:
        min_map = int(os.environ.get("TG_MAP_MIN_LEVEL", "").strip() or "1")
    except ValueError:
        min_map = 1
    try:
        min_text = int(os.environ.get("AIRMET_MIN_LEVEL", "").strip() or "1")
    except ValueError:
        min_text = 1
    with open(args.swwf, encoding="utf-8") as f:
        swwf = json.load(f)

    issued_date = parse_iso(swwf["issued"]).date().isoformat()
    state = read_state()
    ms = state.get("morning") or {}
    if ms.get("date") != issued_date:
        ms = {"date": issued_date, "pl": False, "en": False}
    print(f"Wydanie z {issued_date} (przebieg {swwf['model_run']}); wysłano dziś: PL={ms['pl']}, EN={ms['en']}; force={force}")

    token = os.environ.get("TG_TOKEN", "").strip()
    chats = {
        "pl": [c.strip() for c in os.environ.get("TG_CHAT_IDS", "").split(",") if c.strip()],
        "en": [c.strip() for c in os.environ.get("TG_CHAT_IDS_EN", "").split(",") if c.strip()],
    }
    langs = [l for l in ("pl", "en") if (args.dry_run or chats[l]) and (force or args.dry_run or not ms[l])]
    for l in ("pl", "en"):
        if not chats[l] and not args.dry_run:
            print(f"Brak odbiorców {l.upper()} (sekret TG_CHAT_IDS{'_EN' if l == 'en' else ''}) — pomijam.")
    if not langs:
        print("Nic do wysłania (już wysłano dziś albo brak odbiorców).")
        return 0
    if not args.dry_run and not token:
        print("Brak sekretu TG_TOKEN.")
        return 1

    texts = {}
    if "pl" in langs:
        texts["pl"] = AM.build_message_pl(swwf, AM.load_voivodeships(), min_text)
    if "en" in langs:
        texts["en"] = AM.build_message_en(swwf, AM.load_countries(), min_text)

    todo = morning_map_list(swwf, min_map)
    print("Mapy do wysłania: " + (", ".join(f"Dzień {i + 1}:{k}" for i, k in todo) or "brak (nic nie wystąpi)"))
    maps = {l: [] for l in langs}
    if todo:
        os.makedirs(args.out_dir, exist_ok=True)
        countries, admin1 = load_countries(), load_admin1()
        theme = os.environ.get("TG_THEME", "").strip() or "dark"
        for l in langs:
            for i, k in todo:
                path = os.path.join(args.out_dir, f"swwf_{l}_dzien{i + 1}_{k}.png")
                render_map(swwf["days"][i], k, swwf, countries, admin1, path, theme, lang=l)
                maps[l].append(path)

    if args.dry_run:
        for l in langs:
            print(f"\n===== {l.upper()} =====\n{texts[l]}")
        return 0

    all_ok = True
    for l in langs:
        ok_lang = True
        for n, chat in enumerate(chats[l], 1):
            ok, err = True, ""
            for part in split_text(texts[l]):
                o, e = send_text(token, chat, part)
                ok, err = ok and o, err or e
            if ok and maps[l]:
                o, e = send_maps(token, chat, maps[l], MORNING_CAPTION[l])
                ok, err = ok and o, err or e
            print(f"{l.upper()} odbiorca {n}/{len(chats[l])}: {'wysłano' if ok else 'BŁĄD ' + err}")
            ok_lang = ok_lang and ok
        ms[l] = ms[l] or ok_lang
        all_ok = all_ok and ok_lang
    state["morning"] = ms
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)
    return 0 if all_ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="tylko rysuj i pokaz tekst, nic nie wysylaj")
    ap.add_argument("--out-dir", default="swwf_maps")
    ap.add_argument("--swwf", default=SWWF_JSON)
    args = ap.parse_args()
    mode = os.environ.get("TG_MODE", "").strip().lower() or "morning"
    return main_changes(args) if mode == "changes" else main_morning(args)


if __name__ == "__main__":
    sys.exit(main())
