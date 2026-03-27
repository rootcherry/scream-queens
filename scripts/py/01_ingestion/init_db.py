# scripts/py/init_db.py
import sqlite3
from py.paths import DB_FILE  # database path


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_table_scream_queens(cursor: sqlite3.Cursor) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS scream_queens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            birth_year INTEGER
        );
    """
    )


def create_table_movies(cursor: sqlite3.Cursor) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER,
            imdb_id TEXT UNIQUE,
            box_office INTEGER
        );
    """
    )


def create_table_appearances(cursor: sqlite3.Cursor) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS appearances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scream_queen_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            FOREIGN KEY (scream_queen_id) REFERENCES scream_queens(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id),
            UNIQUE (scream_queen_id, movie_id)
        );
    """
    )


def create_table_jobs(cursor: sqlite3.Cursor) -> None:
    cursor.execute(
        """
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
    """
    )


def create_tables(conn: sqlite3.Connection) -> None:
    """Create all tables if they do not exist."""
    cursor = conn.cursor()
    create_table_scream_queens(cursor)
    create_table_movies(cursor)
    create_table_appearances(cursor)
    create_table_jobs(cursor)
    conn.commit()


def main() -> None:
    """Initialize the database schema."""
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    create_tables(conn)
    conn.close()
    print("SQLite schema initialized successfully.")


if __name__ == "__main__":
    main()
