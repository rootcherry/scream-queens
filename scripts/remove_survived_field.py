import json
import os

# paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_FILE = os.path.join(BASE_DIR, '../data/processed/processed_scream_queens_backup.json')
OUTPUT_FILE = os.path.join(BASE_DIR, '../data/processed/processed_scream_queens_no_survived.json')

# load JSON
with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# remove 'survived' field from every film
for actress in data:
    for film in actress.get('films', []):
        if 'survived' in film:
            del film['survived']

# save cleaned JSON
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"'survived' field removed from all films. Saved to {OUTPUT_FILE}")
