import re
from datetime import datetime
from scream_queens.config import WIKI_BASE_URL


# utils
def is_redlink(link):
    if not link:
        return False
    href = link.get("href", "")
    return "redlink=1" in href

# remove citations like [1]
def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\[\d+\]", "", text).strip()


# extract year from text
def extract_year(text):
    match = re.search(r"\b(19|20)\d{2}\b", str(text))
    return int(match.group()) if match else None


# remove leading year from title
def extract_title(text):
    return re.sub(r"^\(?\d{4}\)?\s*[-–—:]?\s*", "", text).strip()


# detect unreleased content
def is_unreleased(text):
    if not text:
        return False

    t = text.lower()

    keywords = [
        "tba",
        "upcoming",
        "announced",
        "pre-production",
        "post-production",
        "filming",
        "development",
        "planned",
    ]

    if "†" in text:
        return True

    if any(k in t for k in keywords):
        return True

    year = extract_year(text)
    if year and year > datetime.now().year:
        return True

    return False


# filter tv entries
def is_tv(title, role=None):
    text = f"{title} {role or ''}".lower()

    patterns = [
        "tv",
        "television",
        "episode",
        "series",
        "season",
        "mini-series",
        "show",
    ]

    return any(p in text for p in patterns)


# build wiki url
def build_url(link):
    if not link:
        return None

    href = link.get("href", "")

    # if already absolute, return as is
    if href.startswith("http"):
        return href

    return WIKI_BASE_URL + href


# normalize film object
def build_film(title, year, role=None, link=None):
    return {
        "title": clean_text(title),
        "year": year,
        "character": role,
        "url": build_url(link),
    }


# strategy: TABLE
def parse_table(table):
    films = []
    last_year = None
    last_role = None

    for row in table.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if not cells:
            continue

        year = extract_year(cells[0].get_text())
        if year:
            last_year = year
            idx = 1
        else:
            idx = 0

        if len(cells) <= idx:
            continue

        title_cell = cells[idx]
        raw_title = title_cell.get_text(" ", strip=True)

        if not raw_title or is_unreleased(raw_title):
            continue

        title = clean_text(raw_title)

        link = title_cell.find("a", href=True)
        if is_redlink(link):
            link = None

        role = None
        if len(cells) > idx + 1:
            role_text = clean_text(cells[idx + 1].get_text(" ", strip=True))
            if role_text:
                last_role = role_text

        role = last_role

        if is_tv(title, role):
            continue

        films.append(build_film(title, last_year, role, link))

    return films


def find_table(page):
    tables = page.find_all("table", {"class": "wikitable"})

    for table in tables:
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]

        if "year" in headers and ("title" in headers or "film" in headers):
            if any("tv" in h or "series" in h for h in headers):
                continue
            return table

    return None


# strategy: LIST
def parse_list(section):
    films = []
    ul = section.find_next("ul")
    if not ul:
        return films

    for li in ul.find_all("li", recursive=False):
        text = li.get_text(" ", strip=True)

        if is_unreleased(text):
            continue

        year = extract_year(text)
        if not year:
            continue

        link = li.find("a", href=True)
        if is_redlink(link):
            link = None
        title = link.get_text(strip=True) if link else extract_title(text)

        if is_tv(title):
            continue

        films.append(build_film(title, year, None, link))

    return films


# strategy: FALLBACK
def parse_fallback(page):
    films = []

    headings = page.find_all(re.compile("^h[2-3]$"))

    for h in headings:
        if not re.search(r"film|filmography", h.get_text(), re.I):
            continue

        ul = h.find_next("ul")
        if not ul:
            continue

        for li in ul.find_all("li", recursive=False):
            text = li.get_text(" ", strip=True)

            if is_unreleased(text):
                continue

            year = extract_year(text)
            link = li.find("a", href=True)
            if is_redlink(link):
                link = None
            title = link.get_text(strip=True) if link else extract_title(text)

            films.append(build_film(title, year, None, link))

    return films


# orchestrator
def extract_films(page):
    strategies = [
        extract_from_table_strategy,
        extract_from_list_strategy,
        extract_from_fallback_strategy,
    ]

    films = []

    for strategy in strategies:
        result = strategy(page)
        if result:
            films.extend(result)

    films = deduplicate(films)
    return sort_films(films)


# strategy wrappers
def extract_from_table_strategy(page):
    table = find_table(page)
    return parse_table(table) if table else []


def extract_from_list_strategy(page):
    section = page.find(id=re.compile(r"(Filmography|Film)", re.I))
    return parse_list(section) if section else []


def extract_from_fallback_strategy(page):
    return parse_fallback(page)


# post-processing
def deduplicate(films):
    seen = set()
    result = []

    for f in films:
        key = (f["title"], f["year"])
        if key not in seen:
            seen.add(key)
            result.append(f)

    return result


def sort_films(films):
    return sorted(films, key=lambda x: x["year"] or 0)
