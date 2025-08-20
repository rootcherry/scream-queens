import requests
from bs4 import BeautifulSoup
from utils import wait_time

# page cache to avoid lots of reqs
page_cache = {}

# wiki headers
HEADERS_WIKI = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
}


def getPage(url):
    # return cached page if already loaded
    if url in page_cache:
        return page_cache[url]

    try:
        req = requests.get(url, headers=HEADERS_WIKI, timeout=10)
        req.raise_for_status()
        bs = BeautifulSoup(req.text, 'html.parser')

        page_cache[url] = bs
        wait_time()

        return bs
    except Exception as e:
        print(f'Error to access {url}: {e}')
        return None
