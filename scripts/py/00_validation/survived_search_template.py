# scripts/py/survived_search_template.py
import json
from py.paths import PROCESSED_FILE, SURVIVED_FILE

# load processed JSON data
with PROCESSED_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)

# iterate over each actress
for actress in data:
    name = actress.get("name", "Unknown")
    print(name)

    for film in actress.get("films", []):
        title = film.get("title", "Unknown Title")
        year = film.get("year", "Unknown Year")
        character = film.get("character", "Unknown Character")

        print(
            f'Does the character "{character}" played by "{name}" '
            f'in "{title} ({year})" die in the film?'
        )

    print("\n\n")
