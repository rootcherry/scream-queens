# pipeline/setup_dirs.py
from pathlib import Path
from pipeline.core.paths import DATA_DIR, RAW_DIR, CACHE_DIR, PROCESSED_DIR, BACKUP_DIR


# ensures any parent dir | already exists
def ensure_directories_exist():
    dirs_to_create = [DATA_DIR, RAW_DIR, CACHE_DIR, PROCESSED_DIR, BACKUP_DIR]

    for directory in dirs_to_create:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Ensured directory exists: {directory}")


# Call at the pipeline start
if __name__ == "__main__":
    ensure_directories_exist()
