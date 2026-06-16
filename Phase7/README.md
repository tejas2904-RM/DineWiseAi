# Phase 7: Backend Hardening & API Gateway

This phase secures, scales, and hardens the restaurant recommendation API for production traffic.

## What's Implemented

### 1. Rate Limiting (`middleware/rate_limiter.py`)
- **Token-bucket algorithm** per client IP
- Default: 5 requests/second, burst capacity of 10
- Returns `429 Too Many Requests` with `Retry-After` header
- Frontend handles 429 with graceful retry backoff

### 2. API Authentication (`middleware/auth.py`)
- **API key-based authentication** via `Authorization: Bearer <key>` or `x-api-key` header
- **Role-based access control (RBAC):** `user` and `admin` roles
- Built-in demo keys:
  - `phase7-demo-key` (role: user)
  - `phase7-admin-key` (role: user, admin)
- Custom keys via `PHASE7_API_KEYS` env variable
- Endpoints:
  - `GET /v1/auth/status` — check current auth status
  - `GET /v1/metrics` — admin-only
  - `GET /v1/observability/*` — admin-only

### 3. Security Headers (`middleware/security_headers.py`)
Adds the following headers to every response:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

### 4. Circuit Breaker (`middleware/circuit_breaker.py`)
- Protects against LLM provider outages
- States: `CLOSED` (normal), `OPEN` (failing), `HALF_OPEN` (recovery probe)
- Configurable failure threshold (default 3) and recovery timeout (default 30s)
- Returns `503 Service Unavailable` when circuit is open
- Frontend displays circuit breaker state in metadata

### 5. Request Deduplication (`middleware/request_dedup.py`)
- Prevents redundant LLM calls for identical requests
- SHA-256 hash of request path + body as deduplication key
- Concurrent duplicate requests wait for the first to complete
- TTL of 10 seconds per in-flight request

### 6. API Versioning
- All new endpoints prefixed with `/v1/`
- Legacy `/recommendations` redirects to `/v1/recommendations` for backward compatibility

## File Structure

```
Phase7/
  backend/
    main.py                 # FastAPI app with all middleware wired
    schemas.py              # Pydantic models
    requirements.txt
    middleware/
      __init__.py
      rate_limiter.py       # Token-bucket rate limiter
      auth.py               # API key auth + RBAC
      security_headers.py   # Security headers middleware
      circuit_breaker.py    # Circuit breaker for LLM calls
      request_dedup.py      # Request deduplication
  frontend/
    index.html              # UI with API key input
    app.js                  # Auth-aware client with 429 handling
    styles.css              # Extended styles for auth UI
  README.md
```

## Running Phase 7

1. Start the hardened backend (runs on port 8001):
   ```bash
   cd Phase7/backend
   uvicorn main:app --host 0.0.0.0 --port 8001
   ```

2. Open the frontend (`Phase7/frontend/index.html`) in a browser.

3. Enter an API key (default: `phase7-demo-key`) and click **Check Auth**.

4. Submit recommendations. The backend will enforce rate limits, auth, and circuit breaker protection.

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/v1/health` | None | Service health + circuit breaker state |
| GET | `/v1/auth/status` | Optional | Current authentication status |
| POST | `/v1/recommendations` | Required | Get recommendations (rate limited) |
| POST | `/v1/feedback` | Required | Submit feedback |
| GET | `/v1/metrics` | Admin only | Full metrics snapshot |
| GET | `/v1/observability/requests` | Admin only | Recent request traces |
| GET | `/v1/observability/feedback` | Admin only | Recent feedback records |
| POST | `/v1/telemetry` | Required | UX telemetry events |
| POST | `/recommendations` | Required | Legacy redirect to /v1/recommendations |

## Testing Security Features

**Rate Limiting:**
```bash
# Rapid-fire requests to trigger 429
for i in {1..15}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -H "Authorization: Bearer phase7-demo-key" \
    -X POST http://localhost:8001/v1/recommendations \
    -d '{"location":"Bellandur","budget":"medium","cuisine":"any","minRating":4.0}'
done
```

**Invalid API Key:**
```bash
curl -H "Authorization: Bearer invalid-key" \
  -X POST http://localhost:8001/v1/recommendations \
  -d '{"location":"Bellandur","budget":"medium","cuisine":"any","minRating":4.0}'
# Returns 401
```

**Admin-only Metrics:**
```bash
# User key - returns 403
curl -H "Authorization: Bearer phase7-demo-key" \
  http://localhost:8001/v1/metrics

# Admin key - returns 200
curl -H "Authorization: Bearer phase7-admin-key" \
  http://localhost:8001/v1/metrics
```

**Circuit Breaker State:**
```bash
curl http://localhost:8001/v1/health
# Shows "circuitBreaker": "closed" (or "open"/"half_open")
```
