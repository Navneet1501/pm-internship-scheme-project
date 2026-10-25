import { useMemo, useState } from 'react'
import { Link, Route, Routes, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  ArrowUpRight, BarChart3, BriefcaseBusiness, CheckCircle2, Database,
  LayoutDashboard, Menu, PlayCircle, RefreshCw, Search, Sparkles, Users, X,
} from 'lucide-react'
import { DataProvider, useBackendData } from './context/DataContext'
import { ExplanationModal } from './components/ExplanationModal'
import type { Candidate, Internship } from './lib/api'

function App() {
  return (
    <DataProvider>
      <Workspace />
    </DataProvider>
  )
}

const nav = [
  { label: 'Overview', to: '/', icon: LayoutDashboard },
  { label: 'Candidates', to: '/candidates', icon: Users },
  { label: 'Internships', to: '/internships', icon: BriefcaseBusiness },
  { label: 'Allocations', to: '/allocations', icon: CheckCircle2 },
]

function Workspace() {
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)
  const { actionBusy, seed, allocate } = useBackendData()
  const pageTitle = nav.find(item => item.to === location.pathname)?.label || 'Overview'

  return (
    <div className="app-shell">
      <aside className={mobileOpen ? 'sidebar open' : 'sidebar'}>
        <Link className="brand" to="/"><span className="brand-mark">SA</span><span>Smart Allocation</span></Link>
        <div className="workspace-label"><span className="status-dot" /> SIH25033 prototype</div>
        <nav>
          {nav.map(item => {
            const Icon = item.icon
            return (
              <Link
                key={item.to}
                onClick={() => setMobileOpen(false)}
                className={location.pathname === item.to ? 'active' : ''}
                to={item.to}
              >
                <Icon size={18} />{item.label}
              </Link>
            )
          })}
        </nav>
        <div className="sidebar-bottom">
          <button className="logout-link" disabled={actionBusy} onClick={() => seed()}>
            <Database size={18} /> Seed sample data
          </button>
          <button className="logout-link" disabled={actionBusy} onClick={() => allocate()}>
            <PlayCircle size={18} /> Run allocation
          </button>
        </div>
      </aside>
      <button className="mobile-menu" onClick={() => setMobileOpen(!mobileOpen)} aria-label="Toggle navigation">
        {mobileOpen ? <X /> : <Menu />}
      </button>
      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">PM INTERNSHIP SCHEME / {pageTitle.toUpperCase()}</p>
            <h1>{pageTitle}</h1>
          </div>
          <div className="topbar-actions">
            <button className="button secondary" disabled={actionBusy} onClick={() => seed()}>
              <Database size={17} /> Seed data
            </button>
            <button className="button primary" disabled={actionBusy} onClick={() => allocate()}>
              <PlayCircle size={17} /> {actionBusy ? 'Working...' : 'Run allocation'}
            </button>
          </div>
        </header>
        <ActionNotice />
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/candidates" element={<CandidatesPage />} />
          <Route path="/internships" element={<InternshipsPage />} />
          <Route path="/allocations" element={<AllocationsPage />} />
          <Route path="*" element={<Overview />} />
        </Routes>
      </main>
    </div>
  )
}

function ActionNotice() {
  const { actionMessage, actionError, clearActionNotice } = useBackendData()
  if (!actionMessage && !actionError) return null
  return (
    <div className={actionError ? 'error-message notice' : 'success-message notice'}>
      <span>{actionError || actionMessage}</span>
      <button className="notice-dismiss" onClick={clearActionNotice} aria-label="Dismiss"><X size={14} /></button>
    </div>
  )
}

function EmptyState({ onSeed, busy }: { onSeed: () => void; busy: boolean }) {
  return (
    <div className="empty-page">
      <div className="empty-icon"><Database size={24} /></div>
      <h2>No data yet</h2>
      <p>This prototype has no real PMIS dataset. Seed a synthetic batch of candidates and internships to see the pipeline run end to end.</p>
      <button className="button primary" disabled={busy} onClick={onSeed}>
        <Database size={17} /> Seed sample data
      </button>
    </div>
  )
}

