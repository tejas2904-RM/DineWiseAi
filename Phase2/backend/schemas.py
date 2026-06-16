from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from normalizer import normalize_budget, normalize_cuisine, normalize_location, normalize_tags, normalize_text


class RecommendationRequest(BaseModel):
    location: str = Field(min_length=2, max_length=80)
    budget: str = Field(min_length=2, max_length=20)
    cuisine: str = Field(min_length=2, max_length=60)
    minRating: float = Field(ge=0.0, le=5.0)
    tags: Optional[List[str]] = Field(default_factory=list, max_length=10)
    topK: int = Field(default=5, ge=1, le=20)

    @field_validator("location", "budget", "cuisine")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not normalize_text(value):
            raise ValueError("must not be empty")
        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, tags: List[str]) -> List[str]:
        if len(tags) > 10:
            raise ValueError("at most 10 tags are allowed")
        return tags

    @model_validator(mode="after")
    def normalize(self) -> "RecommendationRequest":
        self.location = normalize_location(self.location)
        self.budget = normalize_budget(self.budget)
        self.cuisine = normalize_cuisine(self.cuisine)
        self.tags = normalize_tags(self.tags or [])
        if self.budget not in {"low", "medium", "high"}:
            raise ValueError("budget must be one of: low, medium, high")
        return self


class RecommendationRequestNormalized(BaseModel):
    location: str
    budget: str
    cuisine: str
    minRating: float
    tags: List[str]
    topK: int


class ApiMessage(BaseModel):
    message: str


class ValidationIssue(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: List[ValidationIssue] = Field(default_factory=list)
