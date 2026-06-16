# Data Schema (Phase 0)

This file defines canonical entities and constraints before Phase 1 implementation.

## 1) Core Entities

## `UserPreference`
- `location: string` (required, normalized city name)
- `budget: "low" | "medium" | "high"` (required)
- `cuisine: string` (required, normalized cuisine token)
- `minRating: number` (required, `0.0 <= minRating <= 5.0`)
- `tags?: string[]` (optional, max 10 values)
- `topK?: number` (optional, default 5, max 20)
- `language?: string` (optional, default `en`)

Validation:
- Trim and normalize all string fields.
- Reject empty strings after trimming.
- Disallow control characters in all text fields.

---

## `RestaurantRecord`
- `id: string` (stable unique ID)
- `name: string`
- `location: string` (normalized)
- `cuisine: string[]` (normalized tokens)
- `avgCostForTwo: number` (>= 0)
- `budgetBand: "low" | "medium" | "high"`
- `rating: number` (`0.0 to 5.0`)
- `reviewCount?: number` (>= 0)
- `tags?: string[]`
- `sourceUpdatedAt?: string` (ISO timestamp)

Data quality rules:
- Records missing `name`, `location`, `cuisine`, `avgCostForTwo`, or `rating` are rejected or quarantined.
- Duplicates are resolved by source ID, then by `(name, location)` heuristic.
- Cuisine taxonomy is canonicalized during ingestion.

---

## `RecommendationItem`
- `rank: number` (1-based rank)
- `restaurantId: string` (must exist in candidate set)
- `name: string`
- `cuisine: string`
- `rating: number`
- `estimatedCost: number`
- `reason: string` (human-readable, preference-aligned)

Validation:
- No duplicate `restaurantId` values in final response.
- `rank` values must be unique and sequential.
- `reason` must be non-empty and mention at least one matching user preference.

---

## `RecommendationResponse`
- `requestId: string` (trace identifier)
- `recommendations: RecommendationItem[]` (size `1..topK`)
- `summary?: string`
- `usedFallback: boolean`
- `latencyMs: number`

---

## 2) Derived Fields

- `budgetBand` is derived from `avgCostForTwo` using configurable thresholds.
- `candidateScore` is computed in Phase 3 using hard-filter pass + soft weights.
- `llmConfidence` (optional future field) may be derived from parser checks.

---

## 3) Storage Mapping (Suggested)

### Table: `restaurants`
- `id` (PK)
- `name`
- `location`
- `avg_cost_for_two`
- `budget_band`
- `rating`
- `review_count`
- `tags` (json/array)
- `source_updated_at`

Indexes:
- `(location, budget_band, rating)`
- GIN/full-text index on cuisine and tags (depending on DB choice)

### Table: `restaurant_cuisines`
- `restaurant_id` (FK -> restaurants.id)
- `cuisine`

### Table: `recommendation_feedback`
- `id` (PK)
- `request_id`
- `recommendation_id` (nullable)
- `rating` (`up`/`down`)
- `comment` (nullable)
- `created_at`
