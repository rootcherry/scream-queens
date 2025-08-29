import re
from config import WIKI_BASE_URL


# remove citations [1] n trim extra spaces
def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\[\d+\]", "", text).strip()


# extract year if present"""
def extract_year(text):
    match = re.search(r"\b(19|20)\d{2}\b", str(text))
    return int(match.group()) if match else 0  # return 0 if no year found


# remove leading year n symbols from titles
def extract_title(text):
    return re.sub(r"^\(?\d{4}\)?\s*[-–—:]?\s*", "", text).strip()


# locate the Film or Filmography section
def find_filmography_section(page):
    # first try by section id
    section = page.find(id=re.compile(
        r'^(Films?|Feature_films?|Filmography)$', re.I))
    if section:
        return section.find_parent(['h2', 'h3', 'h4'])

    # fallback: search headers w the word "film"
    for header in page.find_all(['h2', 'h3', 'h4']):
        if "film" in header.get_text(" ", strip=True).lower():
            return header
    return None


# extract films from a filmography table
def extract_from_table(table):
    films = []
    last_year = None
    last_role = None

    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if not cells:
            continue

        # year
        year_cell = cells[0].get_text(strip=True)
        year = extract_year(year_cell)
        if year:
            last_year = year
            data_index = 1  # title is usually after year
        else:
            data_index = 0  # reuse previous year if rowspan

        # title
        title_cell = cells[data_index] if len(cells) > data_index else None
        if not title_cell:
            continue
        title = clean_text(title_cell.get_text(" ", strip=True))
        if not title:
            continue

        # url
        link = title_cell.find("a", href=True)
        url = WIKI_BASE_URL + link["href"] if link else None

        # role/character
        role = None
        if len(cells) > data_index + 1:
            role_cell = cells[data_index + 1]
            role_text = clean_text(role_cell.get_text(" ", strip=True))
            if role_text:
                last_role = role_text
        role = last_role

        # append to list
        films.append({
            "title": title,
            "year": last_year,
            "character": role,
            "url": url
        })

    return films


# extract films from <ul> lists under the filmography section
def extract_from_lists(section):
    ul = section.find_next("ul")
    if not ul:
        return []

    films = []
    for li in ul.find_all("li", recursive=False):
        text = li.get_text(" ", strip=True)
        year = extract_year(text)
        if not year:
            continue

        # extract title n url if available
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


# search for any table that has Year + Title/Film columns
def extract_fallback_tables(page):
    films = []
    for table in page.find_all("table"):
        headers = [h.get_text(strip=True).lower()
                   for h in table.find_all("th")]
        if any("year" in h for h in headers) and (
            any("title" in h for h in headers) or any(
                "film" in h for h in headers)
        ):
            films.extend(extract_from_table(table))
    return films


# extract filmes from wiki filmography(table/list) n fallback
def extract_films(page):
    section = find_filmography_section(page)

    # 1: try to extract from main filmography table
    if section:
        table = section.find_next("table")
        if table:
            films = extract_from_table(table)
            if films:
                return sort_films(films)

        # 2: try extracting from <ul> lists
        films = extract_from_lists(section)
        if films:
            return sort_films(films)

    # fallback: search for any suitable table in the page
    films = extract_fallback_tables(page)
    return sort_films(films)


# return the film year or 0 if missing
def get_film_year(film):
    return film["year"] or 0


# sort films by year in ascending order
def sort_films(films):
    films.sort(key=get_film_year)
    return films
