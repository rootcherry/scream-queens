import express from "express";
import { publishToQueue } from "../../src/queue/publish.js";

const router = express.Router();

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
