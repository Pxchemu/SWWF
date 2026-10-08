#!/usr/bin/env python3
"""Alert SkyPredict na Telegram dla jednego adresu.

Wejscie: sky_polygons.json (wynik sky_eval.js: lista polygonow z lowcyburz.pl).
Stan:    sky_seen.json (identyfikatory juz widzianych polygonow CALEGO KRAJU — publiczne dane,
         bez zadnej informacji o Twojej lokalizacji, bo repo jest publiczne).

Sekrety (tylko GitHub Actions secrets):
  SKY_TG_TOKEN    token OSOBNEGO bota od SkyPredict (nie tego od SWWF)
  SKY_CHAT_IDS    numer(y) czatu odbiorcow alertow SkyPredict (np. tylko Twoj)
  SKY_LAT, SKY_LON  wspolrzedne adresu (zaokraglij do ~0.01 st. = ok. 1 km)
Zmienne:
  SKY_RADIUS_KM   alert tez dla polygonow w tej odleglosci od adresu (domyslnie 10; 0 = tylko wewnatrz)
  SKY_TEST        "1" = doloz sztuczny polygon obejmujacy adres i wyslij alert testowy
  TG_THEME        dark (domyslnie) / light

Zasady:
- pierwsze uruchomienie (brak sky_seen.json) tylko zapamietuje obecne polygony, nic nie wysyla,
- alert idzie tylko dla polygonu NOWEGO lub ZMIENIONEGO (inny zakres, czas, stopien),
  ktory obejmuje adres albo lezy w promieniu,
- skrypt nie drukuje tokenu, numerow czatu ani wspolrzednych.
"""
import argparse
import hashlib
import html
import json
import math
import os
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from shapely.geometry import Point, Polygon  # noqa: E402

import swwf_telegram as st  # noqa: E402  (granice, motywy, wysylka)

POLY_FILE = "sky_polygons.json"
SEEN_FILE = "sky_seen.json"


# ----------------------------------------------------------------------------- dane
def clean_polygons(raw):
    """Walidacja danych z cudzego skryptu: tylko pola i typy, ktorych oczekujemy."""
    out = []
    for p in raw if isinstance(raw, list) else []:
        try:
            coords = [(float(c[0]), float(c[1])) for c in p["coords"]]
            if len(coords) < 3 or not all(-180 <= x <= 180 and -90 <= y <= 90 for x, y in coords):
                continue
            color = p.get("color") or ""
            if not re.fullmatch(r"#?[0-9a-fA-F]{3,8}", color):
                color = "#ef4444"
            elif not color.startswith("#"):
                color = "#" + color
            out.append({
                "type": str(p.get("type", ""))[:60],
                "level": int(p.get("level", 0)),
                "validFrom": str(p.get("validFrom", ""))[:40],
                "validTo": str(p.get("validTo", ""))[:40],
                "content": str(p.get("content", ""))[:20000],
                "color": color,
                "coords": coords,
            })
        except Exception:
            continue
    return out


def poly_id(p):
    cs = ",".join(f"{x:.4f}:{y:.4f}" for x, y in p["coords"])
    raw = f"{p['type']}|{p['level']}|{p['validFrom']}|{p['validTo']}|{cs}"
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


def distance_km(lat0, lon0, coords):
    """Odleglosc adresu od polygonu w km (0 = adres w srodku); rzut lokalny rownokatnikowy."""
    k = math.cos(math.radians(lat0))
    pts = [((x - lon0) * k * 111.32, (y - lat0) * 110.57) for x, y in coords]
    try:
        poly = Polygon(pts)
        if not poly.is_valid:
            poly = poly.buffer(0)
        return float(poly.distance(Point(0, 0)))
    except Exception:
        return float("inf")


