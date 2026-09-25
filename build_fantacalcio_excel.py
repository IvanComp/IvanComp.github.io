from __future__ import annotations

import concurrent.futures
import copy
import datetime as dt
import math
import os
import re
import sys
import time
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

# The bundled document runtime contains openpyxl, while requests/bs4 live in the
# desktop Python user site. Both are read-only dependencies.
sys.path.append("/Users/ivan/Library/Python/3.9/lib/python/site-packages")

import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook, load_workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo


TODAY = dt.date(2026, 9, 5)
OUTPUT = Path("/Users/ivan/Desktop/Site/Guida_Asta_Fantacalcio_Serie_A_2026-27.xlsx")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/140 Safari/537.36"}

URL_GAZZETTA_LIST = "https://www.gazzetta.it/calcio/fantanews/lista-giocatori-fantacalcio-serie-a-2026-27/"
URL_GAZZETTA_HUB = "https://www.gazzetta.it/calcio/fantanews/05-08-2026/fantacalcio-2026-27-titolari-rigoristi-formazioni-squadre-serie-a.shtml"
URL_GAZZETTA_KICKERS = "https://www.gazzetta.it/calcio/fantanews/strumenti-fantacalcio/rigoristi/17-08-2026/rigoristi-serie-a-fantacalcio-tiratori-calci-da-fermo-punizioni.shtml"
URL_GAZZETTA_INJURIES = "https://www.gazzetta.it/calcio/fantanews/strumenti-fantacalcio/indisponibili/lista/"
URL_GAZZETTA_FORMATIONS = "https://www.gazzetta.it/Calcio/prob_form/"
URL_SERIE_A_CALENDAR = "https://www.legaseriea.it/serie-a/news/calendario-della-serie-a-enilive-2026-27"
URL_FC_CURRENT = "https://www.fantacalcio.it/statistiche-serie-a/2026-27/italia"
URL_FC_PREV = "https://www.fantacalcio.it/statistiche-serie-a/2025-26/italia"
URL_ROSTERS = "https://serieaspelare.se/"
URL_TRANSFERMARKT_SEARCH = "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={}"

TEAM_ABBR = {
    "ATA": "Atalanta", "BOL": "Bologna", "CAG": "Cagliari", "COM": "Como",
    "FIO": "Fiorentina", "FRO": "Frosinone", "GEN": "Genoa", "INT": "Inter",
    "JUV": "Juventus", "LAZ": "Lazio", "LEC": "Lecce", "MIL": "Milan",
    "MON": "Monza", "MONZ": "Monza", "NAP": "Napoli", "PAR": "Parma",
    "ROM": "Roma", "SAS": "Sassuolo", "TOR": "Torino", "UDI": "Udinese",
    "VEN": "Venezia",
}
TEAM_CANON = {x.lower(): x for x in [
    "Atalanta", "Bologna", "Cagliari", "Como", "Fiorentina", "Frosinone",
    "Genoa", "Inter", "Juventus", "Lazio", "Lecce", "Milan", "Monza",
    "Napoli", "Parma", "Roma", "Sassuolo", "Torino", "Udinese", "Venezia",
]}
TEAM_CANON.update({"venezia fc": "Venezia"})

ROLE_NAMES = {"P": "Portiere", "D": "Difensore", "C": "Centrocampista", "A": "Attaccante"}
ROLE_SHEET = {"P": "Portieri", "D": "Difensori", "C": "Centrocampisti", "A": "Attaccanti"}
TIER_ORDER = {"TOP": 1, "SEMITOP": 2, "TERZA FASCIA": 3, "QUARTA FASCIA": 4}

# Mese della giornata nel calendario Serie A 2026/27. La 10ª giornata si
# disputa tra il 31 ottobre e il 2 novembre, quindi mantiene entrambi i mesi.
ROUND_MONTH = {
    1: "agosto", 2: "agosto", 3: "settembre", 4: "settembre", 5: "settembre",
    6: "ottobre", 7: "ottobre", 8: "ottobre", 9: "ottobre", 10: "ottobre/novembre",
    11: "novembre", 12: "novembre", 13: "novembre", 14: "dicembre",
    15: "dicembre", 16: "dicembre", 17: "gennaio", 18: "gennaio",
    19: "gennaio", 20: "gennaio", 21: "gennaio", 22: "gennaio",
    23: "febbraio", 24: "febbraio", 25: "febbraio", 26: "febbraio",
    27: "marzo", 28: "marzo", 29: "marzo", 30: "aprile", 31: "aprile",
    32: "aprile", 33: "aprile", 34: "maggio", 35: "maggio",
    36: "maggio", 37: "maggio", 38: "maggio",
}

COLORS = {
    "navy": "16324F", "blue": "1F4E78", "cyan": "DDEBF7", "gold": "FFC000",
    "green": "70AD47", "green_light": "E2F0D9", "orange": "F4B183",
    "orange_light": "FCE4D6", "red": "C00000", "red_light": "F4CCCC",
    "purple": "7030A0", "purple_light": "E4DFEC", "gray": "7F8C8D",
    "gray_light": "E7E6E6", "white": "FFFFFF", "black": "111111",
    "top": "FFD966", "semi": "A9D18E", "third": "BDD7EE", "fourth": "E7E6E6",
}


