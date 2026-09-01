# Freight Forecasting & Vessel Recommendation System

An intelligent decision-support system for bulk cargo procurement to India's East Coast ports. It forecasts freight rate trends and recommends the optimal vessel type for a given cargo, origin, and destination — replacing manual, reactive daily market tracking with data-driven recommendations.

---

## Scope

| Item | Value |
|---|---|
| **Loading (Origin) Ports** | Australia, Indonesia |
| **Discharge (Destination) Ports** | 3 India East Coast ports (Paradip, Vizag, Gangavaram) |
| **Route Matrix** | 2 origins × 3 destinations = 6 fixed routes |
| **Vessel Types Covered** | Handysize, Supramax, Panamax, Capesize |

This is a **one-directional** system: foreign origin → India discharge only. It does not cover India-to-anywhere export routes.

---

## Features

| Feature | Status | Description |
|---|---|---|
| **Vessel Type Recommendation** | Core (build first) | Given cargo qty + route, recommends the best-fit vessel type using port draft/LOA/beam constraints |
| **Freight Rate Forecast** | Core (build first) | Time-series forecast (Prophet/SARIMA) of freight rate trend for the relevant vessel class |
| **Arrival/Departure Board** | Stretch (build second) | Train-station-style board showing scheduled vs actual vessel arrival/departure at each of the 3 India ports |
| **Live Vessel Map** | Stretch (build last) | Live map showing vessel positions along the 6 routes using AIS data |

Build order: **Vessel Recommendation + Forecast → Arrival Board → Live Map.** Do not start the map before the core features are working.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Frontend | React.js + Tailwind CSS + Recharts |
| Backend | FastAPI (Python) |
| ML / Forecasting | Prophet or SARIMA (Python), imported directly into backend as a module — not a separate service |
| Database | PostgreSQL (run via Docker locally) |
| Live Data | aisstream.io (free AIS WebSocket feed) |
| Deployment | Frontend → Vercel · Backend + ML → Render |

**Note on ML placement:** the ML model lives in its own `ml/` folder and is imported directly into the backend as a Python module (`from ml.forecasting.predict import predict_rate`). It runs inside the same FastAPI process — there is no separate ML server, no separate port, and no network call between backend and ML.

---

## Folder Structure

```
freight-forecasting-system/
├── frontend/                          # React app
│   ├── src/
│   │   ├── features/
│   │   │   ├── vessel-recommendation/
│   │   │   │   ├── RecommendationForm.jsx
│   │   │   │   ├── RecommendationResult.jsx
│   │   │   │   └── api.js
│   │   │   ├── freight-forecast/
│   │   │   │   ├── ForecastChart.jsx
│   │   │   │   └── api.js
│   │   │   ├── arrival-board/
│   │   │   │   ├── ArrivalBoard.jsx
│   │   │   │   └── api.js
│   │   │   └── live-map/
│   │   │       ├── LiveMap.jsx
│   │   │       └── api.js
│   │   ├── shared/
│   │   │   ├── components/            # Navbar, Layout, Loader
│   │   │   └── apiClient.js           # shared fetch/axios instance
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/                            # FastAPI app
│   ├── app/
│   │   ├── main.py                     # entrypoint, mounts routers, CORS config
│   │   ├── core/
│   │   │   ├── config.py               # env vars / settings
│   │   │   └── database.py             # PostgreSQL connection
│   │   ├── features/
│   │   │   ├── vessel_recommendation/
│   │   │   │   ├── router.py           # POST /api/recommend-vessel
│   │   │   │   ├── schema.py
│   │   │   │   ├── service.py          # rule-based draft/LOA/beam matching
│   │   │   │   └── constraints_data.py # reads shared port constraint data
│   │   │   ├── freight_forecast/
│   │   │   │   ├── router.py           # POST /api/forecast
│   │   │   │   ├── schema.py
│   │   │   │   └── service.py          # calls ml/forecasting/predict.py
│   │   │   ├── arrival_board/
│   │   │   │   ├── router.py           # GET /api/arrivals?port=Paradip
│   │   │   │   ├── schema.py
│   │   │   │   └── service.py
│   │   │   └── live_map/
│   │   │       ├── router.py           # GET /api/live-vessels
│   │   │       ├── schema.py
│   │   │       └── service.py
│   │   └── shared/
│   │       ├── aisstream_client.py     # shared AIS WebSocket connector
│   │       └── utils.py
│   └── requirements.txt
│
├── ml/                                  # ML code — separate module, imported by backend
│   ├── forecasting/
│   │   ├── train.py                    # trains Prophet/SARIMA on BDI historical data
│   │   ├── predict.py                  # exposes predict_rate(origin, destination, vessel_type)
│   │   ├── data_prep.py                # cleans/loads historical freight index CSVs
│   │   └── model_store/                # saved trained model files (.pkl)
│   ├── notebooks/                      # experimentation only, not used in production
│   └── requirements.txt
│
├── data/                                # shared static reference data
│   ├── port_constraints.json           # draft/LOA/beam limits for Australia, Indonesia + 3 India ports
│   ├── route_matrix.json               # the 6 fixed origin-destination combinations
│   └── bdi_historical.csv              # historical Baltic freight index data for ML training
│
├── docker-compose.yml                  # runs PostgreSQL locally
├── .env.example
└── README.md
```

