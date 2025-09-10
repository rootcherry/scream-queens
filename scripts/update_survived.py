import json
import os

# update the 'survived' field in processed_scream_queens.json using survived_data.json
# configuration
# paths
PROCESS_FILE = os.path.join("..", "data", "processed", "processed_scream_queens.json")
SURVIVED_FILE = os.path.join("..", "data", "processed", "survived_data.json")

# only update these actresses
TARGET_ACTRESSES = ["Megumi Okina", "Yūko Takeuchi"]  # empty list to update all

# load JSON files
with open(PROCESS_FILE, "r", encoding="utf-8") as f:
    processed_data = json.load(f)

with open(SURVIVED_FILE, "r", encoding="utf-8") as f:
    survived_data = json.load(f)

# update survived info
for actress in processed_data:
    name = actress["name"]

    # skip if targeting specific actresses
    if TARGET_ACTRESSES and name not in TARGET_ACTRESSES:
        continue

    count = 0 # initialize survived counter

    for film in actress["films"]:
        title = film["title"]

        # default to None if not found
        survived_status = None
        if name in survived_data and title in survived_data[name]:
            survived_status = survived_data[name][title]

        film["survived"] = survived_status

        if survived_status == 1:
            count += 1

    # update the stats
    actress["stats"]["survived_count"] = count

# save updated JSON
with open(PROCESS_FILE, "w", encoding="utf-8") as f:
    json.dump(processed_data, f, indent=2, ensure_ascii=False)

print(f"Survived status updated for {TARGET_ACTRESSES or 'all actresses'}!")
