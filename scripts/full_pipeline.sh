#!/bin/bash
set -e

# Project root
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "[INFO] Project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT" || exit 1

# Export src to Python path
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

echo "[RESET] Cleaning previous outputs..."
rm -rf "$PROJECT_ROOT/data/processed/*"
rm -rf "$PROJECT_ROOT/data/raw/*"
rm -rf "$PROJECT_ROOT/data/cache/*"

echo "[STEP 1] Scraping scream queens..."
python3 -m scream_queens.main

echo "[STEP 2] Enriching with OMDb..."
python3 -m infrastructure.external.omdb_ok

echo "[STEP 3] Transforming data..."
python3 -m pipeline.transformation.process_final_data

echo "[STEP 4] Running DB pipeline..."
./scripts/reset_and_run_pipeline.sh

echo "[DONE] Full pipeline finished!"
