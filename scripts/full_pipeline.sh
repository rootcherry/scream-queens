#!/bin/bash
set -e

echo "===== FULL HORRORVERSE PIPELINE ====="

# RESET
echo "[RESET] Cleaning previous outputs..."
rm -f data/processed/scream_queens.json
rm -f data/processed/processed_scream_queens_clean.json
rm -f data/cache/omdb_cache.json

# STEP 1: Scraping
echo "[STEP 1] Scraping Wikipedia..."
python3 src/main.py

# STEP 2: OMDb enrichment
echo "[STEP 2] OMDb enrichment..."
python3 infrastructure/external/omdb_ok.py

# STEP 3: Transformation (core)
echo "[STEP 3] Transformation..."
python3 pipeline/transformation/process_final_data.py

# STEP 4: DB Pipeline
echo "[STEP 4] DB Pipeline..."
./scripts/reset_and_run_pipeline.sh

echo "===== DONE ====="
