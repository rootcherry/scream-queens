# scripts/py/ingest_db.py
import json
import sqlite3
from py.paths import DB_FILE, PROCESSED_CLEAN_FILE  # import paths


# get sqlite connection
def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# load JSON data
def load_json() -> list[dict]:
    with PROCESSED_CLEAN_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON top-level list, got: {type(data).__name__}")
    return data


# safely convert value to int
def normalize_int(value):
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# insert scream queen if not exists and return id
def upsert_scream_queen(conn: sqlite3.Connection, name: str) -> int:
    conn.execute(
        "INSERT INTO scream_queens (name) VALUES (?) ON CONFLICT(name) DO NOTHING;",
        (name,),
    )
    row = conn.execute(
        "SELECT id FROM scream_queens WHERE name = ?;", (name,)
    ).fetchone()
    if row is None:
        raise RuntimeError(f"Failed to get scream_queen id for name={name}")
    return int(row[0])


# insert movie or update box_office and return id
def upsert_movie(conn: sqlite3.Connection, title: str, year, box_office) -> int:
    year_i = normalize_int(year)
    box_i = normalize_int(box_office)
    row = conn.execute(
        "SELECT id FROM movies WHERE title = ? AND year IS ?;", (title, year_i)
    ).fetchone()
    if row is not None:
        movie_id = int(row[0])
        if box_i is not None:
            conn.execute(
                "UPDATE movies SET box_office = COALESCE(box_office, ?) WHERE id = ?;",
                (box_i, movie_id),
            )
        return movie_id
    cur = conn.execute(
        "INSERT INTO movies (title, year, box_office) VALUES (?, ?, ?);",
        (title, year_i, box_i),
    )
    return int(cur.lastrowid)


# insert appearance relation
def insert_appearance(
    conn: sqlite3.Connection, scream_queen_id: int, movie_id: int
) -> bool:
    cur = conn.execute(
        "INSERT OR IGNORE INTO appearances (scream_queen_id, movie_id) VALUES (?, ?);",
        (scream_queen_id, movie_id),
    )
    return cur.rowcount == 1


# main ingestion routine
def main() -> None:
    if not DB_FILE.exists():
        raise FileNotFoundError(f"DB not found at {DB_FILE}. Run init_db.py first.")
    if not PROCESSED_CLEAN_FILE.exists():
        raise FileNotFoundError(f"JSON not found at {PROCESSED_CLEAN_FILE}")

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
            before = conn.execute(
                "SELECT 1 FROM scream_queens WHERE name = ?;", (name,)
            ).fetchone()
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
    print(f"DB: {DB_FILE}")
    print(f"Source JSON: {PROCESSED_CLEAN_FILE}")


if __name__ == "__main__":
    main()
