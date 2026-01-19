import express from "express";
import { publishToQueue } from "../../src/queue/publish.js";
import { openDb } from "../../src/db/db.js";

const router = express.Router();

const clampLimit = (value, defaultValue = 20, maxValue = 100) => {
  const n = Number.parseInt(value, 10);
  if (Number.isNaN(n)) return defaultValue;
  if (n <= 0) return defaultValue;
  return Math.min(n, maxValue);
};

// GET /jobs?limit=20
router.get("/", async (req, res) => {
  const limit = clampLimit(req.query.limit, 20, 100);

  try {
    const db = openDb();

    const totalRow = db.prepare("SELECT COUNT(*) AS total FROM jobs").get();
    const total = totalRow?.total ?? 0;

    const items = db
      .prepare(
        `
        SELECT id, job_type, queen_id, status, created_at, finished_at
        FROM jobs
        ORDER BY id DESC
        LIMIT ?
        `,
      )
      .all(limit);

    res.json({
      total,
      returned: items.length,
      items,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to load jobs" });
  }
});

// POST /jobs/recompute
router.post("/recompute", async (req, res) => {
  const { queenId } = req.body;

  if (!Number.isInteger(queenId) || queenId <= 0) {
    return res.status(400).json({ error: "Invalid queenId" });
  }

  const job = {
    type: "RECOMPUTE_STATS",
    createdAt: new Date().toISOString(),
    payload: { queenId },
  };

  try {
    await publishToQueue("horrorverse_jobs", job);

    res.status(202).json({
      status: "enqueued",
      jobType: job.type,
      queenId,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to enqueue job" });
  }
});

export default router;
