# pipeline/ingestion/ingest_db.py

import json
import sqlite3
from pipeline.core.paths import DB_FILE, PROCESSED_CLEAN_FILE


# CONNECTION
def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# LOAD
def load_json() -> list[dict]:
    with PROCESSED_CLEAN_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Expected top-level list")

    return data


def normalize_int(value):
    try:
        return int(value) if value is not None else None
    except:
        return None


# UPSERTS (CLEAN)
def upsert_scream_queen(conn: sqlite3.Connection, name: str) -> int:
    conn.execute(
        """
        INSERT INTO scream_queens (name)
        VALUES (?)
        ON CONFLICT(name) DO NOTHING;
        """,
        (name,),
    )

    return conn.execute(
        "SELECT id FROM scream_queens WHERE name = ?;",
        (name,),
    ).fetchone()[0]


def upsert_movie(conn: sqlite3.Connection, title: str, year, box_office) -> int:
    year_i = normalize_int(year)
    box_i = normalize_int(box_office)

    conn.execute(
        """
        INSERT INTO movies (title, year, box_office)
        VALUES (?, ?, ?)
        ON CONFLICT(title, year) DO UPDATE SET
            box_office = COALESCE(movies.box_office, excluded.box_office);
        """,
        (title, year_i, box_i),
    )

    return conn.execute(
        "SELECT id FROM movies WHERE title = ? AND year IS ?;",
        (title, year_i),
    ).fetchone()[0]


def insert_appearance(conn, queen_id: int, movie_id: int) -> bool:
    cur = conn.execute(
        """
        INSERT OR IGNORE INTO appearances (scream_queen_id, movie_id)
        VALUES (?, ?);
        """,
        (queen_id, movie_id),
    )
    return cur.rowcount == 1


# MAIN
def main() -> None:
    if not DB_FILE.exists():
        raise FileNotFoundError("DB not found")

    if not PROCESSED_CLEAN_FILE.exists():
        raise FileNotFoundError("Processed JSON not found")

    data = load_json()

    inserted_queens = 0
    inserted_movies = 0
    inserted_appearances = 0

    with get_connection() as conn:
        conn.execute("BEGIN;")

        for profile in data:
            name = profile.get("name")
            if not name:
                continue

            before = conn.execute(
                "SELECT 1 FROM scream_queens WHERE name = ?;",
                (name,),
            ).fetchone()

            queen_id = upsert_scream_queen(conn, name)

            if before is None:
                inserted_queens += 1

            for film in profile.get("films", []):
                title = film.get("title")
                if not title:
                    continue

                movie_id_before = conn.execute(
                    "SELECT id FROM movies WHERE title = ? AND year IS ?;",
                    (title, normalize_int(film.get("year"))),
                ).fetchone()

                movie_id = upsert_movie(
                    conn,
                    title,
                    film.get("year"),
                    film.get("box_office"),
                )

                if movie_id_before is None:
                    inserted_movies += 1

                if insert_appearance(conn, queen_id, movie_id):
                    inserted_appearances += 1

        conn.commit()

    print("[OK] Ingestion complete")
    print(f"Queens inserted      : {inserted_queens}")
    print(f"Movies inserted      : {inserted_movies}")
    print(f"Appearances inserted : {inserted_appearances}")
    print(f"DB: {DB_FILE}")


if __name__ == "__main__":
    main()
