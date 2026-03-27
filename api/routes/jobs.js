import express from "express";
import { publishToQueue } from "../../src/queue/publish.js";
import { openDb } from "../../src/db/db.js";

const router = express.Router();

// Helper: clamp number between default and max
const clampLimit = (value, defaultValue = 20, maxValue = 100) => {
  const n = Number.parseInt(value, 10);
  if (Number.isNaN(n) || n <= 0) return defaultValue;
  return Math.min(n, maxValue);
};

// GET /jobs?limit=20
// Return latest jobs with optional limit
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

// GET /jobs/status?status=completed&limit=20
// Return jobs filtered by status
router.get("/status", async (req, res) => {
  const { status } = req.query;
  const limit = clampLimit(req.query.limit, 20, 100);

  const allowedStatuses = ["pending", "running", "completed", "failed"];
  if (!status || !allowedStatuses.includes(status)) {
    return res.status(400).json({ error: "Invalid or missing status" });
  }

  try {
    const db = openDb();
    const items = db
      .prepare(
        `
        SELECT id, job_type, queen_id, status, created_at, finished_at
        FROM jobs
        WHERE status = ?
        ORDER BY id DESC
        LIMIT ?
        `,
      )
      .all(status, limit);

    res.json({
      status,
      returned: items.length,
      items,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to load jobs by status" });
  }
});

// GET /jobs/:id
// Return one job by id
router.get("/:id", async (req, res) => {
  const id = Number.parseInt(req.params.id, 10);
  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ error: "Invalid job id" });
  }

  try {
    const db = openDb();
    const job = db
      .prepare(
        `
        SELECT id, job_type, queen_id, status, created_at, finished_at
        FROM jobs
        WHERE id = ?
        `,
      )
      .get(id);

    if (!job) {
      return res.status(404).json({ error: "Job not found" });
    }

    res.json(job);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to load job" });
  }
});

// GET /jobs/queens/:queenId/jobs
// Return jobs for a specific queen
router.get("/queens/:queenId/jobs", async (req, res) => {
  const queenId = Number.parseInt(req.params.queenId, 10);
  if (!Number.isInteger(queenId) || queenId <= 0) {
    return res.status(400).json({ error: "Invalid queenId" });
  }

  try {
    const db = openDb();
    const items = db
      .prepare(
        `
        SELECT id, job_type, queen_id, status, created_at, finished_at
        FROM jobs
        WHERE queen_id = ?
        ORDER BY id DESC
        `,
      )
      .all(queenId);

    res.json({
      queenId,
      returned: items.length,
      items,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to load queen's jobs" });
  }
});

// POST /jobs/recompute
// Enqueue a recompute stats job for a queen
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
