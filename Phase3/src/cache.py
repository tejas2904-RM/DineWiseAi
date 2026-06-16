from __future__ import annotations

import time
from typing import Any, Dict, Optional, Tuple


class TTLCache:
    def __init__(self, ttl_seconds: int = 120):
        self.ttl_seconds = ttl_seconds
        self._store: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            return None
        expires_at, value = self._store[key]
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.time() + self.ttl_seconds, value)

    def size(self) -> int:
        # Remove expired entries lazily before size report.
        expired = [k for k, (exp, _) in self._store.items() if time.time() > exp]
        for key in expired:
            del self._store[key]
        return len(self._store)
