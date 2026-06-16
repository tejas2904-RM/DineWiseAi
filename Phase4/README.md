# Phase 4 Implementation: LLM Recommendation and Explanation Generation (Groq)

This folder implements **Phase 4** from `Docs/architecture.md` with **Groq** as the LLM provider.

## Scope Covered

- Prompt builder with strict output schema instructions
- Groq LLM adapter
- Output parser and validator
- Hallucination checks (`restaurantId` must exist in candidate set)
- Retry-on-parse-failure flow
- Deterministic fallback recommendations when LLM fails

## Structure

- `src/models.py` - dataclasses for preferences, candidates, and outputs
- `src/prompt_builder.py` - creates structured prompt payload
- `src/groq_adapter.py` - Groq API client wrapper
- `src/parser.py` - strict JSON extraction and validation
- `src/fallback.py` - fallback ranking and templated explanations
- `src/engine.py` - orchestration (LLM + retry + fallback)
- `src/run_phase4.py` - CLI runner
- `requirements.txt`
- `.env.example`

## Environment

Copy `.env.example` and set API key:

- `GROQ_API_KEY=your_key_here`
- `GROQ_MODEL=llama-3.3-70b-versatile` (optional)

## Install and Run

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Run:
   - `python src/run_phase4.py --input ".\sample\phase3_candidates.json" --top-k 5`

## Input Format

The CLI expects a JSON file containing:
- `preferences`
- `candidates` (from Phase 3 output)

See `sample/phase3_candidates.json` for reference.