def fetch(url: str, timeout: int = 40, attempts: int = 4) -> str:
    last = None
    for i in range(attempts):
        try:
            r = requests.get(url, headers=UA, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as exc:
            last = exc
            time.sleep(0.6 * (i + 1))
    raise RuntimeError(f"Impossibile scaricare {url}: {last}")


def clean_text(value: str | None) -> str:
    return " ".join((value or "").replace("\xa0", " ").split())


def add_return_month(status: str | None) -> str | None:
    """Aggiunge il mese del calendario a uno stato come 'Rientro alla 14'."""
    if not status or re.search(r"\([^)]+\)\s*$", status):
        return status
    match = re.search(r"Rientro alla\s+(\d+)", status, flags=re.IGNORECASE)
    if not match:
        return status
    month = ROUND_MONTH.get(int(match.group(1)))
    return f"{status} ({month})" if month else status


def ascii_norm(value: str | None) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", value)


def words_norm(value: str | None) -> list[str]:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
    return re.findall(r"[a-z0-9]+", value)


def title_from_slug(slug: str) -> str:
    particles = {"de", "del", "della", "di", "da", "van", "der", "el", "al", "do"}
    out = []
    for i, token in enumerate(slug.split("-")):
        out.append(token.lower() if i and token.lower() in particles else token.capitalize())
    return " ".join(out)


def split_display_name(value: str | None) -> tuple[str, str]:
    value = clean_text(value)
    match = re.match(r"^(.+?)\s+([A-Za-z]{1,3}(?:\.[A-Za-z]{1,3})*\.)$", value)
    if not match:
        return value, ""
    return match.group(1), re.sub(r"[^A-Za-z]", "", match.group(2)).lower()


def parse_num(text: str | None):
    text = clean_text(text)
    if not text or text in {"-", "–", "—", "n.d."}:
        return None
    try:
        return float(text.replace(".", "").replace(",", "."))
    except Exception:
        return None


def as_int(value):
    if value is None:
        return None
    try:
        return int(float(value))
    except Exception:
        return None


def extract_player_id(url: str) -> str | None:
    parts = urlparse(url).path.strip("/").split("/")
    for p in parts:
        if p.isdigit():
            return p
    return None


def player_slug_gazzetta(url: str) -> str:
    parts = urlparse(url).path.strip("/").split("/")
    if len(parts) >= 2 and parts[-1].isdigit():
        return parts[-2]
    return parts[-1]


def scrape_gazzetta_list() -> list[dict]:
    soup = BeautifulSoup(fetch(URL_GAZZETTA_LIST), "html.parser")
    players = []
    for tr in soup.select("table tr"):
        team = tr.select_one(".hidden-team-name")
        name = tr.select_one(".field-giocatore a")
        role = tr.select_one(".field-ruolo")
        quote = tr.select_one(".field-q")
        if not all([team, name, role, quote]):
            continue
        url = name.get("href", "")
        slug = player_slug_gazzetta(url)
        players.append({
            "name_gazzetta": clean_text(name.get_text()),
            "full_name_gazzetta": title_from_slug(slug),
            "slug_gazzetta": slug,
            "team_gazzetta": TEAM_CANON.get(clean_text(team.get_text()).lower(), clean_text(team.get_text()).title()),
            "role": clean_text(role.get_text()),
            "quote": as_int(parse_num(quote.get_text())) or 0,
            "gazzetta_url": url,
            "gazzetta_id": extract_player_id(url),
        })
    if len(players) < 550:
        raise RuntimeError(f"Listone Gazzetta incompleto: {len(players)} righe")
    return players


def scrape_fantacalcio_stats(url: str) -> list[dict]:
    soup = BeautifulSoup(fetch(url), "html.parser")
    rows = []
    for tr in soup.select("tr.player-row"):
        a = tr.select_one(".player-name a")
        team_cell = tr.select_one('[data-col-key="sq"]')
        if not a or not team_cell:
            continue
        vals = {}
        for td in tr.select("td"):
            key = td.get("data-col-key")
            if key:
                vals[key] = clean_text(td.get_text())
        purl = a.get("href", "")
        pid = extract_player_id(purl)
        rig = vals.get("rig", "")
        rig_scored = rig_taken = None
        m = re.search(r"(\d+)\s*/\s*(\d+)", rig)
        if m:
            rig_scored, rig_taken = int(m.group(1)), int(m.group(2))
        rows.append({
            "fc_display": clean_text(a.get_text()),
            "fc_profile_url": purl,
            "fc_id": pid,
            "team_current": TEAM_ABBR.get(clean_text(team_cell.get_text()), clean_text(team_cell.get_text()).title()),
            "pg": as_int(parse_num(vals.get("pg"))) or 0,
            "mv": parse_num(vals.get("mv")),
            "fm": parse_num(vals.get("mfv")),
            "goals": as_int(parse_num(vals.get("gol"))) or 0,
            "goals_conceded": as_int(parse_num(vals.get("gs"))) or 0,
            "pen_scored": rig_scored,
            "pen_taken": rig_taken,
            "pen_saved": as_int(parse_num(vals.get("rp"))) or 0,
            "assists": as_int(parse_num(vals.get("ass"))) or 0,
            "yellow": as_int(parse_num(vals.get("amm"))) or 0,
            "red": as_int(parse_num(vals.get("esp"))) or 0,
        })
    return rows


def scrape_fc_profile(row: dict) -> dict:
    soup = BeautifulSoup(fetch(row["fc_profile_url"], timeout=35), "html.parser")
    h1 = soup.select_one("h1") or soup.select_one('[itemprop="name"]')
    birth = soup.select_one('meta[itemprop="birthdate"]')
    height = soup.select_one('[itemprop="height"]')
    nat = soup.select_one(".nationalities")
    foot = None
    for dt_node in soup.select(".player-data dt"):
        if clean_text(dt_node.get_text()).lower() == "piede":
            dd = dt_node.find_next_sibling("dd")
            if dd:
                foot = clean_text(dd.get_text())
    out = dict(row)
    out.update({
        "full_name_fc": clean_text(h1.get_text()) if h1 else row["fc_display"],
        "birthdate": birth.get("content") if birth else None,
        "height_cm": as_int(parse_num(clean_text(height.get_text()).replace("cm", ""))) if height else None,
        "nationality": clean_text(nat.get_text()) if nat else None,
        "foot": foot,
    })
    return out


def enrich_fc_profiles(rows: list[dict]) -> list[dict]:
    enriched = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=18) as pool:
        futures = {pool.submit(scrape_fc_profile, row): row for row in rows}
        for future in concurrent.futures.as_completed(futures):
            try:
                enriched.append(future.result())
            except Exception:
                fallback = dict(futures[future])
                fallback["full_name_fc"] = fallback["fc_display"]
                fallback.update({"birthdate": None, "height_cm": None, "nationality": None, "foot": None})
                enriched.append(fallback)
    enriched.sort(key=lambda x: int(x["fc_id"] or 9999999))
    return enriched


def scrape_rosters() -> list[dict]:
    soup = BeautifulSoup(fetch(URL_ROSTERS), "html.parser")
    table = soup.select_one("table.rosa-table")
    rows = []
    if not table:
        return rows
    for tr in table.select("tbody tr"):
        name = clean_text(tr.get("data-name"))
        team = TEAM_CANON.get(clean_text(tr.get("data-team")).lower(), clean_text(tr.get("data-team")))
        if not name:
            continue
        rows.append({
            "full_name_roster": name,
            "team_roster": team,
            "age_roster": as_int(parse_num(tr.get("data-age"))),
            "nationality_roster": clean_text(tr.get("data-nationality")),
            "number": as_int(parse_num(tr.get("data-number"))),
        })
    return rows


def scrape_transfermarkt_demographics(name: str) -> dict | None:
    query = requests.utils.quote(name)
    search_url = URL_TRANSFERMARKT_SEARCH.format(query)
    soup = BeautifulSoup(fetch(search_url, timeout=35), "html.parser")
    choices = {}
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        label = clean_text(a.get_text())
        if "/profil/spieler/" in href and label:
            full_url = "https://www.transfermarkt.com" + href.split("?")[0]
            choices[full_url] = label
    if not choices:
        return None
    target = ascii_norm(name)
    ranked = []
    for url, label in choices.items():
        candidate = ascii_norm(label)
        score = SequenceMatcher(None, target, candidate).ratio()
        if target in candidate or candidate in target:
            score = max(score, 0.97)
        ranked.append((score, url, label))
    ranked.sort(reverse=True)
    score, profile_url, _ = ranked[0]
    if score < 0.76:
        return None
    profile = BeautifulSoup(fetch(profile_url, timeout=35), "html.parser")
    birth_node = profile.select_one('[itemprop="birthDate"]')
    nat_node = profile.select_one('[itemprop="nationality"]')
    height_node = profile.select_one('[itemprop="height"]')
    foot = None
    for node in profile.select(".info-table__content--regular"):
        if clean_text(node.get_text()).lower() == "foot:":
            nxt = node.find_next_sibling()
            if nxt:
                foot = clean_text(nxt.get_text())
            break
    birth_iso = None
    if birth_node:
        m = re.search(r"(\d{2})/(\d{2})/(\d{4})", clean_text(birth_node.get_text()))
        if m:
            birth_iso = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    height_cm = None
    if height_node:
        m = re.search(r"(\d)[,.](\d{2})", clean_text(height_node.get_text()))
        if m:
            height_cm = int(m.group(1)) * 100 + int(m.group(2))
    return {
        "birthdate": birth_iso,
        "nationality": clean_text(nat_node.get_text()) if nat_node else None,
        "height_cm": height_cm,
        "foot": foot,
        "source": profile_url,
    }


def name_similarity(g: dict, candidate_name: str, candidate_display: str | None = None) -> float:
    a = ascii_norm(g["full_name_gazzetta"])
    b = ascii_norm(candidate_name)
    if a == b:
        return 1.0
    if a in b or b in a:
        return 0.99
    # Gazzetta uses "Do Nascimento" / "Giovane" and a few common-name variants.
    seq = SequenceMatcher(None, a, b).ratio()
    aw, bw = words_norm(g["full_name_gazzetta"]), words_norm(candidate_name)
    if aw and bw:
        surname = SequenceMatcher(None, "".join(aw[1:]), "".join(bw[1:])).ratio() if len(aw) > 1 and len(bw) > 1 else 0
        last = SequenceMatcher(None, aw[-1], bw[-1]).ratio()
        first = SequenceMatcher(None, aw[0], bw[0]).ratio()
        seq = max(seq, 0.55 * last + 0.45 * first, 0.7 * surname + 0.3 * first)
    # Both public list pages often abbreviate a player as "Surname I.".  Use
    # that convention as a second independent signal, including Lo./Lu. and D.S.
    g_base, g_initial = split_display_name(g.get("name_gazzetta"))
    c_base, c_initial = split_display_name(candidate_display or candidate_name)
    if ascii_norm(g_base) == ascii_norm(c_base):
        display_score = 0.965
        first_name = (words_norm(g.get("full_name_gazzetta")) or [""])[0]
        if c_initial and first_name:
            display_score += 0.03 if first_name.startswith(c_initial) or c_initial.startswith(first_name[:1]) else -0.07
        if g_initial and c_initial and not (g_initial.startswith(c_initial) or c_initial.startswith(g_initial)):
            display_score -= 0.04
        seq = max(seq, display_score)
    return seq


