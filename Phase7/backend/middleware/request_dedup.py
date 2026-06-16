from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request


class RequestDeduplicator:
    """Deduplicate identical incoming requests to avoid redundant LLM calls."""

    def __init__(self, ttl_seconds: float = 10.0):
        self.ttl_seconds = ttl_seconds
        self._inflight: Dict[str, Dict[str, Any]] = {}

    def _key(self, request: Request, body: bytes) -> str:
        """Generate a stable deduplication key from request path + body."""
        path = request.url.path
        # Hash body to keep keys compact
        body_hash = hashlib.sha256(body).hexdigest()[:16]
        return f"{path}:{body_hash}"

    def start(self, key: str) -> bool:
        """Mark request as in-flight. Returns True if this is the first request."""
        now = time.time()
        self._cleanup(now)
        if key in self._inflight:
            return False
        self._inflight[key] = {"start": now}
        return True

    def finish(self, key: str, response: Any) -> None:
        """Store result for concurrent duplicate requests."""
        if key in self._inflight:
            self._inflight[key]["response"] = response
            self._inflight[key]["ready"] = True

    def get_response(self, key: str) -> Optional[Any]:
        """Poll for duplicate request result."""
        entry = self._inflight.get(key)
        if entry and entry.get("ready"):
            return entry["response"]
        return None

    def remove(self, key: str) -> None:
        if key in self._inflight:
            del self._inflight[key]

    def _cleanup(self, now: float) -> None:
        expired = [k for k, v in self._inflight.items() if (now - v["start"]) > self.ttl_seconds]
        for k in expired:
            del self._inflight[k]


# Global instance
deduplicator = RequestDeduplicator(ttl_seconds=10.0)


async def dedup_dependency(request: Request) -> None:
    """FastAPI dependency for request deduplication (placeholder for middleware usage)."""
    pass
