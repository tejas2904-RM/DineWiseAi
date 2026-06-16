from __future__ import annotations

import json
from typing import Dict, List, Set

from models import Recommendation


def _extract_json_blob(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON object found in LLM output")
    return text[start : end + 1]


def parse_recommendations(raw: str, candidate_ids: Set[str], top_k: int) -> Dict[str, object]:
    blob = _extract_json_blob(raw)
    data = json.loads(blob)

    if "recommendations" not in data or not isinstance(data["recommendations"], list):
        raise ValueError("Missing recommendations list")
    if "summary" not in data or not isinstance(data["summary"], str):
        raise ValueError("Missing summary string")

    recs: List[Recommendation] = []
    seen_ids = set()
    expected_rank = 1
    for item in data["recommendations"][:top_k]:
        if not isinstance(item, dict):
            raise ValueError("Recommendation entry must be object")
        rank = item.get("rank")
        rid = item.get("restaurantId")
        reason = item.get("reason")

        if rank != expected_rank:
            raise ValueError("Ranks must be sequential starting from 1")
        if not isinstance(rid, str) or rid not in candidate_ids:
            raise ValueError(f"Invalid or hallucinated restaurantId: {rid}")
        if rid in seen_ids:
            raise ValueError(f"Duplicate restaurantId: {rid}")
        if not isinstance(reason, str) or len(reason.strip()) < 12:
            raise ValueError("Reason must be non-empty and specific")

        seen_ids.add(rid)
        recs.append(Recommendation(rank=rank, restaurant_id=rid, reason=reason.strip()))
        expected_rank += 1

    if not recs:
        raise ValueError("No valid recommendations parsed")

    return {
        "recommendations": recs,
        "summary": data["summary"].strip(),
    }
