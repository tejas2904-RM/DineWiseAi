from __future__ import annotations

import time
from enum import Enum
from typing import Any, Callable, Dict, Optional

from fastapi import HTTPException


class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker for protecting external service calls (e.g., LLM provider)."""

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 1,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self._state = State.CLOSED
        self._failures = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0

    @property
    def state(self) -> State:
        if self._state == State.OPEN:
            if self._last_failure_time and (time.time() - self._last_failure_time) >= self.recovery_timeout:
                self._state = State.HALF_OPEN
                self._half_open_calls = 0
        return self._state

    def record_success(self) -> None:
        self._failures = 0
        self._state = State.CLOSED
        self._half_open_calls = 0

    def record_failure(self) -> None:
        self._failures += 1
        self._last_failure_time = time.time()
        if self._state == State.HALF_OPEN:
            self._state = State.OPEN
        elif self._failures >= self.failure_threshold:
            self._state = State.OPEN

    def can_execute(self) -> bool:
        s = self.state
        if s == State.CLOSED:
            return True
        if s == State.HALF_OPEN:
            if self._half_open_calls < self.half_open_max_calls:
                self._half_open_calls += 1
                return True
            return False
        return False

    async def call(self, fn: Callable, *args, **kwargs) -> Any:
        if not self.can_execute():
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable (circuit breaker open). LLM provider may be down. Fallback ranking will be used.",
            )
        try:
            result = await fn(*args, **kwargs)
            self.record_success()
            return result
        except Exception:
            self.record_failure()
            raise


# Global circuit breaker for LLM calls
llm_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)


async def circuit_breaker_dependency() -> CircuitBreaker:
    """FastAPI dependency that provides the circuit breaker."""
    return llm_circuit_breaker