def match_people(gplayers: list[dict], candidates: list[dict], name_field: str, team_field: str | None = None) -> dict[int, dict]:
    result = {}
    used = set()
    # Exact normalized names first.
    exact = defaultdict(list)
    for j, c in enumerate(candidates):
        exact[ascii_norm(c.get(name_field))].append(j)
    for i, g in enumerate(gplayers):
        ids = exact.get(ascii_norm(g["full_name_gazzetta"]), [])
        if len(ids) == 1:
            result[i] = candidates[ids[0]]
            used.add(ids[0])
    # Fuzzy matching, with a small bonus for the pre-market team.
    for i, g in enumerate(gplayers):
        if i in result:
            continue
        scored = []
        for j, c in enumerate(candidates):
            if j in used:
                continue
            score = name_similarity(g, c.get(name_field, ""), c.get("fc_display"))
            if team_field and c.get(team_field) == g.get("team_gazzetta"):
                score += 0.025
            scored.append((score, j))
        if not scored:
            continue
        scored.sort(reverse=True)
        best_score, best_j = scored[0]
        second = scored[1][0] if len(scored) > 1 else 0
        if best_score >= 0.89 and (best_score - second >= 0.025 or best_score >= 0.985):
            result[i] = candidates[best_j]
            used.add(best_j)
    return result


def extract_section_text(soup: BeautifulSoup, heading_contains: str) -> str:
    heading_contains = heading_contains.lower()
    headings = soup.find_all(["h2", "h3"])
    for idx, h in enumerate(headings):
        if heading_contains not in clean_text(h.get_text()).lower():
            continue
        texts = []
        current = h
        for node in h.find_all_next(["h2", "h3", "p"]):
            if node is h:
                continue
            if node.name in {"h2", "h3"}:
                break
            txt = clean_text(node.get_text())
            if txt and txt != "—":
                texts.append(txt)
        return " ".join(texts)
    return ""


def scrape_team_guides() -> dict[str, dict]:
    hub = BeautifulSoup(fetch(URL_GAZZETTA_HUB), "html.parser")
    links = {}
    for a in hub.find_all("a", href=True):
        text = clean_text(a.get_text())
        href = a.get("href", "")
        m = re.match(r"(.+?) al fantacalcio$", text, flags=re.I)
        if m and "fantacalcio-2026-27" in href:
            team = TEAM_CANON.get(m.group(1).lower(), m.group(1).title())
            links[team] = href.split("?")[0]
    guides = {}
    for team, url in links.items():
        soup = BeautifulSoup(fetch(url), "html.parser")
        formation = extract_section_text(soup, "probabile formazione")
        surprises = extract_section_text(soup, "possibili sorprese")
        recommended = extract_section_text(soup, "chi prendere al fantacalcio")
        penalties = extract_section_text(soup, "chi batte i rigori")
        # Pull only the first formation paragraph to avoid article chrome.
        formation = formation.split("VIDEO:")[0].strip()
        guides[team] = {
            "url": url, "formation": formation, "surprises": surprises,
            "recommended": recommended, "penalties_text": penalties,
        }
    return guides


def scrape_kickers() -> dict[str, dict]:
    soup = BeautifulSoup(fetch(URL_GAZZETTA_KICKERS), "html.parser")
    main = soup.select_one(".gz-content-center-col") or soup
    lines = [clean_text(x) for x in main.get_text("\n", strip=True).splitlines() if clean_text(x)]
    teams = set(TEAM_CANON.values())
    result = {}
    i = 0
    while i < len(lines):
        if lines[i] in teams:
            team = lines[i]
            pen = free = ""
            block = lines[i + 1:i + 8]
            for j, line in enumerate(block):
                if line.lower().startswith("calci di rigore") and j + 1 < len(block):
                    pen = block[j + 1].rstrip(".")
                if line.lower().startswith("calci di punizione") and j + 1 < len(block):
                    free = block[j + 1].rstrip(".")
            result[team] = {
                "penalties": [clean_text(x) for x in pen.split(",") if clean_text(x)],
                "free_kicks": [clean_text(x) for x in free.split(",") if clean_text(x)],
            }
        i += 1
    return result


def scrape_injuries() -> list[dict]:
    soup = BeautifulSoup(fetch(URL_GAZZETTA_INJURIES), "html.parser")
    result = []
    for card in soup.select(".bck-team-card"):
        team_node = card.select_one(".bck-team-logo span")
        if not team_node:
            continue
        team = TEAM_CANON.get(clean_text(team_node.get_text()).lower(), clean_text(team_node.get_text()))
        for item in card.select(".bck-unavailable-player"):
            a = item.select_one("a.bck-player-link")
            name = item.select_one(".bck-player-name p")
            status = item.select_one(".bck-player-state")
            comment = item.select_one(".bck-player-comment")
            if not name:
                continue
            slug = player_slug_gazzetta(a.get("href", "")) if a else ""
            result.append({
                "team": team, "name": clean_text(name.get_text()), "slug": slug,
                "status": clean_text(status.get_text()) if status else "Indisponibile",
                "comment": clean_text(comment.get_text()) if comment else "",
                "url": a.get("href", "") if a else URL_GAZZETTA_INJURIES,
            })
    return result


def scrape_ballottaggi() -> dict[str, list[tuple[str, str]]]:
    """Legge i testa-a-testa espliciti dalle probabili formazioni Gazzetta."""
    result = defaultdict(list)
    pair_re = re.compile(
        r"([^,;%]+?)-([^,;%]+?)\s*[,;]?\s*\d+\s*%?\s*[-/]\s*\d+\s*%?",
        flags=re.I,
    )
    for url in [URL_GAZZETTA_FORMATIONS]:
        soup = BeautifulSoup(fetch(url), "html.parser")
        for box in soup.select(".bck-box-match-details"):
            for side in ["home", "away"]:
                team_node = box.select_one(f".details-team.is--{side} .details-team__name")
                if not team_node:
                    continue
                raw_team = clean_text(team_node.get_text())
                team = TEAM_CANON.get(raw_team.lower(), raw_team)
                paragraph = next(
                    (p for p in box.select(f"p.is--{side}") if "Ballottaggio:" in clean_text(p.get_text())),
                    None,
                )
                if not paragraph:
                    continue
                text = clean_text(paragraph.get_text()).split(":", 1)[-1]
                for left, right in pair_re.findall(text):
                    pair = (clean_text(left).strip(" .;"), clean_text(right).strip(" .;"))
                    if pair[0].lower() != "nessuno" and pair not in result[team]:
                        result[team].append(pair)
    # La gara del venerdì scompare dalla pagina generale dopo il fischio finale.
    # Conserviamo l'ultimo aggiornamento Gazzetta del 4 settembre per completare
    # Genoa e Como nella fotografia della 3ª giornata.
    completed_match = {
        "Genoa": [("Amorim", "Sow"), ("Vitinha", "Osmajic")],
        "Como": [("Valle", "Kaiki"), ("Couto", "Smolcic"), ("Milla", "Perrone")],
    }
    for team, pairs in completed_match.items():
        if team not in result:
            result[team] = pairs
    return dict(result)


