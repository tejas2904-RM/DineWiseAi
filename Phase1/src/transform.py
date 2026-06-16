from __future__ import annotations

import re
from typing import Dict, List

import pandas as pd


def normalize_text(value: str) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip().lower()


def normalize_location(value: str, aliases: Dict[str, str]) -> str:
    key = normalize_text(value)
    return aliases.get(key, key)


def normalize_cuisine(value: str, aliases: Dict[str, str]) -> str:
    raw = normalize_text(value)
    if not raw:
        return ""
    parts: List[str] = [p.strip() for p in raw.split(",") if p.strip()]
    normalized = [aliases.get(p, p) for p in parts]
    # Keep stable ordering but remove duplicates.
    seen = set()
    unique = []
    for item in normalized:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return ", ".join(unique)


def parse_cost(value) -> float:
    if value is None:
        return float("nan")
    txt = str(value)
    txt = re.sub(r"[^0-9.]", "", txt)
    if not txt:
        return float("nan")
    try:
        return float(txt)
    except ValueError:
        return float("nan")


def parse_rating(value) -> float:
    if value is None:
        return float("nan")
    txt = str(value)
    txt = txt.split("/")[0]
    txt = re.sub(r"[^0-9.]", "", txt)
    if not txt:
        return float("nan")
    try:
        return float(txt)
    except ValueError:
        return float("nan")


def derive_budget_band(cost: float, low_max: float, medium_max: float) -> str:
    if pd.isna(cost):
        return "unknown"
    if cost <= low_max:
        return "low"
    if cost <= medium_max:
        return "medium"
    return "high"
