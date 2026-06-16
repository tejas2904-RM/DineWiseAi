# Definition of Done (Phase 0 to Phase 6)

This checklist defines completion criteria for each implementation phase.

## Phase 0: Foundation and Planning

- API spec is documented and reviewed.
- Data schema and validation rules are finalized.
- Prompt specification and fallback behavior are defined.
- Frontend flow and state model are approved.
- NFR targets are measurable and accepted.

Exit artifact check:
- `api-spec.yaml`
- `data-schema.md`
- `prompt-spec.md`
- `frontend-wireframe.md`
- `nfr-targets.md`

---

## Phase 1: Data Ingestion and Standardization

- Dataset ingestion pipeline runs end-to-end.
- Required columns are mapped and normalized.
- Data quality checks detect nulls/duplicates/type errors.
- Restaurant records are persisted with query indexes.
- Ingestion run logs and error reporting are available.

Quality gates:
- >= 95% records pass quality checks (or documented exceptions).
- No duplicate IDs in output store.

---

## Phase 2: Preference Capture and Validation

- `POST /recommendations` accepts and validates request schema.
- Field-level error messages are returned for invalid input.
- Normalization for location and budget synonyms is implemented.
- Frontend form validates required fields and handles error states.

Quality gates:
- Invalid payloads never reach candidate filtering.
- Validation test suite covers boundaries and malformed inputs.

---

## Phase 3: Candidate Retrieval and Rule-Based Ranking

- Hard filtering and soft scoring logic is implemented.
- Top-N candidate clipping is enforced.
- Deterministic tie-break strategy is in place.
- Cache integration works for repeated queries.

Quality gates:
- Candidate retrieval p95 latency target is met.
- Repeated runs with same input produce stable ranking order.

---

## Phase 4: LLM Recommendation and Explanation Generation

- Prompt builder uses versioned template.
- LLM adapter handles timeout, retry, and provider errors.
- Output schema validation is strict.
- Hallucinated recommendations are rejected.
- Fallback ranking activates automatically on LLM failure.

Quality gates:
- No invalid response schema reaches frontend.
- Fallback path tested for timeout and malformed output cases.

---

## Phase 5: Response Delivery and User Experience

- API returns structured recommendations with metadata.
- Frontend displays cards with explanations and sorting controls.
- Loading, retry, and no-result states are user-friendly.
- Feedback capture endpoint and UI hooks are integrated.

Quality gates:
- End-to-end flow succeeds from form submit to results render.
- Accessibility baseline checks pass for core pages.

---

## Phase 6: Monitoring, Evaluation, and Continuous Improvement

- Metrics for latency/error/fallback/token usage are live.
- Logs and traces support request-level debugging.
- Alerting is configured for key SLO thresholds.
- Offline evaluation framework exists for recommendation quality.
- Feedback data is captured for iterative improvement.

Quality gates:
- Dashboards and alerts validated in staging.
- At least one quality-improvement loop is documented.

---

## Global Done Criteria

- Documentation is current and linked from project docs.
- All phase exit artifacts are present and reviewed.
- CI checks for lint/test/build pass on target branch.
- No critical security issues remain open for production release.