def player_aliases(player: dict) -> list[str]:
    full = player["full_name"]
    display = player["name_gazzetta"]
    aliases = {ascii_norm(full), ascii_norm(display)}
    ws = words_norm(full)
    if ws:
        aliases.add("".join(ws[1:]) if len(ws) > 1 else ws[0])
        aliases.add(ws[-1])
    base = re.sub(r"\s+[A-Z](?:\.[A-Z])?\.$", "", display).strip()
    aliases.add(ascii_norm(base))
    return sorted((x for x in aliases if len(x) >= 4), key=len, reverse=True)


def mentions(text: str, player: dict) -> bool:
    nt = ascii_norm(text)
    return any(alias in nt for alias in player_aliases(player))


def best_name_match(name: str, players: list[dict]) -> dict | None:
    n = ascii_norm(name)
    if not n:
        return None
    scored = []
    for p in players:
        aliases = player_aliases(p)
        score = max([SequenceMatcher(None, n, a).ratio() for a in aliases] + [0])
        if any(n == a for a in aliases):
            score = 1.0
        scored.append((score, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1] if scored and scored[0][0] >= 0.73 else None


def age_on(birthdate: str | None) -> int | None:
    if not birthdate:
        return None
    try:
        born = dt.date.fromisoformat(birthdate[:10])
    except Exception:
        return None
    return TODAY.year - born.year - ((TODAY.month, TODAY.day) < (born.month, born.day))


def percentile(values: list[float], value: float) -> float:
    if not values:
        return 0.0
    less = sum(v < value for v in values)
    equal = sum(v == value for v in values)
    return (less + 0.5 * equal) / len(values)


def assemble_players() -> tuple[list[dict], dict]:
    gplayers = scrape_gazzetta_list()
    current_raw = scrape_fantacalcio_stats(URL_FC_CURRENT)
    previous = scrape_fantacalcio_stats(URL_FC_PREV)
    current = enrich_fc_profiles(current_raw)
    rosters = scrape_rosters()
    guides = scrape_team_guides()
    kickers = scrape_kickers()
    injuries = scrape_injuries()
    ballottaggi = scrape_ballottaggi()

    fc_match = match_people(gplayers, current, "full_name_fc", "team_current")
    roster_match = match_people(gplayers, rosters, "full_name_roster", "team_roster")
    prev_match = match_people(gplayers, previous, "fc_display", "team_current")
    prev_by_id = {x["fc_id"]: x for x in previous if x.get("fc_id")}
    # Fetch older profiles only where current data and the roster control source
    # do not already provide an age. This fills residual unmatched profiles.
    previous_profiles_needed = []
    seen_prev = set()
    for i in range(len(gplayers)):
        if i in fc_match or i in roster_match:
            continue
        candidate = prev_match.get(i)
        if candidate and candidate.get("fc_id") not in seen_prev:
            previous_profiles_needed.append(candidate)
            seen_prev.add(candidate.get("fc_id"))
    previous_profiles = {x.get("fc_id"): x for x in enrich_fc_profiles(previous_profiles_needed)} if previous_profiles_needed else {}

    assembled = []
    for i, g in enumerate(gplayers):
        fc = fc_match.get(i)
        roster = roster_match.get(i)
        prev_candidate = prev_match.get(i)
        prev_profile = previous_profiles.get((prev_candidate or {}).get("fc_id"))
        p = dict(g)
        p["full_name"] = (fc or {}).get("full_name_fc") or (roster or {}).get("full_name_roster") or (prev_profile or {}).get("full_name_fc") or g["full_name_gazzetta"]
        # Il listone Gazzetta aggiornato dopo la chiusura del mercato è la fonte
        # autorevole per appartenenza alla Serie A e squadra attuale. Le fonti
        # secondarie restano utili solo per anagrafiche e statistiche.
        p["team_current"] = g["team_gazzetta"]
        p["team_verified"] = True
        p["fc_match"] = bool(fc)
        p["roster_match"] = bool(roster)
        p["transferred"] = False
        p["birthdate"] = (fc or {}).get("birthdate") or (prev_profile or {}).get("birthdate")
        p["age"] = age_on(p["birthdate"]) or (roster or {}).get("age_roster")
        p["nationality"] = (fc or {}).get("nationality") or (roster or {}).get("nationality_roster") or (prev_profile or {}).get("nationality")
        p["height_cm"] = (fc or {}).get("height_cm") or (prev_profile or {}).get("height_cm")
        p["foot"] = (fc or {}).get("foot") or (prev_profile or {}).get("foot")
        p["shirt_number"] = (roster or {}).get("number")
        p["demographic_source"] = (fc or {}).get("fc_profile_url") or (prev_profile or {}).get("fc_profile_url") or (URL_ROSTERS if roster else None)
        for field in ["pg", "mv", "fm", "goals", "goals_conceded", "pen_scored", "pen_taken", "pen_saved", "assists", "yellow", "red"]:
            p[field] = (fc or {}).get(field)
        p["fc_profile_url"] = (fc or {}).get("fc_profile_url")
        prev = prev_by_id.get((fc or {}).get("fc_id")) or prev_candidate
        for field in ["pg", "mv", "fm", "goals", "assists", "pen_scored", "pen_taken", "pen_saved", "yellow", "red"]:
            p[f"prev_{field}"] = (prev or {}).get(field)
        assembled.append(p)

    # Last-resort demographic lookup for players in Gazzetta but absent from
    # the two secondary roster feeds.
    missing_age = [p for p in assembled if p.get("age") is None]
    if missing_age:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(scrape_transfermarkt_demographics, p["full_name"]): p for p in missing_age}
            for future in concurrent.futures.as_completed(futures):
                p = futures[future]
                try:
                    demo = future.result()
                except Exception:
                    demo = None
                if not demo:
                    continue
                p["birthdate"] = demo.get("birthdate") or p.get("birthdate")
                p["age"] = age_on(p["birthdate"])
                p["nationality"] = p.get("nationality") or demo.get("nationality")
                p["height_cm"] = p.get("height_cm") or demo.get("height_cm")
                p["foot"] = p.get("foot") or demo.get("foot")
                p["demographic_source"] = demo.get("source")

    # Add guide flags by current squad.
    for p in assembled:
        guide = guides.get(p["team_current"], {})
        formation = guide.get("formation", "")
        # The formation paragraph starts after ':' and ends before Allenatore.
        xi_text = formation.split(":", 1)[-1].split("Allenatore", 1)[0] if formation else ""
        p["probable_xi"] = mentions(xi_text, p)
        p["gazzetta_surprise"] = mentions(guide.get("surprises", ""), p)
        p["gazzetta_recommended"] = mentions(guide.get("recommended", ""), p)
        p["guide_url"] = guide.get("url")

    # Kicker hierarchy, resolved inside each current squad.
    by_team = defaultdict(list)
    for p in assembled:
        by_team[p["team_current"]].append(p)
        p["ballottaggio_rivals"] = []
    for team, pairs in ballottaggi.items():
        pool = by_team.get(team, [])
        for left_name, right_name in pairs:
            left = best_name_match(left_name, pool)
            right = best_name_match(right_name, pool)
            if left:
                rival = right["name_gazzetta"] if right else right_name
                if rival not in left["ballottaggio_rivals"]:
                    left["ballottaggio_rivals"].append(rival)
            if right:
                rival = left["name_gazzetta"] if left else left_name
                if rival not in right["ballottaggio_rivals"]:
                    right["ballottaggio_rivals"].append(rival)
    for p in assembled:
        p["penalty_rank"] = None
        p["free_kick_rank"] = None
    for team, data in kickers.items():
        pool = by_team.get(team, [])
        for rank, name in enumerate(data.get("penalties", []), 1):
            match = best_name_match(name, pool)
            if match and match.get("penalty_rank") is None:
                match["penalty_rank"] = rank
        for rank, name in enumerate(data.get("free_kicks", []), 1):
            match = best_name_match(name, pool)
            if match and match.get("free_kick_rank") is None:
                match["free_kick_rank"] = rank

    # Current injury status, preferably matched by full slug, otherwise within squad.
    by_slug = {ascii_norm(p["slug_gazzetta"]): p for p in assembled}
    for p in assembled:
        p["injury_status"] = None
        p["injury_note"] = None
        p["injury_url"] = None
    for inj in injuries:
        match = by_slug.get(ascii_norm(inj["slug"]))
        if not match:
            match = best_name_match(inj["name"], by_team.get(inj["team"], []))
        if match:
            match["injury_status"] = add_return_month(inj["status"])
            match["injury_note"] = inj["comment"]
            match["injury_url"] = inj["url"]

    # Role-specific features and score.
    quotes = {r: [p["quote"] for p in assembled if p["role"] == r] for r in ROLE_NAMES}
    prev_form_values = defaultdict(list)
    for p in assembled:
        pg = p.get("prev_pg") or 0
        fm = p.get("prev_fm") or 0
        bonus = (p.get("prev_goals") or 0) + 0.55 * (p.get("prev_assists") or 0)
        form = (min(pg, 38) / 38) * 0.35 + min(max(fm - 5.2, 0) / 4.5, 1) * 0.4 + min(bonus / (15 if p["role"] == "A" else 10), 1) * 0.25
        p["prev_form_raw"] = form
        prev_form_values[p["role"]].append(form)

    for p in assembled:
        q_pct = percentile(quotes[p["role"]], p["quote"])
        f_pct = percentile(prev_form_values[p["role"]], p["prev_form_raw"])
        score = 68 * q_pct + 7 * f_pct
        score += 10 if p["probable_xi"] else 0
        score += 4 if p["gazzetta_recommended"] else 0
        score += 6 if p["penalty_rank"] == 1 else (3 if p["penalty_rank"] else 0)
        score += 2 if p["free_kick_rank"] == 1 else (1 if p["free_kick_rank"] else 0)
        score += min((p.get("pg") or 0), 2) * 1.5
        if p["injury_status"]:
            m = re.search(r"(\d+)", p["injury_status"])
            score -= 9 if m and int(m.group(1)) >= 8 else 5
        if not p["team_verified"]:
            score -= 8
        score += 2 if p["gazzetta_surprise"] else 0
        p["score"] = round(max(0, min(100, score)), 1)

    # Scarce upper tiers, broad fourth tier: useful for an actual auction shortlist.
    for role in ROLE_NAMES:
        pool = [p for p in assembled if p["role"] == role]
        pool.sort(key=lambda x: (x["score"], x["quote"]), reverse=True)
        n = len(pool)
        cuts = (math.ceil(n * 0.10), math.ceil(n * 0.25), math.ceil(n * 0.50))
        for rank, p in enumerate(pool, 1):
            p["role_rank"] = rank
            if rank <= cuts[0]:
                p["tier"] = "TOP"
            elif rank <= cuts[1]:
                p["tier"] = "SEMITOP"
            elif rank <= cuts[2]:
                p["tier"] = "TERZA FASCIA"
            else:
                p["tier"] = "QUARTA FASCIA"

    # Star bets and compact Gazzetta-style tags.
    for p in assembled:
        stars = 0
        if p["gazzetta_surprise"]:
            stars = 2 if (p["probable_xi"] or (p.get("pg") or 0) >= 1) else 1
            if p["probable_xi"] and (p.get("age") or 99) <= 24 and p["tier"] not in {"TOP"}:
                stars = 3
        elif (p.get("age") or 99) <= 22 and p["probable_xi"] and p["tier"] in {"SEMITOP", "TERZA FASCIA", "QUARTA FASCIA"}:
            stars = 2 if p["quote"] >= 8 else 1
        elif not p.get("prev_pg") and p["gazzetta_recommended"] and p["tier"] != "TOP":
            stars = 1
        p["stars"] = "★" * stars

        if p["ballottaggio_rivals"]:
            titularity = "Ballottaggio (" + " / ".join(p["ballottaggio_rivals"]) + ")"
        elif p["probable_xi"] and (p.get("pg") or 0) >= 2 and not p["injury_status"]:
            titularity = "Titolare fisso"
        elif p["probable_xi"]:
            titularity = "Titolare probabile"
        else:
            titularity = "Rotazione / riserva"
        p["titularity"] = titularity

        tags = [titularity]
        if p["penalty_rank"] == 1:
            tags.append("Rigorista principale")
        elif p["penalty_rank"]:
            tags.append("In lista rigori")
        if p["free_kick_rank"]:
            tags.append("Calci piazzati")
        if p["gazzetta_recommended"]:
            tags.append("Consigliato Gazzetta")
        if p["gazzetta_surprise"]:
            tags.append("Scommessa Gazzetta")
        if (p.get("age") or 99) <= 22:
            tags.append("Under 23")
        if (p.get("prev_pg") or 0) >= 30 and (p.get("prev_mv") or 0) >= 5.9:
            tags.append("Garanzia voto")
        bonus_threshold = {"P": 0, "D": 5, "C": 8, "A": 12}[p["role"]]
        prev_bonus = (p.get("prev_goals") or 0) + (p.get("prev_assists") or 0)
        if p["role"] != "P" and prev_bonus >= bonus_threshold:
            tags.append("Portatore di bonus")
        if p["injury_status"]:
            tags.extend(["Rischio infortunio", "Indisponibile ora"])
            m = re.search(r"(\d+)", p["injury_status"])
            if m and int(m.group(1)) >= 8:
                tags.append("Rientro lungo")
        if not p.get("prev_pg") and p["quote"] >= 4:
            tags.append("Novità / ritorno in A")
        if not p["team_verified"]:
            tags.append("Rosa da verificare")
        if p["transferred"]:
            tags.append("Squadra aggiornata post-mercato")
        p["tags"] = " · ".join(dict.fromkeys(tags))

    meta = {
        "gazzetta_count": len(gplayers),
        "fc_current_count": len(current),
        "fc_matches": len(fc_match),
        "roster_count": len(rosters),
        "roster_matches": len(roster_match),
        "guide_teams": len(guides),
        "kicker_teams": len(kickers),
        "injuries": len(injuries),
        "ballottaggi": sum(len(v) for v in ballottaggi.values()),
    }
    return assembled, meta


