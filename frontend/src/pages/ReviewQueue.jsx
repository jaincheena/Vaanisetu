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
          <h2>Review Queue</h2>
          <p>Amber and red confidence segments awaiting human review & verification</p>
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

      {/* Reviewer name + filter */}
      <div className="card mb-4">
        <div className="flex items-center gap-3" style={{ flexWrap: 'wrap' }}>
          <div style={{ minWidth: 200 }}>
            <label>Reviewer Name</label>
            <input
              className="text-input"
              id="reviewer-name"
              type="text"
              value={reviewer}
              onChange={e => setReviewer(e.target.value)}
              placeholder="e.g. Dr. Patil (BAIF Pune HQ)"
            />
          </div>
          <div style={{ minWidth: 160 }}>
            <label>Status Filter</label>
            <select id="status-filter" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
              <option value="pending">Pending ({stats?.pending || 0})</option>
              <option value="approved">Approved ({stats?.approved || 0})</option>
              <option value="edited">Edited ({stats?.edited || 0})</option>
              <option value="rejected">Rejected ({stats?.rejected || 0})</option>
              <option value="all">All ({stats?.total || 0})</option>
            </select>
          </div>
          <div style={{ alignSelf: 'flex-end', display: 'flex', gap: 8 }}>
            <button className="btn btn-secondary" onClick={load}>↻ Refresh</button>
            <button className="btn btn-secondary" onClick={handleClearTest} title="Purge legacy test entries">🧹 Clean Stale Items</button>
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
