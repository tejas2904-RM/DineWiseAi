from __future__ import annotations

from typing import Dict

import pandas as pd


def quality_metrics(df: pd.DataFrame, rejected_count: int) -> Dict[str, object]:
    total = len(df) + rejected_count
    return {
        "total_input_records": total,
        "clean_records": len(df),
        "rejected_records": rejected_count,
        "duplicate_ids": int(df["id"].duplicated().sum()) if "id" in df.columns else None,
        "missing_by_column": {
            col: int(df[col].isna().sum()) for col in df.columns
        },
        "rating_summary": {
            "min": float(df["rating"].min()) if "rating" in df.columns and not df.empty else None,
            "max": float(df["rating"].max()) if "rating" in df.columns and not df.empty else None,
            "mean": float(df["rating"].mean()) if "rating" in df.columns and not df.empty else None,
        },
    }
