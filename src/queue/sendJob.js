import { publishToQueue } from "./publish.js";

const job = {
  type: "TEST_JOB",
  createdAt: new Date().toISOString(),
  payload: {
    queenId: 1,
    action: "recompute_stats",
  },
};

await publishToQueue("horrorverse_jobs", job);
