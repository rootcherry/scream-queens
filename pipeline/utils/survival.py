import json
from pipeline.core.paths import SURVIVED_FILE


def normalize_survived(value) -> int:
    """Normalize survived field to 0/1"""
    if value is None:
        return 0
    return int(bool(value))


def build_survival_map() -> dict:
    """Build lookup map: { actress -> {(title, year): survived} }"""
    if not SURVIVED_FILE.exists():
        return {}

    with SURVIVED_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    survival_map = {}

    for actress in data:
        name = actress.get("name")
        films = actress.get("films", [])

        film_map = {}
        for film in films:
            key = (film.get("title"), film.get("year"))
            film_map[key] = film.get("survived")

        survival_map[name] = film_map

    return survival_map
