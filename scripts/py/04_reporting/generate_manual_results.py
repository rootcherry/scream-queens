# scripts/py/generate_manual_results.py
from py.paths import PROCESSED_FILE, MANUAL_RESULTS_FILE  # import file paths
import json

# load processed data
with PROCESSED_FILE.open("r", encoding="utf-8") as f:
    processed_data = json.load(f)

manual_results = {}

# build template for each actress and film
for actress in processed_data:
    actress_name = actress["name"]
    manual_results[actress_name] = {}

    for film in actress.get("films", []):
        title = f"{film['title']} {film['year']}"
        manual_results[actress_name][title] = None  # unknown by default

# ensure folder exists and save manual results
MANUAL_RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
with MANUAL_RESULTS_FILE.open("w", encoding="utf-8") as f:
    json.dump(manual_results, f, indent=2, ensure_ascii=False)

print(f"Manual results generated at: {MANUAL_RESULTS_FILE}")
