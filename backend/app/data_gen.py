"""
Synthetic data generator.

There's no real PMIS dataset available, so this creates a realistic-looking
pool of candidates and internships to demo against. Re-run /seed to get a
fresh random batch at any time.
"""

import random
from faker import Faker
from sqlalchemy.orm import Session

from app.models import Candidate, Internship, Allocation

fake = Faker("en_IN")

SKILL_POOL = [
    "python", "excel", "communication", "sql", "data entry", "marketing",
    "graphic design", "tally", "customer service", "javascript", "content writing",
    "electrical wiring", "cad", "social media", "accounting", "java",
]

SECTORS = ["IT", "Finance", "Manufacturing", "Retail", "Healthcare", "Education"]
EDUCATION_LEVELS = ["ITI", "Diploma", "Bachelor's"]
DISTRICTS = [
    "Kanpur", "Lucknow", "Patna", "Ranchi", "Bhopal", "Jaipur",
    "Guwahati", "Raipur", "Varanasi", "Indore", "Nagpur", "Surat",
]


def _random_skills(k_range=(2, 4)):
    k = random.randint(*k_range)
    return ",".join(random.sample(SKILL_POOL, k))


def generate_candidates(n: int):
    candidates = []
    for _ in range(n):
        candidates.append(Candidate(
            name=fake.name(),
            skills=_random_skills(),
            education_level=random.choice(EDUCATION_LEVELS),
            sector_interest=random.choice(SECTORS),
            location=random.choice(DISTRICTS),
            category=random.choices(["general", "reserved"], weights=[0.5, 0.5])[0],
            is_rural=random.random() < 0.45,
            past_participation=random.random() < 0.2,
        ))
    return candidates


def generate_internships(n: int):
    internships = []
    for _ in range(n):
        internships.append(Internship(
            company_name=fake.company(),
            sector=random.choice(SECTORS),
            required_skills=_random_skills(),
            location=random.choice(DISTRICTS),
            capacity=random.randint(3, 10),
            reserved_quota_pct=0.3,
        ))
    return internships


def seed_database(db: Session, n_candidates=150, n_internships=25):
    """Wipes existing data and inserts a fresh synthetic batch."""
    db.query(Allocation).delete()
    db.query(Candidate).delete()
    db.query(Internship).delete()
    db.commit()

    candidates = generate_candidates(n_candidates)
    internships = generate_internships(n_internships)
    db.add_all(candidates)
    db.add_all(internships)
    db.commit()

    return len(candidates), len(internships)
