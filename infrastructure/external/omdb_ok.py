import json
import os
import re
import random
import requests
import time
from dotenv import load_dotenv

load_dotenv()

# Config
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
BASE_URL = "http://www.omdbapi.com/"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
CACHE_DIR = os.path.join(PROJECT_ROOT, "data", "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "omdb_cache.json")
os.makedirs(CACHE_DIR, exist_ok=True)

# load cache
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as fh:
            omdb_cache = json.load(fh)
    except Exception:
        omdb_cache = {}
else:
    omdb_cache = {}


# helper: save cache
def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as fh:
        json.dump(omdb_cache, fh, ensure_ascii=False, indent=4)


# helper: clean movie title
def clean_title(title):
    t = title or ""
    t = re.sub(r"\[.*?\]", "", t)
    t = t.replace("†", "")
    return t.strip()


# helper: parse box office
def parse_box_office(box):
    if not box or str(box).strip().upper() == "N/A":
        return 0
    digits = "".join(ch for ch in str(box) if ch.isdigit())
    return int(digits) if digits else 0


# helper: check if genre is horror
def genre_is_horror(genre):
    return bool(genre) and "horror" in genre.lower()


# helper: title hints
HINT_KEYWORDS = [
    "horror",
    "slasher",
    "scream",
    "vampire",
    "zombie",
    "ghost",
    "witch",
    "haunt",
    "demon",
    "knife",
    "blood",
    "kill",
    "killer",
    "grave",
    "nightmare",
    "cabin",
]


def title_suggests_horror(title):
    t = (title or "").lower()
    return any(kw in t for kw in HINT_KEYWORDS)


# fetch movie from OMDb
def fetch_omdb(title, year=None):
    key = f"{clean_title(title).lower()}_{year or ''}"
    if key in omdb_cache:
        return omdb_cache[key], True  # cached

    if not OMDB_API_KEY:
        return {"Response": "False", "Error": "no api key"}, False

    params = {"t": clean_title(title), "apikey": OMDB_API_KEY, "type": "movie"}
    if year:
        params["y"] = year

    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        data = resp.json()
    except Exception as e:
        return {"Response": "False", "Error": str(e)}, False

    # retry without year if not found
    if data.get("Response") == "False" and year:
        try:
            resp2 = requests.get(
                BASE_URL,
                params={
                    "t": clean_title(title),
                    "apikey": OMDB_API_KEY,
                    "type": "movie",
                },
                timeout=10,
            )
            data = resp2.json()
        except Exception as e2:
            return {"Response": "False", "Error": str(e2)}, False

    omdb_cache[key] = data
    save_cache()
    return data, False


# enrich a single film dict
def enrich_film(film, actress_name=None):
    title = film.get("title")
    year = film.get("year")
    if not title:
        return film

    data, cached = fetch_omdb(title, year)
    if data.get("Response") == "True":
        genre = data.get("Genre")
        box = data.get("BoxOffice")
        film["genre"] = genre
        film["box_office"] = box
        film["is_horror"] = genre_is_horror(genre) or title_suggests_horror(title)
    else:
        # fallback using existing data
        film.setdefault("genre", None)
        film.setdefault("box_office", None)
        film["is_horror"] = title_suggests_horror(title)

    return film
