# Prompt Specification (Phase 0)

This specification defines the prompt strategy for Phase 4 and the contract required by backend services.

## 1) Prompt Objectives

- Rank candidate restaurants for a specific user preference set.
- Generate concise, factual explanations grounded only in candidate data.
- Avoid hallucinations by restricting output to provided candidate IDs.
- Return machine-parseable output matching strict schema.

---

## 2) Prompt Structure

1. **System Instruction**
   - Role: recommendation assistant
   - Boundaries: use only provided candidate records
   - Output format: strict JSON

2. **Developer Instruction**
   - Ranking policy and explanation quality requirements
   - Required response schema and validation constraints

3. **User Context Payload**
   - normalized preferences
   - candidate list with limited fields
   - topK requirement

---

## 3) Candidate Payload Constraints

- Include only required fields: `id`, `name`, `location`, `cuisine`, `avgCostForTwo`, `budgetBand`, `rating`, `tags`.
- Cap candidate list to top-N (default 20; configurable based on token budget).
- Normalize textual fields before insertion into prompt.

---

## 4) Required Output Schema

```json
{
  "recommendations": [
    {
      "rank": 1,
      "restaurantId": "r_123",
      "reason": "Matches your preferred Italian cuisine in Bangalore, stays in the medium budget range, and has a strong 4.4 rating."
    }
  ],
  "summary": "Top picks balance cuisine match, rating, and budget."
}
```

Schema rules:
- `rank` must be unique and sequential.
- `restaurantId` must be from candidate list.
- `reason` must be specific, not generic.
- Response must not include extra fields unless explicitly allowed.

---

## 5) Guardrails and Safety

- Reject model outputs referencing unknown `restaurantId`.
- Retry once with stricter schema reminder if parsing fails.
- If second attempt fails, trigger deterministic fallback ranking.
- Strip unsafe/untrusted text in user-provided tags before prompt assembly.
- Separate user content from system instructions to reduce prompt injection risk.

---

## 6) Fallback Strategy

Fallback is triggered when:
- model timeout occurs,
- provider error persists after retry,
- output parsing or schema validation fails,
- hallucinated IDs exceed repair threshold.

Fallback output:
- deterministic ranking from Phase 3 scores,
- templated reasons using matched attributes,
- `usedFallback: true` in API response.

---

## 7) Prompt Versioning

- Maintain template versions (`v1`, `v2`, etc.) in source control.
- Track per-request `promptVersion` in logs for evaluation.
- Roll out prompt changes gradually behind feature flags in staging first.
