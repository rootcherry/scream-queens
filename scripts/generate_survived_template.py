import json
import os

# path to the folder w raw actress JSON files
RAW_DATA_FOLDER = '../data/raw/'
# output file for survival template
OUTPUT_FILE = '../data/survived_data.json'

# dict that will hold survival info
survived_template = {}

# loop through each file in the raw data folder
for filename in os.listdir(RAW_DATA_FOLDER):
    if filename.endswith('.json'):
        # open n load the raw JSON data
        with open(os.path.join(RAW_DATA_FOLDER, filename)) as f:
            data = json.load(f)

        # get actress name
        actress_name = data.get("name", "Unknown")

        # prepare dict for this actress
        survived_template[actress_name] = {}

        # get films from raw JSON
        films = data.get("films", [])

        # get the year of a film, if year is missing return 0
        def get_year(film):
            return film.get("year") or 0

        # sort films by year
        films_sorted = sorted(films, key=get_year)

        # add each film as a key with value null
        for film in films_sorted:
            title = film.get("title", "Unknown Title")
            year = film.get("year")
            if year:
                key = f"{title} ({year})"
            else:
                key = f"{title} (Unknown)"
            survived_template[actress_name][key] = None  # initialize as null

# save the template JSON
with open(OUTPUT_FILE, 'w') as f:
    json.dump(survived_template, f, indent=2)

print(f"Survival template generated: {OUTPUT_FILE}")
