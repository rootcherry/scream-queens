CREATE TABLE IF NOT EXISTS queen_stats (
  scream_queen_id INTEGER PRIMARY KEY,
  movies_count INTEGER NOT NULL DEFAULT 0,
  box_office_total INTEGER NOT NULL DEFAULT 0,
  box_office_known_count INTEGER NOT NULL DEFAULT 0,
  first_movie_year INTEGER,
  last_movie_year INTEGER,
  recomputed_at TEXT NOT NULL,
  FOREIGN KEY (scream_queen_id) REFERENCES scream_queens(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_queen_stats_movies_count
ON queen_stats(movies_count);