function Overview() {
  const { dashboard, loading, hasCandidates, hasAllocations, actionBusy, seed } = useBackendData()

  if (loading) return <div className="loading-screen">Loading dashboard...</div>
  if (!hasCandidates) return <EmptyState onSeed={seed} busy={actionBusy} />

  const metrics: [string, string | number, string][] = [
    ['TOTAL CANDIDATES', dashboard?.total_candidates ?? 0, 'In this batch'],
    ['ALLOCATED', dashboard?.allocated ?? 0, 'Holding a seat'],
    ['WAITLISTED', dashboard?.waitlisted ?? 0, 'Next in line'],
    ['DECLINED', dashboard?.declined ?? 0, 'Freed up for reallocation'],
  ]

  return (
    <motion.div className="page-stack" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
      <section className="welcome-banner">
        <div>
          <span className="badge"><span className="status-dot" /> Pipeline live</span>
          <h2>Every seat, matched with a reason.</h2>
          <p>Risk-aware, quota-compliant allocation across the current batch of candidates and internships.</p>
        </div>
        <div className="banner-orbit"><div className="orbit-ring" /><Sparkles size={27} /></div>
      </section>

      <section className="metrics-grid">
        {metrics.map(([label, value, hint]) => (
          <div className="metric" key={label}>
            <div className="metric-head"><span>{label}</span><BarChart3 size={18} /></div>
            <strong>{value}</strong>
            <small>{hint}</small>
          </div>
        ))}
      </section>

      <section className="content-grid">
        <div className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">QUOTA COMPLIANCE</p>
              <h3>Reserved seats filled vs. targeted</h3>
            </div>
            <Link className="text-link" to="/allocations">View allocations <ArrowUpRight size={16} /></Link>
          </div>
          {!hasAllocations && <p className="muted">Run allocation to see reserved-seat compliance per internship.</p>}
          {hasAllocations && (
            <table className="data-table">
              <thead>
                <tr><th>Internship</th><th>Reserved target</th><th>Reserved filled</th></tr>
              </thead>
              <tbody>
                {dashboard?.quota_compliance.map(row => (
                  <tr key={row.internship}>
                    <td>{row.internship}</td>
                    <td>{row.reserved_target}</td>
                    <td className={row.reserved_filled >= row.reserved_target ? 'quota-met' : 'quota-short'}>
                      {row.reserved_filled}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        <aside className="panel insight-panel">
          <div className="insight-icon"><Sparkles size={20} /></div>
          <p className="eyebrow">RISK-AWARE MATCHING</p>
          <h3>Average predicted dropout risk</h3>
          <p>Lower is better -- the matcher subtracts a risk penalty from compatibility before ranking candidates.</p>
          <div className="score-line"><span>Allocated candidates</span><strong>{dashboard?.avg_risk_allocated ?? '--'}</strong></div>
          <div className="score-line"><span>Waitlisted candidates</span><strong>{dashboard?.avg_risk_waitlisted ?? '--'}</strong></div>
        </aside>
      </section>
    </motion.div>
  )
}

function CandidatesPage() {
  const { candidates, loading, hasCandidates, actionBusy, seed, decline } = useBackendData()
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState<number | null>(null)

  const filtered = useMemo(() => filterCandidates(candidates, query), [candidates, query])

  if (loading) return <div className="loading-screen">Loading candidates...</div>
  if (!hasCandidates) return <EmptyState onSeed={seed} busy={actionBusy} />

  return (
    <div className="page-stack">
      <div className="explorer-intro">
        <div>
          <span className="badge">{candidates.length} candidates</span>
          <h2>Every candidate in this batch.</h2>
          <p className="muted">Click a row to see why they were (or weren't) matched, and their dropout-risk breakdown.</p>
        </div>
      </div>
      <div className="search-bar">
        <Search size={19} />
        <input value={query} onChange={event => setQuery(event.target.value)} placeholder="Search by name, skill, sector, or location" />
      </div>
      <div className="table-panel">
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th><th>Skills</th><th>Sector</th><th>Location</th>
              <th>Category</th><th>Rural</th><th>Risk score</th><th />
            </tr>
          </thead>
          <tbody>
            {filtered.map(candidate => (
              <tr key={candidate.id} className="clickable-row" onClick={() => setSelected(candidate.id)}>
                <td><strong>{candidate.name}</strong></td>
                <td className="truncate">{candidate.skills}</td>
                <td>{candidate.sector_interest}</td>
                <td>{candidate.location}</td>
                <td><span className={`status ${candidate.category === 'reserved' ? 'status-shortlisted' : ''}`}>{candidate.category}</span></td>
                <td>{candidate.is_rural ? 'Yes' : 'No'}</td>
                <td>{candidate.risk_score !== null ? candidate.risk_score.toFixed(3) : '--'}</td>
                <td onClick={event => event.stopPropagation()}>
                  <button
                    className="text-link danger"
                    disabled={actionBusy}
                    onClick={() => decline(candidate.id)}
                    title="Simulate this candidate declining their offer"
                  >
                    Decline
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {selected !== null && <ExplanationModal candidateId={selected} onClose={() => setSelected(null)} />}
    </div>
  )
}

function InternshipsPage() {
  const { internships, loading, hasCandidates, actionBusy, seed } = useBackendData()
  const [query, setQuery] = useState('')
  const filtered = useMemo(() => filterInternships(internships, query), [internships, query])

  if (loading) return <div className="loading-screen">Loading internships...</div>
  if (!hasCandidates) return <EmptyState onSeed={seed} busy={actionBusy} />

  return (
    <div className="page-stack">
      <div className="explorer-intro">
        <div>
          <span className="badge">{internships.length} internships</span>
          <h2>Every seat on offer.</h2>
          <p className="muted">Each internship's capacity is split into a general pool and a reserved pool at allocation time.</p>
        </div>
      </div>
      <div className="search-bar">
        <Search size={19} />
        <input value={query} onChange={event => setQuery(event.target.value)} placeholder="Search by company, skill, sector, or location" />
      </div>
      <div className="table-panel">
        <table className="data-table">
          <thead>
            <tr><th>Company</th><th>Sector</th><th>Required skills</th><th>Location</th><th>Capacity</th><th>Reserved quota</th></tr>
          </thead>
          <tbody>
            {filtered.map(internship => (
              <tr key={internship.id}>
                <td><strong>{internship.company_name}</strong></td>
                <td>{internship.sector}</td>
                <td className="truncate">{internship.required_skills}</td>
                <td>{internship.location}</td>
                <td>{internship.capacity}</td>
                <td>{Math.round(internship.reserved_quota_pct * 100)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function AllocationsPage() {
  const { allocations, loading, hasCandidates, hasAllocations, actionBusy, seed, allocate, decline } = useBackendData()
  const [selected, setSelected] = useState<number | null>(null)

  if (loading) return <div className="loading-screen">Loading allocations...</div>
  if (!hasCandidates) return <EmptyState onSeed={seed} busy={actionBusy} />

  return (
    <div className="page-stack">
      <div className="explorer-intro">
        <div>
          <span className="badge">{allocations.length} results</span>
          <h2>Who got which seat.</h2>
          <p className="muted">Decline an allocated candidate to watch the next-best waitlisted candidate get promoted automatically.</p>
        </div>
        {!hasAllocations && (
          <button className="button primary" disabled={actionBusy} onClick={() => allocate()}>
            <RefreshCw size={17} /> Run allocation
          </button>
        )}
      </div>
      {!hasAllocations && <p className="muted">No allocation has been run yet for this batch.</p>}
      {hasAllocations && (
        <div className="table-panel">
          <table className="data-table">
            <thead>
              <tr><th>Candidate</th><th>Internship</th><th>Status</th><th>Seat pool</th><th>Compatibility</th><th>Risk</th><th /></tr>
            </thead>
            <tbody>
              {allocations.map(row => (
                <tr key={row.candidate_id} className="clickable-row" onClick={() => setSelected(row.candidate_id)}>
                  <td><strong>{row.candidate_name}</strong></td>
                  <td>{row.company_name || '--'}</td>
                  <td><span className={`status status-${row.status}`}>{row.status}</span></td>
                  <td>{row.seat_type || '--'}</td>
                  <td>{row.compatibility_score !== null ? row.compatibility_score.toFixed(3) : '--'}</td>
                  <td>{row.risk_score !== null ? row.risk_score.toFixed(3) : '--'}</td>
                  <td onClick={event => event.stopPropagation()}>
                    {row.status === 'allocated' && (
                      <button className="text-link danger" disabled={actionBusy} onClick={() => decline(row.candidate_id)}>
                        Decline
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {selected !== null && <ExplanationModal candidateId={selected} onClose={() => setSelected(null)} />}
    </div>
  )
}

function filterCandidates(candidates: Candidate[], query: string) {
  const q = query.toLowerCase()
  if (!q) return candidates
  return candidates.filter(c => `${c.name} ${c.skills} ${c.sector_interest} ${c.location}`.toLowerCase().includes(q))
}

function filterInternships(internships: Internship[], query: string) {
  const q = query.toLowerCase()
  if (!q) return internships
  return internships.filter(i => `${i.company_name} ${i.required_skills} ${i.sector} ${i.location}`.toLowerCase().includes(q))
}

export default App