def text_from_html(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def title_and_desc(content):
    m = re.search(r'class=["\'][^"\']*warntable_title[^"\']*["\'][^>]*>(.*?)</t[dh]>', content, re.S | re.I)
    title = text_from_html(m.group(1)) if m else ""
    m = re.search(r'class=["\'][^"\']*warntable_td[^"\']*["\'][^>]*>(.*?)</t[dh]>', content, re.S | re.I)
    desc = text_from_html(m.group(1)) if m else ""
    desc = re.sub(r"To\s+jest\s+komentarz\.?", "", desc, flags=re.I).strip()
    return title, desc


# ----------------------------------------------------------------------------- mapa
def render_alert_map(p, lat0, lon0, countries, admin1, path, theme):
    th = st.THEMES.get(theme, st.THEMES["dark"])
    xs = [x for x, _ in p["coords"]] + [lon0]
    ys = [y for _, y in p["coords"]] + [lat0]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    half_lat = max((max(ys) - min(ys)) / 2 * 1.5, 1.2)
    half_lon = half_lat / 0.62 * 1.25

    fig = plt.figure(figsize=(8, 6), dpi=130, facecolor=th["fig"])
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    ax.set_facecolor(th["sea"])
    ax.set_xlim(cx - half_lon, cx + half_lon)
    ax.set_ylim(cy - half_lat, cy + half_lat)
    ax.set_aspect(1.0 / 0.62)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color(th["frame"])
    for g in countries:
        for q in st.geom_patches(g, facecolor=th["land"], edgecolor="none", zorder=1):
            ax.add_patch(q)
    for g in admin1:
        for q in st.geom_patches(g, facecolor="none", edgecolor=th["admin"], linewidth=0.5, zorder=3.5):
            ax.add_patch(q)
    for q in st.geom_patches(Polygon(p["coords"]).buffer(0), facecolor=p["color"], edgecolor=th["poly_edge"],
                             linewidth=1.2, alpha=0.6, zorder=3):
        ax.add_patch(q)
    for g in countries:
        for q in st.geom_patches(g, facecolor="none", edgecolor=th["border"], linewidth=0.8, zorder=4):
            ax.add_patch(q)
    halo = [pe.withStroke(linewidth=1.4, foreground=th["halo"])]
    for name, la, lo, dx, dy in st.CITIES:
        if abs(lo - cx) < half_lon and abs(la - cy) < half_lat:
            ax.plot(lo, la, "o", color=th["city"], markersize=2.6, zorder=5)
            ax.text(lo + dx, la + dy, name, fontsize=7, color=th["city"], zorder=6, path_effects=halo)
    ax.plot(lon0, lat0, marker="*", color="#ffffff", markeredgecolor="#000000", markersize=14, zorder=8)
    fig.savefig(path, facecolor=th["fig"])
    plt.close(fig)


# ----------------------------------------------------------------------------- stan
def read_seen():
    try:
        with open(SEEN_FILE, encoding="utf-8") as f:
            return set(json.load(f).get("ids", []))
    except Exception:
        return None  # brak pliku = pierwsze uruchomienie


def write_seen(ids):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump({"ids": sorted(ids)}, f)


# ----------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--polygons", default=POLY_FILE)
    ap.add_argument("--dry-run", action="store_true", help="bez wysylki; rysuje mape do --out-dir")
    ap.add_argument("--out-dir", default="sky_maps")
    args = ap.parse_args()

    try:
        lat0 = float(os.environ.get("SKY_LAT", "").replace(",", "."))
        lon0 = float(os.environ.get("SKY_LON", "").replace(",", "."))
    except ValueError:
        print("Brak/niepoprawne sekrety SKY_LAT, SKY_LON.")
        return 1
    try:
        radius = float(os.environ.get("SKY_RADIUS_KM", "").strip() or "10")
    except ValueError:
        radius = 10.0
    test = os.environ.get("SKY_TEST", "").strip() in ("1", "true", "True")
    theme = os.environ.get("TG_THEME", "").strip() or "dark"

    try:
        with open(args.polygons, encoding="utf-8") as f:
            polys = clean_polygons(json.load(f))
    except Exception as e:
        print(f"Nie udało się wczytać polygonów ({type(e).__name__}) — kończę bez zmian.")
        return 0
    print(f"Aktywnych polygonów SkyPredict: {len(polys)}")

    if test:  # sztuczny polygon obejmujacy adres (tylko do testu calego toru)
        d = 0.08
        polys.append({"type": "TEST", "level": 2, "validFrom": "test", "validTo": "test",
                      "content": '<table><tr><td class="warntable_title">Test alertu — Stopień 2: '
                                 'sztuczny polygon wokół Twojego adresu</td></tr><tr>'
                                 '<td class="warntable_td">To jest tylko test toru powiadomień. '
                                 'Nie ma realnego zagrożenia.</td></tr></table>',
                      "color": "#ef4444",
                      "coords": [(lon0 - d, lat0 - d * 0.62), (lon0 + d, lat0 - d * 0.62),
                                 (lon0 + d, lat0 + d * 0.62), (lon0 - d, lat0 + d * 0.62)]})

    seen = read_seen()
    current_ids = {poly_id(p): p for p in polys}

    if seen is None and not test:
        print("Pierwsze uruchomienie: zapamiętuję obecne polygony, bez wysyłania alertów.")
        if not args.dry_run:
            write_seen(set(current_ids))
        return 0
    seen = seen or set()

    new = [(i, p) for i, p in current_ids.items() if i not in seen]
    alerts = []
    for i, p in new:
        dist = distance_km(lat0, lon0, p["coords"])
        if dist <= max(radius, 0.0):
            alerts.append((p, dist))
    print(f"Nowych/zmienionych polygonów: {len(new)}, z nich dotyczy adresu: {len(alerts)}")

    token = os.environ.get("SKY_TG_TOKEN", "").strip()
    chats = [c.strip() for c in os.environ.get("SKY_CHAT_IDS", "").split(",") if c.strip()]
    if alerts and not args.dry_run and (not token or not chats):
        print("Brak sekretów SKY_TG_TOKEN / SKY_CHAT_IDS.")
        return 1

    all_ok = True
    if alerts:
        countries = st.load_countries()
        admin1 = st.load_admin1()
        os.makedirs(args.out_dir, exist_ok=True)
        for n, (p, dist) in enumerate(alerts, 1):
            title, desc = title_and_desc(p["content"])
            where = ("obejmuje Twój adres" if dist <= 0.05 else f"w odległości ok. {dist:.0f} km od Twojego adresu")
            head = f"⚠️ SkyPredict: {title or p['type'] or 'nowa depesza'}"
            lines = [head, f"Stopień {p['level']} — {where}", f"Ważne: {p['validFrom']} → {p['validTo']}"]
            if desc:
                lines += ["", desc[:550] + ("…" if len(desc) > 550 else "")]
            lines += ["", "Źródło: SkyPredict · Skywarn Polska (nieoficjalne, nie IMGW)."]
            caption = "\n".join(lines)[:1000]
            img = os.path.join(args.out_dir, f"sky_alert_{n}.png")
            render_alert_map(p, lat0, lon0, countries, admin1, img, theme)
            if args.dry_run:
                print(caption)
                continue
            for chat in chats:
                with open(img, "rb") as fh:
                    ok, err = st.tg_call(token, "sendPhoto", {"chat_id": chat, "caption": caption},
                                         {"photo": fh})
                print(f"Alert {n}: {'wysłano' if ok else 'BŁĄD ' + err}")
                all_ok = all_ok and ok

    if not args.dry_run and all_ok and not test:
        write_seen(set(current_ids))  # zapis tylko gdy wszystko wyslane (inaczej ponowimy)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
