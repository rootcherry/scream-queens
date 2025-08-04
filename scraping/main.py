# result
for actress, films in scream_queen_films.items():
    print(f"\nHorror films found for {actress}:")
    for film in films:
        print(f"- {film['year']} | {film['title']} as {film['character']}")


'''
Actresses:
Jamie Lee Curtis
Neve Campbell
Florence Pugh
Vera Farmiga
Megumi Okina
Anya Taylor-Joy

Structure:
Detalhado
scream_queen_films = {
    "Jamie Lee Curtis": [
        {"title": "Halloween", "year": 1978, "character": "Laurie", "url": "..."},
        {"title": "Halloween Kills", "year": 2021, "character": "Laurie", "url": "..."}
    ]
}

Depois
screamQueens = {
    "Jamie Lee Curtis": {
        "movies": ["Halloween (1978)", "Halloween Kills (2021)"],
        "survivals": 2,  # Isso você define conforme regras
        "totalBoxOffice": 450000000,  # Se quiser puxar com API
        "subgenres": ["Slasher"]
    }
}

"title": movie name
"year": year it was released
"character": name of the character played
"url": direct link to the movie's wiki
...
"genre"
"country"
"director"

Keywords:
keywords = ['horror', 'terror', 'slasher', 'thriller', 'supernatural', 'suspense']

'''
