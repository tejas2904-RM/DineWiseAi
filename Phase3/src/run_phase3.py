from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine import CandidateEngine
from models import PreferenceRequest


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Phase 3 candidate retrieval")
    parser.add_argument("--dataset", default=str(Path(__file__).resolve().parents[2] / "Phase1" / "outputs" / "restaurants_clean.csv"))
    parser.add_argument("--location", required=True)
    parser.add_argument("--budget", required=True, choices=["low", "medium", "high"])
    parser.add_argument("--cuisine", required=True)
    parser.add_argument("--min-rating", type=float, required=True)
    parser.add_argument("--tags", default="")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--cache-ttl", type=int, default=120)
    args = parser.parse_args()

    tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
    pref = PreferenceRequest(
        location=args.location,
        budget=args.budget,
        cuisine=args.cuisine,
        min_rating=args.min_rating,
        tags=tags,
        top_k=args.top_k,
    )

    engine = CandidateEngine(Path(args.dataset), cache_ttl_seconds=args.cache_ttl)
    result = engine.retrieve(pref)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
