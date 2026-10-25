# ALGNITE

ALGNITE is a prototype for matching applicants with internship opportunities under the PM Internship Scheme. It explores how considering a candidate’s skills, interests, and location alongside an internship’s requirements could make placements more relevant and the allocation process easier to understand.

## The problem

The PM Internship Scheme brings together a large number of applicants and internship opportunities. Processing applications is only part of the challenge: a candidate also needs to receive an offer that suits them and that they are likely to accept and complete.

The presentation highlights several concerns:

- There can be many more applications than available internship places.
- Some candidates who accept an offer do not go on to join.
- Some interns leave before completing their internship.
- Candidates from rural areas, aspirational districts, and reserved categories may need clearer safeguards to ensure fair access.

ALGNITE explores how better matching, capacity checks, and more transparent allocation could help address these concerns.

## How ALGNITE works

The prototype brings together sample candidate and internship information, then uses it to demonstrate an allocation process:

1. **Compare candidates and internships.** The prototype considers skills, area of interest, and location when estimating how well they fit.
2. **Check available places.** Each internship has a limited capacity, so the allocation avoids assigning more candidates than there are seats.
3. **Apply reserved-seat rules.** The allocation includes a reserved pool as well as general seats.
4. **Review the results.** The dashboard shows who was allocated, who was waitlisted, and information about each internship.
5. **See the reasons for a match.** Users can inspect factors such as shared skills, sector interest, and location.
6. **Try a change.** Users can simulate a candidate declining an offer and see the allocation update.

## What the prototype demonstrates

- Candidate-to-internship matching based on skills, interests, and location
- Allocation that takes internship capacity and reserved seats into account
- A dashboard for browsing candidates, internships, and allocation results
- Explanations that help users understand why a match was made
- A waitlist that can be updated when an offer is declined
- Sample dropout-risk estimates, with factors shown for demonstration

## How the prototype differs from the presentation

The presentation describes the proposed ALGNITE system and its broader goals. This repository contains a smaller working demonstration of some of those ideas.

- **Matching approach:** The presentation proposes NLP and semantic skill matching. This prototype compares listed skills and also considers sector interest and location.
- **Allocation scale:** The presentation describes allocation for the scheme at national scale. This prototype demonstrates the process using generated sample data.
- **Fairness features:** The presentation proposes fairness safeguards for reserved categories and aspirational districts. The prototype demonstrates reserved-seat allocation; it does not implement the full range of proposed fairness checks or monitoring.
- **Risk estimates:** The presentation discusses improving acceptance and retention. The prototype includes sample dropout-risk estimates, but these are based on synthetic data and do not show real-world impact.
- **Data and deployment:** The presentation discusses using scheme data and deploying the system for wider use. This repository is a local educational prototype and is not connected to PMIS or a government service.

These differences describe the current scope of this repository; they do not change the broader ideas shown in the presentation.

## Who could benefit

- **Candidates** could have a better chance of finding internships that fit their skills and preferences.
- **Employers** could spend less time reviewing applications that do not fit their roles.
- **Scheme administrators** could review allocation results and the reasons behind them more easily.

These are intended benefits of the approach, not measured outcomes from this prototype.

## About the demo data

The project generates sample candidates and internships for demonstration. The data and dropout-risk estimates are synthetic. Results are not real PM Internship Scheme decisions, and the risk estimates must not be used to select real candidates.

## Project contents

- `frontend/` — the dashboard for viewing candidates, internships, and allocation results
- `backend/` — the service that prepares sample data, calculates matches, and returns allocation results

## Running the project

The project can be run locally for a demonstration. Start the backend first, then start the dashboard by following the setup instructions in the `backend/` and `frontend/` folders.

## Project status

ALGNITE is an educational prototype based on a proposed smart-allocation approach for the PM Internship Scheme. 
