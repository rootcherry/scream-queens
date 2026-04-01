# src/scream_queens/utils.py
import json
import time
import random
from pipeline.core.paths import RAW_DIR, PROCESSED_FILE
from scream_queens.config import WAIT_TIME_SHORT, WAIT_TIME_LONG


def wait_time(long=False):
    delay = WAIT_TIME_LONG if long else WAIT_TIME_SHORT
    time.sleep(random.uniform(*delay))


def save_raw_json(name, data):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{name.lower().replace(' ', '_')}.json"
    filepath = RAW_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Saved raw data: {filepath}")


def save_processed_json(data, filepath=PROCESSED_FILE):
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Saved processed data: {filepath}")
