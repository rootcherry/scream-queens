import Database from "better-sqlite3";
import path from "path";
import { fileURLToPath } from "url";

// Resolve __dirname for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Absolute path to the SQLite database
const DB_PATH = path.resolve(__dirname, "../../data/db/horrorverse.sqlite3");

/**
 * Loads Scream Queens data from SQLite and reconstructs
 * the same in-memory structure previously built from JSON.
 *
 * Return shape:
 * Map<string, { films: Array<{ title, year, box_office }> }>
 */
const loadFromSQLite = () => {
  // Open database in read-only mode (CLI-friendly, safe)
  const db = new Database(DB_PATH, { readonly: true });

  // Flat query: one row per (scream_queen, movie)
  // LEFT JOIN ensures actresses with no movies are included
  const rows = db
    .prepare(
      `
    SELECT
      sq.name AS scream_queen,
      m.title AS title,
      m.year AS year,
      m.box_office AS box_office
    FROM scream_queens sq
    LEFT JOIN appearances a ON a.scream_queen_id = sq.id
    LEFT JOIN movies m ON m.id = a.movie_id
    ORDER BY sq.name;
  `
    )
    .all();

  db.close();

  // Rebuild the same "index" structure expected by the DSA layer
  const index = new Map();

  for (const row of rows) {
    const name = row.scream_queen;

    // Initialize actress entry if not present
    if (!index.has(name)) {
      index.set(name, { films: [] });
    }

    // If there is no associated movie (LEFT JOIN case), skip
    if (row.title) {
      index.get(name).films.push({
        title: row.title,
        year: row.year,
        box_office: row.box_office,
      });
    }
  }

  return index;
};

export default loadFromSQLite;
