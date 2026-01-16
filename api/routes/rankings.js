import express from "express";

import rankingsRegistry from "../../dsa/rankings/rankingsRegistry.js";
import loadFromSQLite from "../../src/db/sqliteLoader.js";

const router = express.Router();

// List all available rankings
router.get("/", (req, res) => {
  res.json({
    available: Object.keys(rankingsRegistry),
  });
});

// Rankings endpoint
router.get("/:key", (req, res) => {
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

export default router;