MASTER_HEADERS = [
    "Fascia", "Score asta", "✓", "Scommessa", "Nome",
    "Squadra attuale", "Quotazione Gazzetta", "Titolarità", "Tag",
    "Età", "Nazionalità", "Piede",
    "Rigorista", "Punizioni", "Stato fisico / rientro",
    "PG 26/27", "MV 26/27", "FM 26/27", "Gol 26/27", "Assist 26/27", "Rigori 26/27",
    "PG 25/26", "MV 25/26", "FM 25/26", "Gol 25/26", "Assist 25/26", "Rigori 25/26",
    "Scheda Gazzetta", "Scheda statistiche", "Fonte gerarchie",
]


def value_row(p: dict) -> list:
    def rig(scored, taken):
        return f"{scored}/{taken}" if scored is not None and taken is not None else None
    return [
        p["tier"], p["score"], "☐", p["stars"], p["name_gazzetta"],
        p["team_current"], p["quote"], p["titularity"], p["tags"],
        p.get("age"), p.get("nationality"), p.get("foot"),
        ("1°" if p.get("penalty_rank") == 1 else (f"{p['penalty_rank']}°" if p.get("penalty_rank") else None)),
        ("1°" if p.get("free_kick_rank") == 1 else (f"{p['free_kick_rank']}°" if p.get("free_kick_rank") else None)),
        p.get("injury_status"), p.get("pg"), p.get("mv"), p.get("fm"), p.get("goals"), p.get("assists"),
        rig(p.get("pen_scored"), p.get("pen_taken")),
        p.get("prev_pg"), p.get("prev_mv"), p.get("prev_fm"), p.get("prev_goals"), p.get("prev_assists"),
        rig(p.get("prev_pen_scored"), p.get("prev_pen_taken")),
        p.get("gazzetta_url"), p.get("fc_profile_url"), p.get("guide_url"),
    ]


