from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


CANONICAL_COLUMNS = [
    "id",
    "name",
    "location",
    "cuisine",
    "avg_cost_for_two",
    "rating",
    "budget_band",
]


@dataclass
class RawToCanonicalMap:
    id: Optional[str]
    name: Optional[str]
    location: Optional[str]
    cuisine: Optional[str]
    avg_cost_for_two: Optional[str]
    rating: Optional[str]


def resolve_column(columns: List[str], candidates: List[str]) -> Optional[str]:
    col_map = {c.lower().strip(): c for c in columns}
    for key in candidates:
        lookup = key.lower().strip()
        if lookup in col_map:
            return col_map[lookup]
    return None


def build_field_map(columns: List[str], config_field_mapping: Dict[str, List[str]]) -> RawToCanonicalMap:
    return RawToCanonicalMap(
        id=resolve_column(columns, config_field_mapping.get("id", [])),
        name=resolve_column(columns, config_field_mapping.get("name", [])),
        location=resolve_column(columns, config_field_mapping.get("location", [])),
        cuisine=resolve_column(columns, config_field_mapping.get("cuisine", [])),
        avg_cost_for_two=resolve_column(columns, config_field_mapping.get("avg_cost_for_two", [])),
        rating=resolve_column(columns, config_field_mapping.get("rating", [])),
    )
