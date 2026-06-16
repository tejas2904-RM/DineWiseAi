from __future__ import annotations

import re
from typing import Dict, List


LOCATION_ALIASES: Dict[str, str] = {
    "blr": "bangalore",
    "bengaluru": "bangalore",
    "new delhi": "delhi",
    "ncr": "delhi ncr",
}

BUDGET_ALIASES: Dict[str, str] = {
    "cheap": "low",
    "budget": "low",
    "affordable": "low",
    "moderate": "medium",
    "mid": "medium",
    "expensive": "high",
    "premium": "high",
    "luxury": "high",
}


def normalize_text(value: str) -> str:
    compact = re.sub(r"\s+", " ", value or "").strip().lower()
    return compact


def normalize_location(value: str) -> str:
    key = normalize_text(value)
    return LOCATION_ALIASES.get(key, key)


def normalize_budget(value: str) -> str:
    key = normalize_text(value)
    if key in {"low", "medium", "high"}:
        return key
    return BUDGET_ALIASES.get(key, key)


def normalize_cuisine(value: str) -> str:
    return normalize_text(value)


def normalize_tags(tags: List[str]) -> List[str]:
    out = []
    seen = set()
    for tag in tags:
        t = normalize_text(tag)
        if not t:
            continue
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out
