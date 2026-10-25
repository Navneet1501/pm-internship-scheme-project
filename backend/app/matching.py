"""
The core allocation engine: skill-compatibility scoring + a capacitated,
quota-aware Gale-Shapley (deferred acceptance) matcher.

How the quota works
--------------------
Each internship's seats are split into two pools:
  - a "general" pool, open to every candidate on merit
  - a "reserved" pool, open only to candidates flagged category="reserved"
A reserved-category candidate can win a *general* seat purely on merit;
they only fall back to the reserved pool if they don't clear the general
bar. A general-category candidate can never touch a reserved seat. This
mirrors how the real reservation system already works -- we're just
automating the bookkeeping.

How risk factors in
--------------------
Candidates and internships both rank proposals by an "effective score" =
compatibility score minus a risk penalty. This is what makes the ranking
dropout-risk-aware rather than pure similarity matching: two equally
skill-matched candidates aren't treated the same if one is far more
likely to decline or drop out.
"""

from collections import deque

RISK_WEIGHT = 0.35  # how much a candidate's dropout-risk score docks their effective rank


def compatibility_score(candidate, internship) -> float:
    c_skills = set(s.strip() for s in candidate.skills.split(","))
    i_skills = set(s.strip() for s in internship.required_skills.split(","))

    overlap = len(c_skills & i_skills)
    base = overlap / len(i_skills) if i_skills else 0.0

    sector_bonus = 0.15 if candidate.sector_interest == internship.sector else 0.0
    location_bonus = 0.10 if candidate.location == internship.location else 0.0

    return round(base + sector_bonus + location_bonus, 4)


def run_allocation(candidates, internships, risk_scores: dict):
    """
    candidates: list of Candidate ORM objects
    internships: list of Internship ORM objects
    risk_scores: {candidate_id: risk_score in [0,1]}

    Returns a list of dicts, one per candidate:
      {candidate_id, internship_id, status, seat_type, compatibility_score}
    """
    cand_by_id = {c.id: c for c in candidates}
    intern_by_id = {i.id: i for i in internships}

    # seat pools
    general_cap, reserved_cap = {}, {}
    for i in internships:
        r = round(i.capacity * i.reserved_quota_pct)
        general_cap[i.id] = i.capacity - r
        reserved_cap[i.id] = r

    general_held = {i.id: [] for i in internships}   # list of (cand_id, eff_score, compat_score)
    reserved_held = {i.id: [] for i in internships}

    # precompute compatibility + effective score for every viable pair
    compat = {}
    effective = {}
    for c in candidates:
        for i in internships:
            score = compatibility_score(c, i)
            if score <= 0:
                continue  # no genuine overlap -- not a real candidate preference
            compat[(c.id, i.id)] = score
            effective[(c.id, i.id)] = round(score - RISK_WEIGHT * risk_scores.get(c.id, 0.5), 4)

    # candidate preference lists: internships sorted by effective score, best first
    prefs = {}
    for c in candidates:
        options = [i_id for (cid, i_id) in effective if cid == c.id]
        options.sort(key=lambda i_id: effective[(c.id, i_id)], reverse=True)
        prefs[c.id] = options

    pointer = {c.id: 0 for c in candidates}
    current_hold = {}  # candidate_id -> (internship_id, seat_type)

    free = deque(c.id for c in candidates if prefs[c.id])  # skip candidates with zero overlap anywhere

    while free:
        c_id = free.popleft()
        options = prefs[c_id]
        if pointer[c_id] >= len(options):
            continue  # exhausted every option -- stays unmatched

        i_id = options[pointer[c_id]]
        pointer[c_id] += 1
        eff = effective[(c_id, i_id)]
        cand = cand_by_id[c_id]
        placed = False

        # 1) try the general pool first -- merit-first, open to everyone
        pool = general_held[i_id]
        if len(pool) < general_cap[i_id]:
            pool.append((c_id, eff))
            current_hold[c_id] = (i_id, "general")
            placed = True
        else:
            weakest = min(pool, key=lambda t: t[1])
            if eff > weakest[1]:
                pool.remove(weakest)
                pool.append((c_id, eff))
                current_hold[c_id] = (i_id, "general")
                placed = True
                bumped_id = weakest[0]
                current_hold.pop(bumped_id, None)
                free.append(bumped_id)

        # 2) fall back to the reserved pool, only if eligible and still unplaced
        if not placed and cand.category == "reserved":
            rpool = reserved_held[i_id]
            if len(rpool) < reserved_cap[i_id]:
                rpool.append((c_id, eff))
                current_hold[c_id] = (i_id, "reserved")
                placed = True
            else:
                weakest_r = min(rpool, key=lambda t: t[1])
                if eff > weakest_r[1]:
                    rpool.remove(weakest_r)
                    rpool.append((c_id, eff))
                    current_hold[c_id] = (i_id, "reserved")
                    placed = True
                    bumped_id = weakest_r[0]
                    current_hold.pop(bumped_id, None)
                    free.append(bumped_id)

        if not placed:
            free.append(c_id)  # will try the next internship on its list

    # compile results
    results = []
    for c in candidates:
        hold = current_hold.get(c.id)
        if hold:
            i_id, seat_type = hold
            results.append({
                "candidate_id": c.id,
                "internship_id": i_id,
                "status": "allocated",
                "seat_type": seat_type,
                "compatibility_score": compat.get((c.id, i_id)),
            })
        else:
            results.append({
                "candidate_id": c.id,
                "internship_id": None,
                "status": "waitlisted",
                "seat_type": None,
                "compatibility_score": None,
            })
    return results
