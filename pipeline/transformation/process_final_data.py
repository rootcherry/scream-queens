# pipeline/transformation/process_final_data.py

import json
from pipeline.core.paths import PROCESSED_FILE, PROCESSED_CLEAN_FILE
from pipeline.setup_dirs import ensure_directories_exist

from pipeline.utils.normalization import normalize_genres, parse_box_office
from pipeline.utils.survival import build_survival_map, normalize_survived
from pipeline.stats.compute import compute_stats


# PIPELINE ENTRY

# ensure all directories exist
ensure_directories_exist()


def process_final_data():
    data = load_processed_data()

    survival_map = build_survival_map()

    data = normalize_data(data)
    data = enrich_survival(data, survival_map)
    data = compute_stats(data)

    save_clean_data(data)


# LOAD / SAVE
def load_processed_data():
    with PROCESSED_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_clean_data(data):
    with PROCESSED_CLEAN_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] Clean data saved to {PROCESSED_CLEAN_FILE}")


# NORMALIZE
def normalize_data(data):
    result = []

    for actress in data:
        films = []

        for film in actress.get("films", []):
            films.append(
                {
                    "year": film.get("year"),
                    "title": film.get("title"),
                    "character": film.get("character") or "N/A",
                    "genres": normalize_genres(film.get("genre")),
                    "box_office": parse_box_office(film.get("box_office")),
                }
            )

        result.append(
            {
                "name": actress.get("name"),
                "films": films,
                "stats": actress.get("stats", {}),
            }
        )

    return result


# ENRICH
def enrich_survival(data, survival_map):
    for actress in data:
        name = actress["name"]
        actress_survival = survival_map.get(name, {})

        for film in actress["films"]:
            key = (film["title"], film["year"])
            survived_raw = actress_survival.get(key)

            film["survived"] = normalize_survived(survived_raw)

    return data


# MAIN
def main():
    process_final_data()


if __name__ == "__main__":
    main()
