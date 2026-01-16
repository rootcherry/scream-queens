import express from "express";
import Database from "better-sqlite3";
import { join } from "path";

const router = express.Router();

const dbPath = join(process.cwd(), "data/db/horrorverse.sqlite3");
const db = new Database(dbPath, { readonly: true });

// List all scream queens from DB
router.get("/", (req, res) => {
  try {
    const rows = db
      .prepare("SELECT id, name FROM scream_queens ORDER BY name ASC")
      .all();

    res.json(rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Get a single scream queen by id
router.get("/:id", (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ error: "Invalid id" });
  }

  try {
    const row = db
      .prepare("SELECT id, name FROM scream_queens WHERE id = ?")
      .get(id);

    if (!row) {
      return res.status(404).json({ error: "Not found" });
    }

    res.json(row);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Get all films for a scream queen
router.get("/:id/films", (req, res) => {
  const id = Number(req.params.id);

  const order = req.query.order === "asc" ? "ASC" : "DESC";

  const limitRaw = req.query.limit;
  const limit = Number.isFinite(Number(limitRaw))
    ? Math.max(1, Math.min(100, Number(limitRaw)))
    : 10;

  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ error: "Invalid id" });
  }

  try {
    // Primeiro checamos se a queen existe
    const queen = db
      .prepare("SELECT id, name FROM scream_queens WHERE id = ?")
      .get(id);

    if (!queen) {
      return res.status(404).json({ error: "Not found" });
    }

    // Agora buscamos os filmes dela
    const films = db
      .prepare(
        `
    SELECT
      m.id,
      m.title,
      m.year,
      m.imdb_id,
      m.box_office
    FROM appearances a
    JOIN movies m ON a.movie_id = m.id
    WHERE a.scream_queen_id = ?
    ORDER BY m.year ${order}, m.title ${order}
    LIMIT ${limit}
  `
      )
      .all(id);

    res.json({
      queen,
      films,
      count: films.length,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
