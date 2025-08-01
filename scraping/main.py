import requests
from bs4 import BeautifulSoup

scream_queens_url = {
    "Jamie Lee Curtis": "https://en.wikipedia.org/wiki/List_of_Jamie_Lee_Curtis_performances",
    "Neve Campbell": "https://en.wikipedia.org/wiki/Neve_Campbell",
    "Florence Pugh": "https://en.wikipedia.org/wiki/Florence_Pugh",
    "Vera Farmiga": "https://en.wikipedia.org/wiki/Vera_Farmiga_on_screen_and_stage",
    "Megumi Okina": "https://en.wikipedia.org/wiki/Megumi_Okina",
    "Anya Taylor-Joy": "https://en.wikipedia.org/wiki/Anya_Taylor-Joy",
}

movies = []

url = scream_queens_url["Jamie Lee Curtis"]
req = requests.get(url)
bs = BeautifulSoup(req.text, 'html.parser')

# print(bs.find_all('table', {'class': 'wikitable'}))
table = bs.find_all('table', {'class': 'wikitable'})[0]

for row in table.find_all('tr'):
   columns = row.find_all('td')
   if columns:
    data = [col.get_text(strip=True) for col in columns]
    print(data)
    movies.append(data)



'''
Actresses:
Jamie Lee Curtis
Neve Campbell
Florence Pugh
Vera Farmiga
Megumi Okina
Anya Taylor-Joy
'''