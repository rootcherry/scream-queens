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

export default router;
