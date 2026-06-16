from __future__ import annotations

import json
from pathlib import Path

from datasets import load_dataset


def main() -> None:
    print("Loading Hugging Face dataset: ManikaSaini/zomato-restaurant-recommendation")
    ds = load_dataset("ManikaSaini/zomato-restaurant-recommendation")

    info = {
        "splits": list(ds.keys()),
        "splits_detail": {},
    }
    for split_name, split in ds.items():
        info["splits_detail"][split_name] = {
            "rows": len(split),
            "columns": split.column_names,
        }
        print(f"Split '{split_name}': {len(split)} rows, columns: {split.column_names}")
        if len(split) > 0:
            print(f"First record: {split[0]}")

    # Save dataset info
    info_path = Path(__file__).resolve().parent / "hf_dataset_info.json"
    info_path.write_text(json.dumps(info, indent=2), encoding="utf-8")
    print(f"Dataset info saved to: {info_path}")

    # Convert to pandas and save as CSV for ingestion
    train_df = ds["train"].to_pandas()
    raw_path = Path(__file__).resolve().parent / "data" / "raw"
    raw_path.mkdir(parents=True, exist_ok=True)
    csv_path = raw_path / "zomato.csv"
    train_df.to_csv(csv_path, index=False)
    print(f"Dataset saved to: {csv_path} ({len(train_df)} rows)")


if __name__ == "__main__":
    main()
