# pipeline/core/paths.py
from pathlib import Path

# Project Root
# Root folder of the repository
# Using __file__ ensures paths are relative to this script
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
BACKUP_DIR = PROCESSED_DIR / "backup"

# Main processed files
PROCESSED_FILE = PROCESSED_DIR / "scream_queens.json"
PROCESSED_CLEAN_FILE = PROCESSED_DIR / "processed_scream_queens_clean.json"
SURVIVED_FILE = PROCESSED_DIR / "survived_data.json"

# Backup / optional files
PROCESSED_BACKUP_FILE = BACKUP_DIR / "processed_scream_queens_backup.json"
PROCESSED_NO_SURVIVED_FILE = PROCESSED_DIR / "processed_scream_queens_no_survived.json"

# Manual results
MANUAL_RESULTS_FILE = DATA_DIR / "manual_results.json"

# Database
DB_FILE = DATA_DIR / "db" / "horrorverse.sqlite3"
