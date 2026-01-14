import json
import os

# paths
PROCESSED_FILE = "../data/processed/processed_scream_queens.json"
OUTPUT_FILE = "../data/processed/survived_data.json"

# load processed data
with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
    actresses = json.load(f)  # returns a LIST

survived_data = []

# iterate over the list of actresses
for actress in actresses:
    name = actress.get("name")
    films = actress.get("films", [])

    films_survived = []
    for film in films:
        # placeholder for survival logic
        survived = None
        films_survived.append({
            "title": film.get("title"),
            "year": film.get("year"),
            "character": film.get("character"),
            "survived": survived
        })

    survived_data.append({
        "name": name,
        "films": films_survived
    })

# save the result
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(survived_data, f, ensure_ascii=False, indent=4)

print(f"Saved survived data to {OUTPUT_FILE}")
