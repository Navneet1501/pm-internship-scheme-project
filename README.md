# PM Internship Scheme — Smart Allocation Engine

A prototype allocation engine and dashboard for the PM Internship Scheme. It pairs candidates with internship opportunities using skill compatibility and a quota-aware matching algorithm, then adds dropout-risk estimates and explanations to make demo decisions easier to inspect.

## What it does

- Generates synthetic candidate and internship data for demos.
- Scores candidate dropout risk with an XGBoost model trained on synthetic labels.
- Allocates candidates with a quota-aware Gale–Shapley matching algorithm.
- Exposes allocation, dashboard, and candidate explanation endpoints through FastAPI.
- Provides a React, TypeScript, and Vite dashboard for exploring candidates, internships, allocations, and explanations.
- Re-runs allocation when an accepted candidate declines, so a waitlisted candidate can be promoted.

## Project structure

```text
backend/   FastAPI API, matching engine, risk model, and SQLite persistence
frontend/  React + TypeScript dashboard
```

## Run locally

You need Python 3.10+ and Node.js with npm.

### 1. Start the API

In one terminal:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Interactive API documentation is at `http://127.0.0.1:8000/docs`.

### 2. Start the dashboard

In another terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`. The frontend API client defaults to `http://127.0.0.1:8000`; copy `frontend/.env.example` to `frontend/.env.local` to override `VITE_API_URL`.

## Demo workflow

1. Call `POST /seed` to create a fresh synthetic dataset (150 candidates and 25 internships by default).
2. Call `POST /allocate` to calculate risk scores and generate allocations and waitlists.
3. Use `GET /dashboard` and `GET /candidates/{id}/explanation` to inspect results.
4. Call `POST /candidates/{id}/decline` for an allocated candidate to see the system re-run allocation.

The same endpoints are available in the dashboard where implemented.

## Data and prototype notes

All candidate, internship, and training-label data is synthetic. The dropout-risk estimates are for demonstration only and should not be used to make real selection decisions. The backend currently enables permissive CORS for local development; review and restrict it before deployment. This repository is a prototype and has not been reviewed for production use.

## License

No license has been selected yet. Until a license is added, the source remains subject to default copyright restrictions.
