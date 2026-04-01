from scream_queens.config import SCREAM_QUEENS_URLS
from scream_queens.fetch import fetch_page
from scream_queens.parse import extract_films

from scream_queens.pipeline.enrich import enrich_films
from scream_queens.pipeline.filter import filter_horror
from scream_queens.pipeline.transform import normalize_films
from scream_queens.pipeline.stats import compute_stats

from scream_queens.utils import save_raw_json, save_processed_json, wait_time


def scrape_actress(name, url):
    print(f"[INFO] scraping {name}")

    page = fetch_page(url)
    if not page:
        return build_empty(name)

    films = extract_films(page)
    if not films:
        return build_empty(name)

    films = filter_horror(films)
    films = normalize_films(films)

    films = enrich_films(films)

    stats = compute_stats(films)

    return {
        "name": name,
        "films": films,
        "stats": stats,
    }


def build_empty(name):
    return {
        "name": name,
        "films": [],
        "stats": {
            "horror_count": 0,
            "survived_count": None,
            "box_office_total": None,
            "career_span": [None, None],
            "scrape_ok": False,
        },
    }


def main():
    results = []

    for name, url in SCREAM_QUEENS_URLS.items():
        data = scrape_actress(name, url)

        save_raw_json(name, data)
        results.append(data)

        wait_time(long=True)

    save_processed_json(results)

    print("[DONE] scraping finished")


if __name__ == "__main__":
    main()
