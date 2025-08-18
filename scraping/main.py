from config import SCREAM_QUEENS_URLS
from utils import getPage, find_filmography_table, extract_films_from_table, is_horror_related, wait_time


def scrape_films_for_actress(name, url):
    print(f"Scraping films for {name}...")
    bs = getPage(url)
    if not bs:
        print(f"Failed to load page for {name}")
        return []

    table = find_filmography_table(bs)
    if not table:
        print(f"No filmography table found for {name}")
        return []

    films = extract_films_from_table(table)
    horror_films = []
    for film in films:
        if film['url'] and is_horror_related(film['url']):
            horror_films.append(film)

    return horror_films


def main():
    all_films = {}

    # test all actress
    for actress, url in SCREAM_QUEENS_URLS.items():
        horror_films = scrape_films_for_actress(actress, url)
        all_films[actress] = horror_films

        print(f"Horror films found for {actress}:")
        if not horror_films:
            print("- None found")
        else:
            for film in horror_films:
                print(
                    f"- {film['year']} | {film['title']} as {film['character']}")

        wait_time(long=True)

    print("\nResume:")
    for actress, films in all_films.items():
        print(f"{actress}: {len(films)} filmes de horror")


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

'''
