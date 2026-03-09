# CLAUDE.md — GrowEngine Repository Guide

This file provides guidance for AI assistants (e.g., Claude Code) working in this repository.

---

## Project Overview

**GrowEngine** is a full-stack advertising campaign management and recommendation platform. It consists of two independent but related subsystems:

1. **Ad Management Dashboard** — campaign CRUD, real-time analytics, bidding simulation, AI diagnostics
2. **Ad Recommendation System** — personalized ad delivery using collaborative filtering and embeddings

---

## Repository Structure

```
adproto/
├── backend/              # Core Ad Management API (FastAPI, port 8000)
├── frontend/             # Admin Dashboard (React + Vite, port 5173 dev)
├── ad_rec_backend/       # Recommendation System API (FastAPI, port 8001)
├── ad_rec_frontend/      # Recommendation UI (React + Vite, port 5174 dev)
├── Simple_Tiktok_App/    # Android demo app (separate; not part of main stack)
├── web_visualization/    # Standalone visualization helpers
├── scripts/              # DevOps / utility scripts
├── docker-compose.yml    # Full-stack local orchestration
├── start-dev.sh          # Development startup script
├── README.md             # English docs
└── README_CN.md          # Chinese docs
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend language | Python 3.11 |
| Backend framework | FastAPI (async) |
| Frontend framework | React 18/19 with hooks |
| Build tool | Vite |
| Styling | TailwindCSS |
| Charts | Recharts |
| Icons | Lucide React |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions → GitHub Pages |
| Production hosting | Railway (backend), GitHub Pages (frontend) |

---

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (optional, for containerized dev)

### Starting the Full Stack Locally

```bash
# Option A: Docker Compose (recommended)
docker-compose up -d --build

# Option B: Manual
# Terminal 1 — Core backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python generate_mock_data.py   # only needed on first run
uvicorn api:app --reload --port 8000

# Terminal 2 — Admin frontend
cd frontend
npm install
npm run dev                    # http://localhost:5173

# Terminal 3 — RecSys backend (optional)
cd ad_rec_backend
pip install -r requirements.txt
uvicorn api:app --reload --port 8001

# Terminal 4 — RecSys frontend (optional)
cd ad_rec_frontend
npm install
npm run dev                    # http://localhost:5174
```

### Access Points

| Service | Dev URL | Docs |
|---|---|---|
| Admin Dashboard | http://localhost:5173 | — |
| Core API | http://localhost:8000 | http://localhost:8000/docs |
| RecSys UI | http://localhost:5174 | — |
| RecSys API | http://localhost:8001 | http://localhost:8001/docs |

---

## Building for Production

```bash
# Frontend build
cd frontend && npm run build   # output: frontend/dist/

# Backend is deployed via Railway using backend/railway.toml
# Frontend is deployed to GitHub Pages via .github/workflows/deploy.yml
```

---

## Testing

**There is currently no automated test suite.** Testing is done manually via the UI or FastAPI's built-in Swagger docs (`/docs`). When adding new features, test API endpoints manually at `http://localhost:8000/docs`.

---

## Key Source Files

### Backend — `backend/api.py`

The main FastAPI application (~32 KB). Key sections:

- **Campaign CRUD:** `GET/POST/PUT/DELETE /api/campaigns`
- **Metrics:** `GET /api/metrics/realtime`, `GET /api/metrics/trend`
- **Bidding:** `POST /api/bidding/calculate`, `POST /api/bidding/simulate`
- **AI diagnostics:** `GET /api/diagnosis`
- **AI chat:** `POST /api/ai/chat` (single-turn), `POST /api/ai/agent` (streaming with tool-calling)
- **Health:** `GET /health`

### Backend — `backend/simulator.py`

OnlineLp bidding simulator implementing real-time bid optimization with budget constraints and CPA targets.

### Backend — `backend/generate_mock_data.py`

Generates `backend/data/campaigns.json` and `backend/data/metrics_timeseries.json` with 20 realistic test campaigns. Run this on first setup or to reset data.

### Frontend — `frontend/src/App.jsx`

Monolithic React component (~90 KB) containing the entire admin dashboard: campaign table, metrics cards, bidding simulation modal, AI chat interface, and diagnosis panel.

### RecSys Backend — `ad_rec_backend/api.py`

