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

# motywy kolorystyczne (TG_THEME=dark|light, domyslnie dark)
THEMES = {
    "dark": dict(fig="#0f141a", sea="#0b1620", land="#1b232d", border="#7d8a9b", admin="#8fa0b4",
                 text="#e6edf3", sub="#9fb0c3", foot="#7d8a9b", city="#e6edf3", halo="#0f141a",
                 poly_edge="#e6edf3", frame="#3a4757", none_swatch="#1b232d", poly_alpha=0.78),
    "light": dict(fig="#ffffff", sea="#cfe3f1", land="#f3f1ea", border="#8a8a8a", admin="#9a968a",
                  text="#111111", sub="#444444", foot="#666666", city="#222222", halo="#ffffff",
                  poly_edge="#333333", frame="#555555", none_swatch="#ffffff", poly_alpha=0.72),
}

HAZARD_TITLES = {
    "general_winter_risk": "Ogólne ryzyko zimowe",
    "snow_24h_cm": "Śnieg",
    "cold_min_t2m_c": "Mróz",
    "snow_squalls": "Szkwały śnieżne",
    "precip_24h_mm": "Opad (hazard testowy)",
}
SIGNAL_HAZARDS = ["snow_24h_cm", "cold_min_t2m_c", "snow_squalls", "general_winter_risk"]
EMOJI = ["⬜", "🟩", "🟨", "🟧", "🟥", "🟪"]
WEEKDAYS = ["pn", "wt", "śr", "czw", "pt", "sob", "niedz"]
LEVEL_DESC = ["brak zagrożenia", "niewielkie", "podwyższone", "umiarkowane", "wysokie", "ekstremalne"]


# ----------------------------------------------------------------------------- pomocnicze
def parse_iso(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")


def fmt_day_range(a: str, b: str) -> str:
    da, db = parse_iso(a), parse_iso(b)
    return (f"{WEEKDAYS[da.weekday()]} {da:%d.%m} {da:%H:%M} → "
            f"{WEEKDAYS[db.weekday()]} {db:%d.%m} {db:%H:%M}")


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


# ----------------------------------------------------------------------------- rysowanie mapy
def render_map(day: dict, hazard_key: str, swwf: dict, countries, admin1, path: str, theme: str = "dark"):
    th = THEMES.get(theme, THEMES["dark"])
    names = swwf["level_names"]
    colors = swwf["level_colors"]
    hazard = day["hazards"][hazard_key]
    title = HAZARD_TITLES.get(hazard_key, hazard_key)

    fig = plt.figure(figsize=(10, 6.6), dpi=130, facecolor=th["fig"])
    ax = fig.add_axes([0.012, 0.075, 0.69, 0.80])
    ax.set_facecolor(th["sea"])
    ax.set_xlim(LON_MIN, LON_MAX)
    ax.set_ylim(LAT_MIN, LAT_MAX)
    ax.set_aspect(1.0 / 0.62)  # cos(~51.5 st.)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color(th["frame"])

    for g in countries:  # ladu: tlo ladu
        for p in geom_patches(g, facecolor=th["land"], edgecolor="none", zorder=1):
            ax.add_patch(p)
    for g in admin1:  # drobny podzial: wojewodztwa, landy
        for p in geom_patches(g, facecolor="none", edgecolor=th["admin"], linewidth=0.5, zorder=3.5):
            ax.add_patch(p)

    feats = (hazard.get("areas") or {}).get("features") or []
    feats = sorted(feats, key=lambda f: level_index(f["properties"].get("level", ""), names))
    for f in feats:
        lvl = level_index(f["properties"].get("level", ""), names)
        for p in geom_patches(shape(f["geometry"]), facecolor=colors[lvl], edgecolor=th["poly_edge"],
                              linewidth=0.7, alpha=th["poly_alpha"], zorder=3):
            ax.add_patch(p)

    for g in countries:  # granice panstw na wierzchu, nad polygonami
        for p in geom_patches(g, facecolor="none", edgecolor=th["border"], linewidth=0.8, zorder=4):
            ax.add_patch(p)

    halo = [pe.withStroke(linewidth=1.4, foreground=th["halo"])]
    for name, lat, lon, dx, dy in CITIES:
        ax.plot(lon, lat, "o", color=th["city"], markersize=2.4, zorder=5,
                markeredgecolor=th["halo"], markeredgewidth=0.4)
        ax.text(lon + dx, lat + dy, name, fontsize=6.3, color=th["city"], zorder=6, path_effects=halo)

    if not feats:
        ax.text((LON_MIN + LON_MAX) / 2, LAT_MAX - 0.6, "Brak obszarów zagrożenia",
                ha="center", va="center", fontsize=11, color=th["text"],
                bbox=dict(boxstyle="round", fc=th["fig"], ec=th["frame"], alpha=0.92), zorder=7)

    # legenda z boku
    lg = fig.add_axes([0.725, 0.075, 0.26, 0.80])
    lg.set_xlim(0, 1)
    lg.set_ylim(0, 1)
    lg.axis("off")
    lg.text(0, 0.975, "Poziom zagrożenia", fontsize=10, fontweight="bold", va="top", color=th["text"])
    present = {level_index(f["properties"].get("level", ""), names) for f in feats}
    y = 0.90
    for i in range(len(names) - 1, -1, -1):
        face = th["none_swatch"] if i == 0 else colors[i]
        lg.add_patch(Rectangle((0, y - 0.045), 0.16, 0.06, facecolor=face, edgecolor=th["poly_edge"],
                               linewidth=0.7, alpha=0.95))
        lg.text(0.21, y - 0.015, names[i], fontsize=8.5, va="center", color=th["text"],
                fontweight="bold" if i in present else "normal")
        lg.text(0.21, y - 0.055, LEVEL_DESC[i], fontsize=7, va="center", color=th["sub"])
        y -= 0.115
    lg.text(0, 0.19, "Poziom wynika z macierzy:\nprawdopodobieństwo (30 członków\nzespołu GEFS) × intensywność.",
            fontsize=6.8, va="top", color=th["sub"])

    fig.text(0.012, 0.955, f"{title} — {day['label']}", fontsize=15, fontweight="bold",
             va="center", color=th["text"])
    fig.text(0.012, 0.915, f"Ważne: {fmt_day_range(day['valid_from'], day['valid_to'])} (czas polski)",
             fontsize=9.5, color=th["sub"], va="center")
    run = parse_iso(swwf["model_run"])
    issued = parse_iso(swwf["issued"])
    fig.text(0.012, 0.03,
             f"Własna analiza zespołu GEFS (przebieg {run:%d.%m %H:%M}, wydano {issued:%d.%m %H:%M}). "
             "To nie jest oficjalne ostrzeżenie IMGW.",
             fontsize=7, color=th["foot"], va="center")
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
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"signature": digest, "has_signal": has_signal}, f)


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
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="tylko rysuj i pokaz tekst, nic nie wysylaj")
    ap.add_argument("--out-dir", default="swwf_maps")
    ap.add_argument("--swwf", default=SWWF_JSON)
    args = ap.parse_args()

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


if __name__ == "__main__":
    sys.exit(main())
