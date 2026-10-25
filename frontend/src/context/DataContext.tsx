import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import {
  apiErrorMessage,
  declineCandidate,
  getAllocations,
  getCandidates,
  getDashboard,
  getInternships,
  runAllocation,
  seedDatabase,
  type Allocation,
  type Candidate,
  type DashboardStats,
  type Internship,
} from '../lib/api'

type DataContextValue = {
  dashboard: DashboardStats | null
  candidates: Candidate[]
  internships: Internship[]
  allocations: Allocation[]
  loading: boolean
  hasCandidates: boolean
  hasAllocations: boolean
  actionBusy: boolean
  actionMessage: string
  actionError: string
  refresh: () => Promise<void>
  seed: () => Promise<void>
  allocate: () => Promise<void>
  decline: (candidateId: number) => Promise<void>
  clearActionNotice: () => void
}

const DataContext = createContext<DataContextValue | undefined>(undefined)

export function DataProvider({ children }: { children: ReactNode }) {
  const [dashboard, setDashboard] = useState<DashboardStats | null>(null)
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [internships, setInternships] = useState<Internship[]>([])
  const [allocations, setAllocations] = useState<Allocation[]>([])
  const [loading, setLoading] = useState(true)
  const [actionBusy, setActionBusy] = useState(false)
  const [actionMessage, setActionMessage] = useState('')
  const [actionError, setActionError] = useState('')

  const refresh = useCallback(async () => {
    // Every read endpoint here is safe on an empty database -- they just
    // return empty lists / zeroed stats, so this never needs a "no data" guard.
    const [dashboardRes, candidatesRes, internshipsRes, allocationsRes] = await Promise.all([
      getDashboard(),
      getCandidates(),
      getInternships(),
      getAllocations(),
    ])
    setDashboard(dashboardRes)
    setCandidates(candidatesRes)
    setInternships(internshipsRes)
    setAllocations(allocationsRes)
  }, [])

  useEffect(() => {
    setLoading(true)
    refresh()
      .catch(() => setActionError('Could not reach the backend. Is uvicorn running on the configured VITE_API_URL?'))
      .finally(() => setLoading(false))
  }, [refresh])

  const clearActionNotice = useCallback(() => {
    setActionMessage('')
    setActionError('')
  }, [])

  const seed = useCallback(async () => {
    setActionBusy(true)
    clearActionNotice()
    try {
      const result = await seedDatabase(150, 25)
      await refresh()
      setActionMessage(
        `Seeded ${result.candidates_created} candidates and ${result.internships_created} internships.`,
      )
    } catch (error) {
      setActionError(apiErrorMessage(error, 'Seeding failed. Check that the backend is running.'))
    } finally {
      setActionBusy(false)
    }
  }, [refresh, clearActionNotice])

  const allocate = useCallback(async () => {
    setActionBusy(true)
    clearActionNotice()
    try {
      const result = await runAllocation()
      await refresh()
      const allocated = result.filter(r => r.status === 'allocated').length
      const waitlisted = result.filter(r => r.status === 'waitlisted').length
      setActionMessage(`Allocation complete: ${allocated} allocated, ${waitlisted} waitlisted.`)
    } catch (error) {
      setActionError(apiErrorMessage(error, 'Allocation failed. Seed the database first.'))
    } finally {
      setActionBusy(false)
    }
  }, [refresh, clearActionNotice])

  const decline = useCallback(async (candidateId: number) => {
    setActionBusy(true)
    clearActionNotice()
    try {
      await declineCandidate(candidateId)
      await refresh()
      setActionMessage('Candidate declined -- the allocation was re-solved and a waitlisted candidate may now be promoted.')
    } catch (error) {
      setActionError(apiErrorMessage(error, 'Could not decline this candidate.'))
    } finally {
      setActionBusy(false)
    }
  }, [refresh, clearActionNotice])

  const value = useMemo<DataContextValue>(() => ({
    dashboard,
    candidates,
    internships,
    allocations,
    loading,
    hasCandidates: candidates.length > 0,
    hasAllocations: allocations.length > 0,
    actionBusy,
    actionMessage,
    actionError,
    refresh,
    seed,
    allocate,
    decline,
    clearActionNotice,
  }), [dashboard, candidates, internships, allocations, loading, actionBusy, actionMessage, actionError, refresh, seed, allocate, decline, clearActionNotice])

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>
}

export function useBackendData() {
  const context = useContext(DataContext)
  if (!context) throw new Error('useBackendData must be used inside DataProvider')
  return context
}
