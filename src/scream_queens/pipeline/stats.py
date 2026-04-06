# pipeline/stats.py


def compute_stats(films):
    years = [f["year"] for f in films if isinstance(f["year"], int)]

    if years:
        span = [min(years), max(years)]
    else:
        span = [None, None]

    return {
        "horror_count": len(films),
        "box_office_total": None,
        "career_span": span,
        "scrape_ok": bool(films),
    }
