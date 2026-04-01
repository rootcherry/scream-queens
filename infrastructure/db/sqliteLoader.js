import Database from "better-sqlite3";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DB_PATH = path.resolve(__dirname, "../../data/db/horrorverse.sqlite3");

const loadFromSQLite = () => {
  const db = new Database(DB_PATH, { readonly: true });

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
  `,
    )
    .all();

  db.close();

  const index = new Map();

  for (const row of rows) {
    if (!index.has(row.scream_queen)) {
      index.set(row.scream_queen, { films: [] });
    }

    if (row.title) {
      index.get(row.scream_queen).films.push({
        title: row.title,
        year: row.year,
        box_office: row.box_office,
      });
    }
  }

  return index;
};

export default loadFromSQLite;
