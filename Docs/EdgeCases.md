# Detailed Edge Cases: AI-Powered Restaurant Recommendation System

This document lists detailed edge cases for the restaurant recommendation system defined in `Docs/Problemstatment.md`.  
Each edge case includes the scenario, risk, and expected handling behavior.

## 1) User Input Edge Cases

### 1.1 Missing Required Fields
- **Scenario:** User submits request without location, budget, cuisine, or minimum rating.
- **Risk:** Backend filtering becomes ambiguous or fails.
- **Expected Handling:** Reject request with `400 Bad Request`, return field-level validation errors.

### 1.2 Invalid Budget Value
- **Scenario:** User sends budget as `very_low` or numeric values outside defined categories.
- **Risk:** Candidate filter does not map correctly to budget bands.
- **Expected Handling:** Normalize known synonyms where possible; otherwise reject with clear allowed values (`low`, `medium`, `high`).

### 1.3 Invalid Rating Range
- **Scenario:** `minRating` is negative, greater than max rating, or not a number.
- **Risk:** Incorrect filtering or runtime error.
- **Expected Handling:** Validate server-side and reject invalid range (for example, allow only `0.0` to `5.0`).

### 1.4 Ambiguous Location Input
- **Scenario:** User enters abbreviations or alternate city names (`BLR`, `Bengaluru`, `Bangalore`).
- **Risk:** No-match queries due to inconsistent naming.
- **Expected Handling:** Apply location normalization and alias mapping before filtering.

### 1.5 Unsupported Additional Preferences
- **Scenario:** User sends unknown tags (`romantic-rooftop-silent-kids-zone`).
- **Risk:** Over-filtering or ignored user intent without feedback.
- **Expected Handling:** Retain unknown tags as soft hints, log them, and avoid hard failure unless schema strictly disallows unknown fields.

### 1.6 Very Broad Query
- **Scenario:** User only provides city and no other meaningful constraints.
- **Risk:** Huge candidate pool, poor relevance, higher LLM cost.
- **Expected Handling:** Apply default sorting (rating/popularity/cost balance), cap candidate set, and prompt user for refinement.

### 1.7 Over-Constrained Query
- **Scenario:** Narrow location + strict budget + high min rating + rare cuisine.
- **Risk:** Zero candidate results.
- **Expected Handling:** Return fallback recommendations with relaxed constraints and explain what was relaxed.

---

## 2) Dataset and Ingestion Edge Cases

### 2.1 Missing Critical Columns
- **Scenario:** Dataset lacks expected fields (rating, cost, cuisine).
- **Risk:** Pipeline break or incomplete recommendations.
- **Expected Handling:** Fail ingestion with explicit error, alert maintainers, keep last known good dataset active.

### 2.2 Null or Empty Values in Key Fields
- **Scenario:** Restaurant records missing location/cuisine/rating.
- **Risk:** Filtering and ranking bias or runtime errors.
- **Expected Handling:** Impute safe defaults only when valid; otherwise drop low-quality records and track data quality metrics.

### 2.3 Duplicate Restaurants
- **Scenario:** Same restaurant appears multiple times due to ingestion merges.
- **Risk:** Duplicate recommendations in response.
- **Expected Handling:** Deduplicate by stable keys (name + location + source ID), keep best-quality record.

### 2.4 Inconsistent Cuisines
- **Scenario:** Cuisine field contains mixed formats (`North Indian`, `north-indian`, `N. Indian`).
- **Risk:** Poor match quality.
- **Expected Handling:** Canonicalize cuisine taxonomy during preprocessing.

### 2.5 Outdated Dataset Snapshot
- **Scenario:** Closed restaurants still present; ratings stale.
- **Risk:** Low trust in recommendations.
- **Expected Handling:** Add dataset refresh schedule and version metadata in logs and optional API response.

### 2.6 Corrupted Data Types
- **Scenario:** Cost or rating stored as strings with symbols (`Rs. 1200`, `4.3/5`).
- **Risk:** Parsing failures and wrong ranking.
- **Expected Handling:** Robust type parsing with fallback; exclude records that cannot be reliably parsed.

---

## 3) Filtering and Candidate Selection Edge Cases

### 3.1 No Candidates After Hard Filters
- **Scenario:** Strict filters return zero rows.
- **Risk:** Empty user experience.
- **Expected Handling:** Multi-step relaxation strategy:
  1. Expand location radius/alias
  2. Relax rating threshold slightly
  3. Keep cuisine as soft preference
  Return explanation of applied relaxation.

### 3.2 Too Many Candidates
- **Scenario:** Popular city and broad filters produce thousands of rows.
- **Risk:** Slow processing and expensive LLM calls.
- **Expected Handling:** Pre-rank using deterministic scoring and select top-N before prompting.

### 3.3 Cost Boundary Conditions
- **Scenario:** Restaurant cost exactly at budget threshold.
- **Risk:** Inconsistent inclusion/exclusion.
- **Expected Handling:** Define inclusive boundary rules once and apply consistently.

### 3.4 Tie Scores in Pre-Ranking
- **Scenario:** Multiple restaurants share identical pre-ranking score.
- **Risk:** Unstable output between requests.
- **Expected Handling:** Apply deterministic tie-breakers (rating, review count, alphabetical ID).

