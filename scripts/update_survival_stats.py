import json
from pathlib import Path

# path
BASE_DIR = Path(__file__).parent  # dir script
JSON_FILE = BASE_DIR.parent / "data/processed/processed_scream_queens.json"

# updates the 'survived_count' field for each actress
def update_survived_count(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} not found.")

    with file_path.open("r", encoding="utf-8") as f:
        actresses_data = json.load(f)

    for actress in actresses_data:
        survived_count = sum(
            1 for film in actress.get("films", []) if film.get("survived") == 1
        )
        actress.setdefault("stats", {})["survived_count"] = survived_count

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(actresses_data, f, ensure_ascii=False, indent=2)

    print(f"Updated survived_count for {len(actresses_data)} actresses.")


if __name__ == "__main__":
    update_survived_count(JSON_FILE)
