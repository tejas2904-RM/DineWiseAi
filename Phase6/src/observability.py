from __future__ import annotations

import json
import logging
import threading
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Structured JSON logger
# ---------------------------------------------------------------------------
class StructuredLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log_entry.update(record.extra)
        return json.dumps(log_entry, default=str)


def get_logger(name: str = "phase6") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredLogFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


# ---------------------------------------------------------------------------
# Telemetry dataclasses
# ---------------------------------------------------------------------------
@dataclass
class RequestTelemetry:
    request_id: str
    timestamp: str
    location: str
    budget: str
    cuisine: str
    min_rating: float
    tags: List[str]
    top_k: int
    latency_ms: int
    used_fallback: bool
    fallback_reason: Optional[str] = None
    candidate_count: int = 0
    cache_hit: bool = False


@dataclass
class LLMTelemetry:
    request_id: str
    latency_ms: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    attempt: int = 1


@dataclass
class FeedbackRecord:
    request_id: str
    restaurant_id: str
    helpful: bool
    comment: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class UXTelemetry:
    session_id: str
    event: str
    timestamp: str
    payload: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# In-memory metrics store with rolling window
# ---------------------------------------------------------------------------
class MetricsStore:
    """Thread-safe in-memory metrics store with configurable retention."""

    def __init__(self, max_records: int = 10_000):
        self._max_records = max_records
        self._lock = threading.RLock()
        self._requests: deque = deque(maxlen=max_records)
        self._llm_calls: deque = deque(maxlen=max_records)
        self._feedback: deque = deque(maxlen=max_records)
        self._ux_events: deque = deque(maxlen=max_records)
        self._errors: deque = deque(maxlen=max_records)
        self._logger = get_logger("phase6.metrics")

    # -- Recording ------------------------------------------------------------

    def record_request(self, telemetry: RequestTelemetry) -> None:
        with self._lock:
            self._requests.append(telemetry)
        self._logger.info(
            "request_completed",
            extra={"telemetry": asdict(telemetry)},
        )

    def record_llm(self, telemetry: LLMTelemetry) -> None:
        with self._lock:
            self._llm_calls.append(telemetry)
        self._logger.info(
            "llm_call_completed",
            extra={"telemetry": asdict(telemetry)},
        )

    def record_feedback(self, record: FeedbackRecord) -> None:
        with self._lock:
            self._feedback.append(record)
        self._logger.info(
            "feedback_received",
            extra={"feedback": asdict(record)},
        )

    def record_ux(self, event: UXTelemetry) -> None:
        with self._lock:
            self._ux_events.append(event)
        self._logger.info(
            "ux_event",
            extra={"event": asdict(event)},
        )

    def record_error(self, request_id: str, error_type: str, message: str) -> None:
        with self._lock:
            self._errors.append({
                "request_id": request_id,
                "error_type": error_type,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        self._logger.error(
            "error_occurred",
            extra={
                "request_id": request_id,
                "error_type": error_type,
                "message": message,
            },
        )

    # -- Aggregations ---------------------------------------------------------

    @staticmethod
    def _percentile(sorted_values: List[float], p: float) -> float:
        if not sorted_values:
            return 0.0
        k = (len(sorted_values) - 1) * (p / 100.0)
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_values) else f
        if f == c:
            return sorted_values[f]
        return sorted_values[f] * (c - k) + sorted_values[c] * (k - f)

    def _latency_percentiles(self, latencies: List[int]) -> Dict[str, float]:
        if not latencies:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
        s = sorted(latencies)
        return {
            "p50": self._percentile(s, 50),
            "p95": self._percentile(s, 95),
            "p99": self._percentile(s, 99),
        }

    def get_api_metrics(self) -> Dict[str, Any]:
        with self._lock:
            reqs = list(self._requests)
            errs = list(self._errors)

        latencies = [r.latency_ms for r in reqs]
        fallback_count = sum(1 for r in reqs if r.used_fallback)
        cache_hits = sum(1 for r in reqs if r.cache_hit)

        return {
            "total_requests": len(reqs),
            "total_errors": len(errs),
            "error_rate": round(len(errs) / max(len(reqs), 1), 4),
            "fallback_count": fallback_count,
            "fallback_rate": round(fallback_count / max(len(reqs), 1), 4),
            "cache_hit_rate": round(cache_hits / max(len(reqs), 1), 4),
            "latency_ms": self._latency_percentiles(latencies),
        }

    def get_llm_metrics(self) -> Dict[str, Any]:
        with self._lock:
            calls = list(self._llm_calls)

        latencies = [c.latency_ms for c in calls]
        total_tokens = sum(c.total_tokens for c in calls)
        prompt_tokens = sum(c.prompt_tokens for c in calls)
        completion_tokens = sum(c.completion_tokens for c in calls)

        return {
            "total_calls": len(calls),
            "total_tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "avg_tokens_per_call": round(total_tokens / max(len(calls), 1), 2),
            "latency_ms": self._latency_percentiles(latencies),
        }

    def get_feedback_summary(self) -> Dict[str, Any]:
        with self._lock:
            items = list(self._feedback)

        if not items:
            return {"total": 0, "helpful_rate": 0.0}

        helpful = sum(1 for f in items if f.helpful)
        return {
            "total": len(items),
            "helpful_count": helpful,
            "helpful_rate": round(helpful / len(items), 4),
        }

    def get_ux_metrics(self) -> Dict[str, Any]:
        with self._lock:
            events = list(self._ux_events)

        event_counts: Dict[str, int] = {}
        for e in events:
            event_counts[e.event] = event_counts.get(e.event, 0) + 1

        sessions = set(e.session_id for e in events)
        return {
            "total_events": len(events),
            "unique_sessions": len(sessions),
            "event_breakdown": event_counts,
        }

    def snapshot(self) -> Dict[str, Any]:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "api": self.get_api_metrics(),
            "llm": self.get_llm_metrics(),
            "feedback": self.get_feedback_summary(),
            "ux": self.get_ux_metrics(),
        }

    def export_requests(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        with self._lock:
            items = list(self._requests)
        if limit:
            items = items[-limit:]
        return [asdict(r) for r in items]

    def export_feedback(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        with self._lock:
            items = list(self._feedback)
        if limit:
            items = items[-limit:]
        return [asdict(r) for r in items]
