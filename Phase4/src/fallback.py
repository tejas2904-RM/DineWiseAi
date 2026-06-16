from __future__ import annotations

from typing import List

from models import Candidate, Recommendation


def fallback_recommendations(candidates: List[Candidate], top_k: int) -> dict:
    ordered = sorted(
        candidates,
        key=lambda c: (-c.score, -c.rating, c.avg_cost_for_two, c.restaurant_id),
    )
    selected = ordered[:top_k]
    recs: List[Recommendation] = []
    for i, c in enumerate(selected, start=1):
        reason = (
            f"Strong rule-based match for {c.cuisine} in {c.location}, "
            f"rating {c.rating}, budget band {c.budget_band}."
        )
        recs.append(Recommendation(rank=i, restaurant_id=c.restaurant_id, reason=reason))

    summary = "Fallback ranking used due to LLM unavailability or invalid output."
    return {"recommendations": recs, "summary": summary}
