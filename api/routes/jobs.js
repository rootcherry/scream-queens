import express from "express";
import { publishToQueue } from "../../src/queue/publish.js";
import { openDb } from "../../src/db/db.js";

const router = express.Router();

// Helper function to safely clamp numeric values like query limits
const clampLimit = (value, defaultValue = 20, maxValue = 100) => {
  const n = Number.parseInt(value, 10);

  // If value is not a number or invalid, fallback to default
  if (Number.isNaN(n) || n <= 0) return defaultValue;

  // Ensure value does not exceed maxValue
  return Math.min(n, maxValue);
};

// =========================
// GET /jobs
// List all jobs with optional limit
// =========================
router.get("/", async (req, res) => {
  const limit = clampLimit(req.query.limit, 20, 100);

  try {
    const db = openDb();

    // Get total count of jobs
    const totalRow = db.prepare("SELECT COUNT(*) AS total FROM jobs").get();
    const total = totalRow?.total ?? 0;

    // Fetch most recent jobs, limited by query parameter
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

// =========================
// GET /jobs/:id
// Return a single job by its ID
// =========================
router.get("/:id", async (req, res) => {
  const id = Number.parseInt(req.params.id, 10);

  // Validate input
  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ error: "Invalid job id" });
  }

  try {
    const db = openDb();

    // Fetch job by ID
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

// =========================
// GET /jobs/queens/:queenId/jobs
// List all jobs for a specific queen
// =========================
router.get("/queens/:queenId/jobs", async (req, res) => {
  const queenId = Number.parseInt(req.params.queenId, 10);
  const limit = clampLimit(req.query.limit, 10, 100);

  if (!Number.isInteger(queenId) || queenId <= 0) {
    return res.status(400).json({ error: "Invalid queenId" });
  }

  try {
    const db = openDb();

    // Fetch jobs for the queen, ordered by newest first
    const items = db
      .prepare(
        `
        SELECT id, job_type, queen_id, status, created_at, finished_at
        FROM jobs
        WHERE queen_id = ?
        ORDER BY id DESC
        LIMIT ?
        `,
      )
      .all(queenId, limit);

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

// =========================
// POST /jobs/recompute
// Enqueue a recompute stats job for a queen
// =========================
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
    // Send job to RabbitMQ / queue
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
