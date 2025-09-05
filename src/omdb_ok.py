import json
import os
import re
import random
import requests
import time
from dotenv import load_dotenv

from config import WAIT_TIME_SHORT, WAIT_TIME_LONG  # delays
load_dotenv()

OMDB_API_KEY = os.getenv("OMDB_API_KEY")  # OMDb API key from .env
BASE_URL = "http://www.omdbapi.com/"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# input n output JSON files
INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "scream_queens.json")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "processed_scream_queens.json")

# cache folder for OMDb responses
CACHE_DIR = os.path.join(PROJECT_ROOT, "data", "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "omdb_cache.json")

# Delays/API limits
MIN_DELAY, MAX_DELAY = WAIT_TIME_SHORT
FAIL_DELAY_MIN, FAIL_DELAY_MAX = WAIT_TIME_LONG

# horror keywords when OMDb data is incomplete
HINT_KEYWORDS = [
    "horror", "slasher", "scream", "vampire", "zombie", "ghost",
    "witch", "haunt", "demon", "knife", "blood", "kill",
    "killer", "grave", "nightmare", "cabin"
]

# allow forcing reprocessing, ignoring cache n existing updates
FORCE_REPROCESS = os.getenv("OMDB_FORCE_REPROCESS", "0").lower() in ("1", "true", "yes")
os.makedirs(CACHE_DIR, exist_ok=True)

# always ignored
EXCLUDE_FILMS = {"vampire academy", "haunted mansion"}
# ignore even if OMDb says "horror"
FALSE_HORROR_FILMS = {
    "the new mutants",
    "the haunted world of el superbeasto",
    "in search of darkness"
}

# load cache if it exists! otherwise -> start fresh
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as fh:
            omdb_cache = json.load(fh)
    except Exception:
        omdb_cache = {}
else:
    omdb_cache = {}

# persist cache to disk
def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as fh:
        json.dump(omdb_cache, fh, ensure_ascii=False, indent=4)

# normalize movie title by removing brackets, daggers, n trimming
def clean_title(title):
    t = title or ""
    t = re.sub(r"\[.*?\]", "", t)
    t = t.replace("†", "")
    return t.strip()

# convert OMDb's '$123,456' to int(123456)
def parse_box_office(box):
    if not box or str(box).strip().upper() == "N/A":
        return 0
    digits = "".join(ch for ch in str(box) if ch.isdigit())
    return int(digits) if digits else 0

# format int(123456) into '$123,456'
def format_money(amount):
    return None if (not amount or amount <= 0) else "${:,}".format(amount)

# check if OMDb 'Genre' field contains horror
def genre_is_horror(genre):
    return bool(genre) and "horror" in genre.lower()

# guess horror based on keywords in the title
def title_suggests_horror(title):
    t = (title or "").lower()
    return any(kw in t for kw in HINT_KEYWORDS)

# normalize names, remove special chars, lowercase, spaces
def normalize_name(n):
    if not n:
        return ""
    s = re.sub(r"[^\w\s\-]", "", n, flags=re.UNICODE)
    return re.sub(r"\s+", " ", s).strip().lower()

# check if actress's name appears in omdb's 'actors' list
def actress_in_actors_field(actress_name, actors_field):
    if not actors_field:
        return False

    an = normalize_name(actress_name)
    af = normalize_name(actors_field)

    # simple direct match
    if an and an in af:
        return True

    # match (first + last)
    entries = [e.strip() for e in actors_field.split(",") if e.strip()]
    tokens = an.split()
    if not tokens:
        return False

    last = tokens[-1]
    first = tokens[0]
    for entry in entries:
        entry_norm = normalize_name(entry)
        if last and last in entry_norm:
            if first and (first in entry_norm or (first[0] in entry_norm)):
                return True
    return False

# retrieve movie data from omdb api (caching to decrease calls)
def fetch_omdb(title, year=None):
    key = f"{clean_title(title).lower()}_{year or ''}"
    if key in omdb_cache:
        return omdb_cache[key], True

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

    err = str(data.get("Error", "")).lower()
    if "request limit" in err or "limit reached" in err:
        return None, False

    # retry without year if movie not found
    if data.get("Response") == "False" and year:
        try:
            r2 = requests.get(BASE_URL, params={"t": clean_title(title), "apikey": OMDB_API_KEY, "type": "movie"}, timeout=10)
            data = r2.json()
        except Exception as e2:
            return {"Response": "False", "Error": str(e2)}, False

    # save successful response into cache
    omdb_cache[key] = data
    save_cache()
    return data, False

if not os.path.isfile(INPUT_FILE):
    raise SystemExit(f"Input file not found: {INPUT_FILE}")

# load initial actresses dataset
with open(INPUT_FILE, "r", encoding="utf-8") as fh:
    actresses = json.load(fh)

total_api_calls = 0
total_cache_hits = 0
actresses_processed = 0

for idx, actress in enumerate(actresses, start=1):
    name = actress.get("name", "UNKNOWN")
    print(f"\n[{idx}/{len(actresses)}] processing actress: {name}")

    # skip if already processed unless FORCE_REPROCESS is active
    if not FORCE_REPROCESS and actress.get("stats", {}).get("omdb_ok") is True:
        print("already omdb_ok, skipping")
        continue

    films_in = actress.get("films", [])
    all_have_enrichment = bool(films_in) and all(('genre' in f and 'box_office' in f) for f in films_in)
    if not FORCE_REPROCESS and all_have_enrichment:
        actress.setdefault("stats", {})["omdb_ok"] = True
        print("films already updated, skipping")
        continue

    # stats accumulators
    horror_films = []
    total_box_int = 0
    horror_years = []
    seen_keys = set()
    processed_successfully = True

    for film in films_in:
        title = film.get("title")
        year = film.get("year")
        if not title:
            continue

        dedupe_key = (clean_title(title).lower(), year)
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)

        title_clean = clean_title(title).lower()
        if title_clean in EXCLUDE_FILMS:
            print(f"    skipped (explicit exclusion): {title}")
            continue

        print(f"  - {title} ({year})")
        data, cached = fetch_omdb(title, year)
        if data is None:
            # omdb daily limit reached → save progress and exit
            print("OMDb limit reached. Saving progress and exiting.")
            actress.setdefault("stats", {})["omdb_ok"] = False
            processed_successfully = False
            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
            with open(OUTPUT_FILE, "w", encoding="utf-8") as outfh:
                json.dump(actresses, outfh, ensure_ascii=False, indent=4)
            save_cache()
            raise SystemExit(0)

        # handle cache vs live request counters
        if cached:
            total_cache_hits += 1
        else:
            total_api_calls += 1
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

        if data.get("Response") == "True":
            # update film data
            genre = data.get("Genre")
            box_raw = data.get("BoxOffice")
            actors_field = data.get("Actors")
            box_norm = None if not box_raw or str(box_raw).strip().upper() == "N/A" else box_raw

            film["genre"] = genre
            film["box_office"] = box_norm

            # check actress presence in cast
            if not actress_in_actors_field(name, actors_field):
                print(f"    actress '{name}' not in OMDb actors for '{title}', keeping anyway.")

            # decide horror classification using multiple signals
            is_h = (genre_is_horror(genre) or title_suggests_horror(title)) and title_clean not in FALSE_HORROR_FILMS

            if is_h:
                horror_films.append(film)
                total_box_int += parse_box_office(film.get("box_office"))
                if isinstance(year, int):
                    horror_years.append(year)
                print(f"kept (horror). box: {film.get('box_office')}")
            else:
                print(f"skipped (not horror or false positive). genre: {genre or 'unknown'}")

        else:
            # fallback when OMDb fails completely: keep existing updated if present
            existing_genre = film.get("genre")
            existing_box = film.get("box_office")
            film["genre"] = existing_genre
            film["box_office"] = existing_box

            is_h = (genre_is_horror(existing_genre) or title_suggests_horror(title)) and title_clean not in FALSE_HORROR_FILMS
            if is_h:
                horror_films.append(film)
                total_box_int += parse_box_office(film.get("box_office"))
                if isinstance(year, int):
                    horror_years.append(year)
                print(f"kept (fallback, assumed horror). box: {film.get('box_office')}")
            else:
                print(f"skipped (fallback, not horror or false positive). genre: {existing_genre or 'unknown'}")

        time.sleep(0.25)  # short delay

    actress["films"] = horror_films
    actress.setdefault("stats", {})
    actress["stats"]["horror_count"] = len(horror_films)
    actress["stats"]["box_office_total"] = format_money(total_box_int)
    actress["stats"]["career_span"] = (
        [min(horror_years), max(horror_years)]
        if horror_years
        else actress["stats"].get("career_span", [None, None])
    )
    actress["stats"]["omdb_ok"] = True if processed_successfully else False
    actresses_processed += 1

    # save incremental progress
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfh:
        json.dump(actresses, outfh, ensure_ascii=False, indent=4)

# final cache sync
save_cache()

print(f"\nDone. Processed actresses: {actresses_processed}")
print(f"API calls: {total_api_calls}, cache hits: {total_cache_hits}")
print(f"Output saved to: {OUTPUT_FILE}")