---

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (Python package manager — installs dependencies, replaces pip + venv)
- Docker Desktop (for PostgreSQL)
- Git

### Installing `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Windows (PowerShell):
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Note: `uv` and `uvicorn` are different tools, not alternatives to each other. `uv` installs Python packages (replaces `pip`/`venv`); `uvicorn` is the server that actually runs the FastAPI app. Every setup below uses both.

---

## Setup Instructions

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd freight-forecasting-system
```

### 2. Set up PostgreSQL using Docker

Create `docker-compose.yml` in the repo root (if not already present):

```yaml
version: "3.8"
services:
  postgres:
    image: postgres:16
    container_name: freight_postgres
    restart: always
    environment:
      POSTGRES_USER: freight_user
      POSTGRES_PASSWORD: freight_pass
      POSTGRES_DB: freight_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Start the database:
```bash
docker compose up -d
```

Check it's running:
```bash
docker ps
```
You should see `freight_postgres` listed. The database is now available at `localhost:5432` with:
- User: `freight_user`
- Password: `freight_pass`
- Database: `freight_db`

To stop it later: `docker compose down` (add `-v` to also wipe stored data).

### 3. Create your `.env` file

Copy the example and fill in real values:
```bash
cp .env.example .env
```

`.env` should contain:
```
DATABASE_URL=postgresql://freight_user:freight_pass@localhost:5432/freight_db
AISSTREAM_API_KEY=your_aisstream_key_here
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### 4. Set up the backend + ML (Python)

From the repo root (not inside `backend/`):
```bash
uv venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate

uv pip install -r backend/requirements.txt -r ml/requirements.txt
```

Run the backend server (uv manages the environment, uvicorn runs the server):
```bash
uv run uvicorn backend.app.main:app --reload --port 8000
```
`uv run` automatically uses the project's virtual environment, so you don't need to manually activate it every time if you use this form.

Visit `http://localhost:8000/docs` to see the auto-generated FastAPI docs and test endpoints directly.

### 5. Set up the frontend

In a new terminal:
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` for the dashboard.

Make sure `frontend/.env` (or `frontend/.env.local`) has:
```
VITE_API_BASE_URL=http://localhost:8000
```

### 6. Train the ML model (one-time, before first use)

```bash
uv run python ml/forecasting/train.py
```
This reads `data/bdi_historical.csv`, trains the forecasting model, and saves it to `ml/forecasting/model_store/`. Re-run this whenever the historical data is updated.

---

## Running Everything Together (local dev)

You need 3 things running at once, each in its own terminal:

| Terminal | Command | Purpose |
|---|---|---|
| 1 | `docker compose up -d` | PostgreSQL (runs in background, one-time start) |
| 2 | `uv run uvicorn backend.app.main:app --reload --port 8000` | Backend + ML (same process) |
| 3 | `cd frontend && npm run dev` | Frontend dev server |

---

## Deployment

| Component | Platform | Notes |
|---|---|---|
| Frontend | Vercel | Root Directory: `frontend`. Set `VITE_API_BASE_URL` env var to the deployed backend URL. |
| Backend + ML | Render | Root Directory: leave blank (repo root) so `ml/` stays importable. Build Command: `pip install uv && uv pip install -r backend/requirements.txt -r ml/requirements.txt --system`. Start Command: `uvicorn backend.app.main:app --host 0.0.0.0 --port 10000` (uvicorn is the server that runs continuously — `uv` was only needed at build time to install packages) |
| Database | Render PostgreSQL (free tier) or Supabase | Set `DATABASE_URL` env var on Render to point to the managed database |

**CORS reminder:** add your deployed Vercel URL to `CORS_ALLOWED_ORIGINS` in the backend's environment variables on Render, or the frontend's API calls will be blocked by the browser.

**Free-tier note:** Render's free web services spin down after inactivity and take 30–50 seconds to wake up on first request. Hit the backend URL a few minutes before any live demo to warm it up.

---

## Team Workflow

1. Agree on the API contract (endpoints + request/response shape) before writing feature logic.
2. Backend dev builds `vessel_recommendation` and `freight_forecast` routers using mock data first.
3. ML dev works entirely inside `ml/forecasting/`, independent of backend, and exposes one function: `predict_rate(origin, destination, vessel_type)`.
4. Frontend dev builds against the mocked API responses in parallel, then switches to the real backend URL once ready.
5. Once core features work end-to-end, move to the arrival board, then the live map.

---

## Data Sources

| Data | Source |
|---|---|
| Historical freight rates | Baltic Exchange indices (BDI, BCI, BPI, BSI, BHSI) |
| Vessel benchmark specs | Baltic Exchange published Capesize vessel description |
| Live AIS / vessel position | aisstream.io (free WebSocket API) |
| Port infrastructure (draft, LOA, beam) | Compiled manually from port authority sites for Australia, Indonesia, Paradip, Vizag, Gangavaram |
| Commodity (coal) prices | Trading Economics free tier |