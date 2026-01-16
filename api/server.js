import express from "express";

import rankingsRoutes from "./routes/rankings.js";
import screamQueensRoutes from "./routes/screamQueens.js";

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;

// Health check
app.get("/health", (req, res) => {
  res.json({ ok: true });
});

// Mount routes
app.use("/rankings", rankingsRoutes);
app.use("/scream-queens", screamQueensRoutes);

app.listen(PORT, () => {
  console.log(`API running on http://localhost:${PORT}`);
});