### 3.5 Optional Preferences Dominate Ranking
- **Scenario:** Soft tags overrule core constraints.
- **Risk:** Recommendations drift away from user’s primary intent.
- **Expected Handling:** Keep hard constraints mandatory; limit soft-tag contribution using weight caps.

---

## 4) LLM Integration Edge Cases

### 4.1 LLM Timeout
- **Scenario:** Provider does not respond within API timeout.
- **Risk:** End-user request failure.
- **Expected Handling:** Return fallback deterministic recommendations and mark `usedFallback: true`.

### 4.2 Malformed LLM Output
- **Scenario:** Response does not follow expected schema (missing rank/reason).
- **Risk:** Parsing failure.
- **Expected Handling:** Retry once with strict schema prompt; otherwise fallback.

### 4.3 Hallucinated Restaurant Names
- **Scenario:** LLM recommends restaurants not in candidate list.
- **Risk:** Incorrect/unsafe output.
- **Expected Handling:** Validate output IDs against candidate set; discard hallucinated entries and repair list from deterministic ranking.

### 4.4 Repetitive or Generic Explanations
- **Scenario:** All reasons are nearly identical and low-value.
- **Risk:** Poor user trust and reduced usefulness.
- **Expected Handling:** Enforce explanation quality checks (must mention user preference match details).

### 4.5 Prompt Too Large
- **Scenario:** Candidate payload exceeds model context/token budget.
- **Risk:** request failure or truncation.
- **Expected Handling:** Reduce top-N candidates and compress fields before sending to LLM.

### 4.6 Provider Rate Limits
- **Scenario:** LLM API returns rate-limit errors under high traffic.
- **Risk:** cascading failures.
- **Expected Handling:** Queue/retry with backoff, use cache, and shift to fallback ranking when threshold exceeded.

---

## 5) Output and User Experience Edge Cases

### 5.1 Empty Recommendation List
- **Scenario:** Both filtering and fallback fail to produce any results.
- **Risk:** Dead-end user flow.
- **Expected Handling:** Return meaningful no-result state with actionable suggestions (broaden budget/location/rating).

### 5.2 Duplicate Recommendations in Final List
- **Scenario:** Same restaurant appears more than once due to merge/parser issues.
- **Risk:** Reduced perceived quality.
- **Expected Handling:** Deduplicate by `restaurantId` before final response.

### 5.3 Inconsistent Display Data
- **Scenario:** Explanation says "budget-friendly" while estimated cost is high.
- **Risk:** Trust erosion.
- **Expected Handling:** Consistency validation between explanation and structured fields before sending response.

### 5.4 Unsupported UI Locale/Language
- **Scenario:** User expects local language text but output is only in English.
- **Risk:** Poor accessibility.
- **Expected Handling:** Add optional language parameter; if unsupported, default to English with clear fallback.

### 5.5 Frontend/Backend Version Mismatch
- **Scenario:** Frontend expects fields missing from API response.
- **Risk:** UI crashes.
- **Expected Handling:** Version API contracts and keep backward-compatible defaults.

---

## 6) Reliability, Security, and Operational Edge Cases

### 6.1 Backend Service Restart During Request
- **Scenario:** Server restarts while processing recommendation.
- **Risk:** partial response or request drop.
- **Expected Handling:** Idempotent request handling with request IDs and graceful retry messaging.

### 6.2 Database Connectivity Failure
- **Scenario:** DB temporarily unavailable.
- **Risk:** no candidate retrieval.
- **Expected Handling:** Use cached candidate sets where possible; return temporary unavailability error if no fallback exists.

### 6.3 Cache Poisoning or Stale Cache
- **Scenario:** Incorrect or very old recommendations served from cache.
- **Risk:** degraded relevance.
- **Expected Handling:** TTL with cache key versioning and validation checksum on critical data.

### 6.4 Abuse / Prompt Injection via User Preferences
- **Scenario:** User enters malicious prompt-like text in preference fields.
- **Risk:** model manipulation or unsafe output.
- **Expected Handling:** Sanitize inputs, isolate user text from system prompt instructions, apply strict output validation.

### 6.5 Traffic Spikes
- **Scenario:** Sudden high request rate during peak hours.
- **Risk:** degraded latency and LLM failures.
- **Expected Handling:** Rate limiting, autoscaling, queueing, and dynamic fallback to rule-based recommendations.

---

## 7) Suggested Edge Case Test Matrix

- Validate all required field checks and error messages.
- Test boundary values for rating and budget mapping.
- Test zero-result path and relaxation logic.
- Test large-result path with top-N clipping.
- Test LLM timeout, malformed response, hallucination rejection.
- Test duplicate removal and schema consistency checks.
- Test fallback mode correctness and response metadata flags.
- Test cache hit/miss and stale data handling.
- Test malicious user input sanitization and prompt safety.

---

## 8) Minimum Acceptance Criteria for Edge Case Readiness

- No unhandled exceptions for invalid user inputs.
- No hallucinated restaurants in final response.
- Deterministic fallback works when LLM fails.
- Zero-result flows provide helpful next actions.
- API response remains schema-valid across success/fallback/error paths.
- Logs and metrics are sufficient to diagnose failures quickly.
