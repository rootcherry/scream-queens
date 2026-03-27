#!/bin/bash

set -e

echo "===== RESET + RUN PIPELINE ====="

BASE_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$BASE_DIR"

source .venv/bin/activate
export PYTHONPATH=scripts

# -----------------------------
# STEP 0: RESET DB
# -----------------------------
echo "[STEP 0] Reset DB..."
rm -f data/db/horrorverse.sqlite3
python scripts/py/01_ingestion/init_db.py

# -----------------------------
# STEP 1: TRANSFORMATION (gera clean JSON)
# -----------------------------
echo "[STEP 1] Transformation..."
python scripts/py/02_transformation/process_final_data.py

# -----------------------------
# STEP 2: INGESTION
# -----------------------------
echo "[STEP 2] Ingestion..."
python scripts/py/01_ingestion/ingest_db.py

# -----------------------------
# STEP 3: UPDATES
# -----------------------------
echo "[STEP 3] Updates..."
python scripts/py/03_updates/update_box_office_stats.py
python scripts/py/03_updates/update_survival_stats.py
python scripts/py/03_updates/update_processed_with_survival.py

# -----------------------------
# STEP 4: REPORTING
# -----------------------------
echo "[STEP 4] Reporting..."
python scripts/py/04_reporting/generate_manual_results.py

echo "===== PIPELINE DONE ====="
