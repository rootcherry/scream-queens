# src/scream_queens/services/omdb.py
import os
import json
import requests
from pipeline.core.paths import CACHE_DIR
from dotenv import load_dotenv

load_dotenv()

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
BASE_URL = "http://www.omdbapi.com/"

# garante cache no root/data/cache
CACHE_FILE = CACHE_DIR / "omdb_cache.json"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# carregar cache
if CACHE_FILE.exists():
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as fh:
            _cache = json.load(fh)
    except Exception:
        _cache = {}
else:
    _cache = {}

FORCE_REPROCESS = os.getenv("OMDB_FORCE_REPROCESS", "0").lower() in ("1", "true", "yes")


def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as fh:
        json.dump(_cache, fh, ensure_ascii=False, indent=4)


def fetch_movie(title, year=None):
    key = f"{title.lower()}_{year or ''}"

    # usar cache
    if key in _cache and not FORCE_REPROCESS:
        return _cache[key], True

    if not OMDB_API_KEY:
        return {"Response": "False", "Error": "No API key"}, False

    params = {"t": title, "apikey": OMDB_API_KEY, "type": "movie"}
    if year:
        params["y"] = year

    try:
        res = requests.get(BASE_URL, params=params, timeout=10)
        data = res.json()
    except Exception as e:
        return {"Response": "False", "Error": str(e)}, False

    # retry sem ano se não encontrado
    if data.get("Response") == "False" and year:
        return fetch_movie(title, None)

    _cache[key] = data
    save_cache()
    return data, False
