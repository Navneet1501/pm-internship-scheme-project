"""
SQLAlchemy ORM models: Candidate, Internship, Allocation.

Skills are stored as a comma-separated string to keep the prototype
schema simple (no separate join table) -- fine for a hackathon build,
easy to normalize into a proper many-to-many table later if needed.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    skills = Column(String, nullable=False)          # "python,sql,excel"
    education_level = Column(String, nullable=False)  # "Diploma" / "ITI" / "Bachelor's"
    sector_interest = Column(String, nullable=False)  # "IT" / "Finance" / "Manufacturing" ...
    location = Column(String, nullable=False)          # home district
    category = Column(String, nullable=False)          # "general" or "reserved"
    is_rural = Column(Boolean, default=False)
    past_participation = Column(Boolean, default=False)  # took part in a scheme before

    # filled in once the risk model has run
    risk_score = Column(Float, nullable=True)

    allocations = relationship("Allocation", back_populates="candidate")


class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    required_skills = Column(String, nullable=False)
    location = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    reserved_quota_pct = Column(Float, default=0.3)  # fraction of seats reserved

    allocations = relationship("Allocation", back_populates="internship")


class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    internship_id = Column(Integer, ForeignKey("internships.id"), nullable=True)  # null if unallocated
    status = Column(String, nullable=False)   # "allocated" | "waitlisted" | "declined"
    seat_type = Column(String, nullable=True)  # "general" | "reserved"
    compatibility_score = Column(Float, nullable=True)

    candidate = relationship("Candidate", back_populates="allocations")
    internship = relationship("Internship", back_populates="allocations")
