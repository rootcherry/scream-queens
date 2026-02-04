import json
import sqlite3
from pathlib import Path


DB_PATH = Path("data/db/horrorverse.sqlite3")
JSON_PATH = Path("data/processed/processed_scream_queens_clean.json")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def load_json() -> list[dict]:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Expected JSON top-level list, got: {type(data).__name__}")

    return data


def normalize_int(value):
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def upsert_scream_queen(conn: sqlite3.Connection, name: str) -> int:
    # Idempotent insert (name is UNIQUE)
    conn.execute(
        "INSERT INTO scream_queens (name) VALUES (?) ON CONFLICT(name) DO NOTHING;",
        (name,),
    )
    row = conn.execute("SELECT id FROM scream_queens WHERE name = ?;", (name,)).fetchone()
    if row is None:
        raise RuntimeError(f"Failed to get scream_queen id for name={name}")
    return int(row[0])


def upsert_movie(conn: sqlite3.Connection, title: str, year, box_office) -> int:
    """
    We do NOT have imdb_id in the clean JSON sample.
    So we treat a movie as unique by (title, year).
    """
    year_i = normalize_int(year)
    box_i = normalize_int(box_office)

    # Try to find existing movie first
    row = conn.execute(
        "SELECT id FROM movies WHERE title = ? AND year IS ?;",
        (title, year_i),
    ).fetchone()
    if row is not None:
        movie_id = int(row[0])
        # Best-effort update box_office if we now have it and DB is NULL
        if box_i is not None:
            conn.execute(
                "UPDATE movies SET box_office = COALESCE(box_office, ?) WHERE id = ?;",
                (box_i, movie_id),
            )
        return movie_id

    # Insert new movie
    cur = conn.execute(
        "INSERT INTO movies (title, year, box_office) VALUES (?, ?, ?);",
        (title, year_i, box_i),
    )
    return int(cur.lastrowid)


def insert_appearance(conn: sqlite3.Connection, scream_queen_id: int, movie_id: int) -> bool:
    """
    Returns True if inserted, False if already existed.
    UNIQUE(scream_queen_id, movie_id) protects idempotency.
    """
    cur = conn.execute(
        "INSERT OR IGNORE INTO appearances (scream_queen_id, movie_id) VALUES (?, ?);",
        (scream_queen_id, movie_id),
    )
    return cur.rowcount == 1


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DB not found at {DB_PATH}. Run init_db.py first.")

    if not JSON_PATH.exists():
        raise FileNotFoundError(f"JSON not found at {JSON_PATH}")

    data = load_json()

    inserted_queens = 0
    inserted_movies = 0
    inserted_appearances = 0

    with get_connection() as conn:
        conn.execute("BEGIN;")

        for profile in data:
            name = profile.get("name")
            films = profile.get("films", [])

            if not name:
                continue

            before = conn.execute("SELECT 1 FROM scream_queens WHERE name = ?;", (name,)).fetchone()
            queen_id = upsert_scream_queen(conn, name)
            if before is None:
                inserted_queens += 1

            if not isinstance(films, list):
                continue

            for film in films:
                title = film.get("title")
                year = film.get("year")
                box_office = film.get("box_office")

                if not title:
                    continue

                # movie insert detection
                exists = conn.execute(
                    "SELECT 1 FROM movies WHERE title = ? AND year IS ?;",
                    (title, normalize_int(year)),
                ).fetchone()

                movie_id = upsert_movie(conn, title, year, box_office)
                if exists is None:
                    inserted_movies += 1

                if insert_appearance(conn, queen_id, movie_id):
                    inserted_appearances += 1

        conn.commit()

    print("Ingestion complete.")
    print(f"Inserted scream_queens : {inserted_queens}")
    print(f"Inserted movies        : {inserted_movies}")
    print(f"Inserted appearances   : {inserted_appearances}")
    print(f"DB: {DB_PATH}")
    print(f"Source JSON: {JSON_PATH}")


if __name__ == "__main__":
    main()
