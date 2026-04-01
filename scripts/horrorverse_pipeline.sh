#!/bin/bash

set -e  # exit on any error
BASE_DIR=$(cd "$(dirname "$0")/.." && pwd)  # project root

# Paths and environment
PIPELINE_DIR="$BASE_DIR/pipeline"
VENV_DIR="$BASE_DIR/.venv"  # path to your virtualenv
export PYTHONPATH="$PIPELINE_DIR"  # point to pipeline modules

# activate virtual environment
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    echo "Activated venv: $VENV_DIR"
else
    echo "No virtual environment found at $VENV_DIR. Continuing without venv."
fi

# Dry-run flag
DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "===== Running in DRY-RUN mode ====="
fi

echo "===== Horrorverse Pipeline Start ====="

# STEP 0: Environment ready
echo "[STEP 0] Environment ready"
echo "PYTHONPATH=$PYTHONPATH"

# STEP 1: Test API endpoints
echo "[STEP 1] Testing API endpoints"
ENDPOINTS=(
    "/jobs?limit=5"
    "/jobs"
    "/jobs/1"
    "/jobs/abc"
    "/jobs/9999"
    "/jobs/status?status=completed&limit=5"
    "/jobs/status?status=failed"
    "/jobs/status?status=unknown"
    "/jobs/queens/1/jobs"
    "/jobs/queens/abc/jobs"
)

for ep in "${ENDPOINTS[@]}"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000$ep")
    echo "GET $ep ... HTTP $STATUS"
done

# STEP 2: Trigger recompute jobs
echo "[STEP 2] Trigger recompute jobs"
for qid in {1..10}; do
    if $DRY_RUN; then
        echo "Dry-run: would trigger recompute for queenId=$qid"
    else
        curl -s -X POST "http://localhost:3000/jobs/queens/$qid/recompute" > /dev/null
        echo "Triggered recompute for queenId=$qid"
    fi
done

# STEP 3: Monitor running jobs
echo "[STEP 3] Monitor running jobs"
if ! $DRY_RUN; then
    PENDING=$(curl -s "http://localhost:3000/jobs/status?status=pending" | jq length)
    RUNNING=$(curl -s "http://localhost:3000/jobs/status?status=running" | jq length)
    echo "Pending: $PENDING | Running: $RUNNING"
else
    echo "Dry-run: would monitor jobs"
fi

# STEP 4: Run Python pipeline modules
PIPELINE_MODULES=(
    "validation.00_validate_processed"
    "ingestion.init_db"
    "ingestion.ingest_db"
    "transformation.process_final_data"
    "transformation.rebuild_survived_data"
    "transformation.remove_survived_field"
    "updates.update_box_office_stats"
    "updates.update_processed_with_survival"
    "updates.update_survival_stats"
    "updates.update_survived"
    "reporting.generate_manual_results"
)

echo "[STEP 4] Running pipeline modules"
for module in "${PIPELINE_MODULES[@]}"; do
    if $DRY_RUN; then
        echo "Dry-run: would run $module"
    else
        echo "Running $module"
        python3 -m "$module" || { echo "Error in $module"; exit 1; }
    fi
done

echo "===== Horrorverse Pipeline Finished ====="
