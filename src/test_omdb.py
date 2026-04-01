from pipeline.enrich import enrich_films

# teste mínimo com 1 atriz + filmes fictícios
films = [
    {"title": "Scream", "year": 1996},
    {"title": "Vampire Academy", "year": 2014},
    {"title": "Unknown Horror Movie", "year": 2020},
]

# rodar enrich
enriched = enrich_films(films)

# mostrar resultado
for f in enriched:
    print(f)
