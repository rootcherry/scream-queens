#!/bin/bash
# Full Horrorverse pipeline: recompute, wait for jobs, run post-processing
set -euo pipefail
IFS=$'\n\t'

BASE_DIR="$(dirname "$0")"
PY_SCRIPTS="$BASE_DIR/py"

echo "===== Horrorverse Full Pipeline Start ====="

# Step 1: Trigger recompute jobs
MAX_QUEEN_ID=10
for id in $(seq 1 $MAX_QUEEN_ID); do
    echo "Triggering recompute for queenId=$id"
    curl -s -X POST "http://localhost:3000/jobs/recompute" -d "queenId=$id" > /dev/null
done

# Step 2: Monitor jobs
all_done=0
timeout=300
elapsed=0
sleep_interval=2
while [ $all_done -eq 0 ]; do
    pending=$(curl -s "http://localhost:3000/jobs?status=pending" | jq '.length // 0')
    running=$(curl -s "http://localhost:3000/jobs?status=running" | jq '.length // 0')
    echo "Pending: $pending | Running: $running"

    if [ "$pending" -eq 0 ] && [ "$running" -eq 0 ]; then
        all_done=1
        break
    fi

    sleep $sleep_interval
    elapsed=$((elapsed + sleep_interval))
    if [ $elapsed -ge $timeout ]; then
        echo "Timeout reached, some jobs may not have finished."
        break
    fi
done

# Step 3: Run Python scripts
SCRIPTS_ORDER=(
    "00_validation/00_validate_processed.py"
    "00_validation/survived_search_template.py"
    "01_ingestion/init_db.py"
    "01_ingestion/ingest_db.py"
    "02_transformation/process_final_data.py"
    "02_transformation/rebuild_survived_data.py"
    "02_transformation/remove_survived_field.py"
    "03_updates/update_processed_with_survival.py"
    "03_updates/update_survived.py"
    "03_updates/update_survival_stats.py"
    "03_updates/update_box_office_stats.py"
    "04_reporting/generate_manual_results.py"
)

for script in "${SCRIPTS_ORDER[@]}"; do
    echo "Running $script..."
    python3 "$PY_SCRIPTS/$script" || { echo "$script failed! Aborting."; exit 1; }
done

echo "===== Horrorverse Full Pipeline Finished ====="
