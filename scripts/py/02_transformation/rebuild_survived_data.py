# scripts/py/rebuild_survived_data.py
import json
from py.paths import PROCESSED_FILE, SURVIVED_FILE  # import paths

# load processed data
with PROCESSED_FILE.open("r", encoding="utf-8") as f:
    actresses = json.load(f)  # list of actresses

survived_data = []

# iterate over actresses
for actress in actresses:
    name = actress.get("name")
    films = actress.get("films", [])

    films_survived = []
    for film in films:
        # placeholder for survival info
        survived = None
        films_survived.append(
            {
                "title": film.get("title"),
                "year": film.get("year"),
                "character": film.get("character"),
                "survived": survived,
            }
        )

    survived_data.append({"name": name, "films": films_survived})

# save survived data
SURVIVED_FILE.parent.mkdir(parents=True, exist_ok=True)
with SURVIVED_FILE.open("w", encoding="utf-8") as f:
    json.dump(survived_data, f, ensure_ascii=False, indent=4)

print(f"Saved survived data to {SURVIVED_FILE}")
