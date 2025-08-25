import re

from config import WIKI_BASE_URL


def clean_text(text):
    # remove citation brackets n trims whitespace
    if not text:
        return ""
    return re.sub(r"\[\d+\]", "", text).strip()


def extract_year(text):
    # extracts a 4 digit year if present
    match = re.search(r"\b(19|20)\d{2}\b", text)
    return int(match.group()) if match else None


def extract_title(text):
    # removes leading year n returns the cleaned film title
    return re.sub(r"^\(?\d{4}\)?\s*[-–—:]?\s*", "", text).strip()


def find_filmography_section(bs):
    # "Films" or "Filmography" sections
    films_head = bs.find(id=re.compile(r'^(Films?|Feature_films?)$', re.I))
    if films_head:
        return films_head.find_parent(['h2', 'h3', 'h4'])

    filmog_head = bs.find(id=re.compile(r'^Filmography$', re.I))
    if filmog_head:
        return filmog_head.find_parent(['h2', 'h3', 'h4'])

    # find any header containing "film"
    for header in bs.find_all(['h2', 'h3', 'h4']):
        if "film" in header.get_text(" ", strip=True).lower():
            return header

    return None


def extract_from_table(table):
    # extracts films from a structured table layout
    films = []
    current_year = None

    for row in table.find_all("tr"):
        # detect year in the row
        year = None
        for td in row.find_all("td"):
            t = td.get_text(strip=True)
            if re.fullmatch(r"\d{4}", t):
                year = t
                break
        if year:
            current_year = year

        if not current_year:
            continue

        # locate film title cell
        title_cell = row.find("th", attrs={"scope": "row"})
        if not title_cell:
            title_cell = row.find("i") or row.find("td")
            if title_cell and not hasattr(title_cell, "get_text"):
                title_cell = None

        if not title_cell:
            continue

        title = clean_text(title_cell.get_text(" ", strip=True))
        if not title:
            continue

        # film URL (if available)
        link = title_cell.find("a", href=True)
        url = WIKI_BASE_URL + link["href"] if link else None

        # locate character/role column
        role_text = None
        role_td = None
        if title_cell.name == "th":
            role_td = title_cell.find_next_sibling("td")
        if not role_td and title_cell.name == "i" and title_cell.parent and title_cell.parent.name in ("th", "td"):
            role_td = title_cell.parent.find_next_sibling("td")
        if not role_td:
            # choose first non-year <td> if nothing else found
            tds = row.find_all("td")
            candidates = [td for td in tds if not re.fullmatch(
                r"\d{4}", td.get_text(strip=True))]
            if candidates:
                role_td = candidates[0]
        if role_td:
            role_text = clean_text(role_td.get_text(" ", strip=True)) or None

        films.append({
            "title": title,
            "year": int(current_year),
            "character": role_text,
            "url": url
        })

    return films


def extract_from_lists(start_section):
    # extracts films from <ul> lists when no table exists
    section = start_section.find_next("ul")
    if not section:
        return []

    films = []
    for li in section.find_all("li", recursive=False):
        text = li.get_text(" ", strip=True)
        year = extract_year(text)
        if not year:
            continue

        link = li.find("a", href=True)
        title = link.get_text(strip=True) if link else extract_title(text)
        url = WIKI_BASE_URL + link["href"] if link else None

        films.append({
            "title": clean_text(title),
            "year": year,
            "character": None,
            "url": url
        })

    return films


def extract_fallback_tables(bs):
    # looks for any wikitable with Year + Title columns
    films = []
    for table in bs.find_all("table"):
        headers = [h.get_text(strip=True).lower()
                   for h in table.find_all("th")]
        if any("year" in h for h in headers) and (any("title" in h for h in headers) or any("film" in h for h in headers)):
            films.extend(extract_from_table(table))
    return films


def extract_films(bs):
    # try filmography section then tables n lists
    section = find_filmography_section(bs)
    if section:
        # try tables first
        next_table = section.find_next("table")
        if next_table:
            films = extract_from_table(next_table)
            if films:
                return films

        # try lists in this section
        films = extract_from_lists(section)
        if films:
            return films

    # parse any table with Year + Title columns
    films = extract_fallback_tables(bs)
    if films:
        return films

    return []
