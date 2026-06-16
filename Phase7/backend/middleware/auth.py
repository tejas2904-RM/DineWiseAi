from __future__ import annotations

import os
import secrets
from typing import Dict, List, Optional, Set

from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# In-memory API key store (production would use Vault/AWS Secrets Manager)
_API_KEYS: Dict[str, Dict[str, object]] = {
    "phase7-demo-key": {"roles": ["user"], "rate": 5, "capacity": 10},
    "phase7-admin-key": {"roles": ["user", "admin"], "rate": 20, "capacity": 50},
}


def _load_keys_from_env() -> None:
    env_keys = os.getenv("PHASE7_API_KEYS", "")
    if env_keys:
        for pair in env_keys.split(","):
            if "=" in pair:
                key, roles_raw = pair.split("=", 1)
                roles = [r.strip() for r in roles_raw.split("|")]
                _API_KEYS[key.strip()] = {"roles": roles, "rate": 20, "capacity": 50}


_load_keys_from_env()

security_bearer = HTTPBearer(auto_error=False)


def _extract_key(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    # Also support x-api-key header
    return request.headers.get("x-api-key", "")


def api_key_auth(request: Request) -> Dict[str, object]:
    """Validate API key and return associated metadata."""
    key = _extract_key(request)
    if not key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Provide it via Authorization: Bearer <key> or x-api-key header.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    meta = _API_KEYS.get(key)
    if not meta:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return meta


def require_role(role: str):
    """Dependency factory that requires a specific role."""
    def checker(request: Request) -> Dict[str, object]:
        meta = api_key_auth(request)
        roles: List[str] = meta.get("roles", [])
        if role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required role: {role}",
            )
        return meta
    return checker


def get_rate_for_key(key: str) -> tuple:
    meta = _API_KEYS.get(key, {})
    return meta.get("rate", 5), meta.get("capacity", 10)
