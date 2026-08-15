import React, { useState, useEffect } from 'react'
import ConfidenceBadge from '../components/ConfidenceBadge'

const STATUS_COLORS = {
  completed: 'var(--green-accent)',
  failed:    'var(--red)',
  queued:    'var(--text-muted)',
  processing:'var(--amber)',
  translating:'var(--amber)',
}

export default function History() {
  const [jobs, setJobs] = useState([])
  const [filterMode, setFilterMode] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    const q = new URLSearchParams()
    if (filterMode)   q.set('mode', filterMode)
    if (filterStatus) q.set('status', filterStatus)
    fetch(`/api/jobs/history?${q}`)
      .then(r => r.json())
      .then(d => { setJobs(d); setLoading(false) })
      .catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [filterMode, filterStatus])

  const fmt = (iso) => {
    if (!iso) return '—'

    const hasTimezone = /Z$|[+-]\d{2}:\d{2}$/.test(iso)
    const utcDate = new Date(hasTimezone ? iso : `${iso}Z`)

    return utcDate.toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div>
      <div className="page-header">
        <h2>Job History</h2>
        <p>All submitted translation jobs</p>
      </div>

      {/* Filters */}
      <div className="card mb-4">
        <div className="flex items-center gap-3">
          <div style={{ minWidth: 160 }}>
            <label>Mode</label>
            <select id="filter-mode" value={filterMode} onChange={e => setFilterMode(e.target.value)}>
              <option value="">All Modes</option>
              <option value="translate">Translate</option>
              <option value="reverse_bridge">Reverse Bridge</option>
            </select>
          </div>
          <div style={{ minWidth: 160 }}>
            <label>Status</label>
            <select id="filter-status" value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
              <option value="">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="queued">Queued</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div style={{ alignSelf: 'flex-end' }}>
            <button className="btn btn-secondary" onClick={load}>↻ Refresh</button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          Loading jobs…
        </div>
      ) : jobs.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          No jobs found. Submit your first translation above.
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>File</th>
                <th>Mode</th>
                <th>Languages</th>
                <th>Status</th>
                <th>Confidence</th>
                <th>Queued</th>
                <th>Completed</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map(job => (
                <tr key={job.id}>
                  <td>
                    <div className="truncate" title={job.filename}>{job.filename || '—'}</div>
                    <div className="text-small text-muted font-mono">{job.id.slice(0, 8)}…</div>
                  </td>
                  <td>
                    <span className="badge grey">
                      {job.mode === 'reverse_bridge' ? '🎙️ Farmer' : '📤 Translate'}
                    </span>
                  </td>
                  <td>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                      {Array.isArray(job.target_langs)
                        ? job.target_langs.slice(0, 3).join(', ') +
                          (job.target_langs.length > 3 ? ` +${job.target_langs.length - 3}` : '')
                        : '—'}
                    </div>
                  </td>
                  <td>
                    <span style={{ color: STATUS_COLORS[job.status] || 'var(--text)' }}>
                      ● {job.status}
                    </span>
                  </td>
                  <td>
                    <ConfidenceBadge
                      level={job.confidence_level}
                      score={job.avg_confidence}
                    />
                  </td>
                  <td className="text-small text-muted">{fmt(job.queued_at)}</td>
                  <td className="text-small text-muted">{fmt(job.completed_at)}</td>
                  <td>
                    {job.status === 'completed' && (
                      <a
                        className="btn btn-sm btn-secondary"
                        href={`/api/jobs/${job.id}/download?token=${localStorage.getItem('vaani_token')}`}
                        download
                      >
                        ⬇️ ZIP
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
