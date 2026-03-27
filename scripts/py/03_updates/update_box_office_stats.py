# scripts/py/update_box_office_stats.py
import json
import shutil
from py.paths import PROCESSED_FILE, BACKUP_DIR  # import paths


# parse box office string to integer
def parse_box_office(value: str) -> int:
    if not value or value == "N/A":
        return 0
    return int(value.replace("$", "").replace(",", "").strip())


# format integer to box office string
def format_box_office(value: int) -> str:
    return f"${value:,}" if value > 0 else "N/A"


# create backup of JSON
def backup_json():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / "processed_scream_queens_boxoffice.bak"
    shutil.copy(PROCESSED_FILE, backup_path)
    print(f"Backup created at: {backup_path}")


# update box office stats in JSON
def update_box_office_stats():
    if not PROCESSED_FILE.exists():
        raise FileNotFoundError(f"{PROCESSED_FILE} not found.")

    with PROCESSED_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    for actress in data:
        films = actress.get("films", [])
        box_values = [parse_box_office(f.get("box_office", "N/A")) for f in films]

        if not box_values:
            continue

        total = sum(box_values)
        avg = (
            round(total / len([v for v in box_values if v > 0]), 2)
            if any(box_values)
            else 0
        )
        best = max(box_values) if box_values else 0
        worst = min([v for v in box_values if v > 0], default=0)

        actress.setdefault("stats", {})
        actress["stats"]["box_office_total"] = format_box_office(total)
        actress["stats"]["box_office_avg"] = format_box_office(int(avg))
        actress["stats"]["box_office_best"] = format_box_office(best)
        actress["stats"]["box_office_worst"] = format_box_office(worst)

        for film in films:
            raw = film.get("box_office", "N/A")
            film["box_office"] = format_box_office(parse_box_office(raw))

    backup_json()

    with PROCESSED_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Box office stats updated successfully in: {PROCESSED_FILE}")


if __name__ == "__main__":
    update_box_office_stats()
