from __future__ import annotations

from typing import List, Tuple

import pandas as pd

from models import CandidateResult, PreferenceRequest


def _normalize_text(value: str) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _split_csv_text(value: str) -> List[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    return [_normalize_text(part) for part in str(value).split(",") if _normalize_text(part)]


def _query_key(pref: PreferenceRequest) -> str:
    tags = ",".join(sorted([_normalize_text(t) for t in pref.tags]))
    return f"{_normalize_text(pref.location)}|{_normalize_text(pref.budget)}|{_normalize_text(pref.cuisine)}|{pref.min_rating:.2f}|{tags}|{pref.top_k}"


def apply_hard_filters(df: pd.DataFrame, pref: PreferenceRequest) -> pd.DataFrame:
    location = _normalize_text(pref.location)
    budget = _normalize_text(pref.budget)
    filtered = df.copy()

    filtered = filtered[filtered["location"].astype(str).str.lower() == location]
    filtered = filtered[filtered["budget_band"].astype(str).str.lower() == budget]
    filtered = filtered[filtered["rating"] >= pref.min_rating]
    return filtered


def score_candidates(filtered: pd.DataFrame, pref: PreferenceRequest) -> List[CandidateResult]:
    cuisine_query = _normalize_text(pref.cuisine)
    tags_query = {_normalize_text(tag) for tag in pref.tags if _normalize_text(tag)}

    results: List[Tuple[float, CandidateResult]] = []

    for _, row in filtered.iterrows():
        cuisines = set(_split_csv_text(row.get("cuisine", "")))
        row_tags = set(_split_csv_text(row.get("tags", "")))

        cuisine_score = 40.0 if cuisine_query in cuisines else 0.0
        tag_overlap = len(tags_query.intersection(row_tags))
        tag_score = float(min(tag_overlap * 8, 24))
        rating_score = float(row["rating"]) * 6.0  # max 30

        final_score = cuisine_score + tag_score + rating_score
        reason_parts = []
        if cuisine_score > 0:
            reason_parts.append("matches requested cuisine")
        if tag_overlap > 0:
            reason_parts.append(f"matches {tag_overlap} optional preference(s)")
        reason_parts.append(f"has rating {row['rating']}")
        reason = ", ".join(reason_parts)

        item = CandidateResult(
            restaurant_id=str(row["id"]),
            name=str(row["name"]),
            location=str(row["location"]),
            cuisine=str(row["cuisine"]),
            rating=float(row["rating"]),
            avg_cost_for_two=float(row["avg_cost_for_two"]),
            budget_band=str(row["budget_band"]),
            score=round(final_score, 3),
            cuisine_score=round(cuisine_score, 3),
            tag_score=round(tag_score, 3),
            rating_score=round(rating_score, 3),
            reason=reason,
        )
        results.append((final_score, item))

    # Deterministic ordering:
    # 1) descending final score
    # 2) descending rating
    # 3) ascending avg_cost_for_two (value preference)
    # 4) ascending restaurant_id
    ordered = sorted(
        [item for _, item in results],
        key=lambda x: (-x.score, -x.rating, x.avg_cost_for_two, x.restaurant_id),
    )
    return ordered


def key_for_request(pref: PreferenceRequest) -> str:
    return _query_key(pref)
