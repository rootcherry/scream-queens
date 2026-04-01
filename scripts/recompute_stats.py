import sqlite3
from datetime import datetime
import json


DB_PATH = "data/db/horrorverse.sqlite3"
DATA_PATH = "data/processed/processed_scream_queens_clean.json"


def get_queen_id(conn, name):
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM scream_queens WHERE name = ?",
        (name,),
    )

    row = cursor.fetchone()
    return row[0] if row else None


def compute_stats(actress):
    films = actress["films"]

    movies_count = len(films)

    box_values = [f["box_office"] for f in films if f["box_office"] is not None]
    years = [f["year"] for f in films if f["year"]]

    return {
        "movies_count": movies_count,
        "box_office_total": sum(box_values) if box_values else 0,
        "box_office_known_count": len(box_values),
        "first_movie_year": min(years) if years else None,
        "last_movie_year": max(years) if years else None,
    }


def save_stats(conn, queen_id, stats):
    cursor = conn.cursor()

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
            stats["movies_count"],
            stats["box_office_total"],
            stats["box_office_known_count"],
            stats["first_movie_year"],
            stats["last_movie_year"],
            datetime.utcnow().isoformat(),
        ),
    )


def main():
    print("[stats] loading data...")
    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)

    print("[stats] recomputing...")
    count = 0

    for actress in data:
        stats = compute_stats(actress)

        queen_id = get_queen_id(conn, actress["name"])

        if not queen_id:
            print(f"[warn] queen not found: {actress['name']}")
            continue

        save_stats(conn, queen_id, stats)
        count += 1

    conn.commit()
    conn.close()

    print(f"[stats] done. updated {count} queens.")


if __name__ == "__main__":
    main()
