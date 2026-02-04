from pathlib import Path
import sqlite3

DB_PATH = Path("data/db/horrorverse.sqlite3")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scream_queens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            birth_year INTEGER
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER,
            imdb_id TEXT UNIQUE,
            box_office INTEGER
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appearances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scream_queen_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            FOREIGN KEY (scream_queen_id) REFERENCES scream_queens(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id),
            UNIQUE (scream_queen_id, movie_id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_type TEXT NOT NULL,
            queen_id INTEGER,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            started_at TEXT,
            finished_at TEXT,
            error TEXT
        );
    """)


    conn.commit()


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection()
    create_tables(conn)
    conn.close()

    print("SQLite schema initialized successfully.")


if __name__ == "__main__":
    main()
