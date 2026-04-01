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
            genre = film.get("genre")

            if genre and "horror" in genre.lower():
                horror_count += 1

            if film.get("survived") == 1:
                survived_count += 1

            if film["box_office"] is not None:
                box_values.append(film["box_office"])

        years = [f["year"] for f in films if f["year"]]

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
            "omdb_ok": actress.get("stats", {}).get("omdb_ok", False),
        }

    return data

def test_save_one_stat():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # pegar atriz
    cursor.execute("SELECT id, name FROM scream_queens LIMIT 1")
    queen_id, name = cursor.fetchone()

    print(f"Testing with: {name} (id={queen_id})")

    # carregar data processada (usa teu JSON)
    import json

    with PROCESSED_CLEAN_FILE.open() as f:
        data = json.load(f)

    # achar atriz no JSON
    actress = next(a for a in data if a["name"] == name)

    films = actress["films"]
    box_values = [f["box_office"] for f in films if f["box_office"] is not None]

    box_office_total = sum(box_values) if box_values else 0
    box_office_known_count = len(box_values)
    movies_count = len(films)
    years = [f["year"] for f in films if f["year"]]

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

    print(f"Saved real movies_count: {movies_count}")


if __name__ == "__main__":
    test_save_one_stat()
