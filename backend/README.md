# SIH25033 — Smart Allocation Engine (backend prototype)

FastAPI + SQLite (via SQLAlchemy) + XGBoost + SHAP. Implements the pipeline
from your Technical Approach slide: skill compatibility → dropout-risk
scoring → quota-aware Gale-Shapley allocation → explainability.

## Setup

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs — FastAPI's auto-generated Swagger UI.
You can test every endpoint from there with no frontend needed.

## Demo flow (this is your viva script)

1. **POST /seed** — generates 150 synthetic candidates and 25 internships.
   Re-run any time for a fresh batch.
2. **POST /allocate** — scores every candidate's dropout risk, runs the
   quota-aware matcher, returns the full allocation list.
3. **GET /dashboard** — allocated / waitlisted counts, average risk in
   each group, and reserved-quota compliance per internship.
4. **GET /candidates/{id}/explanation** — pick any candidate ID from the
   /allocate response. Returns *why* they got that match (shared skills,
   sector/location fit) and *why* their risk score is what it is (SHAP,
   in plain language).
5. **POST /candidates/{id}/decline** — pick an *allocated* candidate ID.
   This is the standout demo moment: it marks them declined and
   re-solves the whole allocation, so you can show a waitlisted
   candidate getting promoted into the freed seat live. Check
   /dashboard before and after to see the numbers move.

## What's real vs. what's simulated

- The **matching algorithm and quota logic are real** — this is an actual
  capacitated, quota-respecting Gale-Shapley implementation, not a mock.
- The **dropout-risk model is trained on synthetic labels** (correlated
  with rurality, past participation, education, category, plus noise),
  because no real PMIS historical outcome data exists yet. Swap
  `generate_training_data()` in `app/risk_model.py` for a real query the
  moment real data is available — nothing downstream changes.
- **Skill compatibility** is overlap-based (shared skills ÷ required
  skills, plus sector/location bonuses) — simple on purpose, upgradeable
  to embeddings/TF-IDF later without touching the matching logic itself.

## Project layout

```
app/
  main.py         FastAPI app + all endpoints
  database.py     SQLAlchemy engine/session (SQLite; swap URL for Postgres)
  models.py       ORM models: Candidate, Internship, Allocation
  schemas.py      Pydantic response shapes (the API's JSON contract)
  data_gen.py     Synthetic candidate/internship generator (Faker)
  risk_model.py   XGBoost dropout-risk model + SHAP explainer
  matching.py     The core allocation engine (Gale-Shapley + quotas)
```

## Switching to PostgreSQL later

Change one line in `app/database.py`:

```python
DATABASE_URL = "postgresql://user:password@localhost/sih25033"
```

Everything else — models, schemas, endpoints — stays identical, because
none of it talks to SQLite directly; it all goes through SQLAlchemy.

## Connecting your React frontend

CORS is already open (`allow_origins=["*"]`) so your dev server can call
this directly. Point Axios/fetch at `http://127.0.0.1:8000` and the five
endpoints above are everything the dashboard needs.
