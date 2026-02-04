import json
import shutil
import os

# paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
JSON_FILE = os.path.join(DATA_DIR, "processed_scream_queens.json")
BACKUP_DIR = os.path.join(DATA_DIR, "backup")

# convert string into int return 0 or invalid if N/A
def parse_box_office(value: str) -> int:
    if not value or value == "N/A":
        return 0
    return int(value.replace("$", "").replace(",", "").strip())

# format int into a $ string return N/A if val 0
def format_box_office(value: int) -> str:
    return f"${value:,}" if value > 0 else "N/A"

# backup
def backup_json():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backup_path = os.path.join(BACKUP_DIR, "processed_scream_queens_boxoffice.bak")
    shutil.copy(JSON_FILE, backup_path)
    print(f"Backup created at: {backup_path}")

# update box office stats
def update_box_office_stats():
     # load existing JSON
    if not os.path.exists(JSON_FILE):
        raise FileNotFoundError(f"{JSON_FILE} not found.")

    with open(JSON_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    # iterate actresses
    for actress in data:
        films = actress.get("films", [])

        # extract numeric box office values
        box_office_values = [parse_box_office(film.get("box_office", "N/A")) for film in films]

        if not box_office_values:
            continue

        # compute stats
        total = sum(box_office_values)
        avg = round(
            total / len([v for v in box_office_values if v > 0]), 2
        ) if any(box_office_values) else 0
        best = max(box_office_values) if box_office_values else 0
        worst = min([v for v in box_office_values if v > 0], default=0)

        # update stats in JSON
        actress.setdefault("stats", {})
        actress["stats"]["box_office_total"] = format_box_office(total)
        actress["stats"]["box_office_avg"] = format_box_office(int(avg))
        actress["stats"]["box_office_best"] = format_box_office(best)
        actress["stats"]["box_office_worst"] = format_box_office(worst)

        # normalize each film's box office format
        for film in films:
            raw_value = film.get("box_office", "N/A")
            film["box_office"] = format_box_office(parse_box_office(raw_value))

    # backup b4 saving
    backup_json()

    # save updated JSON
    with open(JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"Box office stats updated successfully in: {JSON_FILE}")


if __name__ == "__main__":
    update_box_office_stats()
