# pipeline/core/paths.py
from pathlib import Path

# Project Root -> pyproject.toml
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if not (BASE_DIR / "pyproject.toml").exists():
    raise RuntimeError("pyproject.toml not found in project root")

# Data directories
DATA_DIR = BASE_DIR / "data"        # root/data
RAW_DIR = DATA_DIR / "raw"
CACHE_DIR = DATA_DIR / "cache"
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
