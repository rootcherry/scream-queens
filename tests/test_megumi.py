import requests
from bs4 import BeautifulSoup

html = 'https://en.wikipedia.org/wiki/Megumi_Okina'


def find_filmography_list(bs):

    # Search for all headers h2 and h3 (because some actresses use h2, others h3)
    headers = bs.find_all(['h2', 'h3'])

    for header in headers:
        header_text = header.get_text(strip=True).lower()

        # Check for either "filmography" or "film"
        if 'filmography' in header_text or header_text == 'film':
            next_tag = header.find_next_sibling()

            # Walk through siblings until we find the list <ul>
            while next_tag:
                # Stop if we reach another section before finding <ul>
                if next_tag.name in ['h2', 'h3']:
                    break
                if next_tag.name == 'ul':
                    return next_tag
                next_tag = next_tag.find_next_sibling()
    return None


def main():
    req = requests.get(html, timeout=10)
    req.raise_for_status()

    bs = BeautifulSoup(req.text, 'html.parser')
    ul_tag = find_filmography_list(bs)

    if ul_tag:
        films = [li.get_text(strip=True) for li in ul_tag.find_all('li')]
        print(f"Found {len(films)} films:")
        for film in films:
            print("-", film)
    else:
        print("No film list found.")


if __name__ == "__main__":
    main()
