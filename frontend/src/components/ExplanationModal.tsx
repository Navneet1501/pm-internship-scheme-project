import { useEffect, useState } from 'react'
import { X, Sparkles, ShieldAlert } from 'lucide-react'
import { getExplanation, type Explanation } from '../lib/api'

export function ExplanationModal({ candidateId, onClose }: { candidateId: number; onClose: () => void }) {
  const [data, setData] = useState<Explanation | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    getExplanation(candidateId)
      .then(result => { if (!cancelled) setData(result) })
      .catch(() => { if (!cancelled) setError('Could not load an explanation for this candidate.') })
    return () => { cancelled = true }
  }, [candidateId])

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel" onClick={event => event.stopPropagation()}>
        <button className="modal-close" aria-label="Close" onClick={onClose}><X size={18} /></button>
        {error && <p className="error-message">{error}</p>}
        {!error && !data && <p className="muted">Loading explanation...</p>}
        {data && <>
          <p className="eyebrow">CANDIDATE #{data.candidate_id}</p>
          <h2>{data.candidate_name}</h2>
          <span className={`status status-${data.match_status.replace(/\s+/g, '-')}`}>{data.match_status}</span>

          <div className="explanation-section">
            <div className="explanation-heading"><Sparkles size={17} /> Why this match</div>
            {data.matched_internship && <p className="muted">Matched internship: <strong>{data.matched_internship}</strong></p>}
            {data.match_reasons.length > 0
              ? <ul className="reason-list">{data.match_reasons.map(reason => <li key={reason}>{reason}</li>)}</ul>
              : <p className="muted">No allocation has been made for this candidate yet.</p>}
          </div>

          <div className="explanation-section">
            <div className="explanation-heading"><ShieldAlert size={17} /> Dropout-risk reasoning</div>
            {data.risk_score !== null
              ? <p className="muted">Predicted risk score: <strong>{data.risk_score.toFixed(3)}</strong></p>
              : <p className="muted">Risk has not been scored yet -- run an allocation first.</p>}
            {data.risk_reasons.length > 0 && <ul className="reason-list">{data.risk_reasons.map(reason => <li key={reason}>{reason}</li>)}</ul>}
          </div>
        </>}
      </div>
    </div>
  )
}
