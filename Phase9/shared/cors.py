"""Shared CORS origin parsing for production deployment (Phase 9)."""

from __future__ import annotations

import os


def parse_cors_origins(
    env_key: str = "CORS_ORIGINS",
    defaults: tuple[str, ...] = (),
) -> list[str]:
    raw = os.getenv(env_key, "").strip()
    if raw:
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    return list(defaults)
