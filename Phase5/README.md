# Phase 5: Response Delivery and User Experience

This phase integrates Phases 2–4 into a complete end-to-end recommendation service with a polished frontend.

## Backend

**File:** `backend/main.py`

Orchestrates the full pipeline:
1. **Preference capture & validation** (Phase 2 style normalizer)
2. **Candidate retrieval & rule-based scoring** (Phase 3 engine)
3. **LLM recommendation & explanation generation** (Phase 4 engine via Groq)
4. **Response enrichment** — adds `name`, `cuisine`, `rating`, `estimatedCost` to each recommendation
5. **Metadata** — `requestId`, `latencyMs`, `usedFallback`, `fallbackReason`

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/recommendations` | Main recommendation endpoint |
| GET | `/health` | Service health check |
| GET | `/metrics` | Lightweight metrics (cache size) |
| POST | `/feedback` | Record user feedback per recommendation |

### Run the backend

```bash
cd Phase5/backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Frontend

**Files:** `frontend/index.html`, `frontend/app.js`, `frontend/styles.css`

Features:
- Preference form with validation
- Progressive loading stages (preferences → candidates → recommendations)
- Recommendation cards showing **name**, **cuisine**, **rating**, **estimated cost**, and **explanation**
- Cuisine filter pills
- Sorting by rank, rating (asc/desc), cost (asc/desc)
- Fallback banner when LLM fails
- Retry and refine-search buttons
- Per-card feedback (thumbs up/down)

### Run the frontend

Serve the `frontend/` folder with any static server:

```bash
cd Phase5/frontend
python -m http.server 8080
```

Then open `http://localhost:8080` in a browser.

## Architecture Alignment

Implements the Phase 5 responsibilities from `Docs/architecture.md`:

- **Backend:** Structured response with metadata, pagination support (`topK`), fallback transparency.
- **Frontend:** Card layout, sorting, filtering, follow-up refinement, fallback handling, feedback capture.
