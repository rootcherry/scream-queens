#!/bin/bash

echo "===== FULL HORRORVERSE PIPELINE ====="

echo "[STEP 1] Scraping Wikipedia..."
python3 src/main.py

echo "[STEP 2] OMDb enrichment..."
python3 src/omdb_ok.py

echo "[STEP 3] DB Pipeline..."
./scripts/reset_and_run_pipeline.sh

echo "===== DONE ====="