def style_title(ws, title: str, subtitle: str, end_col: int):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=end_col)
    c = ws.cell(1, 1, title)
    c.font = Font(name="Arial", size=20, bold=True, color=COLORS["white"])
    c.fill = PatternFill("solid", fgColor=COLORS["navy"])
    c.alignment = Alignment(vertical="center")
    ws.row_dimensions[1].height = 34
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=end_col)
    c = ws.cell(2, 1, subtitle)
    c.font = Font(name="Arial", size=10, italic=True, color=COLORS["blue"])
    c.fill = PatternFill("solid", fgColor=COLORS["cyan"])
    c.alignment = Alignment(vertical="center")
    ws.row_dimensions[2].height = 25


def apply_table_style(ws, header_row: int, start_row: int, end_row: int, end_col: int, table_name: str):
    header_fill = PatternFill("solid", fgColor=COLORS["blue"])
    for cell in ws[header_row]:
        if cell.column <= end_col:
            cell.font = Font(name="Arial", size=9, bold=True, color=COLORS["white"])
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[header_row].height = 36
    for row in ws.iter_rows(min_row=start_row, max_row=end_row, max_col=end_col):
        for cell in row:
            cell.font = Font(name="Arial", size=9, color=COLORS["black"])
            cell.alignment = Alignment(vertical="top", wrap_text=False)
        row[0].fill = PatternFill("solid", fgColor={
            "TOP": COLORS["top"], "SEMITOP": COLORS["semi"],
            "TERZA FASCIA": COLORS["third"], "QUARTA FASCIA": COLORS["fourth"],
        }.get(row[0].value, COLORS["white"]))
        row[2].alignment = Alignment(horizontal="center", vertical="center")
        if row[3].value:
            row[3].font = Font(name="Arial", size=11, bold=True, color=COLORS["gold"])
        if row[14].value:
            row[14].fill = PatternFill("solid", fgColor=COLORS["red_light"])
            row[14].font = Font(name="Arial", size=9, bold=True, color=COLORS["red"])
    if end_row >= start_row:
        end_letter = get_column_letter(end_col)
        ref = f"A{header_row}:{end_letter}{end_row}"
        tab = Table(displayName=table_name, ref=ref)
        tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        ws.add_table(tab)
    # Nessuna riga o colonna bloccata, anche dopo l'importazione in Google Sheets.
    ws.freeze_panes = None
    ws.auto_filter.ref = f"A{header_row}:{get_column_letter(end_col)}{end_row}"
    ws.sheet_view.showGridLines = False
    ws.row_dimensions.group(start_row, end_row, hidden=False)


def set_player_widths(ws):
    widths = {
        "A": 16, "B": 11, "C": 3.2, "D": 12, "E": 22, "F": 17, "G": 13, "H": 36, "I": 54,
        "J": 7, "K": 23, "L": 9, "M": 10, "N": 10, "O": 34, "P": 9, "Q": 9, "R": 9,
        "S": 9, "T": 10, "U": 12, "V": 9, "W": 9, "X": 9, "Y": 9, "Z": 10, "AA": 12,
        "AB": 16, "AC": 17, "AD": 17,
    }
    for col, width in widths.items():
        ws.column_dimensions[col].width = width


def write_player_sheet(ws, title: str, subtitle: str, players: list[dict], table_name: str):
    style_title(ws, title, subtitle, len(MASTER_HEADERS))
    header_row = 4
    for col, header in enumerate(MASTER_HEADERS, 1):
        ws.cell(header_row, col, header)
    start = header_row + 1
    for r, p in enumerate(players, start):
        for c, value in enumerate(value_row(p), 1):
            cell = ws.cell(r, c, value)
            if c in {17, 18, 23, 24} and isinstance(value, (float, int)):
                cell.number_format = "0.00"
            if c == 2 and isinstance(value, (float, int)):
                cell.number_format = "0.0"
            if c in {28, 29, 30} and value:
                cell.value = "Apri"
                cell.hyperlink = value
                cell.style = "Hyperlink"
        if p.get("demographic_source"):
            ws.cell(r, 10).comment = Comment("Fonte anagrafica: " + p["demographic_source"], "Codex")
    end = start + len(players) - 1
    apply_table_style(ws, header_row, start, end, len(MASTER_HEADERS), table_name)
    set_player_widths(ws)
    ws.cell(header_row, 3).comment = Comment(
        "Selezione compatibile con Google Sheets: scegli ☐ o ☑. Lo script fornito converte la colonna in checkbox native e sincronizzate.",
        "Codex",
    )
    ws.cell(header_row, 15).comment = Comment(
        "Il mese tra parentesi deriva dal calendario Serie A Enilive 2026/27: " + URL_SERIE_A_CALENDAR,
        "Codex",
    )
    ws.conditional_formatting.add(f"B{start}:B{end}", ColorScaleRule(start_type="min", start_color="F8696B", mid_type="percentile", mid_value=50, mid_color="FFEB84", end_type="max", end_color="63BE7B"))
    checkbox_validation = DataValidation(type="list", formula1='"☐,☑"', allow_blank=False)
    checkbox_validation.promptTitle = "Selezione giocatore"
    checkbox_validation.prompt = "Scegli ☐ oppure ☑."
    checkbox_validation.errorTitle = "Valore non valido"
    checkbox_validation.error = "Usa soltanto ☐ o ☑."
    checkbox_validation.showInputMessage = True
    checkbox_validation.showErrorMessage = True
    ws.add_data_validation(checkbox_validation)
    checkbox_validation.add(f"C{start}:C{end}")


