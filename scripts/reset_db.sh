#!/usr/bin/env bash

echo "Resetting database..."

rm -f data/db/horrorverse.sqlite3

python scripts/py/01_ingestion/init_db.py

echo "Database reset complete."
