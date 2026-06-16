from __future__ import annotations

import json
from typing import List

from models import Candidate, Preference


def build_prompt(preference: Preference, candidates: List[Candidate], top_k: int) -> str:
    compact_candidates = [
        {
            "restaurantId": c.restaurant_id,
            "name": c.name,
            "location": c.location,
            "cuisine": c.cuisine,
            "rating": c.rating,
            "avgCostForTwo": c.avg_cost_for_two,
            "budgetBand": c.budget_band,
            "baseScore": c.score,
        }
        for c in candidates
    ]

    payload = {
        "userPreference": {
            "location": preference.location,
            "budget": preference.budget,
            "cuisine": preference.cuisine,
            "minRating": preference.min_rating,
            "tags": preference.tags,
        },
        "topK": top_k,
        "candidates": compact_candidates,
    }

    instruction = (
        "You are a restaurant recommendation engine. "
        "Use only the provided candidates. Do not invent restaurants. "
        "Return strictly valid JSON with this schema:\n"
        "{\n"
        '  "recommendations": [\n'
        '    {"rank": 1, "restaurantId": "id", "reason": "specific reason"}\n'
        "  ],\n"
        '  "summary": "short summary"\n'
        "}\n"
        "Rules:\n"
        "1) Include at most topK recommendations.\n"
        "2) rank must be unique and sequential from 1.\n"
        "3) restaurantId must be selected from candidates only.\n"
        "4) reason must be specific and reference user preferences.\n"
        "5) Output JSON only, no markdown."
    )

    return f"{instruction}\n\nINPUT:\n{json.dumps(payload, ensure_ascii=True)}"
