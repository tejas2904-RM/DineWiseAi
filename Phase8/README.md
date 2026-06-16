# Phase 8 — Advanced Frontend & Personalization

Phase 8 implements the user-facing application layer described in
`Docs/architecture.md`:

- **Backend** (`backend/`, port **8002**) — FastAPI service that stores user
  profiles, search history, and favorites in JSON files, and proxies
  recommendation/feedback calls through to the Phase 7 hardened API gateway
  (port 8001).
- **Frontend** (`frontend/`, port **8082**) — Next.js 14 (App Router) PWA
  with TypeScript + Tailwind CSS, dark mode, OpenStreetMap (Leaflet)
  integration, and Web Share API support.

```
Browser  ──►  Next.js (8082)  ──/api/*──►  FastAPI Phase 8 (8002)  ──►  Phase 7 (8001)
                                                  │
                                                  └──►  data/*.json  (users, history, favorites)
```

## Prerequisites

- Phase 7 running on `http://localhost:8001` (`Phase7/backend/main.py`).
  Phase 8 calls `POST /v1/recommendations` and `POST /v1/feedback` on
  Phase 7 with a Bearer token (`phase7-demo-key` by default).
- Node.js 18+ and Python 3.10+.

## Backend — install & run

```powershell
cd c:\P1_RRS\Phase8\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

Environment variables:

| Var | Default | Description |
|-----|---------|-------------|
| `PHASE7_BASE` | `http://localhost:8001` | Phase 7 base URL |
| `PHASE8_DEFAULT_KEY` | `phase7-demo-key` | Fallback API key forwarded to Phase 7 |

State is persisted to `Phase8/backend/data/{users,history,favorites}.json`
(created on first write).

## Frontend — install & run

```powershell
cd c:\P1_RRS\Phase8\frontend
npm install
npm run dev
```

Open <http://localhost:8082>.

## API surface (Phase 8 backend)

| Method | Path | Notes |
|--------|------|-------|
| GET    | `/api/v1/health` | service heartbeat |
| GET    | `/api/v1/users/{userId}` | profile (auto-created) |
| PUT    | `/api/v1/users/{userId}` | update name/email |
| GET    | `/api/v1/history?userId=...&limit=20` | most-recent first |
| GET    | `/api/v1/favorites?userId=...` | list favorites |
| POST   | `/api/v1/favorites` | add favorite |
| DELETE | `/api/v1/favorites/{restaurantId}?userId=...` | remove |
| POST   | `/api/v1/recommendations` | proxies to Phase 7, also saves history |
| POST   | `/api/v1/feedback` | proxies to Phase 7 |
| GET    | `/api/v1/auth/status` | proxies to Phase 7 |

## Features

- **Personalized dashboard** — time-of-day greeting, editable display name.
- **Recent searches** — last 5 searches shown as quick-replay chips.
- **Map view** — OpenStreetMap tiles via Leaflet, markers spread radially
  around the requested location; toggle list/map.
- **Dark mode** — class-based, syncs with `prefers-color-scheme`,
  persisted in `localStorage` (`phase8-theme`).
- **Accessibility** — semantic landmarks, skip-link, `aria-*` attributes,
  visible focus rings, `prefers-reduced-motion` support.
- **PWA** — `/manifest.json` + `/sw.js` (cache-first for static, network
  for `/api/*`). Installable on supported browsers.
- **Social sharing** — Web Share API with clipboard fallback.
- **Favorites & feedback** — heart toggle and thumbs up/down per result.

## Folder layout

```
Phase8/
├── backend/
│   ├── main.py            # FastAPI app (port 8002)
│   ├── schemas.py         # Pydantic models
│   ├── user_store.py      # JSON persistence (thread-safe)
│   └── requirements.txt
└── frontend/
    ├── package.json       # next dev -p 8082
    ├── next.config.js     # /api/* → http://localhost:8002/api/*
    ├── tailwind.config.ts # darkMode: 'class'
    ├── public/
    │   ├── manifest.json
    │   ├── sw.js
    │   └── icon.svg
    └── src/
        ├── app/
        │   ├── layout.tsx      # ThemeProvider + Navbar/Footer
        │   ├── globals.css     # CSS-variable theme
        │   ├── page.tsx        # Dashboard
        │   ├── history/page.tsx
        │   └── favorites/page.tsx
        ├── components/
        │   ├── Navbar.tsx
        │   ├── Footer.tsx
        │   ├── ThemeToggle.tsx
        │   ├── PreferenceForm.tsx
        │   ├── RecommendationCard.tsx   # share + favorite + feedback
        │   ├── RecentSearches.tsx
        │   └── MapView.tsx              # Leaflet
        └── lib/
            ├── api.ts             # fetch client
            ├── theme-provider.tsx # dark-mode Context
            └── user-store.ts      # localStorage SavedSearch
```

## Quick smoke test

1. Start Phase 7 on 8001.
2. Start Phase 8 backend on 8002.
3. Start Phase 8 frontend on 8082.
4. In the dashboard fill `Indiranagar / North Indian / medium / 4.0`,
   click **Find restaurants**.
5. Toggle list/map, heart a card, switch to **Favorites** and
   **History** to verify persistence.
