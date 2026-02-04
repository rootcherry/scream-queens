import os
import json
import time
import random
from config import WAIT_TIME_SHORT, WAIT_TIME_LONG


def wait_time(long=False):
    delay = WAIT_TIME_LONG if long else WAIT_TIME_SHORT
    time.sleep(random.uniform(*delay))


def save_raw_json(name, data):
    raw_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
    os.makedirs(raw_path, exist_ok=True)
    filename = f"{name.lower().replace(' ', '_')}.json"
    filepath = os.path.join(raw_path, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Saved raw data: {filepath}")


def save_processed_json(data, filename="scream_queens.json"):
    processed_path = os.path.join(
        os.path.dirname(__file__), '..', 'data', 'processed'
    )
    os.makedirs(processed_path, exist_ok=True)
    filepath = os.path.join(processed_path, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Saved processed data: {filepath}")
