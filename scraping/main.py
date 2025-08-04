import random
import re
import time

import requests
from bs4 import BeautifulSoup

# wikipedia filmography pages
scream_queens_urls = {
    "Jamie Lee Curtis": "https://en.wikipedia.org/wiki/List_of_Jamie_Lee_Curtis_performances",
    "Neve Campbell": "https://en.wikipedia.org/wiki/Neve_Campbell",
    "Florence Pugh": "https://en.wikipedia.org/wiki/Florence_Pugh",
    "Vera Farmiga": "https://en.wikipedia.org/wiki/Vera_Farmiga_on_screen_and_stage",
    "Megumi Okina": "https://en.wikipedia.org/wiki/Megumi_Okina",
    "Anya Taylor-Joy": "https://en.wikipedia.org/wiki/Anya_Taylor-Joy",
}

WAIT_TIME_SHORT = (5, 10)
WAIT_TIME_LONG = (10, 15)
WIKI_BASE_URL = 'https://en.wikipedia.org'


def getPage(url):
    try:
        req = requests.get(url)
        req.raise_for_status()
        return BeautifulSoup(req.text, 'html.parser')
    except Exception as e:
        print(f'Error to access {url}: {e}')
        return None


def is_horror_related(url):
    bs = getPage(url)
    if not bs:
        return False

    keywords = ['horror', 'terror', 'slasher',
                'thriller', 'supernatural', 'suspense']
    text = bs.get_text().lower()

    return any(word in text for word in keywords)


# example scream queens
scream_queen_films = {}

for actress, html in scream_queens_urls.items():
    bs = getPage(html)

    if not bs:
        print("Page not loaded for {actress}.")
        continue

    # find all wikitables
    tables = bs.find_all('table', {'class': 'wikitable'})

    if not tables:
        print(f"No filmography table found for {actress}")
        continue

    print(f"\nFilmography table found for {actress}\n")

    first_table = tables[0]
    # track of the last year
    current_year = None

    # loop each row in table
    for row in first_table.find_all('tr'):
        # th/tds
        year = row.find('th')
        columns = row.find_all('td')

        # update current_year if there's a new <th>
        if year:
            current_year = year.text.strip()

        if not columns or len(columns) < 2 or not current_year:
            continue

        title_cell = columns[0]
        title = title_cell.text.strip()
        role = columns[1].text.strip()

        link = title_cell.find('a', href=True)
        if link:
            film_url = WIKI_BASE_URL + link['href']
            if is_horror_related(film_url):
                film = {
                    "title": title,
                    "year": current_year,
                    "character": role,
                    "url": film_url
                }
                scream_queen_films.setdefault(actress, []).append(film)

            # wait time
            # time.sleep(random.uniform(*WAIT_TIME_SHORT))

# result
for actress, films in scream_queen_films.items():
    print(f"\nHorror films found for {actress}:")
    for film in films:
        print(f"- {film['year']} | {film['title']} as {film['character']}")


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
        "survivals": 2,  # Isso você define conforme regras
        "totalBoxOffice": 450000000,  # Se quiser puxar com API
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
