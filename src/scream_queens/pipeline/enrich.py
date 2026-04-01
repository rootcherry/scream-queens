from scream_queens.services.omdb import (
    fetch_movie,
)  # or infrastructure.external.omdb_ok.fetch_omdb
import time
import random


# simple genre check
def is_horror_genre(genre):
    return genre and "horror" in genre.lower()


# simple title keyword fallback
HINT_KEYWORDS = ["horror", "scream", "ghost", "kill", "nightmare"]


def title_suggests_horror(title):
    t = (title or "").lower()
    return any(kw in t for kw in HINT_KEYWORDS)


# parse box office '$123,456' -> int(123456)
def parse_box_office(box):
    if not box or box == "N/A":
        return 0
    digits = "".join(c for c in box if c.isdigit())
    return int(digits) if digits else 0


# enrich one film dict
def enrich_film(film, actress_name=None, delay_range=(0.5, 1.5)):
    title = film.get("title")
    year = film.get("year")
    if not title:
        return film

    # fetch OMDb
    data, cached = fetch_movie(title, year)  # expects (data_dict, cached_flag)
    if not data or data.get("Response") != "True":
        # fallback: keep original
        film.setdefault("genre", None)
        film.setdefault("box_office", None)
        film["is_horror"] = title_suggests_horror(title)
        return film

    genre = data.get("Genre")
    box = data.get("BoxOffice")

    film["genre"] = genre
    film["box_office"] = None if not box or box == "N/A" else box

    # horror determination
    is_h = is_horror_genre(genre) or title_suggests_horror(title)
    film["is_horror"] = is_h

    # optional delay to respect API limits
    if not cached:
        time.sleep(random.uniform(*delay_range))

    return film


# enrich list of films
def enrich_films(films, actress_name=None):
    enriched = []
    for f in films:
        enriched.append(enrich_film(f, actress_name=actress_name))
    return enriched
