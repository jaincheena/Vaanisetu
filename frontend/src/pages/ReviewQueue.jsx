import React, { useState, useEffect } from 'react'
import ConfidenceBadge from '../components/ConfidenceBadge'

export default function ReviewQueue() {
  const [items, setItems] = useState([])
  const [stats, setStats] = useState(null)
  const [reviewer, setReviewer] = useState('')
  const [editStates, setEditStates] = useState({})
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('pending')

  const [feedback, setFeedback] = useState(null)

  const load = () => {
    setLoading(true)
    Promise.all([
      fetch(`/api/review/queue?status=${statusFilter}`).then(r => r.json()),
      fetch('/api/review/stats').then(r => r.json()),
    ]).then(([q, s]) => {
      setItems(Array.isArray(q) ? q : [])
      setStats(s)
      setLoading(false)
    }).catch(() => setLoading(false))
  }

  useEffect(load, [statusFilter])

  const action = async (id, act, editedText) => {
    try {
      const res = await fetch(`/api/review/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: act, edited_text: editedText, reviewer: reviewer || 'BAIF Field Officer' }),
      })
      const data = await res.json()
      if (data.success) {
        setFeedback(`✓ Segment successfully ${act === 'approve' ? 'approved' : act === 'edit' ? 'edited & approved' : 'rejected'} and stored in Translation Memory!`)
        setTimeout(() => setFeedback(null), 4000)
      }
    } catch (e) {
      console.error(e)
    }
    load()
  }

  const handleClearTest = async () => {
    await fetch('/api/review/clear-all', { method: 'DELETE' })
    setFeedback('✓ Cleaned up test items from review queue!')
    setTimeout(() => setFeedback(null), 3000)
    load()
  }

  const setEdit = (id, val) =>
    setEditStates(s => ({ ...s, [id]: val }))

  const getEdit = (id, fallback) =>
    editStates[id] !== undefined ? editStates[id] : fallback

  return (
    <div>
      <div className="page-header flex items-center justify-between">
        <div>
          <h2>Review & Verification Queue <span style={{ color: '#D97706', fontSize: 18, fontWeight: 700 }}>(सत्यापन कतार)</span></h2>
          <p>Confidence Gate: Agronomist verification queue ensuring 100% precision on chemical dosages and technical terms</p>
        </div>
        {stats && (
          <div className="flex gap-2">
            <span className="badge amber">{stats.pending} pending</span>
            <span className="badge green">{stats.approved} approved</span>
            <span className="badge grey">{stats.rejected} rejected</span>
          </div>
        )}
      </div>

      {feedback && (
        <div className="card mb-4" style={{ background: 'rgba(82, 196, 135, 0.12)', borderColor: 'var(--green)', color: 'var(--green)', padding: '12px 16px', fontSize: 13, fontWeight: 500 }}>
          {feedback}
        </div>
      )}

      {/* ── Modern Reviewer Signature & Filter Toolbar (Dark Theme) ── */}
      <div className="card mb-6" style={{ padding: '20px 24px', background: '#111C30', borderRadius: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16, marginBottom: 18 }}>
          {/* Reviewer Signature Field */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flex: 1, minWidth: 280 }}>
            <div style={{
              width: 40,
              height: 40,
              borderRadius: 10,
              background: 'rgba(245, 158, 11, 0.2)',
              color: '#FBBF24',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 20,
              flexShrink: 0
            }}>
              👨‍🔬
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', letterSpacing: '0.5px', textTransform: 'uppercase', marginBottom: 4 }}>
                Reviewer Signature & Identity
              </label>
              <input
                className="text-input"
                id="reviewer-name"
                type="text"
                value={reviewer}
                onChange={e => setReviewer(e.target.value)}
                placeholder="e.g. Dr. Patil (BAIF Pune HQ Agronomist)"
                style={{ padding: '8px 12px', fontSize: 13.5, fontWeight: 600 }}
              />
            </div>
          </div>

          {/* Action Tools */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <button
              className="btn btn-secondary"
              onClick={load}
              type="button"
              style={{ fontSize: 13, padding: '8px 16px', borderRadius: 8 }}
            >
              ↻ Refresh
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleClearTest}
              type="button"
              title="Purge legacy test entries"
              style={{ fontSize: 13, padding: '8px 16px', borderRadius: 8 }}
            >
              🧹 Clean Stale Items
            </button>
          </div>
        </div>

        {/* Segmented Status Filter Tabs */}
        <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: 16 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>
            Filter by Verification Status:
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {[
              { key: 'pending', label: '⏳ Pending', count: stats?.pending || 0, color: '#FBBF24', bg: 'rgba(245, 158, 11, 0.25)' },
              { key: 'approved', label: '✓ Approved', count: stats?.approved || 0, color: '#34D399', bg: 'rgba(16, 185, 129, 0.25)' },
              { key: 'edited', label: '✏️ Edited', count: stats?.edited || 0, color: '#A5B4FC', bg: 'rgba(99, 102, 241, 0.25)' },
              { key: 'rejected', label: '✗ Rejected', count: stats?.rejected || 0, color: '#F87171', bg: 'rgba(239, 68, 68, 0.25)' },
              { key: 'all', label: '📋 All Items', count: stats?.total || 0, color: '#CBD5E1', bg: 'rgba(255, 255, 255, 0.1)' },
            ].map(tab => {
              const isSelected = statusFilter === tab.key
              return (
                <button
                  key={tab.key}
                  type="button"
                  onClick={() => setStatusFilter(tab.key)}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 8,
                    padding: '8px 16px',
                    borderRadius: 20,
                    fontSize: 13,
                    fontWeight: isSelected ? 700 : 600,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    border: `1.5px solid ${isSelected ? tab.color : 'rgba(255, 255, 255, 0.1)'}`,
                    background: isSelected ? tab.bg : '#0B1120',
                    color: isSelected ? tab.color : '#94A3B8',
                    boxShadow: isSelected ? `0 2px 10px ${tab.color}35` : 'none'
                  }}
                >
                  <span>{tab.label}</span>
                  <span style={{
                    fontSize: 11,
                    fontWeight: 800,
                    padding: '2px 7px',
                    borderRadius: 12,
                    background: isSelected ? 'rgba(0, 0, 0, 0.4)' : 'rgba(255, 255, 255, 0.08)',
                    color: isSelected ? tab.color : '#94A3B8'
                  }}>
                    {tab.count}
                  </span>
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          Loading…
        </div>
      ) : items.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          {statusFilter === 'pending' ? '✅ No pending reviews — all clear!' : 'No items found.'}
        </div>
      ) : (
        <div>
          {items.map(item => {
            const editVal = getEdit(item.id, item.translated_text)
            const isEditing = editStates[item.id] !== undefined

            return (
              <div className="card mb-4" key={item.id}>
                {/* Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-small text-muted font-mono">
                      Job {item.job_id.slice(0, 8)}… · Seg #{item.segment_index}
                    </span>
                    <span className="badge grey">
                      {item.source_lang} → {item.target_lang}
                    </span>
                  </div>
                  <ConfidenceBadge level={item.confidence < 0.65 ? 'red' : 'amber'} score={item.confidence} />
                </div>

                {/* Bilingual panes */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', background: 'var(--bg-input)', padding: '16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)' }}>
                  <div>
                    <div className="section-label" style={{ marginBottom: 8 }}>Source ({item.source_lang})</div>
                    <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>{item.source_text}</p>
                  </div>
                  <div>
                    <div className="section-label" style={{ marginBottom: 8 }}>Translation ({item.target_lang})</div>
                    {item.status === 'pending' ? (
                      <textarea
                        className="text-input"
                        id={`edit-${item.id}`}
                        value={editVal}
                        onChange={e => setEdit(item.id, e.target.value)}
                        rows={3}
                        style={{ marginBottom: 0 }}
                      />
                    ) : (
                      <p style={{ fontSize: 13, color: 'var(--text)' }}>{item.edited_translation || item.translated_text}</p>
                    )}
                  </div>
                </div>

                {/* Actions */}
                {item.status === 'pending' && (
                  <div className="flex gap-2 mt-2">
                    <button
                      className="btn btn-sm btn-primary"
                      onClick={() => action(item.id, editVal !== item.translated_text ? 'edit' : 'approve', editVal)}
                      id={`btn-approve-${item.id}`}
                    >
                      {editVal !== item.translated_text ? '✏️ Save Edit' : '✓ Approve'}
                    </button>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => action(item.id, 'reject', null)}
                      id={`btn-reject-${item.id}`}
                    >
                      ✗ Reject
                    </button>
                  </div>
                )}

                {item.status !== 'pending' && (
                  <div className="text-small text-muted mt-2">
                    ✓ {item.status} by {item.reviewer || 'anonymous'}
                    {item.reviewed_at && ` on ${new Date(item.reviewed_at).toLocaleString('en-IN')}`}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
