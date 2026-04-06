import json
from pipeline.core.paths import PROCESSED_CLEAN_FILE

with PROCESSED_CLEAN_FILE.open() as f:
    data = json.load(f)

top = sorted(data, key=lambda x: x["stats"]["score"], reverse=True)

print("\n=== TOP SCREAM QUEENS ===\n")

for actress in top[:10]:
    print(
        f'{actress["stats"]["rank"]}. {actress["name"]} '
        f'(Score: {actress["stats"]["score"]})'
    )
