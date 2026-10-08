#!/usr/bin/env python3
"""SWWF -> opisowy komunikat tekstowy na NAJBLIŻSZĄ DOBĘ (PROTOTYP).

Z swwf.json (wynik generate_swwf.py) bierze tylko Dzień 1 i pisze krótkie podsumowanie prozą:
co się zapowiada, gdzie (województwa), jak mocno i jak pewnie, oraz czy prognoza zmieniła się
względem poprzedniego przebiegu. Uwzględnia opady, śnieg, mróz i szkwały śnieżne.

Obszar liczony z siatki natywnej (0,25°), tylko pola leżące w Polsce: województwo wchodzi do
opisu, gdy co najmniej MIN_COVER jego pól osiąga dany poziom; "w większości" = co najmniej
MOST_COVER. Granice: voivodeships_pl.geojson (w repo; jeśli go brak, pobierane i zapisywane).

Użycie:
  python swwf_airmet.py                       # czyta swwf.json, pisze airmet_pl.txt (Polska, PL)
                                              # i airmet_ce.txt (Europa Środkowa, EN) oraz drukuje oba
  python swwf_airmet.py swwf.json --out-pl a.txt --out-ce b.txt
Zmienne: AIRMET_MIN_LEVEL (domyślnie 1 = SLIGHT) — najniższy poziom ujmowany w komunikacie.
"""
import argparse
import json
import os
import statistics
import sys
import urllib.request
from datetime import datetime, timezone

from shapely.geometry import Point, shape
from shapely.prepared import prep

VOIV_FILE = "voivodeships_pl.geojson"
ADMIN1_URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
              "master/geojson/ne_10m_admin_1_states_provinces.geojson")
MIN_COVER = 0.15     # udział pól województwa na danym poziomie, od którego je wymieniamy
MOST_COVER = 0.70    # od tego udziału: "w większości"
WEEKDAYS = ["pn", "wt", "śr", "czw", "pt", "sob", "nd"]

# dopełniacz i miejscownik nazw województw (do zdań typu "w północnej części woj. podlaskiego")
GEN = {"dolnośląskie": "dolnośląskiego", "kujawsko-pomorskie": "kujawsko-pomorskiego",
       "lubelskie": "lubelskiego", "lubuskie": "lubuskiego", "łódzkie": "łódzkiego",
       "małopolskie": "małopolskiego", "mazowieckie": "mazowieckiego", "opolskie": "opolskiego",
       "podkarpackie": "podkarpackiego", "podlaskie": "podlaskiego", "pomorskie": "pomorskiego",
       "śląskie": "śląskiego", "świętokrzyskie": "świętokrzyskiego",
       "warmińsko-mazurskie": "warmińsko-mazurskiego", "wielkopolskie": "wielkopolskiego",
       "zachodniopomorskie": "zachodniopomorskiego"}
LOC = {k: v[:-4] + "im" for k, v in GEN.items()}   # -kiego -> -kim (śląskiego -> śląskim)

# nazwy zjawisk wg poziomu 1-5 (zgodnie z progami intensywności z generatora)
PHENOMENON = {
    "precip_24h_mm": ["", "słabe lub umiarkowane opady", "dość intensywne opady", "intensywne opady",
                      "bardzo intensywne opady", "ekstremalne opady"],
    "snow_24h_cm": ["", "słabe opady śniegu", "umiarkowane opady śniegu", "intensywne opady śniegu",
                    "bardzo intensywne opady śniegu", "ekstremalne opady śniegu"],
    "cold_min_t2m_c": ["", "mróz", "silny mróz", "silny mróz", "bardzo silny mróz", "ekstremalny mróz"],
    "snow_squalls": ["", "gwałtowne opady śniegu", "gwałtowne opady śniegu",
                     "gwałtowne opady śniegu o charakterze szkwałów", "silne szkwały śnieżne",
                     "ekstremalne szkwały śnieżne"],
}
TITLE = {"precip_24h_mm": "Opady", "snow_24h_cm": "Śnieg", "cold_min_t2m_c": "Mróz",
         "snow_squalls": "Szkwały śnieżne"}
