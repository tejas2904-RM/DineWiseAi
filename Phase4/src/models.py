from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Preference:
    location: str
    budget: str
    cuisine: str
    min_rating: float
    tags: List[str] = field(default_factory=list)


@dataclass
class Candidate:
    restaurant_id: str
    name: str
    location: str
    cuisine: str
    rating: float
    avg_cost_for_two: float
    budget_band: str
    score: float
    reason: str = ""


@dataclass
class Recommendation:
    rank: int
    restaurant_id: str
    reason: str


@dataclass
class RecommendationResponse:
    recommendations: List[Recommendation]
    summary: str
    used_fallback: bool
