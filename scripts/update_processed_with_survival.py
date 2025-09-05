import json
import os
import re
import shutil
from datetime import datetime
from rapidfuzz import fuzz, process

# paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_FILE = os.path.join(BASE_DIR, '../data/processed/processed_scream_queens.json')
SURVIVED_FILE = os.path.join(BASE_DIR, '../data/processed/survived_data.json')
BACKUP_DIR = os.path.join(BASE_DIR, '../data/processed/backup')

# check if backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

# backup w timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = os.path.join(BACKUP_DIR, f"processed_scream_queens_{timestamp}.json")
shutil.copy(PROCESSED_FILE, backup_file)
print(f"📦 Backup saved to {backup_file}")

# normalize film titles for matching
def normalize_title(title: str) -> str:
    title = re.sub(r'\([^)]*\)', '', title)
    title = re.sub(r'\[[^]]*\]', '', title)
    title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title.strip().lower()

# load JSON files
with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
    processed_data = json.load(f)

with open(SURVIVED_FILE, 'r', encoding='utf-8') as f:
    survived_data = json.load(f)

# update survived info
for actress in processed_data:
    name = actress['name']
    survived_actress = next((a for a in survived_data if a['name'] == name), None)
    if not survived_actress:
        print(f"Actress '{name}' not found in survived_data.json")
        continue

    survived_films = survived_actress.get('films', [])

    for film in actress.get('films', []):
        # skip if already filled
        if film.get('survived') is not None:
            continue

        film_title_norm = normalize_title(film['title'])
        film_year = film.get('year')

        # exact title match
        match = next(
            (f for f in survived_films if normalize_title(f['title']) == film_title_norm),
            None
        )

        # fuzzy match if no exact
        if not match:
            titles_map = {normalize_title(f['title']): f for f in survived_films}
            matches = process.extract(film_title_norm, list(titles_map.keys()), scorer=fuzz.ratio, score_cutoff=80)
            if matches:
                best_match_title = matches[0][0]
                match = titles_map[best_match_title]

        # year-based fallback
        if not match:
            match = next((f for f in survived_films if f.get('year') == film_year), None)

        # update survived
        if match:
            film['survived'] = match.get('survived')
        else:
            film['survived'] = None
            print(f"Could not find survived info for '{film['title']}' ({film_year})")

# save updated JSON
with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
    json.dump(processed_data, f, indent=2, ensure_ascii=False)

print("processed_scream_queens.json successfully updated w survived info!")
