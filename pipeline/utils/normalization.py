import re


def normalize_genres(genre_str: str) -> list[str]:
    """Normalize genre string into list of cleaned genres"""
    if not genre_str or genre_str == "N/A":
        return ["Unknown"]
    raw = re.split(r",|\|", genre_str)
    seen = set()
    genres = [
        g.strip().title()
        for g in raw
        if g.strip() and not (g.strip() in seen or seen.add(g.strip()))
    ]
    return genres or ["Unknown"]


def normalize_title(title: str) -> str:
    """Normalize film title for matching (remove punctuation, lower case)"""
    title = re.sub(r'\([^)]*\)|\[[^]]*\]', '', title)
    title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title.strip().lower()


def parse_box_office(value: str) -> int | None:
    """Convert box office string like '$123,456' to int"""
    if not value or value == "N/A":
        return None

    digits = re.sub(r"[^\d]", "", value)
    return int(digits) if digits else None
