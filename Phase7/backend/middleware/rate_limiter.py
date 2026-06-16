from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Optional

from fastapi import HTTPException, Request


@dataclass
class Bucket:
    tokens: float
    last_update: float


class RateLimiter:
    """Token-bucket rate limiter per client key (IP or user)."""

    def __init__(self, rate: float = 10, capacity: float = 20):
        """
        Args:
            rate: tokens added per second.
            capacity: maximum bucket size.
        """
        self.rate = rate
        self.capacity = capacity
        self._buckets: Dict[str, Bucket] = {}

    def _consume(self, key: str) -> bool:
        now = time.time()
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = Bucket(tokens=self.capacity, last_update=now)
            self._buckets[key] = bucket

        # Add tokens based on elapsed time
        elapsed = now - bucket.last_update
        bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
        bucket.last_update = now

        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False

    def is_allowed(self, key: str) -> bool:
        return self._consume(key)

    def get_wait_time(self, key: str) -> float:
        bucket = self._buckets.get(key)
        if bucket is None or bucket.tokens >= 1:
            return 0.0
        return (1 - bucket.tokens) / self.rate


# Global instance (shared across requests)
rate_limiter = RateLimiter(rate=5, capacity=10)


async def rate_limit_dependency(request: Request) -> None:
    """FastAPI dependency that enforces rate limiting by client IP."""
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.is_allowed(client_ip):
        retry_after = int(rate_limiter.get_wait_time(client_ip)) + 1
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please slow down.",
            headers={"Retry-After": str(retry_after)},
        )
