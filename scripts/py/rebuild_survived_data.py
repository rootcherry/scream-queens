from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_FILE = BASE_DIR / "data" / "processed" / "processed_scream_queens.json"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "survived_data.json"

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
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(survived_data, f, ensure_ascii=False, indent=4)


print(f"Saved survived data to {OUTPUT_FILE}")
