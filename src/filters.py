import re
from fetch import getPage
from config import HORROR_KEYWORDS


def is_horror_related(url):
    bs = getPage(url)

    if not bs:
        return False

    #  first 3 paragraphs
    lead_paragraphs = bs.find_all('p')[:3]
    lead_text = " ".join(p.get_text() for p in lead_paragraphs).lower()

    # check for horror keywords
    pattern = r'\b(' + '|'.join(HORROR_KEYWORDS) + r')\b'
    return bool(re.search(pattern, lead_text))
