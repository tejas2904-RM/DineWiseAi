# Phase 6: Monitoring, Evaluation, and Continuous Improvement

This phase adds production observability, offline evaluation, and feedback loops to the restaurant recommendation pipeline.

## What's Implemented

### 1. Backend Observability (`src/observability.py`)
- **Structured JSON logging** for every request, LLM call, feedback event, and UX event
- **In-memory metrics store** with rolling window (10,000 records)
- **Computed metrics:**
  - API latency: p50, p95, p99
  - LLM latency and token usage (prompt/completion/total)
  - Fallback rate and error rate
  - Cache hit rate
  - Feedback helpful rate
  - UX event breakdown by session

### 2. Enhanced Endpoints (Phase5 backend)
- `GET /metrics` — full snapshot of API, LLM, feedback, and UX metrics
- `GET /observability/requests` — recent request traces (anonymized)
- `GET /observability/feedback` — recent feedback records
- `POST /telemetry` — ingest frontend UX events
- `POST /feedback` — now stores feedback in the metrics store

### 3. Frontend Telemetry (`Phase5/frontend/app.js`)
Tracks the following events (best-effort, fire-and-forget):
- `form_started` — user first focuses an input field
- `form_submitted` — valid form submission
- `form_validation_error` — validation failure
- `results_rendered` — recommendation cards displayed
- `request_error` — network/server error
- `request_retry` — user clicks retry
- `feedback_given` — thumbs up/down clicked
- `sort_changed` — sort dropdown changed
- `refine_clicked` — user clicks refine

### 4. Offline Evaluation (`src/eval_runner.py`)
Runs a benchmark suite against the live API and computes:
- Success rate per query
- Average latency
- Fallback rate
- Location relevance precision (do returned restaurants match the requested area?)
- Average rating of recommendations

Usage:
```bash
cd Phase6/src
python eval_runner.py
# or with custom URL / benchmark
python eval_runner.py http://localhost:8000 benchmark_queries.json
```

### 5. LLM Telemetry (Phase4 engine)
- Each LLM call now records: latency, prompt tokens, completion tokens, total tokens, model name
- Token usage is extracted from Groq API `usage` field
- Retry attempts are tracked separately

## File Changes

| File | Change |
|------|--------|
| `Phase6/src/observability.py` | New — metrics store and structured logging |
| `Phase6/src/eval_runner.py` | New — offline evaluation runner |
| `Phase6/src/benchmark_queries.json` | New — 8 benchmark preference sets |
| `Phase4/src/groq_adapter.py` | Modified — returns token usage metadata |
| `Phase4/src/engine.py` | Modified — captures LLM latency and token usage per attempt |
| `Phase5/backend/main.py` | Modified — wires observability into all endpoints |
| `Phase5/backend/schemas.py` | Modified — adds `UXTelemetryEvent` schema |
| `Phase5/frontend/app.js` | Modified — emits UX telemetry events |

## Running the Full Stack

1. Start the backend (from Phase5):
   ```bash
   cd Phase5/backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. Open the frontend (`Phase5/frontend/index.html`) in a browser.

3. Run offline evaluation:
   ```bash
   cd Phase6/src
   python eval_runner.py
   ```

4. View metrics:
   ```bash
   curl http://localhost:8000/metrics
   curl http://localhost:8000/observability/requests
   curl http://localhost:8000/observability/feedback
   ```
