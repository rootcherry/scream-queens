import { join } from "path";

import express from "express";
import Database from "better-sqlite3";

import rankingsRegistry from "../dsa/rankings/rankingsRegistry.js";
import loadFromSQLite from "../src/db/sqliteLoader.js";

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;

const dbPath = join(process.cwd(), "data/db/horrorverse.sqlite3");
const db = new Database(dbPath, { readonly: true });

// Health check
app.get("/health", (req, res) => {
  res.json({ ok: true });
});

// List all available rankings
app.get("/rankings", (req, res) => {
  res.json({
    available: Object.keys(rankingsRegistry),
  });
});

// Rankings endpoint
app.get("/rankings/:key", (req, res) => {
  const { key } = req.params;
  const order = req.query.order || "desc";
  const limitRaw = req.query.limit;
  const limit = Number.isFinite(Number(limitRaw)) ? Number(limitRaw) : 10;

  const rankFn = rankingsRegistry[key];
  if (!rankFn) {
    return res.status(400).json({
      error: "Unknown ranking key",
      available: Object.keys(rankingsRegistry),
    });
  }

  try {
    const index = loadFromSQLite();
    const ranking = rankFn(index, order);
    const safeLimit = Math.max(1, Math.min(limit, 100));

    res.json({
      key,
      order,
      limit: safeLimit,
      results: ranking.slice(0, safeLimit),
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// List all scream queens from DB
app.get("/scream-queens", (req, res) => {
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

app.listen(PORT, () => {
  console.log(`API running on http://localhost:${PORT}`);
});
