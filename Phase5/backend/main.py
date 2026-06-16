from __future__ import annotations

import importlib.util
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from schemas import (
    ErrorDetail,
    ErrorResponse,
    FeedbackRequest,
    RecommendationItem,
    RecommendationRequest,
    RecommendationResponse,
    UXTelemetryEvent,
)

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "Phase1" / "outputs" / "restaurants_clean.csv"
PHASE3_SRC = PROJECT_ROOT / "Phase3" / "src"
PHASE4_SRC = PROJECT_ROOT / "Phase4" / "src"

# ---------------------------------------------------------------------------
# Phase 6: Observability
# ---------------------------------------------------------------------------
PHASE6_SRC = PROJECT_ROOT / "Phase6" / "src"
if str(PHASE6_SRC) not in sys.path:
    sys.path.insert(0, str(PHASE6_SRC))

from observability import (  # noqa: E402
    FeedbackRecord,
    LLMTelemetry,
    MetricsStore,
    RequestTelemetry,
    UXTelemetry,
)

metrics_store = MetricsStore(max_records=10_000)

# Load Groq API key from Phase4 .env
load_dotenv(dotenv_path=PROJECT_ROOT / "Phase4" / ".env", override=True)

# ---------------------------------------------------------------------------
# Helper: load a module from an explicit file path
# ---------------------------------------------------------------------------
def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Load Phase3 modules (order matters: models -> cache -> scoring -> engine)
# ---------------------------------------------------------------------------
p3_models = _load_module("p3_models", PHASE3_SRC / "models.py")
sys.modules["models"] = p3_models

p3_cache = _load_module("p3_cache", PHASE3_SRC / "cache.py")
sys.modules["cache"] = p3_cache

p3_scoring = _load_module("p3_scoring", PHASE3_SRC / "scoring.py")
sys.modules["scoring"] = p3_scoring

p3_engine = _load_module("p3_engine", PHASE3_SRC / "engine.py")
sys.modules["engine"] = p3_engine

# Save Phase3 short-name entries and clear them for Phase4 loading
_saved_short_names = {}
for _short in ("models", "cache", "scoring", "engine"):
    _saved_short_names[_short] = sys.modules.get(_short)
    if _short in sys.modules:
        del sys.modules[_short]

# ---------------------------------------------------------------------------
# Load Phase4 modules (order matters: models -> fallback/parser/prompt/groq -> engine)
# ---------------------------------------------------------------------------
p4_models = _load_module("p4_models", PHASE4_SRC / "models.py")
sys.modules["models"] = p4_models

p4_groq_adapter = _load_module("p4_groq_adapter", PHASE4_SRC / "groq_adapter.py")
sys.modules["groq_adapter"] = p4_groq_adapter

p4_fallback = _load_module("p4_fallback", PHASE4_SRC / "fallback.py")
sys.modules["fallback"] = p4_fallback

p4_parser = _load_module("p4_parser", PHASE4_SRC / "parser.py")
sys.modules["parser"] = p4_parser

p4_prompt_builder = _load_module("p4_prompt_builder", PHASE4_SRC / "prompt_builder.py")
sys.modules["prompt_builder"] = p4_prompt_builder

p4_engine = _load_module("p4_engine", PHASE4_SRC / "engine.py")
sys.modules["engine"] = p4_engine

# Restore Phase3 short-name entries so the rest of the app can use them if needed
for _short, _mod in _saved_short_names.items():
    if _mod is not None:
        sys.modules[_short] = _mod

# ---------------------------------------------------------------------------
# Initialize engines
# ---------------------------------------------------------------------------
candidate_engine = p3_engine.CandidateEngine(DATASET_PATH, cache_ttl_seconds=120)
groq_adapter = p4_groq_adapter.GroqAdapter()
llm_engine = p4_engine.Phase4Engine(groq_adapter)

# ---------------------------------------------------------------------------
# Normalizer (mirrors Phase2 normalizer)
# ---------------------------------------------------------------------------
import re  # noqa: E402

LOCATION_ALIASES = {
    "blr": "bangalore",
    "bengaluru": "bangalore",
    "new delhi": "delhi",
    "ncr": "delhi ncr",
}

BUDGET_ALIASES = {
    "cheap": "low",
    "budget": "low",
    "affordable": "low",
    "moderate": "medium",
    "mid": "medium",
    "expensive": "high",
    "premium": "high",
    "luxury": "high",
}


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def _normalize_location(value: str) -> str:
    key = _normalize_text(value)
    return LOCATION_ALIASES.get(key, key)


def _normalize_budget(value: str) -> str:
    key = _normalize_text(value)
    if key in {"low", "medium", "high"}:
        return key
    return BUDGET_ALIASES.get(key, key)


def _normalize_cuisine(value: str) -> str:
    return _normalize_text(value)


def _normalize_tags(tags: List[str]) -> List[str]:
    out = []
    seen = set()
    for tag in tags:
        t = _normalize_text(tag)
        if not t:
            continue
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="Phase5 Recommendation API", version="1.0.0")

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
            ErrorDetail(field=loc or "body", message=err.get("msg", "invalid value"))
        )
    metrics_store.record_error(
        request_id=str(uuid.uuid4()),
        error_type="VALIDATION_ERROR",
        message=str(exc),
    )
    payload = ErrorResponse(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details=details,
    )
    return JSONResponse(status_code=400, content=payload.model_dump())


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    }


