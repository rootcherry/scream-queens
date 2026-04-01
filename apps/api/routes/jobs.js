import express from "express";
import { publishToQueue } from "../../../infrastructure/queue/publish.js";
import { openDb } from "../../../infrastructure/db/db.js";

const router = express.Router();

// Helper: clamp number between default and max
const clampLimit = (value, defaultValue = 20, maxValue = 100) => {
  const n = Number.parseInt(value, 10);
  if (Number.isNaN(n) || n <= 0) return defaultValue;
  return Math.min(n, maxValue);
};

// GET /jobs
router.get("/", (req, res) => {
  const limit = clampLimit(req.query.limit, 20, 100);

  try {
    const db = openDb();

    const totalRow = db.prepare("SELECT COUNT(*) as total FROM jobs").get();

    const items = db
      .prepare(
        `
        SELECT SELECT id, job_type, status, created_at, started_at, finished_at, attempts
        FROM jobs
        ORDER BY id DESC
        LIMIT ?
      `,
      )
      .all(limit);

    res.json({
      total: totalRow.total,
      returned: items.length,
      items,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to load jobs" });
  }
});

// GET /jobs/status
router.get("/status", (req, res) => {
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
        SELECT id, job_type, status, created_at
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

// GET /jobs/metrics
router.get("/metrics", (req, res) => {
  try {
    const db = openDb();

    const rows = db
      .prepare(
        `
        SELECT status, COUNT(*) as count
        FROM jobs
        GROUP BY status
      `,
      )
      .all();

    const statusCounts = {
      pending: 0,
      running: 0,
      completed: 0,
      failed: 0,
    };

    rows.forEach((r) => {
      statusCounts[r.status] = r.count;
    });

    res.json(statusCounts);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to load metrics" });
  }
});

// GET /jobs/:id
router.get("/:id", (req, res) => {
  const id = Number(req.params.id);

  try {
    const db = openDb();

    const job = db.prepare(`SELECT * FROM jobs WHERE id = ?`).get(id);

    if (!job) {
      return res.status(404).json({ error: "Job not found" });
    }

    res.json(job);
  } catch (err) {
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
    job_type: "RECOMPUTE_STATS",
    status: "pending",
    created_at: new Date().toISOString(),
    payload: { queenId },
  };

  try {
    await publishToQueue("horrorverse_jobs", job);

    res.status(202).json({
      status: "enqueued",
      jobType: job.job_type,
      queenId,
    });
  } catch (err) {
    console.error("enqueue error:", err);
    res.status(500).json({ error: "Failed to enqueue job" });
  }
});

export default router;
