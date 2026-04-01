# STATS
def compute_stats(data):
    for actress in data:
        films = actress["films"]

        horror_count = 0
        survived_count = 0
        box_values = []

        for film in films:
            if "Horror" in film["genres"]:
                horror_count += 1

            if film["survived"] == 1:
                survived_count += 1

            if film["box_office"] is not None:
                box_values.append(film["box_office"])

        years = [f["year"] for f in films if f["year"]]

        actress["stats"] = {
            "horror_count": horror_count,
            "survived_count": survived_count,
            "box_office_total": sum(box_values) if box_values else None,
            "box_office_avg": (
                int(sum(box_values) / len(box_values)) if box_values else None
            ),
            "box_office_best": max(box_values) if box_values else None,
            "box_office_worst": min(box_values) if box_values else None,
            "career_span": [min(years), max(years)] if years else None,
            "omdb_ok": actress.get("stats", {}).get("omdb_ok", False),
        }

    return data
