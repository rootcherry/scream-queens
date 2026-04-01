def parse_box_office(value: str) -> int:
    """Convert box office string to integer (0 if N/A)"""
    if not value or value == "N/A":
        return 0
    return int(value.replace("$", "").replace(",", "").strip())


def format_box_office(value: int) -> str:
    """Format integer as box office string"""
    return f"${value:,}" if value > 0 else "N/A"


def calculate_box_office_stats(films: list[dict]) -> dict:
    """Calculate total, average, best, worst box office"""
    values = [parse_box_office(f.get("box_office", "N/A")) for f in films]
    total = sum(values)
    avg = round(total / len([v for v in values if v > 0]), 2) if any(values) else 0
    best = max(values) if values else 0
    worst = min([v for v in values if v > 0], default=0)
    return {"total": total, "avg": avg, "best": best, "worst": worst}
