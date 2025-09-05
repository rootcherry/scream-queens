from config import SCREAM_QUEENS_URLS
from fetch import getPage
from parse import extract_films
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

    # extract tables or lists
    all_films = extract_films(bs)

    if not all_films:
        print(f"No films found for {name}")
        return {}

    # filter only horror films
    horror_films = []
    for film in all_films:
        if film["url"] and is_horror_related(film["url"]):
            horror_films.append(film)

    # calculate career span
    years = []
    for film in horror_films:
        y = str(film.get("year") or "").strip()
        if y.isdigit():
            years.append(int(y))
    career_span = [min(years), max(years)] if years else [None, None]

    # if found valid years, span is [first horror film, last horror film]
    # else [None, None]
    career_span = [min(years), max(years)] if years else [None, None]

    # build list of film dictionaries
    films_data = []
    for film in horror_films:
        y = str(film.get("year") or "").strip()
        films_data.append(
            {
                "year": int(y) if y.isdigit() else film.get("year"),
                "title": film.get("title"),
                "character": film.get("character"),
            }
        )

    # return structured data - JSON
    return {
        "name": name,
        "films": films_data,
        "stats": {
            "horror_count": len(horror_films),
            "survived_count": None,
            "box_office_total": None,
            "career_span": career_span,
        },
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