@app.get("/observability/requests")
async def recent_requests(limit: int = 20):
    return {
        "requests": metrics_store.export_requests(limit=limit),
    }


@app.get("/observability/feedback")
async def recent_feedback(limit: int = 20):
    return {
        "feedback": metrics_store.export_feedback(limit=limit),
    }


@app.get("/metrics")
async def metrics():
    snapshot = metrics_store.snapshot()
    return {
        "service": "phase5-recommendation-api",
        "cacheSize": candidate_engine.cache.size(),
        **snapshot,
    }


@app.post("/recommendations")
async def create_recommendation(payload: RecommendationRequest):
    start_time = time.time()
    request_id = str(uuid.uuid4())

    # Normalize inputs
    location = _normalize_location(payload.location)
    budget = _normalize_budget(payload.budget)
    cuisine = _normalize_cuisine(payload.cuisine)
    tags = _normalize_tags(payload.tags or [])

    # Phase 3: Candidate retrieval
    pref3 = p3_models.PreferenceRequest(
        location=location,
        budget=budget,
        cuisine=cuisine,
        min_rating=payload.minRating,
        tags=tags,
        top_k=payload.topK,
    )
    phase3_result = candidate_engine.retrieve(pref3)
    candidates_raw = phase3_result.get("candidates", [])
    cache_hit = phase3_result.get("cacheHit", False)

    # Convert to Phase4 candidate objects
    phase4_candidates = []
    for c in candidates_raw:
        phase4_candidates.append(
            p4_models.Candidate(
                restaurant_id=c["restaurant_id"],
                name=c["name"],
                location=c["location"],
                cuisine=c["cuisine"],
                rating=c["rating"],
                avg_cost_for_two=c["avg_cost_for_two"],
                budget_band=c["budget_band"],
                score=c["score"],
                reason=c.get("reason", ""),
            )
        )

    # Phase 4: LLM recommendation
    pref4 = p4_models.Preference(
        location=location,
        budget=budget,
        cuisine=cuisine,
        min_rating=payload.minRating,
        tags=tags,
    )
    phase4_result = llm_engine.generate(
        preference=pref4,
        candidates=phase4_candidates,
        top_k=payload.topK,
    )

    # Enrich recommendations with candidate metadata
    candidate_map = {c.restaurant_id: c for c in phase4_candidates}
    enriched_recs: List[RecommendationItem] = []
    for rec in phase4_result["recommendations"]:
        cand = candidate_map.get(rec.restaurant_id)
        if cand:
            enriched_recs.append(
                RecommendationItem(
                    rank=rec.rank,
                    restaurantId=rec.restaurant_id,
                    name=cand.name,
                    cuisine=cand.cuisine,
                    rating=cand.rating,
                    estimatedCost=cand.avg_cost_for_two,
                    reason=rec.reason,
                )
            )

    latency_ms = int((time.time() - start_time) * 1000)
    used_fallback = phase4_result.get("used_fallback", False)

    # Phase 6: Record telemetry
    metrics_store.record_request(
        RequestTelemetry(
            request_id=request_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            location=location,
            budget=budget,
            cuisine=cuisine,
            min_rating=payload.minRating,
            tags=tags,
            top_k=payload.topK,
            latency_ms=latency_ms,
            used_fallback=used_fallback,
            fallback_reason=phase4_result.get("fallback_reason"),
            candidate_count=len(candidates_raw),
            cache_hit=cache_hit,
        )
    )

    for llm_t in phase4_result.get("llm_telemetry", []):
        metrics_store.record_llm(
            LLMTelemetry(
                request_id=request_id,
                latency_ms=llm_t.get("latency_ms", 0),
                prompt_tokens=llm_t.get("prompt_tokens", 0),
                completion_tokens=llm_t.get("completion_tokens", 0),
                total_tokens=llm_t.get("total_tokens", 0),
                model=llm_t.get("model", ""),
                attempt=llm_t.get("attempt", 1),
            )
        )

    return RecommendationResponse(
        requestId=request_id,
        recommendations=enriched_recs,
        summary=phase4_result.get("summary", ""),
        usedFallback=used_fallback,
        latencyMs=latency_ms,
        fallbackReason=phase4_result.get("fallback_reason"),
    )


@app.post("/feedback")
async def create_feedback(payload: FeedbackRequest):
    metrics_store.record_feedback(
        FeedbackRecord(
            request_id=payload.requestId,
            restaurant_id=payload.restaurantId,
            helpful=payload.helpful,
            comment=payload.comment,
        )
    )
    return {
        "requestId": payload.requestId,
        "restaurantId": payload.restaurantId,
        "helpful": payload.helpful,
        "status": "recorded",
    }


@app.post("/telemetry")
async def create_telemetry(payload: UXTelemetryEvent):
    metrics_store.record_ux(
        UXTelemetry(
            session_id=payload.sessionId,
            event=payload.event,
            timestamp=datetime.now(timezone.utc).isoformat(),
            payload=payload.payload,
        )
    )
    return {"status": "recorded"}
