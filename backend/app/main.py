"""
SIH25033 -- AI-Based Smart Allocation Engine for PM Internship Scheme
Prototype backend.

Run with:  uvicorn app.main:app --reload
Docs at:   http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app import models, schemas
from app.data_gen import seed_database
from app.matching import run_allocation, compatibility_score
from app.risk_model import RiskModel

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SIH25033 Smart Allocation Engine (prototype)")

# Without this, calls from your React dev server (localhost:5173/3000) will
# silently fail. Tighten allow_origins before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trained once at startup, reused for every request -- this is what makes
# /allocate and /explanation fast.
risk_model = RiskModel()


@app.post("/seed")
def seed(n_candidates: int = 150, n_internships: int = 25, db: Session = Depends(get_db)):
    """Wipes existing data and generates a fresh synthetic batch to demo against."""
    n_c, n_i = seed_database(db, n_candidates, n_internships)
    return {"candidates_created": n_c, "internships_created": n_i}


@app.get("/candidates", response_model=list[schemas.CandidateOut])
def list_candidates(db: Session = Depends(get_db)):
    return db.query(models.Candidate).all()


@app.get("/internships", response_model=list[schemas.InternshipOut])
def list_internships(db: Session = Depends(get_db)):
    return db.query(models.Internship).all()


@app.post("/allocate", response_model=list[schemas.AllocationOut])
def allocate(db: Session = Depends(get_db)):
    """
    Runs the full pipeline: score every candidate's dropout risk, run the
    quota-aware matcher, and persist the results. Safe to call again after
    a /decline -- it re-solves from scratch over whoever is still active,
    which is what gives you correct, stable reallocation rather than an
    ad-hoc patch.
    """
    candidates = db.query(models.Candidate).all()
    internships = db.query(models.Internship).all()
    if not candidates or not internships:
        raise HTTPException(400, "No data yet -- call POST /seed first.")

    declined_ids = {
        a.candidate_id for a in db.query(models.Allocation)
        .filter(models.Allocation.status == "declined").all()
    }
    active_candidates = [c for c in candidates if c.id not in declined_ids]

    # score (and persist) dropout risk for every active candidate
    risk_scores = {}
    for c in active_candidates:
        score = risk_model.score(c)
        c.risk_score = score
        risk_scores[c.id] = score
    db.commit()

    results = run_allocation(active_candidates, internships, risk_scores)

    # wipe previous non-declined allocation rows, then insert the fresh result
    db.query(models.Allocation).filter(models.Allocation.status != "declined").delete()
    db.commit()

    out = []
    cand_by_id = {c.id: c for c in candidates}
    intern_by_id = {i.id: i for i in internships}

    # keep declined candidates visible in the response too, so a caller
    # can see the full picture after a /decline, not just the re-solved rest
    for prior in db.query(models.Allocation).filter(models.Allocation.status == "declined").all():
        cand = cand_by_id[prior.candidate_id]
        out.append(schemas.AllocationOut(
            candidate_id=cand.id, candidate_name=cand.name,
            internship_id=None, company_name=None,
            status="declined", seat_type=None,
            compatibility_score=None, risk_score=cand.risk_score,
        ))

    for r in results:
        row = models.Allocation(
            candidate_id=r["candidate_id"],
            internship_id=r["internship_id"],
            status=r["status"],
            seat_type=r["seat_type"],
            compatibility_score=r["compatibility_score"],
        )
        db.add(row)
        cand = cand_by_id[r["candidate_id"]]
        intern = intern_by_id.get(r["internship_id"]) if r["internship_id"] else None
        out.append(schemas.AllocationOut(
            candidate_id=cand.id, candidate_name=cand.name,
            internship_id=intern.id if intern else None,
            company_name=intern.company_name if intern else None,
            status=r["status"], seat_type=r["seat_type"],
            compatibility_score=r["compatibility_score"],
            risk_score=risk_scores.get(cand.id),
        ))
    db.commit()
    return out


@app.get("/allocations", response_model=list[schemas.AllocationOut])
def list_allocations(db: Session = Depends(get_db)):
    rows = db.query(models.Allocation).all()
    out = []
    for r in rows:
        out.append(schemas.AllocationOut(
            candidate_id=r.candidate.id, candidate_name=r.candidate.name,
            internship_id=r.internship.id if r.internship else None,
            company_name=r.internship.company_name if r.internship else None,
            status=r.status, seat_type=r.seat_type,
            compatibility_score=r.compatibility_score,
            risk_score=r.candidate.risk_score,
        ))
    return out


@app.post("/candidates/{candidate_id}/decline")
def decline(candidate_id: int, db: Session = Depends(get_db)):
    """
    Simulates a candidate declining their offer. Marks them declined and
    re-runs /allocate over everyone else -- watch a waitlisted candidate
    get promoted into the freed seat. This is the "dynamic reallocation"
    behaviour live, not just a slide claim.
    """
    alloc = db.query(models.Allocation).filter(
        models.Allocation.candidate_id == candidate_id,
        models.Allocation.status == "allocated",
    ).first()
    if not alloc:
        raise HTTPException(404, "No active allocation for this candidate to decline.")

    alloc.status = "declined"
    db.commit()

    return allocate(db)  # re-solve and return the fresh allocation set


@app.get("/candidates/{candidate_id}/explanation", response_model=schemas.ExplanationOut)
def explain(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(404, "Candidate not found.")

    alloc = db.query(models.Allocation).filter(
        models.Allocation.candidate_id == candidate_id
    ).first()

    match_reasons = []
    matched_internship_name = None
    if alloc and alloc.internship_id:
        intern = db.query(models.Internship).filter(models.Internship.id == alloc.internship_id).first()
        matched_internship_name = intern.company_name
        c_skills = set(s.strip() for s in candidate.skills.split(","))
        i_skills = set(s.strip() for s in intern.required_skills.split(","))
        shared = c_skills & i_skills
        if shared:
            match_reasons.append(f"Shared skills: {', '.join(shared)}")
        if candidate.sector_interest == intern.sector:
            match_reasons.append(f"Sector interest matches ({intern.sector})")
        if candidate.location == intern.location:
            match_reasons.append(f"Same location ({intern.location})")
        match_reasons.append(f"Compatibility score: {alloc.compatibility_score}")
        if alloc.seat_type:
            match_reasons.append(f"Placed via {alloc.seat_type} seat pool")

    risk_reasons = risk_model.explain(candidate)

    return schemas.ExplanationOut(
        candidate_id=candidate.id,
        candidate_name=candidate.name,
        match_status=alloc.status if alloc else "not yet allocated",
        matched_internship=matched_internship_name,
        match_reasons=match_reasons,
        risk_score=candidate.risk_score,
        risk_reasons=risk_reasons,
    )


@app.get("/dashboard", response_model=schemas.DashboardStats)
def dashboard(db: Session = Depends(get_db)):
    allocations = db.query(models.Allocation).all()
    total = db.query(models.Candidate).count()
    allocated = [a for a in allocations if a.status == "allocated"]
    waitlisted = [a for a in allocations if a.status == "waitlisted"]
    declined = [a for a in allocations if a.status == "declined"]

    def avg_risk(rows):
        scores = [r.candidate.risk_score for r in rows if r.candidate.risk_score is not None]
        return round(sum(scores) / len(scores), 3) if scores else None

    quota_rows = []
    for intern in db.query(models.Internship).all():
        reserved_target = round(intern.capacity * intern.reserved_quota_pct)
        reserved_filled = len([
            a for a in allocated
            if a.internship_id == intern.id and a.seat_type == "reserved"
        ])
        quota_rows.append({
            "internship": intern.company_name,
            "reserved_target": reserved_target,
            "reserved_filled": reserved_filled,
        })

    return schemas.DashboardStats(
        total_candidates=total,
        allocated=len(allocated),
        waitlisted=len(waitlisted),
        declined=len(declined),
        avg_risk_allocated=avg_risk(allocated),
        avg_risk_waitlisted=avg_risk(waitlisted),
        quota_compliance=quota_rows,
    )
