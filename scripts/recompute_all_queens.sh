#!/bin/bash
# scripts/recompute_all_queens.sh
# Description: Trigger recompute for all queens and log job IDs

LOG_FILE="jobs_run.log"
> "$LOG_FILE"  # Clear previous log

echo "===== Starting Recompute for All Queens ====="

# Fetch all queens IDs (assuming /queens endpoint returns JSON array)
QUEEN_IDS=$(curl -s http://localhost:3000/queens | jq -r '.[].id')

for QUEEN_ID in $QUEEN_IDS; do
    echo "Triggering recompute for queenId=$QUEEN_ID ..."
    RESPONSE=$(curl -s -X POST "http://localhost:3000/jobs/recompute" -d "queenId=$QUEEN_ID")

    # Extract jobId from response (assuming JSON response {jobId: ...})
    JOB_ID=$(echo "$RESPONSE" | jq -r '.jobId // "N/A"')

    echo "queenId=$QUEEN_ID -> jobId=$JOB_ID"
    echo "$(date +'%Y-%m-%d %H:%M:%S') | queenId=$QUEEN_ID | jobId=$JOB_ID" >> "$LOG_FILE"
done

echo "===== Recompute Trigger Completed ====="
echo "All job IDs saved to $LOG_FILE"
