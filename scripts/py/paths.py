# scripts/py/paths.py
from pathlib import Path

# Root of the project (repo root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Folder with processed data
DATA_DIR = BASE_DIR / "data" / "processed"

# Main processed files
PROCESSED_FILE = DATA_DIR / "processed_scream_queens.json"
PROCESSED_CLEAN_FILE = DATA_DIR / "processed_scream_queens_clean.json"
SURVIVED_FILE = DATA_DIR / "survived_data.json"

# Backup folder
BACKUP_DIR = DATA_DIR / "backup"

# Manual results file
MANUAL_RESULTS_FILE = BASE_DIR / "data" / "manual_results.json"

# SQLite database file
DB_FILE = BASE_DIR / "data" / "db" / "horrorverse.sqlite3"

# Optional: files for remove_survived script
PROCESSED_BACKUP_FILE = BACKUP_DIR / "processed_scream_queens_backup.json"
PROCESSED_NO_SURVIVED_FILE = DATA_DIR / "processed_scream_queens_no_survived.json"
