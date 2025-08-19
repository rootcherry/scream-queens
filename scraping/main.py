import json
import os

from config import SCREAM_QUEENS_URLS
from utils import getPage, find_filmography_table, extract_films_from_table, is_horror_related, wait_time

RAW_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')


def scrape_films_for_actress(name, url):
    # log, debbuging n tracking
    print(f"Scraping films for {name}...")

    # load actress's page
    bs = getPage(url)
    if not bs:
        print(f"Failed to load page for {name}")
        return []

    # try to locate filmography table
    table = find_filmography_table(bs)
    if not table:
        print(f"No filmography table found for {name}")
        return {}

    # extract all films from table
    all_films = extract_films_from_table(table)

    # filter only horror films
    horror_films = []
    for film in all_films:
        if film["url"] and is_horror_related(film["url"]):
            horror_films.append(film)

    # calculate career span
    years = []
    for film in horror_films:
        # year is numeric
        if film["year"].isdigit():
            years.append(int(film["year"]))

    # if found valid years, span is [first horror film, last horror film]  else [None, None]
    career_span = [min(years), max(years)] if years else [None, None]

    # build list of film dictionaries
    films_data = []
    for film in horror_films:
        film_entry = {
            "year": int(film["year"]) if film["year"].isdigit() else film["year"],
            "title": film["title"],
            "character": film["character"]
        }
        films_data.append(film_entry)

    # return structured data - JSON
    return {
        "name": name,
        "films": films_data,
        "stats": {
            "horror_count": len(horror_films),
            "survived_count": None,    # manually later
            "box_office_total": None,  # optional later
            "career_span": career_span  # first/last year of horror films
        }
    }


def save_raw_json(name, data):
    os.makedirs(RAW_PATH, exist_ok=True)
    filename = f"{name.lower().replace(' ', '_')}.json"
    filepath = os.path.join(RAW_PATH, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Saved raw data: {filepath}")


def main():
    all_actresses_data = []

    for actress, url in SCREAM_QUEENS_URLS.items():
        actress_data = scrape_films_for_actress(actress, url)
        if actress_data:
            save_raw_json(actress, actress_data)
            all_actresses_data.append(actress_data)

        wait_time(long=True)


if __name__ == "__main__":
    main()

'''
Actresses:
Jamie Lee Curtis
Neve Campbell
Florence Pugh
Vera Farmiga
Megumi Okina
Anya Taylor-Joy

Structure:
Detalhado
scream_queen_films = {
    "Jamie Lee Curtis": [
        {"title": "Halloween", "year": 1978, "character": "Laurie", "url": "..."},
        {"title": "Halloween Kills", "year": 2021, "character": "Laurie", "url": "..."}
    ]
}

Depois
screamQueens = {
    "Jamie Lee Curtis": {
        "movies": ["Halloween (1978)", "Halloween Kills (2021)"],
        "survivals": 2,
        "totalBoxOffice": 450000000,
        "subgenres": ["Slasher"]
    }
}

"title": movie name
"year": year it was released
"character": name of the character played
"url": direct link to the movie's wiki
...
"genre"
"country"
"director"

Keywords:
keywords = ['horror', 'terror', 'slasher', 'thriller', 'supernatural', 'suspense']

fields - JSON
(essentials)
name
films (year, title, character)
stats (horror_count(num horror films), survived_count(how many times survived), career_span(years active in horror))
(useful)
films (subgenre, survived)
(optional)
box_office
stats (box_office_total(box office receipts))
'''
