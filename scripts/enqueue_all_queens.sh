#!/usr/bin/env bash

# enqueue recompute job for all queens

API_URL="http://localhost:3000"

echo "Fetching all queens..."

# clean output: no headers, no formatting
IDS=$(sqlite3 -noheader -batch data/db/horrorverse.sqlite3 "SELECT id FROM scream_queens;")

COUNT=0

for ID in $IDS; do
  echo "Enqueue queen $ID"

  curl -s -X POST "$API_URL/jobs/recompute" \
    -H "Content-Type: application/json" \
    -d "{\"queenId\": $ID}" > /dev/null

  COUNT=$((COUNT+1))
done

echo "Done. Enqueued $COUNT jobs."
