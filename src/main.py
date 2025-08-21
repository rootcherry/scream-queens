from config import SCREAM_QUEENS_URLS
from fetch import getPage
from parse import find_filmography_table, extract_films_from_table
from filters import is_horror_related
from utils import save_raw_json, save_processed_json, wait_time


def scrape_films_for_actress(name, url):
    # log, debbuging n tracking
    print(f"Scraping films for {name}...")

    # load actress's page
    bs = getPage(url)
    if not bs:
        print(f"Failed to load page for {name}")
        return {}

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
        films_data.append({
            "year": int(film["year"]) if film["year"].isdigit() else film["year"],
            "title": film["title"],
            "character": film["character"]
        })

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


def main():
    all_actresses_data = []

    for actress, url in SCREAM_QUEENS_URLS.items():
        actress_data = scrape_films_for_actress(actress, url)
        if actress_data:
            # save raw JSON p actress
            save_raw_json(actress, actress_data)
            all_actresses_data.append(actress_data)

        wait_time(long=True)

    # save processed JSON
    if all_actresses_data:
        save_processed_json(all_actresses_data)

    print("Scraping finished. raw n processed data saved.")


if __name__ == "__main__":
    main()
