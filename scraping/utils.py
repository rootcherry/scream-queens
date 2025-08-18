import random
import re
import time

import requests
from bs4 import BeautifulSoup
from config import WAIT_TIME_SHORT, WAIT_TIME_LONG, WIKI_BASE_URL, HORROR_KEYWORDS

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


def find_filmography_table(bs):
    headers = bs.find_all('h2', 'h3')
    for header in headers:
        if header.text and 'film' in header.text.lower():
            next_tag = header.find_next_sibling()
            while next_tag:
                if next_tag.name == 'table':
                    return next_tag
                next_tag = next_tag.find_next_sibling()

    for table in bs.find_all('table'):
        headers = table.find_all('th')
        column_names = [h.get_text(strip=True).lower() for h in headers]
        if any('year' in c for c in column_names) and any('title' in c for c in column_names):
            return table

    return None


def is_horror_related(url):
    bs = getPage(url)

    if not bs:
        return False

    lead_paragraphs = bs.find_all('p')[:3]
    lead_text = " ".join(p.get_text() for p in lead_paragraphs).lower()

    pattern = r'\b(' + '|'.join(HORROR_KEYWORDS) + r')\b'
    return bool(re.search(pattern, lead_text))


def extract_films_from_table(table):
    films = []
    # track of the last year
    current_year = None

    # loop each row in table
    for row in table.find_all('tr'):
        # th/tds
        year = row.find('th')
        columns = row.find_all('td')

        # update curr_year if there's a new <th>
        if year:
            current_year = year.text.strip()

        if not columns or len(columns) < 2 or not current_year:
            continue

        title_cell = columns[0]
        title = title_cell.text.strip()
        role = columns[1].text.strip()

        link = title_cell.find('a', href=True)
        url = None
        if link:
            url = WIKI_BASE_URL + link['href']

        films.append({
            'title': title,
            'year': current_year,
            'character': role,
            'url': url
        })

    return films


def wait_time(long=False):
    if long:
        time.sleep(random.uniform(*WAIT_TIME_LONG))
    else:
        time.sleep(random.uniform(*WAIT_TIME_SHORT))
