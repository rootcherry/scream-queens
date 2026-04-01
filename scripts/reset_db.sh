#!/usr/bin/env bash

set -e

echo "Resetting database..."

rm -f data/db/horrorverse.sqlite3

source .venv/bin/activate

echo "[db] init schema..."
PYTHONPATH=./pipeline python pipeline/ingestion/init_db.py

echo "[db] loading data..."
PYTHONPATH=./pipeline python pipeline/ingestion/ingest_db.py

echo "[db] applying migrations..."
sqlite3 data/db/horrorverse.sqlite3 < infrastructure/db/002_add_queen_stats.sql
sqlite3 data/db/horrorverse.sqlite3 < infrastructure/db/003_add_attempts_to_jobs.sql

echo "Database ready."
