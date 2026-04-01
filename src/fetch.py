import requests
from bs4 import BeautifulSoup
from utils import wait_time

# page cache to avoid lots of reqs
_page_cache = {}

# wiki headers
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
}


def fetch_page(url, retries=2):
    # return cached page
    if url in _page_cache:
        return _page_cache[url]

    for attempt in range(retries + 1):
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            res.raise_for_status()

            soup = BeautifulSoup(res.text, "html.parser")
            _page_cache[url] = soup

            wait_time()
            return soup

        except Exception as e:
            if attempt == retries:
                print(f"[ERROR] fetch failed: {url} ({e})")
                return None


getPage = fetch_page
