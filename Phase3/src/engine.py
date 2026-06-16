from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd

from cache import TTLCache
from models import CandidateResult, PreferenceRequest
from scoring import apply_hard_filters, key_for_request, score_candidates


class CandidateEngine:
    def __init__(self, dataset_path: Path, cache_ttl_seconds: int = 120):
        self.dataset_path = dataset_path
        self.cache = TTLCache(ttl_seconds=cache_ttl_seconds)
        self.df = self._load_dataset(dataset_path)

    def _load_dataset(self, path: Path) -> pd.DataFrame:
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")
        df = pd.read_csv(path)
        required_cols = {"id", "name", "location", "cuisine", "avg_cost_for_two", "rating", "budget_band"}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Dataset missing required columns: {sorted(missing)}")
        return df

    def retrieve(self, pref: PreferenceRequest) -> Dict[str, object]:
        req_key = key_for_request(pref)
        cached = self.cache.get(req_key)
        if cached is not None:
            return {
                "cacheHit": True,
                "cacheSize": self.cache.size(),
                **cached,
            }

        filtered = apply_hard_filters(self.df, pref)
        ranked: List[CandidateResult] = score_candidates(filtered, pref)
        top = ranked[: pref.top_k]

        payload = {
            "cacheHit": False,
            "filteredCount": int(len(filtered)),
            "returnedCount": int(len(top)),
            "candidates": [item.__dict__ for item in top],
        }
        self.cache.set(req_key, payload)
        payload["cacheSize"] = self.cache.size()
        return payload