ORDER = ["snow_24h_cm", "cold_min_t2m_c", "snow_squalls", "precip_24h_mm"]
ICON = {1: "🟩", 2: "🟨", 3: "🟧", 4: "🟥", 5: "🟪"}


def parse_iso(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")


def fmt_t(s):
    d = parse_iso(s)
    return f"{WEEKDAYS[d.weekday()]} {d:%d.%m} {d:%H:%M}"


# ----------------------------------------------------------------------------- geometria
def load_voivodeships():
    """-> lista (nazwa, geometria) dla 16 województw."""
    if os.path.exists(VOIV_FILE):
        with open(VOIV_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return [(ft["properties"]["name"], shape(ft["geometry"])) for ft in data["features"]]
    print("Brak voivodeships_pl.geojson — pobieram granice (Natural Earth, ~40 MB) i zapisuję cache.",
          file=sys.stderr)
    from shapely.geometry import mapping
    req = urllib.request.Request(ADMIN1_URL, headers={"User-Agent": "meteopanel-swwf"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode())
    out, feats = [], []
    for ft in data["features"]:
        if ft["properties"].get("adm0_a3") != "POL":
            continue
        name = ft["properties"]["name_pl"].replace("województwo ", "")
        g = shape(ft["geometry"]).simplify(0.01)
        out.append((name, g))
        feats.append({"type": "Feature", "properties": {"name": name}, "geometry": mapping(g)})
    with open(VOIV_FILE, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": feats}, f, ensure_ascii=False, separators=(",", ":"))
    return out


def cells_by_voivodeship(grid, voivs):
    """-> {nazwa: [(i, j, lat, lon), ...]} — pola siatki, których środek leży w województwie."""
    prepared = [(n, prep(g)) for n, g in voivs]
    out = {n: [] for n, _ in voivs}
    for i, la in enumerate(grid["lat"]):
        for j, lo in enumerate(grid["lon"]):
            p = Point(lo, la)
            for n, pg in prepared:
                if pg.contains(p):
                    out[n].append((i, j, la, lo))
                    break
    return out


def region_direction(cells_hit, cells_all):
    """(ns, ew): 'N'/'S'/'' i 'E'/'W'/'' — gdzie w obszarze leży zbiór pól cells_hit."""
    lats = [c[2] for c in cells_all]
    lons = [c[3] for c in cells_all]
    span_la, span_lo = max(lats) - min(lats), max(lons) - min(lons)
    if span_la < 1e-6 and span_lo < 1e-6:
        return "", ""
    cla = sum(c[2] for c in cells_hit) / len(cells_hit) - sum(lats) / len(lats)
    clo = sum(c[3] for c in cells_hit) / len(cells_hit) - sum(lons) / len(lons)
    ns = "N" if span_la > 0 and cla > 0.2 * span_la else "S" if span_la > 0 and cla < -0.2 * span_la else ""
    ew = "E" if span_lo > 0 and clo > 0.2 * span_lo else "W" if span_lo > 0 and clo < -0.2 * span_lo else ""
    return ns, ew


def part_of_region(cells_hit, cells_all):
    """Kierunek części województwa jako przymiotnik w miejscowniku ('północno-wschodniej'), albo ''."""
    ns, ew = region_direction(cells_hit, cells_all)
    ns = {"N": "północna", "S": "południowa", "": ""}[ns]
    ew = {"E": "wschodnia", "W": "zachodnia", "": ""}[ew]
    word = f"{ns[:-1]}o-{ew}" if ns and ew else (ns or ew)
    return word[:-1] + "ej" if word else ""      # północna -> północnej, północno-wschodnia -> północno-wschodniej


def area_phrase(level, grid_levels, cells):
    """Opis obszaru dla pól o poziomie >= level: np. 'w większości woj. A i B oraz w północnej części woj. C'."""
    most, parts = [], []
    for name, cs in cells.items():
        if not cs:
            continue
        hit = [c for c in cs if grid_levels[c[0]][c[1]] >= level]
        cover = len(hit) / len(cs)
        if cover < MIN_COVER:
            continue
        if cover >= MOST_COVER:
            most.append(name)
        else:
            parts.append((name, part_of_region(hit, cs)))
    n_all = len(cells)
    pieces = []
    if len(most) == n_all:
        pieces.append("na obszarze całego kraju")
    elif len(most) >= n_all - 4 and most:
        missing = [n for n in cells if n not in most]
        pieces.append("na większości obszaru kraju (poza woj. " + join_pl([LOC[n] for n in missing]) + ")")
    elif most:
        pieces.append("w większości woj. " + join_pl([LOC[n] for n in most]))
    if parts and len(most) < n_all:
        sub = []
        for name, d in parts:
            prep_w = "we" if d.startswith("w") else "w"
            sub.append(f"{prep_w} {d} części woj. {GEN[name]}" if d else f"w części woj. {GEN[name]}")
        if len(sub) > 4 and not most:
            pieces.append("lokalnie w wielu regionach (woj. " + join_pl([LOC[n] for n, _ in parts]) + ")")
        else:
            pieces.append(("oraz " if pieces else "") + join_pl(sub))
    if not pieces:   # obszar mniejszy niż MIN_COVER każdego województwa: wskaż województwa z choćby jednym polem
        touched = [n for n, cs in cells.items()
                   if any(grid_levels[c[0]][c[1]] >= level for c in cs)]
        if touched:
            pieces.append("na niewielkim obszarze (woj. " + join_pl([LOC[n] for n in touched]) + ")")
    return " ".join(pieces)


def join_pl(items):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " i " + items[-1]


# ----------------------------------------------------------------------------- opis słowny
def chance_word(p):
    if p >= 85:
        return "bardzo prawdopodobne"
    if p >= 60:
        return "prawdopodobne"
    if p >= 30:
        return "możliwe"
    return "mało prawdopodobne, ale nie wykluczone"


def fmt_val(v, unit):
    return f"{round(v):d} {unit}".replace("-", "−") if unit == "°C" else f"{round(v):d} {unit}"


def intensity_phrase(key, vals):
    """Typowa i szczytowa wartość mediany zespołu w obszarze."""
    if key == "cold_min_t2m_c":
        typ, peak = statistics.median(vals), min(vals)
        a, b = f"{round(typ):d}".replace("-", "−"), f"{round(peak):d}".replace("-", "−")
        if a == b:
            return f"temperatura minimalna około {a}°C"
        return f"temperatura minimalna zwykle około {a}°C, lokalnie do {b}°C"
    unit = {"precip_24h_mm": "mm", "snow_24h_cm": "cm", "snow_squalls": "J/kg"}[key]
    typ, peak = statistics.median(vals), max(vals)
    if key == "snow_squalls":
        return ""
    what = "suma opadu" if key == "precip_24h_mm" else "przyrost świeżego śniegu"
    if peak < 1:
        return f"{what} poniżej 1 {unit}"
    if round(typ) == round(peak) or peak < 1.5 * typ or peak - typ < 2:
        return f"{what} około {round(peak):d} {unit}"
    return f"{what} zwykle około {max(1, round(typ)):d} {unit}, lokalnie do {round(peak):d} {unit}"


def hazard_paragraph(day, key, names, cells, min_level):
    h = day["hazards"].get(key)
    if not h:
        return None
    lv = h["level_grid"]
    in_pl = [(c[0], c[1]) for cs in cells.values() for c in cs]
    present = sorted({lv[i][j] for i, j in in_pl if lv[i][j] >= min_level}, reverse=True)
    if not present:
        return None
    top = present[0]
    area_top = [(i, j) for i, j in in_pl if lv[i][j] >= top]
    vals = [h["median_intensity"][i][j] for i, j in area_top]
    probs = [h["probability_grid"][i][j] for i, j in area_top]
    where = area_phrase(top, lv, cells)
    what = PHENOMENON[key][top]
    sentence = f"{ICON.get(top, '')} {TITLE[key]} — poziom {names[top]}: {what}"
    if where:
        sentence += f" {where}"
    sentence += "."
    details = []
    inten = intensity_phrase(key, vals)
    if inten:
        details.append(inten[0].upper() + inten[1:])
    p_typ = statistics.median(probs)
    details.append(f"Wystąpienie zjawiska na tym poziomie jest {chance_word(p_typ)} (szansa ok. {round(p_typ):d}%)")
    text = [sentence, "  " + ". ".join(details) + "."]
    # szerszy zasięg słabszego zjawiska, jeśli różni się od zasięgu najwyższego poziomu
    if len(present) > 1:
        low = present[-1]
        w_low = area_phrase(low, lv, cells)
        if w_low and w_low != where:
            text.append(f"  Słabsze zjawisko (poziom {names[low]}) obejmuje szerszy obszar: {w_low}.")
    return top, "\n".join(text)


def polish_max(day, key, cells, names):
    h = day["hazards"].get(key)
    if not h:
        return 0
    lv = h["level_grid"]
    return max([lv[i][j] for cs in cells.values() for (i, j, _, _) in cs] or [0])


def trend_sentence(day, cells, names):
    """Zmiana poziomów w Polsce względem poprzedniego przebiegu (z bloków 'trend' generatora)."""
    ups = downs = active = 0
    ref = None
    max_now = max_before = 0
    for key in ORDER:
        tr = (day["hazards"].get(key) or {}).get("trend")
        if not tr:
            continue
        ref = ref or tr
        lv = day["hazards"][key]["level_grid"]
        diff = tr["change_grid"]
        for cs in cells.values():
            for (i, j, _, _) in cs:
                now, was = lv[i][j], lv[i][j] - diff[i][j]
                if now > 0 or was > 0:
                    active += 1
                    ups += now > was
                    downs += now < was
                max_now, max_before = max(max_now, now), max(max_before, was)
    if ref is None:
        return ""
    utc = parse_iso(ref["reference_run"]).astimezone(timezone.utc)
    head = f"W porównaniu z poprzednim przebiegiem ({utc:%H}Z, {round(ref['hours_earlier'])} h wcześniej)"
    if not active:
        return f"{head} nadal brak zagrożeń."
    if not ups and not downs:
        return f"{head} prognoza jest praktycznie niezmieniona."
    parts = []
    if ups:
        parts.append(f"poziom zagrożenia wzrósł na {round(100 * ups / active)}% obszaru objętego zjawiskami")
    if downs:
        parts.append(f"poziom zagrożenia spadł na {round(100 * downs / active)}% obszaru objętego zjawiskami")
    s = f"{head} " + " i ".join(parts)
    if max_now != max_before:
        s += f"; najwyższy poziom zmienił się z {names[max_before]} na {names[max_now]}"
    return s + "."


def build_message_pl(swwf, voivs, min_level=1):
    names = swwf["level_names"]
    cells = cells_by_voivodeship(swwf["grid"], voivs)
    day = swwf["days"][0]
    issued = parse_iso(swwf["issued"])
    out = ["SWWF — PROGNOZA ZAGROŻEŃ NA NAJBLIŻSZĄ DOBĘ (PROTOTYP)",
           f"Ważna: {fmt_t(day['valid_from'])} → {fmt_t(day['valid_to'])} (czas polski)",
           f"Przebieg GEFS: {fmt_t(swwf['model_run'])} · wydano {issued:%d.%m %H:%M}",
           ""]
    paragraphs = []
    for key in ORDER:
        res = hazard_paragraph(day, key, names, cells, min_level)
        if res:
            paragraphs.append((res[0], ORDER.index(key), key, res[1]))
    paragraphs.sort(key=lambda t: (-t[0], t[1]))

    # --- w skrócie ---
    if not paragraphs:
        out.append("W SKRÓCIE: w najbliższej dobie nie prognozujemy w Polsce zagrożeń zimowych "
                   "ani istotnych opadów.")
    else:
        top = paragraphs[0][0]
        lead = [p for p in paragraphs if p[0] == top]
        nm = join_pl([TITLE[p[2]].lower() for p in lead])
        if top >= 4:
            tone = "Prognozujemy poważne zagrożenie"
        elif top == 3:
            tone = "Prognozujemy znaczące zagrożenie"
        elif top == 2:
            tone = "Prognozujemy podwyższone zagrożenie"
        else:
            tone = "Zagrożenie jest niewielkie"
        out.append(f"W SKRÓCIE: {tone} — najwyższy poziom to {names[top]} ({nm}).")
        general = polish_max(day, "general_winter_risk", cells, names)
        if general > top:
            out.append(f"Jednoczesne wystąpienie kilku zjawisk podnosi ogólny poziom ryzyka zimowego "
                       f"do {names[general]}.")
    out.append("")
    for _, _, _, text in paragraphs:
        out.append(text)
        out.append("")
    t = trend_sentence(day, cells, names)
    if t:
        out.append(t)
        out.append("")
    out.append("Własna analiza zespołu 30 prognoz GEFS — nie jest oficjalnym ostrzeżeniem IMGW. "
               "Wielkości podano orientacyjnie (mediana zespołu); świeży śnieg w cm bywa przeszacowany.")
    return "\n".join(out)


# ============================================================================= EUROPA ŚRODKOWA (EN)
# Wszystkie cztery kraje objęte SWWF traktowane identycznie: ten sam poziom szczegółowości
# (kraj w całości / większość / część z kierunkiem), kolejność alfabetyczna, bez podziału na regiony.
MIN_COVER_CE = 0.08   # kraje są duże, więc niżej niż dla województw; poniżej: "isolated areas"
COUNTRIES_FILE = "countries_ce.geojson"
COUNTRIES_URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
                 "master/geojson/ne_10m_admin_0_countries.geojson")
CE_ISO = {"DEU": "Germany", "POL": "Poland", "CZE": "Czechia", "SVK": "Slovakia"}
WEEKDAYS_EN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
PHENOMENON_EN = {
    "precip_24h_mm": ["", "light to moderate precipitation", "fairly heavy precipitation",
                      "heavy precipitation", "very heavy precipitation", "extreme precipitation"],
    "snow_24h_cm": ["", "light snowfall", "moderate snowfall", "heavy snowfall",
                    "very heavy snowfall", "extreme snowfall"],
    "cold_min_t2m_c": ["", "frost", "severe frost", "severe frost", "very severe frost", "extreme frost"],
    "snow_squalls": ["", "sudden heavy snow showers", "sudden heavy snow showers",
                     "snow squalls", "severe snow squalls", "extreme snow squalls"],
}
TITLE_EN = {"precip_24h_mm": "Precipitation", "snow_24h_cm": "Snow", "cold_min_t2m_c": "Cold",
            "snow_squalls": "Snow squalls"}
DIR_EN = {("N", ""): "northern", ("S", ""): "southern", ("", "E"): "eastern", ("", "W"): "western",
          ("N", "E"): "north-eastern", ("N", "W"): "north-western",
          ("S", "E"): "south-eastern", ("S", "W"): "south-western"}


def load_countries():
    """-> lista (nazwa angielska, geometria) dla DEU/POL/CZE/SVK, alfabetycznie."""
    if os.path.exists(COUNTRIES_FILE):
        with open(COUNTRIES_FILE, encoding="utf-8") as f:
            data = json.load(f)
        out = [(ft["properties"]["name"], shape(ft["geometry"])) for ft in data["features"]]
        return sorted(out, key=lambda t: t[0])
    print("Brak countries_ce.geojson — pobieram granice państw i zapisuję cache.", file=sys.stderr)
    from shapely.geometry import mapping
    req = urllib.request.Request(COUNTRIES_URL, headers={"User-Agent": "meteopanel-swwf"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode())
    out, feats = [], []
    for ft in data["features"]:
        iso = ft["properties"].get("ISO_A3")
        if iso in CE_ISO:
            g = shape(ft["geometry"]).simplify(0.02)
            out.append((CE_ISO[iso], g))
            feats.append({"type": "Feature", "properties": {"name": CE_ISO[iso], "iso3": iso},
                          "geometry": mapping(g)})
    with open(COUNTRIES_FILE, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": feats}, f, separators=(",", ":"))
    return sorted(out, key=lambda t: t[0])


def fmt_t_en(s):
    d = parse_iso(s)
    zone = {7200: "CEST", 3600: "CET"}.get(int(d.utcoffset().total_seconds()), "local time")
    return f"{WEEKDAYS_EN[d.weekday()]} {d.day:02d} {MONTHS_EN[d.month - 1]} {d:%H:%M} {zone}"


def join_en(items):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def chance_word_en(p):
    if p >= 85:
        return "very likely"
    if p >= 60:
        return "likely"
    if p >= 30:
        return "possible"
    return "unlikely but not ruled out"


def area_phrase_en(level, grid_levels, cells):
    """Ten sam schemat dla każdego kraju: 'the whole of X' / 'most of X' / 'the southern part of X'."""
    pieces, touched_only = [], []
    for name, cs in cells.items():
        if not cs:
            continue
        hit = [c for c in cs if grid_levels[c[0]][c[1]] >= level]
        cover = len(hit) / len(cs)
        if cover >= 0.95:
            pieces.append(f"the whole of {name}")
        elif cover >= MOST_COVER:
            pieces.append(f"most of {name}")
        elif cover >= MIN_COVER_CE:
            d = DIR_EN.get(region_direction(hit, cs), "")
            pieces.append(f"the {d} part of {name}" if d else f"parts of {name}")
        elif hit:
            touched_only.append(name)
    if touched_only:
        pieces.append(f"isolated areas of {join_en(touched_only)}")
    return join_en(pieces)


def intensity_phrase_en(key, vals):
    if key == "snow_squalls":
        return ""
    if key == "cold_min_t2m_c":
        typ, peak = statistics.median(vals), min(vals)
        a, b = f"{round(typ):d}".replace("-", "−"), f"{round(peak):d}".replace("-", "−")
        if a == b:
            return f"Minimum temperature around {a} °C"
        return f"Minimum temperature typically around {a} °C, locally down to {b} °C"
    unit = "mm" if key == "precip_24h_mm" else "cm"
    what = "Precipitation total" if key == "precip_24h_mm" else "Fresh snow depth"
    typ, peak = statistics.median(vals), max(vals)
    if peak < 1:
        return f"{what} below 1 {unit}"
    if round(typ) == round(peak) or peak < 1.5 * typ or peak - typ < 2:
        return f"{what} around {round(peak):d} {unit}"
    return f"{what} typically around {max(1, round(typ)):d} {unit}, locally up to {round(peak):d} {unit}"


def hazard_paragraph_en(day, key, names, cells, min_level):
    h = day["hazards"].get(key)
    if not h:
        return None
    lv = h["level_grid"]
    in_area = [(c[0], c[1]) for cs in cells.values() for c in cs]
    present = sorted({lv[i][j] for i, j in in_area if lv[i][j] >= min_level}, reverse=True)
    if not present:
        return None
    top = present[0]
    area_top = [(i, j) for i, j in in_area if lv[i][j] >= top]
    vals = [h["median_intensity"][i][j] for i, j in area_top]
    probs = [h["probability_grid"][i][j] for i, j in area_top]
    where = area_phrase_en(top, lv, cells)
    what = PHENOMENON_EN[key][top]
    text = [f"{ICON.get(top, '')} {TITLE_EN[key]} — level {names[top]}: {what} over {where}."]
    details = []
    inten = intensity_phrase_en(key, vals)
    if inten:
        details.append(inten)
    p_typ = statistics.median(probs)
    details.append(f"Occurrence at this level is {chance_word_en(p_typ)} (about {round(p_typ):d}% chance)")
    text.append("  " + ". ".join(details) + ".")
    if len(present) > 1:
        low = present[-1]
        w_low = area_phrase_en(low, lv, cells)
        if w_low and w_low != where:
            text.append(f"  The weaker signal (level {names[low]}) covers a wider area: {w_low}.")
    return top, "\n".join(text)


def trend_sentence_en(day, cells, names):
    ups = downs = active = 0
    ref = None
    max_now = max_before = 0
    for key in ORDER:
        tr = (day["hazards"].get(key) or {}).get("trend")
        if not tr:
            continue
        ref = ref or tr
        lv = day["hazards"][key]["level_grid"]
        diff = tr["change_grid"]
        for cs in cells.values():
            for (i, j, _, _) in cs:
                now, was = lv[i][j], lv[i][j] - diff[i][j]
                if now > 0 or was > 0:
                    active += 1
                    ups += now > was
                    downs += now < was
                max_now, max_before = max(max_now, now), max(max_before, was)
    if ref is None:
        return ""
    utc = parse_iso(ref["reference_run"]).astimezone(timezone.utc)
    head = f"Compared with the previous run ({utc:%H}Z, {round(ref['hours_earlier'])} h earlier)"
    if not active:
        return f"{head}, there are still no hazards."
    if not ups and not downs:
        return f"{head}, the forecast is essentially unchanged."
    parts = []
    if ups:
        parts.append(f"hazard levels rose over {round(100 * ups / active)}% of the affected area")
    if downs:
        parts.append(f"hazard levels fell over {round(100 * downs / active)}% of the affected area")
    s = f"{head}, " + " and ".join(parts)
    if max_now != max_before:
        s += f"; the highest level changed from {names[max_before]} to {names[max_now]}"
    return s + "."


def build_message_en(swwf, countries, min_level=1):
    names = swwf["level_names"]
    cells = cells_by_voivodeship(swwf["grid"], countries)   # ta sama procedura: pola siatki wg jednostek
    day = swwf["days"][0]
    issued = parse_iso(swwf["issued"])
    nice = join_en([n for n, _ in countries])
    out = ["SWWF — CENTRAL EUROPE WINTER HAZARD OUTLOOK, NEXT 24 HOURS (PROTOTYPE)",
           f"Valid: {fmt_t_en(day['valid_from'])} → {fmt_t_en(day['valid_to'])}",
           f"Area: {nice} · GEFS run {fmt_t_en(swwf['model_run'])} · issued {fmt_t_en(swwf['issued'])}",
           ""]
    paragraphs = []
    for key in ORDER:
        res = hazard_paragraph_en(day, key, names, cells, min_level)
        if res:
            paragraphs.append((res[0], ORDER.index(key), key, res[1]))
    paragraphs.sort(key=lambda t: (-t[0], t[1]))
    if not paragraphs:
        out.append(f"SUMMARY: no winter hazards or significant precipitation are expected over {nice} "
                   f"during the next 24 hours.")
    else:
        top = paragraphs[0][0]
        lead = join_en([TITLE_EN[p[2]].lower() for p in paragraphs if p[0] == top])
        tone = ("A serious hazard is forecast" if top >= 4 else
                "A significant hazard is forecast" if top == 3 else
                "An elevated hazard is forecast" if top == 2 else "The hazard is low")
        out.append(f"SUMMARY: {tone} — the highest level is {names[top]} ({lead}).")
        general = polish_max(day, "general_winter_risk", cells, names)
        if general > top:
            out.append(f"The combination of several hazards raises the overall winter risk to {names[general]}.")
    out.append("")
    for _, _, _, text in paragraphs:
        out.append(text)
        out.append("")
    t = trend_sentence_en(day, cells, names)
    if t:
        out.append(t)
        out.append("")
    out.append("Own analysis of a 30-member GEFS ensemble — not an official warning. Amounts are indicative "
               "(ensemble median); fresh-snow depth in cm tends to be overestimated.")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("swwf", nargs="?", default="swwf.json")
    ap.add_argument("--out-pl", default="airmet_pl.txt")
    ap.add_argument("--out-ce", default="airmet_ce.txt")
    args = ap.parse_args()
    with open(args.swwf, encoding="utf-8") as f:
        swwf = json.load(f)
    min_level = int(os.environ.get("AIRMET_MIN_LEVEL", "1"))
    pl = build_message_pl(swwf, load_voivodeships(), min_level)
    ce = build_message_en(swwf, load_countries(), min_level)
    for path, text in ((args.out_pl, pl), (args.out_ce, ce)):
        with open(path, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    print(pl)
    print("\n" + "=" * 78 + "\n")
    print(ce)


if __name__ == "__main__":
    main()
