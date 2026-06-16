from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd
import yaml

from quality import quality_metrics
from schema import CANONICAL_COLUMNS, build_field_map
from transform import (
    derive_budget_band,
    normalize_cuisine,
    normalize_location,
    parse_cost,
    parse_rating,
)


def load_input(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".json":
        return pd.read_json(path)
    raise ValueError(f"Unsupported input format: {suffix}. Use CSV or JSON.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 1 ingestion pipeline")
    parser.add_argument("--input", required=True, help="Path to raw CSV/JSON")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[1] / "config.yaml"),
        help="Path to config.yaml",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)
    config_path = Path(args.config)
    output_dir.mkdir(parents=True, exist_ok=True)

    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    raw = load_input(input_path)
    field_map = build_field_map(list(raw.columns), cfg["field_mapping"])

    required = ["name", "location", "cuisine", "avg_cost_for_two", "rating"]
    missing_required_mappings = [
        key for key in required if getattr(field_map, key) is None
    ]
    if missing_required_mappings:
        raise ValueError(
            "Missing source mappings for required fields: "
            + ", ".join(missing_required_mappings)
        )

    import unicodedata

    def _sanitize_id(value: str) -> str:
        # Normalize unicode and remove non-ascii to keep IDs LLM-safe
        txt = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
        return re.sub(r"[^a-z0-9_-]+", "-", txt.lower()).strip("-")

    df = pd.DataFrame()
    if field_map.id:
        df["id"] = raw[field_map.id].astype(str).str.strip()
    else:
        # Stable generated ID if source does not provide one.
        df["id"] = (
            raw[field_map.name].astype(str).apply(_sanitize_id)
            + "::"
            + raw[field_map.location].astype(str).apply(_sanitize_id)
        )

    df["name"] = raw[field_map.name].astype(str).str.strip()
    df["location"] = raw[field_map.location].apply(
        lambda v: normalize_location(v, cfg["normalization"]["location_aliases"])
    )
    df["cuisine"] = raw[field_map.cuisine].apply(
        lambda v: normalize_cuisine(v, cfg["normalization"]["cuisine_aliases"])
    )
    df["avg_cost_for_two"] = raw[field_map.avg_cost_for_two].apply(parse_cost)
    df["rating"] = raw[field_map.rating].apply(parse_rating)

    low_max = cfg["normalization"]["budget_thresholds"]["low_max"]
    medium_max = cfg["normalization"]["budget_thresholds"]["medium_max"]
    df["budget_band"] = df["avg_cost_for_two"].apply(
        lambda c: derive_budget_band(c, low_max, medium_max)
    )

    # Quality filters.
    qcfg = cfg["quality"]
    valid_rating = df["rating"].between(qcfg["min_rating"], qcfg["max_rating"], inclusive="both")
    non_empty = (
        (df["name"].str.len() > 0)
        & (df["location"].str.len() > 0)
        & (df["cuisine"].str.len() > 0)
    )
    valid_cost = df["avg_cost_for_two"] >= 0
    accepted_mask = valid_rating & non_empty & valid_cost

    accepted = df[accepted_mask].copy()
    rejected = df[~accepted_mask].copy()

    # Deduplication: ID first, then name+location fallback.
    accepted = accepted.drop_duplicates(subset=["id"], keep="first")
    accepted = accepted.drop_duplicates(subset=["name", "location"], keep="first")

    # Enforce canonical column ordering.
    accepted = accepted[[col for col in CANONICAL_COLUMNS if col in accepted.columns]]
    rejected = rejected[[col for col in CANONICAL_COLUMNS if col in rejected.columns]]

    accepted_path = output_dir / "restaurants_clean.csv"
    rejected_path = output_dir / "restaurants_rejected.csv"
    report_path = output_dir / "quality_report.json"

    accepted.to_csv(accepted_path, index=False)
    rejected.to_csv(rejected_path, index=False)

    report = quality_metrics(accepted, rejected_count=len(rejected))
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Clean data written to: {accepted_path}")
    print(f"Rejected data written to: {rejected_path}")
    print(f"Quality report written to: {report_path}")


if __name__ == "__main__":
    main()
