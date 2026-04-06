import json
import math
import sqlite3
from datetime import datetime
from pipeline.core.paths import DB_FILE, PROCESSED_CLEAN_FILE


# STATS
def compute_stats(data):
    for actress in data:
        films = actress["films"]

        horror_count = 0
        survived_count = 0
        box_values = []

        for film in films:
            # [OK] use normalized boolean instead of string parsing
            if "Horror" in film.get("genres", []):
                horror_count += 1

            # [OK] survival flag
            if film.get("survived") == 1:
                survived_count += 1

            # [OK] only accept integers (avoid string issues)
            box = film.get("box_office")
            if isinstance(box, int):
                box_values.append(box)

        years = [f["year"] for f in films if f.get("year")]

        box_total = sum(box_values) if box_values else 0
        career_length = (max(years) - min(years)) if years else 0

        score = (
            (horror_count * 3)
            + (survived_count * 5)
            + (math.log10(box_total + 1) if box_total > 0 else 0)
            + career_length
        )

        actress["stats"] = {
            "horror_count": horror_count,
            "survived_count": survived_count,
            "box_office_total": sum(box_values) if box_values else None,
            "box_office_avg": (
                int(sum(box_values) / len(box_values)) if box_values else None
            ),
            "box_office_best": max(box_values) if box_values else None,
            "box_office_worst": min(box_values) if box_values else None,
            "career_span": [min(years), max(years)] if years else None,
            # [OK] true if at least one valid box_office exists
            "omdb_ok": any(isinstance(f.get("box_office"), int) for f in films),
            "career_length": (max(years) - min(years)) if years else 0,
            "score": round(score, 2),
        }

    return data


# TEST DB INSERT (DEBUG)
def test_save_one_stat():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # get one actress
    cursor.execute("SELECT id, name FROM scream_queens LIMIT 1")
    queen_id, name = cursor.fetchone()

    print(f"Testing with: {name} (id={queen_id})")

    # load processed JSON
    with PROCESSED_CLEAN_FILE.open() as f:
        data = json.load(f)

    # find actress
    actress = next(a for a in data if a["name"] == name)

    films = actress["films"]
    stats = actress.get("stats", {})

    # [OK] reuse computed stats instead of recalculating
    box_values = [
        f["box_office"] for f in films if isinstance(f.get("box_office"), int)
    ]

    movies_count = len(films)
    box_office_total = stats.get("box_office_total") or 0
    box_office_known_count = len(box_values)

    years = [f["year"] for f in films if f.get("year")]
    first_year = min(years) if years else None
    last_year = max(years) if years else None

    cursor.execute(
        """
    INSERT INTO queen_stats (
        scream_queen_id,
        movies_count,
        box_office_total,
        box_office_known_count,
        first_movie_year,
        last_movie_year,
        recomputed_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(scream_queen_id) DO UPDATE SET
        movies_count=excluded.movies_count,
        box_office_total=excluded.box_office_total,
        box_office_known_count=excluded.box_office_known_count,
        first_movie_year=excluded.first_movie_year,
        last_movie_year=excluded.last_movie_year,
        recomputed_at=excluded.recomputed_at
    """,
        (
            queen_id,
            movies_count,
            box_office_total,
            box_office_known_count,
            first_year,
            last_year,
            datetime.utcnow().isoformat(),
        ),
    )

    conn.commit()
    conn.close()

    print(f"[OK] Saved stats for {name}")
    print(f"Movies: {movies_count}")
    print(f"Box office total: {box_office_total}")


if __name__ == "__main__":
    test_save_one_stat()
