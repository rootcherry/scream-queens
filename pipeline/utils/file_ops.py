from pathlib import Path
import json
import shutil
from datetime import datetime


def load_json(path: Path):
    """Load JSON file from path"""
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path: Path, indent=2):
    """Save data as JSON to path"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def backup_json(src: Path, backup_dir: Path, suffix: str = None):
    """Create a timestamped backup of src in backup_dir"""
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = suffix or src.stem
    backup_path = backup_dir / f"{name}_{timestamp}.bak.json"
    shutil.copy(src, backup_path)
    return backup_path
