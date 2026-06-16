# Phase 1 Implementation: Data Ingestion and Standardization

This folder implements **Phase 1** from `Docs/architecture.md`:
- Ingest raw Zomato-style restaurant data
- Clean and normalize records
- Deduplicate entries
- Generate data quality reports
- Export query-ready datasets

## Folder Structure

- `src/ingest.py` - CLI ingestion pipeline entrypoint
- `src/transform.py` - normalization and transformation logic
- `src/quality.py` - quality checks and metrics
- `src/schema.py` - canonical fields and schema helpers
- `config.yaml` - ingestion and normalization configuration
- `requirements.txt` - Python dependencies
- `outputs/` - generated cleaned files and reports

## Input Expectations

The pipeline accepts CSV/JSON with fields that can map to:
- restaurant name
- location/city
- cuisines
- average cost
- rating

Raw field names can vary; mapping is configured in `config.yaml`.

## Quick Start

1. Create environment and install dependencies:
   - `python -m venv .venv`
   - `.venv\Scripts\activate`
   - `pip install -r requirements.txt`

2. Run ingestion:
   - `python src/ingest.py --input "..\data\raw\zomato.csv" --output ".\outputs"`

3. Review generated files in `outputs/`:
   - `restaurants_clean.csv`
   - `restaurants_rejected.csv`
   - `quality_report.json`

## Phase 1 Completion Criteria Covered

- Null/type/duplicate checks
- Canonical location and cuisine normalization
- Budget band derivation from cost
- Query-ready cleaned output
- Quality report for auditability
