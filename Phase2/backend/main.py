from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from schemas import ErrorResponse, RecommendationRequest, RecommendationRequestNormalized, ValidationIssue

app = FastAPI(title="Phase2 Recommendation API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    details = []
    for err in exc.errors():
        loc = ".".join(str(part) for part in err.get("loc", []) if part != "body")
        details.append(
            ValidationIssue(field=loc or "body", message=err.get("msg", "invalid value")).model_dump()
        )
    payload = ErrorResponse(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details=[ValidationIssue(**item) for item in details],
    )
    return JSONResponse(status_code=400, content=payload.model_dump())


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/recommendations")
async def create_recommendation(payload: RecommendationRequest):
    normalized = RecommendationRequestNormalized(
        location=payload.location,
        budget=payload.budget,
        cuisine=payload.cuisine,
        minRating=payload.minRating,
        tags=payload.tags or [],
        topK=payload.topK,
    )

    # Phase 2 stops at normalized preference capture.
    return {
        "requestId": str(uuid4()),
        "stage": "phase2_preference_captured",
        "normalizedInput": normalized.model_dump(),
        "nextPhase": "candidate_retrieval_and_ranking",
        "message": "Preferences validated and normalized successfully.",
    }
