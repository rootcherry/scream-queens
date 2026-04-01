import express from "express";
import Database from "better-sqlite3";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const router = express.Router();

// --- Corrige caminho absoluto do DB ---
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const dbPath = join(__dirname, "../../../data/db/horrorverse.sqlite3");

// Conecta ao SQLite
const db = new Database(dbPath, { readonly: true });

// --- Rotas ---

// List all scream queens
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

// Get single scream queen by ID
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

// Get films for a scream queen
router.get("/:id/films", (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ error: "Invalid id" });
  }

  const order = req.query.order === "asc" ? "ASC" : "DESC";
  const limitRaw = req.query.limit;
  const limit = Number.isFinite(Number(limitRaw))
    ? Math.max(1, Math.min(100, Number(limitRaw)))
    : 10;

  try {
    // Verifica se a scream queen existe
    const queen = db
      .prepare("SELECT id, name FROM scream_queens WHERE id = ?")
      .get(id);

    if (!queen) {
      return res.status(404).json({ error: "Not found" });
    }

    // Total de filmes
    const totalRow = db
      .prepare(
        "SELECT COUNT(*) AS total FROM appearances WHERE scream_queen_id = ?",
      )
      .get(id);
    const total = totalRow?.total ?? 0;

    // Lista de filmes com LIMIT
    const films = db
      .prepare(
        `SELECT
          m.id,
          m.title,
          m.year,
          m.imdb_id,
          m.box_office
        FROM appearances a
        JOIN movies m ON a.movie_id = m.id
        WHERE a.scream_queen_id = ?
        ORDER BY m.year ${order}, m.title ${order}
        LIMIT ?`,
      )
      .all(id, limit);

    res.json({
      queen,
      films,
      total,
      returned: films.length,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
