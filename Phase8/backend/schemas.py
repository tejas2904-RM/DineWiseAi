from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class UserProfile(BaseModel):
    userId: str
    name: str = ""
    email: Optional[str] = None
    createdAt: str = Field(default_factory=_utc_now)


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class HistoryEntry(BaseModel):
    requestId: str
    timestamp: str
    userId: str = "anonymous"
    location: str
    budget: str
    cuisine: str
    minRating: float
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)


class FavoriteCreate(BaseModel):
    userId: str = "anonymous"
    restaurantId: str
    name: str = ""
    cuisine: str = ""
    rating: float = 0.0
    estimatedCost: float = 0.0


class FavoriteItem(BaseModel):
    restaurantId: str
    name: str
    cuisine: str
    rating: float
    estimatedCost: float
    addedAt: str


class RecommendationRequest(BaseModel):
    location: str
    budget: str
    cuisine: str
    minRating: float = 4.0
    tags: Optional[List[str]] = None
    topK: int = 5
    userId: str = "anonymous"


class RecommendationItem(BaseModel):
    rank: int
    restaurantId: str
    name: str
    cuisine: str
    rating: float
    estimatedCost: float
    reason: str


class RecommendationResponse(BaseModel):
    requestId: str
    recommendations: List[RecommendationItem]
    summary: Optional[str] = None
    usedFallback: bool = False
    latencyMs: int = 0
    fallbackReason: Optional[str] = None
    circuitBreakerState: Optional[str] = None


class FeedbackRequest(BaseModel):
    requestId: str
    restaurantId: str
    helpful: bool
    comment: Optional[str] = None
    userId: str = "anonymous"
