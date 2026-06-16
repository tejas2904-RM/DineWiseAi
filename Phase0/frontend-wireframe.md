# Frontend Flow and Wireframe Notes (Phase 0)

This document defines frontend flow and state expectations before implementation.

## 1) Primary UX Flow

1. User lands on recommendation page.
2. User fills preference form.
3. User submits request.
4. UI shows progressive loading states.
5. UI renders recommendation cards with explanations.
6. User refines filters or submits feedback.

---

## 2) Screen-Level Wireframe (Textual)

## Screen A: Preference Form
- Header: app title + short helper text
- Form fields:
  - Location (text/autocomplete)
  - Budget (single-select)
  - Cuisine (text/select)
  - Minimum rating (slider/input)
  - Additional preferences (chips/multi-select)
- CTA: "Get Recommendations"
- Validation hints below fields

## Screen B: Loading
- Step indicator:
  - Validating preferences
  - Finding candidates
  - Generating AI recommendations
- Skeleton cards placeholder

## Screen C: Results
- Summary banner (optional)
- Recommendation cards:
  - Name
  - Cuisine
  - Rating
  - Estimated cost
  - Why this matches you
- Actions:
  - Sort (rating/cost/relevance)
  - Refine preferences
  - Feedback (thumbs up/down)

## Screen D: Empty/No-Result State
- Message: no exact match found
- Suggestions: relax one or more constraints
- CTA: "Try broader filters"

---

## 3) Frontend State Model (Suggested)

State domains:
- `formState`: field values and validation errors
- `requestState`: idle/loading/success/error
- `resultState`: recommendations + metadata
- `uiState`: sort order, expanded cards, toasts

Required transitions:
- `idle -> loading -> success`
- `idle -> loading -> error`
- `success -> loading` (on refinement)

---

## 4) Responsive and Accessibility Requirements

- Mobile-first layout for small screens.
- All controls keyboard-navigable.
- Proper labels and ARIA attributes on form fields.
- Color contrast compliant for status and feedback indicators.

---

## 5) Frontend-Backend Contract Requirements

- Frontend only sends schema-valid payloads.
- Frontend gracefully handles:
  - validation errors (`400`)
  - rate limits (`429`)
  - server errors (`500/503`)
- Frontend displays fallback mode clearly when `usedFallback=true`.
