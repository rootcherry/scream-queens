import json

# path to the processed JSON w multiple actresses
PROCESSED_JSON_PATH = '../data/processed/processed_scream_queens.json'

# load processed JSON
with open(PROCESSED_JSON_PATH, 'r') as f:
    data = json.load(f)

# iterate over each actress in the list
for actress in data:
    print(f'{actress['name']}')
    name = actress["name"]
    films = actress.get("films", [])

    for film in films:
        title = film.get("title", "Unknown Title")
        year = film.get("year", "Unknown Year")
        character = film.get("character", "Unknown Character")

        print(
            f'Does the character "{character}" played by "{name}" '
            f'in "{title} ({year})" die in the film?'
        )
    print('\n\n')
