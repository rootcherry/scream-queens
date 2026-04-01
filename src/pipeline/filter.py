# pipeline/filter.py

from filters import is_horror_related


# keep only horror films
def filter_horror(films):
    result = []

    for film in films:
        if film["url"] and is_horror_related(film["url"]):
            result.append(film)

    return result
