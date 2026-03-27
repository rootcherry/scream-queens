#!/bin/bash
# scripts/test_jobs.sh
# Script to test Scream-Queens jobs endpoints
BASE_URL="http://localhost:3000"

echo "===== Jobs Endpoints Test ====="

# List latest 5 jobs
echo -n "GET /jobs?limit=5 ... "
curl -s "$BASE_URL/jobs?limit=5" | jq . >/dev/null && echo "OK" || echo "FAIL"

# Default limit (20)
echo -n "GET /jobs ... "
curl -s "$BASE_URL/jobs" | jq . >/dev/null && echo "OK" || echo "FAIL"

# Limit above max
echo -n "GET /jobs?limit=500 ... "
curl -s "$BASE_URL/jobs?limit=500" | jq . >/dev/null && echo "OK" || echo "FAIL"

# Job by valid ID
echo -n "GET /jobs/10 ... "
curl -s "$BASE_URL/jobs/10" | jq . >/dev/null && echo "OK" || echo "FAIL"

# Job by invalid ID
echo -n "GET /jobs/abc ... "
curl -s "$BASE_URL/jobs/abc" | jq . >/dev/null && echo "OK" || echo "FAIL"

# Job by non-existent ID
echo -n "GET /jobs/9999 ... "
curl -s "$BASE_URL/jobs/9999" | jq . >/dev/null && echo "OK" || echo "FAIL"

# First 5 completed jobs
echo -n "GET /jobs/status?status=completed&limit=5 ... "
curl -s "$BASE_URL/jobs/status?status=completed&limit=5" | jq . >/dev/null && echo "OK" || echo "FAIL"

# All failed jobs
echo -n "GET /jobs/status?status=failed ... "
curl -s "$BASE_URL/jobs/status?status=failed" | jq . >/dev/null && echo "OK" || echo "FAIL"

# Invalid status
echo -n "GET /jobs/status?status=unknown ... "
curl -s "$BASE_URL/jobs/status?status=unknown" | jq . >/dev/null && echo "OK" || echo "FAIL"

# Jobs of a valid queen
echo -n "GET /jobs/queens/1/jobs ... "
curl -s "$BASE_URL/jobs/queens/1/jobs" | jq . >/dev/null && echo "OK" || echo "FAIL"

# Queen ID invalid
echo -n "GET /jobs/queens/abc/jobs ... "
curl -s "$BASE_URL/jobs/queens/abc/jobs" | jq . >/dev/null && echo "OK" || echo "FAIL"

# Recompute valid job
echo -n "POST /jobs/recompute (queenId=1) ... "
curl -s -X POST "$BASE_URL/jobs/recompute" \
  -H "Content-Type: application/json" \
  -d '{"queenId":1}' | jq . >/dev/null && echo "OK" || echo "FAIL"

# Recompute invalid job
echo -n "POST /jobs/recompute (queenId=-5) ... "
curl -s -X POST "$BASE_URL/jobs/recompute" \
  -H "Content-Type: application/json" \
  -d '{"queenId":-5}' | jq . >/dev/null && echo "OK" || echo "FAIL"

# Recompute missing queenId
echo -n "POST /jobs/recompute (missing queenId) ... "
curl -s -X POST "$BASE_URL/jobs/recompute" \
  -H "Content-Type: application/json" \
  -d '{}' | jq . >/dev/null && echo "OK" || echo "FAIL"

echo "===== Test Finished ====="
