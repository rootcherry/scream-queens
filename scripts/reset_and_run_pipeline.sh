#!/bin/bash
set -e

echo "===== RESET + RUN PIPELINE ====="

BASE_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$BASE_DIR"

source .venv/bin/activate
export PYTHONPATH=.

# STEP 0: RESET DB
echo "[STEP 0] Reset DB..."
rm -f data/db/horrorverse.sqlite3
python3 -m pipeline.ingestion.init_db

# STEP 1: TRANSFORMATION
echo "[STEP 1] Transformation..."
python3 -m pipeline.transformation.process_final_data

# STEP 2: INGESTION
echo "[STEP 2] Ingestion..."
python3 -m pipeline.ingestion.ingest_db

# STEP 3: REPORTING
echo "[STEP 3] Reporting..."
python3 -m pipeline.reporting.generate_manual_results

echo "===== PIPELINE DONE ====="
