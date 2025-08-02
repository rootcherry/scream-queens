import requests
import re
from bs4 import BeautifulSoup

# wikipedia filmography pages
scream_queens_urls = {
    "Jamie Lee Curtis": "https://en.wikipedia.org/wiki/List_of_Jamie_Lee_Curtis_performances",
    "Neve Campbell": "https://en.wikipedia.org/wiki/Neve_Campbell",
    "Florence Pugh": "https://en.wikipedia.org/wiki/Florence_Pugh",
    "Vera Farmiga": "https://en.wikipedia.org/wiki/Vera_Farmiga_on_screen_and_stage",
    "Megumi Okina": "https://en.wikipedia.org/wiki/Megumi_Okina",
    "Anya Taylor-Joy": "https://en.wikipedia.org/wiki/Anya_Taylor-Joy",
}

# select an actress to scrape
html = scream_queens_urls["Jamie Lee Curtis"]

# http request and parse response
req = requests.get(html)
bs = BeautifulSoup(req.text, 'html.parser')

# all tables with the class 'wikitable'
tables = bs.find_all('table', class_=re.compile(r'\bwikitable\b'))


# check if exists at least one table
if tables:
    first_table = tables[0]
    caption = first_table.find('caption')

    # check for a caption and the word 'film'
    if caption and 'film' in caption.text.lower():
        print("Table is related to film.")
    else:
        print("First 'wikitable' is not about film.")

else:
    print("No 'wikitable' found on the page.")

'''
Actresses:
Jamie Lee Curtis
Neve Campbell
Florence Pugh
Vera Farmiga
Megumi Okina
Anya Taylor-Joy
'''
