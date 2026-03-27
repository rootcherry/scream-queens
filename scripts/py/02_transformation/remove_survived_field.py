# scripts/py/remove_survived_data.py
import json
from py.paths import (
    PROCESSED_BACKUP_FILE,
    PROCESSED_NO_SURVIVED_FILE,
)  # import paths

# load backup processed data
with PROCESSED_BACKUP_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)

# remove 'survived' field from all films
for actress in data:
    for film in actress.get("films", []):
        film.pop("survived", None)

# save cleaned data
PROCESSED_NO_SURVIVED_FILE.parent.mkdir(parents=True, exist_ok=True)
with PROCESSED_NO_SURVIVED_FILE.open("w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"'survived' field removed from all films. Saved to {PROCESSED_NO_SURVIVED_FILE}")
