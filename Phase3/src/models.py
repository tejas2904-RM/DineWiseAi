from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class PreferenceRequest:
    location: str
    budget: str
    cuisine: str
    min_rating: float
    tags: List[str] = field(default_factory=list)
    top_k: int = 10


@dataclass
class CandidateResult:
    restaurant_id: str
    name: str
    location: str
    cuisine: str
    rating: float
    avg_cost_for_two: float
    budget_band: str
    score: float
    cuisine_score: float
    tag_score: float
    rating_score: float
    reason: str
