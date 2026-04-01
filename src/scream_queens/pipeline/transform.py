# pipeline/transform.py


def normalize_films(films):
    result = []

    for f in films:
        y = str(f.get("year") or "").strip()

        result.append(
            {
                "year": int(y) if y.isdigit() else f.get("year"),
                "title": f.get("title"),
                "character": f.get("character"),
            }
        )

    return result
