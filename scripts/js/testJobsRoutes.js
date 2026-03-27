// scripts/py/testJobsRoutes.js
import fetch from "node-fetch";

const API = "http://localhost:3000/jobs";

// Helper: log com título
function logTitle(title) {
  console.log("\n====", title, "====");
}

// Test GET /jobs?limit=5
async function testJobsList() {
  logTitle("GET /jobs?limit=5");
  const res = await fetch(`${API}?limit=5`);
  const data = await res.json();
  console.log(JSON.stringify(data, null, 2));
}

// Test GET /jobs/status?status=completed
async function testJobsByStatus() {
  logTitle("GET /jobs/status?status=completed");
  const res = await fetch(`${API}/status?status=completed&limit=5`);
  const data = await res.json();
  console.log(JSON.stringify(data, null, 2));
}

// Test GET /jobs/:id
async function testJobById(id) {
  logTitle(`GET /jobs/${id}`);
  const res = await fetch(`${API}/${id}`);
  const data = await res.json();
  console.log(JSON.stringify(data, null, 2));
}

// Test GET /jobs/queens/:queenId/jobs
async function testJobsByQueen(queenId) {
  logTitle(`GET /jobs/queens/${queenId}/jobs`);
  const res = await fetch(`${API}/queens/${queenId}/jobs`);
  const data = await res.json();
  console.log(JSON.stringify(data, null, 2));
}

// Test GET /jobs/metrics
async function testJobsMetrics() {
  logTitle("GET /jobs/metrics");
  const res = await fetch(`${API}/metrics`);
  const data = await res.json();
  console.log(JSON.stringify(data, null, 2));
}

// Test POST /jobs/recompute
async function testEnqueueJob(queenId = 1) {
  logTitle(`POST /jobs/recompute (queenId=${queenId})`);
  const res = await fetch(`${API}/recompute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ queenId }),
  });
  const data = await res.json();
  console.log(JSON.stringify(data, null, 2));
}

async function runAllTests() {
  await testJobsList();
  await testJobsByStatus();
  await testJobsByQueen(1);

  // Pegar último job id para testar GET /jobs/:id
  const lastJobRes = await fetch(`${API}?limit=1`);
  const lastJobData = await lastJobRes.json();
  const lastJobId = lastJobData.items?.[0]?.id;
  if (lastJobId) await testJobById(lastJobId);

  await testJobsMetrics();
  await testEnqueueJob(1); // cria um job para ver se fila funciona
}

runAllTests().catch(console.error);
