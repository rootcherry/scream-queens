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

// GET /jobs/:id
// Goal: return ONE job from SQLite using its id
router.get("/:id", async (req, res) => {
  // STEP 1: read id from the URL and convert to number
  const id = Number.parseInt(req.params.id, 10);

  // STEP 2: basic validation to avoid invalid input
  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ error: "Invalid job id" });
  }

  try {
    // STEP 3: open read-only connection to SQLite
    const db = openDb();

    // STEP 4: fetch one job from the jobs table
    const job = db
      .prepare(
        `
        SELECT
          id,
          job_type,
          queen_id,
          status,
          created_at,
          finished_at
        FROM jobs
        WHERE id = ?
        `,
      )
      .get(id);

    // STEP 5: handle "not found"
    if (!job) {
      return res.status(404).json({ error: "Job not found" });
    }

    // STEP 6: return the job to the client
    res.json(job);
  } catch (err) {
    // STEP 7: catch unexpected errors
    console.error(err);
    res.status(500).json({ error: "Failed to load job" });
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
