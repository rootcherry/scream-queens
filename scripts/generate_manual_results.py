import json
import os

# paths
PROCESSED_FILE = os.path.join('..', 'data', 'processed', 'processed_scream_queens.json')
MANUAL_RESULTS_FILE = os.path.join('..', 'data', 'manual_results.json')

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
os.makedirs(os.path.dirname(MANUAL_RESULTS_FILE), exist_ok=True)
with open(MANUAL_RESULTS_FILE, 'w', encoding='utf-8') as f:
    json.dump(manual_results, f, indent=2, ensure_ascii=False)

print(f"Manual results generated at: {MANUAL_RESULTS_FILE}")
