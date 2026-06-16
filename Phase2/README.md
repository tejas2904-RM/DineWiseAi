# Phase 2 Implementation: Preference Capture and Validation

This folder implements **Phase 2** from `Docs/architecture.md`:
- Backend endpoint for preference capture and validation
- Input normalization and schema enforcement
- Frontend form with client-side validation, loading, and retry state

## Structure

- `backend/`
  - `main.py` - FastAPI app and endpoints
  - `schemas.py` - request/response models and validators
  - `normalizer.py` - value normalization rules
  - `requirements.txt`
- `frontend/`
  - `index.html`
  - `styles.css`
  - `app.js`

## Backend Run

1. Create virtual environment and install dependencies:
   - `python -m venv .venv`
   - `.venv\Scripts\activate`
   - `pip install -r backend/requirements.txt`
2. Start API:
   - `uvicorn backend.main:app --reload --port 8000`

## Frontend Run

You can open `frontend/index.html` directly in browser for local validation flow.
For API calls, ensure backend is running at `http://localhost:8000`.

## Implemented Phase 2 Requirements

- `POST /recommendations` endpoint
- Server-side schema validation and clear field-level errors
- Input normalization for location and budget synonyms
- Client-side form validation and helpful UX messages
- Loading, error, and retry UI states
