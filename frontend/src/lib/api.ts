import axios from 'axios'

// This points at the SIH25033 FastAPI backend (see app/main.py).
// Run the backend with: uvicorn app.main:app --reload  (defaults to :8000)
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  headers: { 'Content-Type': 'application/json' },
})

// ---- Types mirroring app/schemas.py exactly -------------------------------

export type Candidate = {
  id: number
  name: string
  skills: string
  education_level: string
  sector_interest: string
  location: string
  category: 'general' | 'reserved'
  is_rural: boolean
  past_participation: boolean
  risk_score: number | null
}

export type Internship = {
  id: number
  company_name: string
  sector: string
  required_skills: string
  location: string
  capacity: number
  reserved_quota_pct: number
}

export type AllocationStatus = 'allocated' | 'waitlisted' | 'declined'

export type Allocation = {
  candidate_id: number
  candidate_name: string
  internship_id: number | null
  company_name: string | null
  status: AllocationStatus
  seat_type: 'general' | 'reserved' | null
  compatibility_score: number | null
  risk_score: number | null
}

export type QuotaRow = {
  internship: string
  reserved_target: number
  reserved_filled: number
}

export type DashboardStats = {
  total_candidates: number
  allocated: number
  waitlisted: number
  declined: number
  avg_risk_allocated: number | null
  avg_risk_waitlisted: number | null
  quota_compliance: QuotaRow[]
}

export type Explanation = {
  candidate_id: number
  candidate_name: string
  match_status: string
  matched_internship: string | null
  match_reasons: string[]
  risk_score: number | null
  risk_reasons: string[]
}

// ---- Calls mirroring app/main.py endpoints exactly ------------------------

export async function seedDatabase(nCandidates = 150, nInternships = 25) {
  const response = await api.post<{ candidates_created: number; internships_created: number }>(
    '/seed',
    null,
    { params: { n_candidates: nCandidates, n_internships: nInternships } },
  )
  return response.data
}

export async function getCandidates() {
  const response = await api.get<Candidate[]>('/candidates')
  return response.data
}

export async function getInternships() {
  const response = await api.get<Internship[]>('/internships')
  return response.data
}

export async function runAllocation() {
  const response = await api.post<Allocation[]>('/allocate')
  return response.data
}

export async function getAllocations() {
  const response = await api.get<Allocation[]>('/allocations')
  return response.data
}

export async function declineCandidate(candidateId: number) {
  const response = await api.post<Allocation[]>(`/candidates/${candidateId}/decline`)
  return response.data
}

export async function getExplanation(candidateId: number) {
  const response = await api.get<Explanation>(`/candidates/${candidateId}/explanation`)
  return response.data
}

export async function getDashboard() {
  const response = await api.get<DashboardStats>('/dashboard')
  return response.data
}

// Best-effort extraction of FastAPI's error detail, so the UI can show
// "No data yet -- call POST /seed first." instead of a generic failure.
export function apiErrorMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
  }
  return fallback
}
