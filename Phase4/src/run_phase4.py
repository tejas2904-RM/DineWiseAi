from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from engine import Phase4Engine
from groq_adapter import GroqAdapter
from models import Candidate, Preference


def load_phase3_payload(path: Path) -> tuple[Preference, List[Candidate]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    p = raw["preferences"]
    preference = Preference(
        location=p["location"],
        budget=p["budget"],
        cuisine=p["cuisine"],
        min_rating=float(p["minRating"]),
        tags=p.get("tags", []),
    )

    candidates = []
    for c in raw.get("candidates", []):
        candidates.append(
            Candidate(
                restaurant_id=c["restaurant_id"],
                name=c["name"],
                location=c["location"],
                cuisine=c["cuisine"],
                rating=float(c["rating"]),
                avg_cost_for_two=float(c["avg_cost_for_two"]),
                budget_band=c["budget_band"],
                score=float(c["score"]),
                reason=c.get("reason", ""),
            )
        )
    return preference, candidates


def serialize_response(data: dict) -> dict:
    payload = {
        "recommendations": [
            {
                "rank": r.rank,
                "restaurantId": r.restaurant_id,
                "reason": r.reason,
            }
            for r in data["recommendations"]
        ],
        "summary": data["summary"],
        "usedFallback": data["used_fallback"],
    }
    if data.get("fallback_reason") is not None:
        payload["fallbackReason"] = data["fallback_reason"]
    return payload


def main() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=env_path, override=True)
    parser = argparse.ArgumentParser(description="Run Phase 4 LLM recommendation using Groq")
    parser.add_argument("--input", required=True, help="Path to phase3 candidate json")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    preference, candidates = load_phase3_payload(Path(args.input))
    engine = Phase4Engine(GroqAdapter())
    result = engine.generate(preference=preference, candidates=candidates, top_k=args.top_k)
    print(json.dumps(serialize_response(result), indent=2))


if __name__ == "__main__":
    main()
