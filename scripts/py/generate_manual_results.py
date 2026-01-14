from pathlib import Path
import json

# project root: scripts/py/generate_manual_results.py -> parents[2] = repo root
BASE_DIR = Path(__file__).resolve().parents[2]

PROCESSED_FILE = BASE_DIR / "data" / "processed" / "processed_scream_queens.json"
MANUAL_RESULTS_FILE = BASE_DIR / "data" / "manual_results.json"

# load processed data
with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
    processed_data = json.load(f)

manual_results = {}

# build template based on processed titles
for actress in processed_data:
    actress_name = actress['name']
    manual_results[actress_name] = {}

    for film in actress['films']:
        title = f"{film['title']} {film['year']}"
        manual_results[actress_name][title] = None # unknow by default

# save for manual annotation
MANUAL_RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
with MANUAL_RESULTS_FILE.open("w", encoding="utf-8") as f:
    json.dump(manual_results, f, indent=2, ensure_ascii=False)

print(f"Manual results generated at: {MANUAL_RESULTS_FILE}")
