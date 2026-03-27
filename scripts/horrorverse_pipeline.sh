#!/bin/bash
# Handles ingestion, transformation, updates, and reporting

set -e  # exit on errors
BASE_DIR=$(cd "$(dirname "$0")/.." && pwd)  # project root
SCRIPTS_DIR="$BASE_DIR/scripts"

# PYTHONPATH must point to scripts/ to find py/ modules
export PYTHONPATH="$SCRIPTS_DIR"

DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "===== Running in DRY-RUN mode ====="
fi

echo "===== Horrorverse Pipeline Start ====="

# -----------------------------
# STEP 0: Setup environment
# -----------------------------
echo "[STEP 0] Setup environment..."
echo "PYTHONPATH set to $PYTHONPATH"

# -----------------------------
# STEP 1: Test API endpoints
# -----------------------------
echo "[STEP 1] Testing API endpoints..."
declare -a ENDPOINTS=(
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

# -----------------------------
# STEP 2: Trigger recompute jobs
# -----------------------------
echo "[STEP 2] Trigger recompute jobs..."
for qid in {1..10}; do
    if $DRY_RUN; then
        echo "Dry-run: would trigger recompute for queenId=$qid"
    else
        echo "Triggering recompute for queenId=$qid"
        curl -s -X POST "http://localhost:3000/jobs/queens/$qid/recompute" > /dev/null
    fi
done

# -----------------------------
# STEP 3: Monitor running jobs
# -----------------------------
echo "[STEP 3] Monitor running jobs..."
if ! $DRY_RUN; then
    # simple check (adjust if your API returns actual job status)
    PENDING=$(curl -s "http://localhost:3000/jobs/status?status=pending" | jq length)
    RUNNING=$(curl -s "http://localhost:3000/jobs/status?status=running" | jq length)
    echo "Pending: $PENDING | Running: $RUNNING"
else
    echo "Dry-run: would monitor jobs"
fi

# -----------------------------
# STEP 4: Validate Python scripts syntax
# -----------------------------
echo "[STEP 4] Validate Python scripts syntax..."
for script in "${PY_SCRIPTS[@]}"; do
    if $DRY_RUN; then
        echo "Dry-run: would check syntax for $script"
    else
        echo "Checking $script syntax..."
        python3 -m py_compile "$SCRIPTS_DIR/$script" || { echo "$script failed syntax check"; exit 1; }
    fi
done

# -----------------------------
# STEP 5: Run Python scripts
# -----------------------------
echo "[STEP 5] Run Python scripts..."
for script in "${PY_SCRIPTS[@]}"; do
    if $DRY_RUN; then
        echo "Dry-run: would run $script"
    else
        echo "Running $script..."
        python3 "$SCRIPTS_DIR/$script" || { echo "Error running $script"; exit 1; }
    fi
done

echo "===== Horrorverse Pipeline Finished ====="