def add_modern_checkboxes(path: Path, sheet_names: list[str]):
    """Trasforma le celle booleane della colonna C in checkbox native di Excel."""
    main_ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    pkg_rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    ct_ns = "http://schemas.openxmlformats.org/package/2006/content-types"
    fpb_ns = "http://schemas.microsoft.com/office/spreadsheetml/2022/featurepropertybag"
    ET.register_namespace("", main_ns)
    ET.register_namespace("r", rel_ns)
    ET.register_namespace("xfpb", fpb_ns)

    with zipfile.ZipFile(path, "r") as zin:
        files = {name: zin.read(name) for name in zin.namelist()}

    workbook = ET.fromstring(files["xl/workbook.xml"])
    rels = ET.fromstring(files["xl/_rels/workbook.xml.rels"])
    rel_targets = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
    target_parts = []
    for sheet in workbook.find(f"{{{main_ns}}}sheets"):
        if sheet.attrib.get("name") in sheet_names:
            rid = sheet.attrib[f"{{{rel_ns}}}id"]
            target = rel_targets[rid].lstrip("/")
            target_parts.append(target if target.startswith("xl/") else "xl/" + target)

    # Duplica lo stile della prima cella di spunta e vi aggiunge la proprietà
    # Checkbox introdotta da Excel 365/2024.
    first_sheet = ET.fromstring(files[target_parts[0]])
    first_cell = first_sheet.find(f".//{{{main_ns}}}c[@r='C5']")
    base_style = int(first_cell.attrib.get("s", "0"))
    styles = ET.fromstring(files["xl/styles.xml"])
    cell_xfs = styles.find(f"{{{main_ns}}}cellXfs")
    checkbox_xf = copy.deepcopy(list(cell_xfs)[base_style])
    old_ext = checkbox_xf.find(f"{{{main_ns}}}extLst")
    if old_ext is not None:
        checkbox_xf.remove(old_ext)
    ext_lst = ET.SubElement(checkbox_xf, f"{{{main_ns}}}extLst")
    ext = ET.SubElement(ext_lst, f"{{{main_ns}}}ext", {"uri": "{C7286773-470A-42A8-94C5-96B5CB345126}"})
    ET.SubElement(ext, f"{{{fpb_ns}}}xfComplement", {"i": "0"})
    checkbox_style = len(list(cell_xfs))
    cell_xfs.append(checkbox_xf)
    cell_xfs.set("count", str(checkbox_style + 1))
    files["xl/styles.xml"] = ET.tostring(styles, encoding="utf-8", xml_declaration=True)

    for part in target_parts:
        root = ET.fromstring(files[part])
        for cell in root.findall(f".//{{{main_ns}}}c"):
            coordinate = cell.attrib.get("r", "")
            if coordinate.startswith("C") and coordinate[1:].isdigit() and int(coordinate[1:]) >= 5:
                cell.set("s", str(checkbox_style))
                cell.set("t", "b")
        files[part] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    fpb_path = "xl/featurePropertyBag/featurePropertyBag.xml"
    files[fpb_path] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<FeaturePropertyBags xmlns="http://schemas.microsoft.com/office/spreadsheetml/2022/featurepropertybag">'
        '<bag type="Checkbox"/><bag type="XFControls"><bagId k="CellControl">0</bagId></bag>'
        '<bag type="XFComplement"><bagId k="XFControls">1</bagId></bag>'
        '<bag type="XFComplements" extRef="XFComplementsMapperExtRef"><a k="MappedFeaturePropertyBags">'
        '<bagId>2</bagId></a></bag></FeaturePropertyBags>'
    ).encode("utf-8")

    existing = [r for r in rels if r.attrib.get("Type", "").endswith("/FeaturePropertyBag")]
    if not existing:
        ids = [int(m.group(1)) for r in rels if (m := re.fullmatch(r"rId(\d+)", r.attrib.get("Id", "")))]
        ET.SubElement(rels, f"{{{pkg_rel_ns}}}Relationship", {
            "Id": f"rId{max(ids, default=0) + 1}",
            "Type": "http://schemas.microsoft.com/office/2022/11/relationships/FeaturePropertyBag",
            "Target": "featurePropertyBag/featurePropertyBag.xml",
        })
    files["xl/_rels/workbook.xml.rels"] = ET.tostring(rels, encoding="utf-8", xml_declaration=True)

    content_types = ET.fromstring(files["[Content_Types].xml"])
    if not any(x.attrib.get("PartName") == "/xl/featurePropertyBag/featurePropertyBag.xml" for x in content_types):
        ET.SubElement(content_types, f"{{{ct_ns}}}Override", {
            "PartName": "/xl/featurePropertyBag/featurePropertyBag.xml",
            "ContentType": "application/vnd.ms-excel.featurepropertybag+xml",
        })
    files["[Content_Types].xml"] = ET.tostring(content_types, encoding="utf-8", xml_declaration=True)

    temp_path = path.with_suffix(".checkboxes.xlsx")
    with zipfile.ZipFile(temp_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            zout.writestr(name, data)
    os.replace(temp_path, path)


def write_readme(wb: Workbook, meta: dict, players: list[dict]):
    ws = wb.active
    ws.title = "LEGGIMI"
    style_title(ws, "Guida asta Fantacalcio — Serie A 2026/27", "Listone Gazzetta + gerarchie e stato fisico aggiornati al 5 settembre 2026", 8)
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 4
    ws.column_dimensions["B"].width = 28
    ws.column_dimensions["C"].width = 78
    ws.column_dimensions["D"].width = 22
    ws.column_dimensions["E"].width = 22
    ws.column_dimensions["F"].width = 22
    ws.column_dimensions["G"].width = 22
    ws.column_dimensions["H"].width = 22

    rows = [
        (4, "Come usarlo", "Parti dai fogli per ruolo, filtra la fascia e poi usa Score asta, titolarità, tag, rigoristi e stato fisico. La checkbox stretta tra Score asta e Scommessa serve per segnare manualmente i tuoi obiettivi e filtrarli. Le stelline identificano le scommesse: ★ prudente, ★★ interessante, ★★★ forte upside."),
        (6, "Perimetro", f"{meta['gazzetta_count']} calciatori presenti nel listone pubblico Gazzetta 2026/27 consultato il 5 settembre, dopo la chiusura del mercato. Squadre e quotazioni provengono direttamente dal listone aggiornato."),
        (8, "Fasce", "Quattro fasce calcolate separatamente per ruolo: TOP = primo 10%; SEMITOP = fino al 25%; TERZA FASCIA = fino al 50%; QUARTA FASCIA = restante 50%. Lo score privilegia la quotazione Gazzetta e corregge per titolarità, rendimento 2025/26, rigori/punizioni, indicazioni Gazzetta e indisponibilità."),
        (10, "Titolarità", "È un’etichetta, non un numero. “Titolare fisso” = XI tipo Gazzetta e impiego nelle prime due giornate; “Titolare probabile” = XI tipo; “Ballottaggio (Nome)” = testa-a-testa esplicito nelle probabili formazioni della 3ª giornata; gli altri sono rotazione/riserva."),
        (12, "Scommesse", "Le stelline partono dalle sezioni “possibili sorprese” delle schede squadra Gazzetta; completano l'elenco alcuni Under 23 già nell'XI tipo e nuove entrate consigliate. ★★★ richiede anche titolarità e profilo giovane/non-top."),
        (14, "Stato fisico", "“Rischio infortunio” viene usato quando il giocatore risulta attualmente indisponibile nella pagina Gazzetta della 3ª giornata. Quando è indicata una giornata di rientro, aggiungo tra parentesi il mese del calendario Serie A 2026/27, per esempio “Rientro alla 14 (dicembre)”. Non è una previsione medica per l'intera stagione."),
        (16, "Dati 26/27", "Presenze, medie, gol, assist e rigori sono una fotografia dopo due giornate e pesano poco nello score. I dati 2025/26 servono per distinguere garanzie e portatori di bonus."),
        (18, "Aggiornamento mercato", "Il file è stato rigenerato sul listone Gazzetta disponibile il 5 settembre, dopo la chiusura del mercato: i ceduti fuori dalla Serie A sono esclusi e i nuovi inserimenti sono inclusi."),
    ]
    for row, label, text in rows:
        ws.cell(row, 2, label).font = Font(name="Arial", size=11, bold=True, color=COLORS["blue"])
        ws.cell(row, 3, text).font = Font(name="Arial", size=10, color=COLORS["black"])
        ws.cell(row, 3).alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=8)
        ws.row_dimensions[row].height = 44 if row != 8 else 58

    ws.cell(21, 2, "Legenda fasce").font = Font(name="Arial", size=12, bold=True, color=COLORS["blue"])
    for idx, (tier, fill) in enumerate([("TOP", "top"), ("SEMITOP", "semi"), ("TERZA FASCIA", "third"), ("QUARTA FASCIA", "fourth")], 22):
        ws.cell(idx, 2, tier)
        ws.cell(idx, 2).fill = PatternFill("solid", fgColor=COLORS[fill])
        ws.cell(idx, 2).font = Font(name="Arial", bold=True)
    ws.cell(21, 4, "Copertura dati").font = Font(name="Arial", size=12, bold=True, color=COLORS["blue"])
    coverage = [
        ("Listone Gazzetta", meta["gazzetta_count"]), ("Profili/statistiche abbinati", meta["fc_matches"]),
        ("Rose esterne abbinate", meta["roster_matches"]), ("Schede squadra Gazzetta", meta["guide_teams"]),
        ("Squadre con gerarchie piazzati", meta["kicker_teams"]), ("Indisponibili censiti", meta["injuries"]),
        ("Ballottaggi espliciti", meta["ballottaggi"]),
    ]
    for r, (label, value) in enumerate(coverage, 22):
        ws.cell(r, 4, label).font = Font(name="Arial", bold=True)
        ws.cell(r, 5, value).font = Font(name="Arial")

    ws.cell(30, 2, "Fonti").font = Font(name="Arial", size=12, bold=True, color=COLORS["blue"])
    sources = [
        ("Listone e quotazioni Gazzetta", URL_GAZZETTA_LIST, "Ufficiale; consultato 05/09/2026"),
        ("Schede squadre Gazzetta", URL_GAZZETTA_HUB, "XI tipo, consigli e sorprese; consultate 05/09/2026"),
        ("Probabili formazioni Gazzetta", URL_GAZZETTA_FORMATIONS, "Ballottaggi della 3ª giornata; aggiornati 05/09/2026"),
        ("Rigoristi e punizioni Gazzetta", URL_GAZZETTA_KICKERS, "Gerarchie; consultate 05/09/2026"),
        ("Indisponibili Gazzetta", URL_GAZZETTA_INJURIES, "Stato 3ª giornata; consultato 05/09/2026"),
        ("Calendario Serie A 2026/27", URL_SERIE_A_CALENDAR, "Mese associato alla giornata di rientro"),
        ("Statistiche Fantacalcio.it", URL_FC_CURRENT, "Anagrafica e dati 2026/27; consultati 05/09/2026"),
        ("Statistiche 2025/26", URL_FC_PREV, "Storico rendimento; consultato 05/09/2026"),
        ("Rose e anagrafiche di controllo", URL_ROSTERS, "Controllo incrociato; consultato 05/09/2026"),
        ("Anagrafiche residue", "https://www.transfermarkt.com/", "Usato solo per i nomi non coperti dalle fonti precedenti"),
    ]
    for r, (label, url, note) in enumerate(sources, 31):
        ws.cell(r, 2, label).font = Font(name="Arial", bold=True)
        ws.cell(r, 3, url)
        ws.cell(r, 3).hyperlink = url
        ws.cell(r, 3).style = "Hyperlink"
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
        ws.cell(r, 8, note).font = Font(name="Arial", size=9, italic=True, color=COLORS["gray"])
    ws.freeze_panes = "B1"


