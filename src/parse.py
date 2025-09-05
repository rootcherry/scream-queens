import re
from datetime import datetime
from config import WIKI_BASE_URL

# remove citations like [1] and trim spaces
def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\[\d+\]", "", text).strip()

# detect unreleased/future films
def is_unreleased_or_future(text):
    if not text:
        return False

    lower_text = text.lower()

    # keywords commonly used for unreleased films
    unreleased_keywords = [
        "tba",
        "to be announced",
        "to be determined",
        "upcoming",
        "announced",
        "pre-production",
        "post-production",
        "filming",
        "development",
        "planned",
        "expected",
        "future release",
    ]
    if "†" in text:
        return True
    if any(keyword in lower_text for keyword in unreleased_keywords):
        return True

    # check for future years
    year = extract_year(text)
    current_year = datetime.now().year
    if year and year > current_year:
        return True

    return False

# extract a valid year from text
def extract_year(text):
    match = re.search(r"\b(19|20)\d{2}\b", str(text))
    return int(match.group()) if match else 0

# clean up the title, rm leading years/symbols
def extract_title(text):
    return re.sub(r"^\(?\d{4}\)?\s*[-–—:]?\s*", "", text).strip()

# TV filter
def is_tv_entry(title, role=None):
    tv_patterns = [
        r"\bTV\b",
        r"television",
        r"episode",
        r"episodes",
        r"series",
        r"mini-series",
        r"season",
        r"chapter",
        r"segment",
        r"tv movie",
        r"show",
        r"anthology",
    ]
    combined = f"{title} {role or ''}".lower()
    return any(
        re.search(pattern, combined, re.IGNORECASE) for pattern in tv_patterns
    )

# locate the correct "Film" table <thead>
def get_film_table(page):
    tables = page.find_all("table", {"class": "wikitable"})
    for table in tables:
        # skip tables explicitly labeled as TV or series
        caption = table.find("caption")
        if caption and re.search(
            r"television|tv|series", caption.get_text(), re.I
        ):
            continue

        # extract headers to validate if this is a film table
        thead = table.find("thead")
        headers = set()
        if thead:
            headers = {
                th.get_text(strip=True).lower() for th in thead.find_all("th")
            }
        elif table.find("tr"):
            headers = {
                th.get_text(strip=True).lower()
                for th in table.find("tr").find_all("th")
            }

        # skip tables that look like TV content
        if any(
            "television" in h or "tv" in h or "series" in h for h in headers
        ):
            continue

        # identify a valid film table by required headers
        if "year" in headers and ("title" in headers or "film" in headers):
            return table

    return None

# extract films from a given filmography table
def extract_from_table(table):
    films = []
    last_year = None
    last_role = None

    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if not cells:
            continue

        # first cell may contain the year
        year_cell = cells[0].get_text(strip=True)
        year = extract_year(year_cell)
        if year:
            last_year = year
            data_index = 1
        else:
            data_index = 0

        # if no enough cells, skip
        if len(cells) <= data_index:
            continue

        # extract film title
        title_cell = cells[data_index]
        title = clean_text(title_cell.get_text(" ", strip=True))
        if not title:
            continue

        # ignore unreleased/future films
        if is_unreleased_or_future(title_cell.get_text(" ", strip=True)):
            continue

        # build URL if available
        link = title_cell.find("a", href=True)
        url = WIKI_BASE_URL + link["href"] if link else None

        # extract role if available
        role = None
        if len(cells) > data_index + 1:
            role_cell = cells[data_index + 1]
            role_text = clean_text(role_cell.get_text(" ", strip=True))
            if role_text:
                last_role = role_text
        role = last_role

        # ignore TV entries
        if is_tv_entry(title, role):
            continue

        films.append(
            {"title": title, "year": last_year, "character": role, "url": url}
        )

    return films

# extract films from <ul> lists under the filmography section
def extract_from_lists(section):
    ul = section.find_next("ul")
    if not ul:
        return []
    films = []
    for li in ul.find_all("li", recursive=False):
        text = li.get_text(" ", strip=True)

        # ignore unreleased/future films
        if is_unreleased_or_future(text):
            continue

        year = extract_year(text)
        if not year:
            continue

        link = li.find("a", href=True)
        title = link.get_text(strip=True) if link else extract_title(text)
        url = WIKI_BASE_URL + link["href"] if link else None

        # ignore TV entries
        if is_tv_entry(title):
            continue

        films.append(
            {
                "title": clean_text(title),
                "year": year,
                "character": None,
                "url": url,
            }
        )
    return films

# extract films from a wiki filmography page
def extract_films(page):
    films = []
    table = get_film_table(page)
    if table:
        films = extract_from_table(table)
        if films:
            return sort_films(films)

    section = page.find(id=re.compile(r"(Filmography|Film)", re.I))
    if section:
        films = extract_from_lists(section)
        if films:
            return sort_films(films)

    return sort_films(films)

# sort films by year helper
def get_film_year(film):
    return film["year"] or 0

def sort_films(films):
    films.sort(key=get_film_year)
    return films
