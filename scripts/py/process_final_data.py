from pathlib import Path
import json
import re

# project root: scripts/py/process_final_data.py -> parents[2] = repo root
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"
INPUT_FILE = DATA_DIR / "processed_scream_queens.json"
OUTPUT_FILE = DATA_DIR / "processed_scream_queens_clean.json"


# normalize genres into a clean list
def normalize_genres(genre_str):
    if not genre_str or genre_str == "N/A":
        return ["Unknown"]

    # split by comma or pipe
    raw_genres = re.split(r",|\|", genre_str)

    # strip spaces, capitalize first letter
    genres = [g.strip().title() for g in raw_genres if g.strip()]

    # remove duplicates, keeping order
    seen = set()
    genres = [g for g in genres if not (g in seen or seen.add(g))]

    return genres if genres else ["Unknown"]


# convert box office to int if possible
def parse_box_office(value):
    if not value or value == "N/A":
        return None

    digits = re.sub(r"[^\d]", "", value)
    return int(digits) if digits else None


# ensure survived field is 0 or 1, never None
def update_survived(films):
    updated = []
    for film in films:
        survived = film.get("survived")
        film["survived"] = int(bool(survived)) if survived is not None else 0
        updated.append(film)
    return updated


# normalize data for one actress
def process_actress(actress):
    films = []
    horror_count = 0
    survived_count = 0
    box_office_values = []

    for film in actress.get("films", []):
        genres = normalize_genres(film.get("genre"))
        box_office_int = parse_box_office(film.get("box_office"))
        survived_int = film.get("survived")
        survived_int = int(bool(survived_int)) if survived_int is not None else 0

        if "Horror" in genres:
            horror_count += 1
        if survived_int == 1:
            survived_count += 1
        if box_office_int is not None:
            box_office_values.append(box_office_int)

        films.append(
            {
                "year": film.get("year"),
                "title": film.get("title"),
                "character": film.get("character") or "N/A",
                "genres": genres,
                "box_office": box_office_int,
                "survived": survived_int,
            }
        )

    # calculate box office stats
    box_office_total = sum(box_office_values) if box_office_values else None
    box_office_avg = (
        int(box_office_total / len(box_office_values)) if box_office_values else None
    )
    box_office_best = max(box_office_values) if box_office_values else None
    box_office_worst = min(box_office_values) if box_office_values else None

    return {
        "name": actress.get("name"),
        "films": films,
        "stats": {
            "horror_count": horror_count,
            "survived_count": survived_count,
            "box_office_total": box_office_total,
            "career_span": [
                min(f["year"] for f in films if f["year"]),
                max(f["year"] for f in films if f["year"]),
            ]
            if films
            else None,
            "omdb_ok": actress.get("stats", {}).get("omdb_ok", False),
            "box_office_avg": box_office_avg,
            "box_office_best": box_office_best,
            "box_office_worst": box_office_worst,
        },
    }


def main():
    # read input file
    with INPUT_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # process each actress
    clean_data = [process_actress(a) for a in data]

    # save cleaned data
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)

    print(f"Processing complete. Clean data saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
