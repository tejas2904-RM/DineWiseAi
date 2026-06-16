# Phase 9 — Backend Deployment on Render

Phase 9 packages everything needed to deploy the **Phase 7** (hardened gateway) and **Phase 8** (personalization API) backends to [Render](https://render.com), as specified in `Docs/architecture.md`.

```
Browser / Vercel (Phase 10)
        │
        ▼
  Render: rrs-phase8  ──►  Render: rrs-phase7  ──►  Groq LLM
        │                         │
        └── persistent disk       └── restaurants_clean.csv (repo)
            (users/history/favorites)
```

## Folder layout

```
Phase9/
  render.yaml           # Render Blueprint (two web services)
  .env.example          # Environment variable reference
  docker-compose.yml    # Local stack mirroring production topology
  docker/
    Dockerfile.phase7   # Optional container build for Phase 7
    Dockerfile.phase8   # Optional container build for Phase 8
  scripts/
    smoke_test.py       # Post-deploy health + recommendation checks
  shared/
    cors.py             # CORS helper (reference; logic inlined in backends)
  README.md
```

## Prerequisites

- GitHub (or GitLab) repo containing the **full monorepo** (`Phase1`–`Phase8`).
- [Render](https://render.com) account.
- `GROQ_API_KEY` from [Groq Console](https://console.groq.com/).
- `Phase1/outputs/restaurants_clean.csv` committed or generated before deploy.

## Quick deploy (Render Blueprint)

1. **Copy the blueprint to the repo root** (Render expects `render.yaml` at the root by default):

   ```powershell
   copy Phase9\render.yaml render.yaml
   ```

   Alternatively, create a Blueprint in the Render dashboard and point it at `Phase9/render.yaml`.

2. **Connect your repository** in Render → **New** → **Blueprint**.

3. **Set secrets** when prompted (or in the dashboard after create):
   - `GROQ_API_KEY` — required for Phase 7 LLM calls
   - `PHASE7_API_KEYS` — optional custom API keys (`key:role,...`)

4. **Deploy.** Render creates:
   - `rrs-phase7` — health: `/v1/health`
   - `rrs-phase8` — health: `/api/v1/health`, 1 GB persistent disk on `Phase8/backend/data`

5. **Update CORS** on both services after you have a Vercel URL (Phase 10):

   ```
   CORS_ORIGINS=http://localhost:8082,https://your-app.vercel.app
   ```

6. **Smoke test:**

   ```powershell
   python Phase9/scripts/smoke_test.py `
     --phase7 https://rrs-phase7.onrender.com `
     --phase8 https://rrs-phase8.onrender.com
   ```

## Service configuration

### Phase 7 (`rrs-phase7`)

| Setting | Value |
|---------|-------|
| Root directory | `Phase7/backend` |
| Build | `pip install -r requirements.txt` |
| Start | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Health check | `/v1/health` |

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key (secret) |
| `GROQ_MODEL` | Default: `llama-3.3-70b-versatile` |
| `PHASE7_API_KEYS` | Optional `key:role` pairs |
| `CORS_ORIGINS` | Comma-separated allowed origins |

### Phase 8 (`rrs-phase8`)

| Setting | Value |
|---------|-------|
| Root directory | `Phase8/backend` |
| Build | `pip install -r requirements.txt` |
| Start | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Health check | `/api/v1/health` |
| Disk | `/opt/render/project/src/Phase8/backend/data` (1 GB) |

| Variable | Description |
|----------|-------------|
| `PHASE7_BASE` | Auto-wired from Phase 7 `RENDER_EXTERNAL_URL` in blueprint |
| `PHASE8_DEFAULT_KEY` | API key forwarded to Phase 7 (default: `phase7-demo-key`) |
| `PHASE8_DATASET` | Path to `restaurants_clean.csv` on Render |
| `CORS_ORIGINS` | Comma-separated allowed origins |

## Local Docker stack

Test the same topology locally before pushing to Render:

```powershell
# From repo root — requires Phase4/.env with GROQ_API_KEY
docker compose -f Phase9/docker-compose.yml up --build
```

- Phase 7: http://localhost:8001  
- Phase 8: http://localhost:8002  

Phase 8 data persists in a Docker volume (`phase8-data`).

## Manual Render setup (without Blueprint)

If you prefer creating services manually:

1. **New Web Service** → Python → root `Phase7/backend` → set env vars → health `/v1/health`.
2. **New Web Service** → Python → root `Phase8/backend` → set `PHASE7_BASE` to Phase 7 URL → attach disk at `Phase8/backend/data` → health `/api/v1/health`.

## Notes

- **Free tier:** Render free web services spin down after inactivity; first request may be slow (cold start).
- **Persistent disk:** Required on paid plans for Phase 8 JSON storage; free tier cannot attach disks — data resets on redeploy.
- **Monorepo paths:** Phase 7 imports modules from `Phase3`–`Phase6` and reads `Phase1/outputs/restaurants_clean.csv`. Deploy the entire repository, not isolated backend folders.
- **Phase 10:** Point the Vercel frontend at the Phase 8 Render URL (`NEXT_PUBLIC_API_BASE` or `next.config.js` rewrites).

## Related docs

- `Docs/architecture.md` — Phase 9 & 10 deployment architecture
- `Phase7/README.md` — API gateway details
- `Phase8/README.md` — Personalization API details
