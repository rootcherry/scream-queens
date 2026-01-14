#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed" / "processed_scream_queens.json"

def main() -> int:
    if not PROCESSED.exists():
        print(f"[ERROR] processed file not found: {PROCESSED}")
        print("Run: python src/omdb_ok.py")
        return 1

    data = json.loads(PROCESSED.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        print(f"[ERROR] expected top-level list, got: {type(data).__name__}")
        return 1

    print(f"[OK] file: {PROCESSED}")
    print(f"[OK] actresses: {len(data)}")

    if len(data) == 0:
        print("[WARN] empty list")
        return 0

    first = data[0]
    print("\nSchema (first item):")
    if isinstance(first, dict):
        print("  keys:", sorted(first.keys()))
        print("  name:", first.get("name"))
        films = first.get("films", [])
        stats = first.get("stats", {})
        print("  films:", type(films).__name__, "len:", (len(films) if hasattr(films, "__len__") else "n/a"))
        print("  stats:", type(stats).__name__, "keys:", (sorted(stats.keys()) if isinstance(stats, dict) else stats))
        if films:
            f0 = films[0]
            if isinstance(f0, dict):
                print("\nFirst film keys:", sorted(f0.keys()))
                print("  title:", f0.get("title"), "| year:", f0.get("year"))
    else:
        print(f"  [WARN] first item is not dict: {type(first).__name__}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