Recommendation endpoints:
- `GET /api/rec/ads` — personalized ad recommendations
- `GET /api/rec/similar` — item-to-item similarity
- `POST /api/rec/click` — log click events
- `POST /api/rec/train` — trigger retraining
- `GET /api/rec/stats` — CTR and engagement metrics

### RecSys Backend — `ad_rec_backend/data_manager.py`

Thread-safe singleton that loads all CSV data into memory on startup. Handles ads, visitors, embeddings, and click logs.

---

## Data Models

### Campaign (Pydantic)

```python
class Campaign(BaseModel):
    id: int
    name: str
    status: str          # "active" | "learning" | "paused"
    budget: float
    bid: float
    spend: float
    impressions: int
    clicks: int
    ctr: float
    cvr: float
    cpa: float
    roi: float
    learning_stage: str  # "learning" | "passed" | "failed"
    bid_type: str        # "CPC" | "CPM" | "oCPM" | "NOBID"
    created_at: Optional[str]
    updated_at: Optional[str]
```

### Data Files

| File | Purpose |
|---|---|
| `backend/data/campaigns.json` | Campaign metadata |
| `backend/data/metrics_timeseries.json` | Time-series performance metrics |
| `ad_rec_backend/data/ads.csv` | Ad catalog |
| `ad_rec_backend/data/visitors.csv` | User profiles |
| `ad_rec_backend/data/clicks.csv` | Click event log |
| `ad_rec_backend/data/ad_embeddings.csv` | Ad feature vectors |
| `ad_rec_backend/data/visitor_embeddings.csv` | User feature vectors |

---

## Environment Variables

### `frontend/.env.development`
```
VITE_API_BASE_URL=http://localhost:8000
```

### `frontend/.env.production`
```
VITE_API_BASE_URL=https://adproto-huzhe012508-qk1u7b48.leapcell.dev
```

### Backend LLM Integration (configure via env vars)
The AI chat/agent endpoints call an external LLM API. The default endpoint is `https://680728.xyz/v1` with model `qwen-max`. Override via environment variables before running the backend.

### Optional RecSys Services
The recommendation backend optionally connects to:
- Java RecSysServer: `http://localhost:6010`
- TensorFlow Serving: `http://localhost:8501`
- Redis: `localhost:6379`

These are not required; the system falls back gracefully if unavailable.

---

## Code Conventions

### Python
- Follow **PEP 8**
- Use **async/await** for all FastAPI endpoints
- Use **Pydantic BaseModel** for all request and response schemas
- Thread-safe **singleton pattern** for data managers (see `DataManager`, `ClickCollector`)

### JavaScript / React
- **Functional components** and React hooks only (no class components)
- **Lucide React** for all icons
- **Recharts** for data visualizations
- API calls go through the service wrapper in `frontend/src/services/api.js`
- TailwindCSS utility classes for styling (no separate CSS files)

### Git Commits
- Use **present tense, imperative mood** (e.g., `Add bidding simulation endpoint`)
- Keep the first line under **72 characters**
- Reference issue numbers when relevant

### File Formatting
- All files must end with a **newline character**
- No trailing whitespace

---

## Deployment

### GitHub Pages (Frontend)
Triggered automatically on push to `main` via `.github/workflows/deploy.yml`. Vite builds with `base: '/adproto/'` set in `frontend/vite.config.js`.

### Railway (Backend)
Configured via `backend/railway.toml` and `backend/Dockerfile`. Gunicorn runs FastAPI in production mode.

### Docker Compose (Full Stack)
```bash
docker-compose up -d --build
# Frontend on port 3000, Backend on port 8000
```

---

## Known Limitations / Areas for Improvement

- **No automated tests** — no pytest or Jest setup exists
- **CORS is open** (`allow_origins=["*"]`) — should be restricted in production
- **No authentication** — all API endpoints are public
- **LLM credentials** should be moved to environment variables, not hardcoded
- **`frontend/src/App.jsx` is very large** (~90 KB) — consider splitting into smaller components

---

## External Documentation

- FastAPI auto-generated Swagger UI: `/docs` on any running backend
- [README.md](./README.md) — English user guide and architecture overview
- [README_CN.md](./README_CN.md) — Chinese documentation
- [CONTRIBUTING.md](./CONTRIBUTING.md) — Contribution guidelines and PR process
