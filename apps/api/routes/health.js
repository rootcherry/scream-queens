const express = require("express");
const router = express.Router();
const db = require("../db");

router.get("/", async (req, res) => {
  try {
    await db.get("SELECT 1"); // quick DB check
    res.json({ status: "ok" });
  } catch (err) {
    console.error("Health check failed:", err);
    res.status(500).json({ status: "error" });
  }
});

module.exports = router;
