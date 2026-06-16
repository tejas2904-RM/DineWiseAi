from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    location: str = Field(min_length=2, max_length=80)
    budget: str = Field(min_length=2, max_length=20)
    cuisine: str = Field(min_length=2, max_length=60)
    minRating: float = Field(ge=0.0, le=5.0)
    tags: Optional[List[str]] = Field(default_factory=list, max_length=10)
    topK: int = Field(default=5, ge=1, le=20)


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
    summary: str
    usedFallback: bool
    latencyMs: int
    fallbackReason: Optional[str] = None
    circuitBreakerState: Optional[str] = None


class FeedbackRequest(BaseModel):
    requestId: str
    restaurantId: str
    helpful: bool
    comment: Optional[str] = None


class ErrorDetail(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: List[ErrorDetail] = Field(default_factory=list)


class AuthStatusResponse(BaseModel):
    authenticated: bool
    roles: List[str]
    rate_limit: Dict[str, Any]
