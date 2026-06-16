# Non-Functional Requirement Targets (Phase 0)

This file defines measurable baseline targets for implementation and sign-off.

## 1) Performance Targets

- API p50 latency: <= 1200 ms
- API p95 latency: <= 3000 ms
- LLM call timeout: 5000 ms hard timeout
- Candidate filtering latency (no LLM): <= 300 ms p95

## 2) Reliability Targets

- API availability: >= 99.5% monthly
- Successful response rate (2xx + graceful fallback): >= 99.0%
- Fallback success rate when LLM fails: >= 99.9%
- Zero unhandled exceptions for validation errors

## 3) Scalability Targets

- Initial sustained throughput: 50 requests/minute
- Burst capacity: 5x sustained throughput for 2 minutes
- Horizontal scaling supported at API tier

## 4) Cost Targets

- Mean LLM token cost/request below predefined budget threshold
- Cache hit ratio for repeated queries >= 30% after warm-up
- Cost spike alert if daily spend exceeds threshold

## 5) Security Targets

- All secrets stored in secret manager
- No sensitive data in application logs
- Rate limiting enabled on recommendation endpoint
- Input sanitization for all user-provided text fields

## 6) Observability Targets

- 100% request IDs propagated end-to-end
- Structured logs for recommendation lifecycle events
- Metrics dashboards for latency, error, fallback, and token usage
- Alerts for p95 latency and error-rate threshold breaches

## 7) Acceptance Checks

- Targets are encoded in monitoring dashboards and alerts.
- Load and failure tests prove fallback and latency behavior.
- Security checklist is completed before production release.
