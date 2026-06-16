# Phase 3 Implementation: Candidate Retrieval and Rule-Based Ranking

This folder implements **Phase 3** from `Docs/architecture.md`:
- Hard filtering (location, budget, minimum rating)
- Soft scoring (cuisine match, tag match, rating/popularity tie-breakers)
- Top-N candidate selection for LLM handoff
- Query-level caching for repeated preference requests

## Structure

- `src/models.py` - dataclasses for request and candidate records
- `src/cache.py` - in-memory TTL cache
- `src/scoring.py` - filtering and scoring logic
- `src/engine.py` - orchestration layer for retrieval + caching
- `src/run_phase3.py` - CLI runner using Phase 1 cleaned output
- `requirements.txt` - dependencies

## Input Dataset

Default input path:
- `../Phase1/outputs/restaurants_clean.csv`

Expected columns:
- `id`, `name`, `location`, `cuisine`, `avg_cost_for_two`, `rating`, `budget_band`

Optional columns:
- `tags` (comma-separated)
- `review_count`

## Quick Start

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Run example:
   - `python src/run_phase3.py --location "Bangalore" --budget medium --cuisine italian --min-rating 4.0 --tags "family-friendly,quick-service" --top-k 10`

## Output

Returns ranked candidates with:
- score breakdown
- deterministic ranking
- cache hit/miss metadata
