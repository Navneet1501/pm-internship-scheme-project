"""Pydantic schemas -- these define the exact JSON shape the API speaks.
Agree on this shape with your frontend teammate early; it rarely needs
to change even as the logic behind it gets more sophisticated.
"""

from pydantic import BaseModel
from typing import Optional


class CandidateOut(BaseModel):
    id: int
    name: str
    skills: str
    education_level: str
    sector_interest: str
    location: str
    category: str
    is_rural: bool
    past_participation: bool
    risk_score: Optional[float] = None

    class Config:
        from_attributes = True


class InternshipOut(BaseModel):
    id: int
    company_name: str
    sector: str
    required_skills: str
    location: str
    capacity: int
    reserved_quota_pct: float

    class Config:
        from_attributes = True


class AllocationOut(BaseModel):
    candidate_id: int
    candidate_name: str
    internship_id: Optional[int]
    company_name: Optional[str]
    status: str
    seat_type: Optional[str]
    compatibility_score: Optional[float]
    risk_score: Optional[float]

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_candidates: int
    allocated: int
    waitlisted: int
    declined: int
    avg_risk_allocated: Optional[float]
    avg_risk_waitlisted: Optional[float]
    quota_compliance: list  # list of {internship, reserved_target, reserved_filled}


class ExplanationOut(BaseModel):
    candidate_id: int
    candidate_name: str
    match_status: str
    matched_internship: Optional[str]
    match_reasons: list        # why this internship (top overlapping skills etc.)
    risk_score: Optional[float]
    risk_reasons: list         # SHAP-derived top contributing factors
