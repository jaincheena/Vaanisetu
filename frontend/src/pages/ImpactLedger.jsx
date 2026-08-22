import React, { useState, useEffect } from 'react'

// Indian numbering, and never "0.00 Crores" for a four-figure sum.
const formatRupees = (value) => {
  const n = Number(value) || 0
  if (n >= 1e7) return `₹${(n / 1e7).toFixed(2)} Cr`
  if (n >= 1e5) return `₹${(n / 1e5).toFixed(2)} L`
  if (n >= 1e3) return `₹${(n / 1e3).toFixed(1)}K`
  return `₹${n.toFixed(0)}`
}

export default function ImpactLedger() {
  const [summary, setSummary] = useState(null)
  const [config, setConfig] = useState([])
  const [editRows, setEditRows] = useState({})
  const [saving, setSaving] = useState({})
  const [saveError, setSaveError] = useState({})
  const [loading, setLoading] = useState(true)

  const load = () => {
    Promise.all([
      fetch('/api/impact').then(r => r.json()),
      fetch('/api/impact/config').then(r => r.json()),
    ]).then(([s, c]) => {
      setSummary(s)
      setConfig(c)
      setLoading(false)
    }).catch(() => setLoading(false))
  }

  useEffect(load, [])

  const saveConfig = async (lang, fph, rpm) => {
    // These rates drive an audit report, so a rejected value must not sit on
    // screen looking saved. The API enforces >= 1; mirror that here so the
    // user gets told rather than silently ignored.
    if (!Number.isFinite(+fph) || +fph < 1 || !Number.isFinite(+rpm) || +rpm < 1) {
      setSaveError(e => ({ ...e, [lang]: 'Both values must be 1 or more' }))
      return
    }
    setSaving(s => ({ ...s, [lang]: true }))
    setSaveError(e => ({ ...e, [lang]: null }))
    try {
      const r = await fetch('/api/impact/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: lang, farmers_per_hour: +fph, translation_rate_per_min: +rpm }),
      })
      if (!r.ok) throw new Error(`Server rejected the change (${r.status})`)
      // Clear the pending edit so the row falls back to the stored value —
      // otherwise a stale local edit shadows what the server actually holds.
      setEditRows(rows => {
        const next = { ...rows }
        delete next[lang]
        return next
      })
      load()
    } catch (err) {
      setSaveError(e => ({ ...e, [lang]: err.message }))
    } finally {
      setSaving(s => ({ ...s, [lang]: false }))
    }
  }

  const setRow = (lang, field, val) =>
    setEditRows(r => ({ ...r, [lang]: { ...(r[lang] || {}), [field]: val } }))

  const getVal = (row, field) =>
    editRows[row.language]?.[field] ?? row[field]

  const maxBarVal = summary?.language_breakdown?.length
    ? Math.max(...summary.language_breakdown.map(r => r.farmers_reachable), 1)
    : 1

  if (loading) return (
    <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
      Loading impact data…
    </div>
  )

  return (
    <div>
      <div className="page-header flex items-center justify-between">
        <div>
          <h2>Impact & Reach Ledger <span style={{ color: '#D97706', fontSize: 18, fontWeight: 700 }}>(वाणीसेतु प्रभाव लेज़र)</span></h2>
          <p>Tracking multi-lingual advisory output, commercial translation savings, and rural farmer reach across 16 states</p>
        </div>
        <a
          className="btn btn-secondary"
          href="/api/impact/export/pdf"
          download
          id="btn-export-pdf"
        >
          📄 Export Formal PDF Report
        </a>
      </div>

      {/* Stat tiles */}
      {summary && (
        <>
          <div className="stat-grid mb-4">
            <div className="stat-tile">
              <div className="stat-label">Advisory Hours Localized</div>
              <div className="stat-value">{(summary.total_hours ?? 0).toFixed(1)} hrs</div>
              <div className="stat-sub">source runtime, counted once per job</div>
            </div>
            <div className="stat-tile">
              <div className="stat-label">Cost Saved vs Agency</div>
              <div className="stat-value">{formatRupees(summary.total_cost_saved)}</div>
              <div className="stat-sub">at the per-language rates configured below</div>
            </div>
            <div className="stat-tile">
              <div className="stat-label">Farmers Reachable</div>
              <div className="stat-value">{Number(summary.total_farmers_reachable ?? 0).toLocaleString('en-IN')}</div>
              <div className="stat-sub">capacity at the configured rate — not farmers served</div>
            </div>
            <div className="stat-tile">
              <div className="stat-label">Completed Jobs</div>
              <div className="stat-value">{summary.job_count}</div>
              <div className="stat-sub">multi-format packages</div>
            </div>
          </div>

          <div className="card mb-6" style={{ padding: '12px 16px' }}>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6 }}>
              <strong style={{ color: 'var(--text)' }}>How these figures are calculated.</strong>{' '}
              Hours are the runtime of the source advisory, counted once per job however many
              languages it was localized into. Cost saved is advisory minutes × the configured
              agency rate, per target language. <strong style={{ color: 'var(--text)' }}>Farmers
              Reachable is a capacity estimate</strong> — VaaniSetu produces the files but does not
              deliver them, so this is potential reach, not a count of farmers served.
              {summary.unmeasured_job_count > 0 && (
                <> {summary.unmeasured_job_count} earlier job{summary.unmeasured_job_count === 1 ? '' : 's'} predate
                duration tracking and {summary.unmeasured_job_count === 1 ? 'is' : 'are'} excluded from every figure above.</>
              )}
            </div>
          </div>
        </>
      )}

      {/* Language breakdown */}
      {summary?.language_breakdown?.length > 0 && (
        <div className="card mb-4">
          <div className="card-title">Farmers Reachable — By Regional Language</div>
          <div className="bar-chart">
            {summary.language_breakdown.map(row => (
              <div className="bar-row" key={row.language}>
                <div className="bar-label">{row.language}</div>
                <div className="bar-track">
                  <div
                    className="bar-fill"
                    style={{ width: `${(row.farmers_reachable / maxBarVal) * 100}%` }}
                  />
                </div>
                <div className="bar-value">{Number(row.farmers_reachable).toLocaleString('en-IN')}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Config table */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="card-title" style={{ margin: 0 }}>Regional Rate Configuration</div>
          <span className="text-small text-muted">Rates used for the figures above and the PDF report</span>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Language</th>
                <th>Farmers Reachable / Hour</th>
                <th>Human Agency Rate (₹/min)</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {config.map(row => (
                <tr key={row.language}>
                  <td style={{ fontWeight: 500 }}>{row.language}</td>
                  <td>
                    <input
                      className="text-input"
                      type="number"
                      id={`fph-${row.language}`}
                      value={getVal(row, 'farmers_per_hour')}
                      onChange={e => setRow(row.language, 'farmers_per_hour', e.target.value)}
                      style={{ width: 100, padding: '4px 8px' }}
                      min={1}
                    />
                  </td>
                  <td>
                    <input
                      className="text-input"
                      type="number"
                      id={`rpm-${row.language}`}
                      value={getVal(row, 'translation_rate_per_min')}
                      onChange={e => setRow(row.language, 'translation_rate_per_min', e.target.value)}
                      style={{ width: 100, padding: '4px 8px' }}
                      min={1}
                    />
                  </td>
                  <td>
                    <button
                      className="btn btn-sm btn-secondary"
                      disabled={saving[row.language]}
                      onClick={() => saveConfig(
                        row.language,
                        getVal(row, 'farmers_per_hour'),
                        getVal(row, 'translation_rate_per_min'),
                      )}
                    >
                      {saving[row.language] ? '…' : '💾 Save'}
                    </button>
                    {saveError[row.language] && (
                      <div style={{ fontSize: 11, color: 'var(--red)', marginTop: 4 }}>
                        ⚠️ {saveError[row.language]}
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
