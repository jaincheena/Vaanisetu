import React, { useState, useEffect } from 'react'
import ConfidenceBadge from '../components/ConfidenceBadge'

const STATUS_COLORS = {
  completed: 'var(--green)',
  failed:    'var(--red)',
  queued:    'var(--text-muted)',
  processing:'var(--amber)',
  translating:'var(--amber)',
  generating: 'var(--accent)',
}

function formatErrorSummary(log) {
  if (!log) return 'Pipeline Error'
  if (log.includes('FFmpeg') || log.includes('extract') || log.includes('audio')) return 'Audio Extraction Error'
  if (log.includes('transcribe') || log.includes('Whisper')) return 'Speech Transcription Error'
  if (log.includes('translate') || log.includes('IndicTrans')) return 'Translation Error'
  if (log.includes('Unsupported file type')) return 'Unsupported File Format'
  if (log.includes('FileNotFound')) return 'File Not Found'
  if (log.includes('fake_tts')) return 'Mock Test Runner Note'
  const firstLine = log.split('\n')[0].replace(/^Error:\s*/i, '').trim()
  return firstLine.length > 25 ? firstLine.slice(0, 25) + '…' : firstLine
}

export default function History() {
  const [jobs, setJobs] = useState([])
  const [filterMode, setFilterMode] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [feedback, setFeedback] = useState(null)

  const load = () => {
    setLoading(true)
    const q = new URLSearchParams()
    if (filterMode)   q.set('mode', filterMode)
    if (filterStatus) q.set('status', filterStatus)
    fetch(`/api/jobs/history?${q}`)
      .then(r => r.json())
      .then(d => { setJobs(Array.isArray(d) ? d : []); setLoading(false) })
      .catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [filterMode, filterStatus])

  const handleClearTestJobs = async () => {
    if (!window.confirm('Clear synthetic test jobs and old failed runs from history?')) return
    await fetch('/api/jobs/history/clear', { method: 'DELETE' })
    setFeedback('✓ Cleaned up test jobs from history!')
    setTimeout(() => setFeedback(null), 3000)
    load()
  }

  const handleDeleteJob = async (jobId) => {
    await fetch(`/api/jobs/${jobId}`, { method: 'DELETE' })
    load()
  }

  const handleCancelJob = async (jobId) => {
    try {
      const r = await fetch(`/api/jobs/${jobId}/cancel`, { method: 'POST' })
      if (r.ok) {
        setFeedback('✓ Job stopped/cancelled!')
        setTimeout(() => setFeedback(null), 3000)
        load()
      }
    } catch (e) {
      console.error(e)
    }
  }

  const fmt = (iso) => {
    if (!iso) return '—'
    const hasTimezone = /Z$|[+-]\d{2}:\d{2}$/.test(iso)
    const utcDate = new Date(hasTimezone ? iso : `${iso}Z`)
    return utcDate.toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const filteredJobs = jobs.filter(j => {
    if (!search) return true
    const q = search.toLowerCase()
    return (
      (j.filename && j.filename.toLowerCase().includes(q)) ||
      (j.id && j.id.toLowerCase().includes(q)) ||
      (j.source_lang && j.source_lang.toLowerCase().includes(q)) ||
      (Array.isArray(j.target_langs) && j.target_langs.some(l => l.toLowerCase().includes(q)))
    )
  })

  return (
    <div>
      <div className="page-header flex items-center justify-between">
        <div>
          <h2>History & Audit Trail <span style={{ color: '#D97706', fontSize: 18, fontWeight: 700 }}>(इतिहास और ऑडिट)</span></h2>
          <p>Complete audit log of all agricultural video, voice, and advisory localization jobs across BAIF state blocks</p>
        </div>
        <div className="flex gap-2">
          <button className="btn btn-secondary" onClick={handleClearTestJobs}>
            🧹 Purge Test Runs
          </button>
        </div>
      </div>

      {feedback && (
        <div className="card mb-4" style={{ background: 'rgba(82, 196, 135, 0.12)', borderColor: 'var(--green)', color: 'var(--green)', padding: '12px 16px', fontSize: 13, fontWeight: 500 }}>
          {feedback}
        </div>
      )}

      {/* ── Modern Search & Filter Hub (Dark Theme) ── */}
      <div className="card mb-6" style={{ padding: '22px 26px', background: '#111C30', borderRadius: 16 }}>
        {/* Search Input Bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 18 }}>
          <div style={{
            position: 'relative',
            flex: 1,
            display: 'flex',
            alignItems: 'center'
          }}>
            <span style={{
              position: 'absolute',
              left: 14,
              fontSize: 16,
              color: '#94A3B8',
              pointerEvents: 'none'
            }}>
              🔍
            </span>
            <input
              type="text"
              className="text-input"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search by filename, language, Marathi/Hindi script, or job ID…"
              style={{
                paddingLeft: 42,
                paddingRight: search ? 36 : 14,
                fontSize: 14,
                borderRadius: 10
              }}
            />
            {search && (
              <button
                type="button"
                onClick={() => setSearch('')}
                style={{
                  position: 'absolute',
                  right: 12,
                  background: 'none',
                  border: 'none',
                  color: '#94A3B8',
                  cursor: 'pointer',
                  fontSize: 14
                }}
              >
                ✕
              </button>
            )}
          </div>

          <button
            className="btn btn-secondary"
            onClick={load}
            type="button"
            style={{ fontSize: 13.5, padding: '10px 18px', borderRadius: 10 }}
          >
            ↻ Refresh
          </button>
        </div>

        {/* Filter Controls Row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 14, paddingTop: 14, borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
          {/* Mode Segmented Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 11.5, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.4px' }}>
              Mode:
            </span>
            {[
              { key: '', label: 'All Modes' },
              { key: 'translate', label: '📤 Advisory Translation' },
              { key: 'reverse_bridge', label: '🎙️ Farmer Voice' },
            ].map(m => {
              const isSelected = filterMode === m.key
              return (
                <button
                  key={m.key}
                  type="button"
                  onClick={() => setFilterMode(m.key)}
                  style={{
                    padding: '6px 14px',
                    borderRadius: 20,
                    fontSize: 12.5,
                    fontWeight: isSelected ? 700 : 500,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    border: `1.5px solid ${isSelected ? '#F59E0B' : 'rgba(255, 255, 255, 0.1)'}`,
                    background: isSelected ? 'rgba(245, 158, 11, 0.25)' : '#0B1120',
                    color: isSelected ? '#FBBF24' : '#94A3B8',
                    boxShadow: isSelected ? '0 2px 10px rgba(245, 158, 11, 0.25)' : 'none'
                  }}
                >
                  {m.label}
                </button>
              )
            })}
          </div>

          {/* Status Segmented Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 11.5, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.4px' }}>
              Status:
            </span>
            {[
              { key: '', label: 'All Statuses' },
              { key: 'completed', label: '● Completed', color: '#34D399', bg: 'rgba(16, 185, 129, 0.25)' },
              { key: 'queued', label: '● Queued', color: '#FBBF24', bg: 'rgba(245, 158, 11, 0.25)' },
              { key: 'failed', label: '● Failed', color: '#F87171', bg: 'rgba(239, 68, 68, 0.25)' },
            ].map(s => {
              const isSelected = filterStatus === s.key
              const activeColor = s.color || '#FBBF24'
              const activeBg = s.bg || 'rgba(245, 158, 11, 0.25)'
              return (
                <button
                  key={s.key}
                  type="button"
                  onClick={() => setFilterStatus(s.key)}
                  style={{
                    padding: '6px 14px',
                    borderRadius: 20,
                    fontSize: 12.5,
                    fontWeight: isSelected ? 700 : 500,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    border: `1.5px solid ${isSelected ? activeColor : 'rgba(255, 255, 255, 0.1)'}`,
                    background: isSelected ? activeBg : '#0B1120',
                    color: isSelected ? activeColor : '#94A3B8',
                    boxShadow: isSelected ? `0 2px 10px ${activeColor}35` : 'none'
                  }}
                >
                  {s.label}
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          Loading jobs…
        </div>
      ) : filteredJobs.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          No jobs found matching your filters.
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Advisory / File</th>
                <th>Mode</th>
                <th>Language Routing</th>
                <th>Status</th>
                <th>Confidence</th>
                <th>Queued At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredJobs.map(job => (
                <tr key={job.id}>
                  <td>
                    <div style={{ fontWeight: 600, color: 'var(--text)', fontSize: 13 }}>
                      {job.filename ? (
                        job.filename.endsWith('.mp4') ? '🎬 ' + job.filename :
                        job.filename.endsWith('.mp3') || job.filename.endsWith('.wav') ? '🎙️ ' + job.filename :
                        '📄 ' + job.filename
                      ) : '🌱 Advisory Text'}
                    </div>
                    <div className="text-small text-muted font-mono">{job.id.slice(0, 8)}…</div>
                  </td>
                  <td>
                    <span className={`badge ${job.mode === 'reverse_bridge' ? 'amber' : 'grey'}`}>
                      {job.mode === 'reverse_bridge' ? '🎙️ Field Query' : '📤 Broadcast'}
                    </span>
                  </td>
                  <td>
                    <div style={{ fontSize: 12, fontWeight: 500, color: 'var(--text)' }}>
                      <span style={{ color: 'var(--text-muted)' }}>{job.source_lang || 'Source'}</span>
                      <span style={{ margin: '0 4px', color: 'var(--accent)' }}>➔</span>
                      {Array.isArray(job.target_langs) ? job.target_langs.join(', ') : '—'}
                    </div>
                  </td>
                  <td>
                    <span
                      style={{ color: STATUS_COLORS[job.status] || 'var(--text)', fontWeight: 600, fontSize: 12, cursor: job.error_log ? 'help' : 'default' }}
                      title={job.error_log || ''}
                    >
                      ● {job.status.toUpperCase()}
                    </span>
                    {job.status === 'failed' && job.error_log && (
                      <div
                        className="text-small"
                        style={{ color: 'var(--red)', fontSize: 11, marginTop: 2, maxWidth: 160, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}
                        title={`Full Error Log:\n${job.error_log}`}
                      >
                        ⚠️ {formatErrorSummary(job.error_log)}
                      </div>
                    )}
                  </td>
                  <td>
                    {job.status === 'completed' && job.avg_confidence != null ? (
                      <ConfidenceBadge
                        level={job.confidence_level || (job.avg_confidence >= 0.85 ? 'green' : 'amber')}
                        score={job.avg_confidence}
                      />
                    ) : (
                      <span className="text-small text-muted" style={{ fontSize: 12 }}>
                        {job.status === 'completed' ? '—' : job.status === 'failed' ? 'N/A' : '⏳ Pending'}
                      </span>
                    )}
                  </td>
                  <td className="text-small text-muted">{fmt(job.queued_at)}</td>
                  <td>
                    <div className="flex gap-2" style={{ alignItems: 'center' }}>
                      {!['completed', 'failed', 'cancelled'].includes(job.status) && (
                        <button
                          className="btn btn-sm btn-secondary"
                          style={{ color: 'var(--red)', borderColor: 'var(--red)', padding: '3px 8px', fontSize: 11, fontWeight: 600 }}
                          onClick={() => handleCancelJob(job.id)}
                          title="Stop ongoing job"
                        >
                          🛑 Stop
                        </button>
                      )}
                      {job.status === 'completed' && (
                        <a
                          className="btn btn-sm btn-secondary"
                          href={`/api/jobs/${job.id}/download${localStorage.getItem('vaani_token') ? `?token=${localStorage.getItem('vaani_token')}` : ''}`}
                          download
                          title="Download ZIP Package"
                        >
                          ⬇️ ZIP
                        </a>
                      )}
                      <button
                        className="btn btn-sm btn-secondary"
                        style={{ color: 'var(--red)', padding: '3px 8px' }}
                        onClick={() => handleDeleteJob(job.id)}
                        title="Delete from history"
                      >
                        🗑️
                      </button>
                    </div>
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