def write_summary(wb: Workbook, players: list[dict]):
    ws = wb.create_sheet("Riepilogo")
    style_title(ws, "Riepilogo asta", "Conteggi automatici per ruolo e fascia; usa i filtri nei fogli giocatori per la selezione finale", 9)
    ws.sheet_view.showGridLines = False
    headers = ["Ruolo", "Totale", "TOP", "SEMITOP", "TERZA FASCIA", "QUARTA FASCIA", "Scommesse", "Titolari", "Indisponibili"]
    for c, h in enumerate(headers, 1):
        ws.cell(4, c, h)
    role_labels = [("P", "Portieri"), ("D", "Difensori"), ("C", "Centrocampisti"), ("A", "Attaccanti")]
    for r, (role, label) in enumerate(role_labels, 5):
        sheet = ROLE_SHEET[role]
        last_row = sum(1 for p in players if p["role"] == role) + 4
        name_range = f"'{sheet}'!$E$5:$E${last_row}"
        tier_range = f"'{sheet}'!$A$5:$A${last_row}"
        bet_range = f"'{sheet}'!$D$5:$D${last_row}"
        titularity_range = f"'{sheet}'!$H$5:$H${last_row}"
        injury_range = f"'{sheet}'!$O$5:$O${last_row}"
        ws.cell(r, 1, label)
        ws.cell(r, 2, f'=COUNTA({name_range})')
        for c, tier in enumerate(["TOP", "SEMITOP", "TERZA FASCIA", "QUARTA FASCIA"], 3):
            ws.cell(r, c, f'=COUNTIF({tier_range},"{tier}")')
        ws.cell(r, 7, f'=COUNTIF({bet_range},"<>")')
        ws.cell(r, 8, f'=COUNTIF({titularity_range},"Titolare*")')
        ws.cell(r, 9, f'=COUNTIF({injury_range},"<>")')
    ws.cell(9, 1, "TOTALE")
    for c in range(2, 10):
        col = chr(64 + c)
        ws.cell(9, c, f"=SUM({col}5:{col}8)")
    for cell in ws[4]:
        cell.font = Font(name="Arial", bold=True, color=COLORS["white"])
        cell.fill = PatternFill("solid", fgColor=COLORS["blue"])
        cell.alignment = Alignment(wrap_text=True, horizontal="center")
    for row in ws.iter_rows(min_row=5, max_row=9, max_col=9):
        for cell in row:
            cell.font = Font(name="Arial", size=10, bold=(cell.row == 9))
            cell.alignment = Alignment(horizontal="center")
    fills = [COLORS["white"], COLORS["white"], COLORS["top"], COLORS["semi"], COLORS["third"], COLORS["fourth"], COLORS["purple_light"], COLORS["green_light"], COLORS["red_light"]]
    for c, fill in enumerate(fills, 1):
        for r in range(5, 10):
            ws.cell(r, c).fill = PatternFill("solid", fgColor=fill)
    for col, width in zip("ABCDEFGHI", [21, 12, 12, 12, 16, 17, 14, 14, 15]):
        ws.column_dimensions[col].width = width
    ws.freeze_panes = "B1"

    ws.cell(12, 1, "Lettura rapida").font = Font(name="Arial", size=13, bold=True, color=COLORS["blue"])
    notes = [
        "Score asta: indice 0–100, utile per ordinare; non è un prezzo d'acquisto.",
        "Quotazione Gazzetta: valore ufficiale del listone pubblico consultato il 5 settembre.",
        "Squadra attuale: controllo post-mercato aggiornato per orientarsi sulle rose definitive.",
        "Infortuni: nei fogli per ruolo filtra la colonna “Stato fisico / rientro” ed escludi le celle vuote. Controlla sempre la data di rientro prima dell’asta.",
    ]
    for r, note in enumerate(notes, 13):
        ws.cell(r, 1, "• " + note)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
        ws.cell(r, 1).font = Font(name="Arial", size=10)


def build_workbook(players: list[dict], meta: dict):
    players_sorted = sorted(players, key=lambda p: ("PDCA".index(p["role"]), TIER_ORDER[p["tier"]], -p["score"], p["full_name"]))
    wb = Workbook()
    wb.remove(wb.active)
    ws = wb.create_sheet("Tutti i giocatori")
    write_player_sheet(ws, "Tutti i giocatori", f"{len(players_sorted)} nomi del listone Gazzetta 2026/27 — ordinati per ruolo, fascia e score", players_sorted, "TblTuttiGiocatori")

    for role, sheet in ROLE_SHEET.items():
        pool = [p for p in players_sorted if p["role"] == role]
        ws = wb.create_sheet(sheet)
        write_player_sheet(ws, sheet, f"{len(pool)} {ROLE_NAMES[role].lower()}i — quattro fasce e gerarchie d'asta", pool, f"Tbl{sheet}")

    # Selection helper: the user can mark auction targets without breaking tables.
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if cell.font.name != "Arial":
                    cell.font = Font(name="Arial", size=cell.font.sz or 10, bold=cell.font.bold, italic=cell.font.italic, color=cell.font.color)
    wb.calculation.fullCalcOnLoad = True
    wb.calculation.forceFullCalc = True
    wb.calculation.calcMode = "auto"
    wb.save(OUTPUT)


def validate_output(players: list[dict], meta: dict):
    wb = load_workbook(OUTPUT, data_only=False)
    assert wb.sheetnames == ["Tutti i giocatori", "Portieri", "Difensori", "Centrocampisti", "Attaccanti"]
    ws = wb["Tutti i giocatori"]
    assert ws.max_row == len(players) + 4
    roles = Counter(p["role"] for p in players)
    assert sum(roles.values()) == len(players), roles
    assert set(roles) == {"P", "D", "C", "A"}, roles
    assert sum(1 for p in players if p["tier"] == "TOP") > 50
    assert sum(1 for p in players if p["stars"]) > 20
    assert sum(1 for p in players if p["injury_status"]) > 30
    assert all(p["team_verified"] for p in players)
    # I collegamenti alle fonti devono sopravvivere alla scrittura.
    assert ws["AB5"].hyperlink is not None
    assert ws["C5"].value == "☐"
    assert ws.freeze_panes is None
    for sheet in wb.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    assert "#REF!" not in cell.value and "#NAME?" not in cell.value
    return {
        "file": str(OUTPUT), "players": len(players), "roles": dict(roles),
        "tiers": dict(Counter(p["tier"] for p in players)),
        "bets": sum(1 for p in players if p["stars"]),
        "injured": sum(1 for p in players if p["injury_status"]),
        "verified_current_team": sum(1 for p in players if p["team_verified"]),
        "transfers_flagged": sum(1 for p in players if p["transferred"]),
        "meta": meta,
    }


if __name__ == "__main__":
    players, metadata = assemble_players()
    build_workbook(players, metadata)
    print(validate_output(players, metadata))
