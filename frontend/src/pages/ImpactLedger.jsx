import React, { useState, useEffect } from 'react'

export default function ImpactLedger() {
  const [summary, setSummary] = useState(null)
  const [config, setConfig] = useState([])
  const [editRows, setEditRows] = useState({})
  const [saving, setSaving] = useState({})
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
    setSaving(s => ({ ...s, [lang]: true }))
    await fetch('/api/impact/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ language: lang, farmers_per_hour: +fph, translation_rate_per_min: +rpm }),
    })
    setSaving(s => ({ ...s, [lang]: false }))
    load()
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
          <h2>Impact Ledger</h2>
          <p>Cumulative social impact of all completed translation jobs</p>
        </div>
        <a
          className="btn btn-secondary"
          href="/api/impact/export/pdf"
          download
          id="btn-export-pdf"
        >
          📄 Export PDF
        </a>
      </div>

      {/* Stat tiles */}
      {summary && (
        <div className="stat-grid">
          <div className="stat-tile">
            <div className="stat-label">Hours Translated</div>
            <div className="stat-value">{summary.total_hours.toFixed(1)}</div>
            <div className="stat-sub">hours of content</div>
          </div>
          <div className="stat-tile">
            <div className="stat-label">Cost Saved</div>
            <div className="stat-value">₹{(summary.total_cost_saved/1000).toFixed(1)}K</div>
            <div className="stat-sub">vs. professional translation</div>
          </div>
          <div className="stat-tile">
            <div className="stat-label">Farmers Reachable</div>
            <div className="stat-value">{Number(summary.total_farmers_reachable).toLocaleString('en-IN')}</div>
            <div className="stat-sub">across completed jobs</div>
          </div>
          <div className="stat-tile">
            <div className="stat-label">Completed Jobs</div>
            <div className="stat-value">{summary.job_count}</div>
            <div className="stat-sub">translation jobs done</div>
          </div>
        </div>
      )}

      {/* Language breakdown */}
      {summary?.language_breakdown?.length > 0 && (
        <div className="card mb-4">
          <div className="card-title">Farmers Reachable — By Language</div>
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
          <div className="card-title" style={{ margin: 0 }}>Rate Configuration</div>
          <span className="text-small text-muted">Edit multipliers to adjust projections</span>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Language</th>
                <th>Farmers/Hour</th>
                <th>Rate (₹/min)</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {config.map(row => (
                <tr key={row.language}>
                  <td style={{ fontWeight: 500 }}>{row.language}</td>
                  <td>
                    <input
                      type="number"
                      id={`fph-${row.language}`}
                      value={getVal(row, 'farmers_per_hour')}
                      onChange={e => setRow(row.language, 'farmers_per_hour', e.target.value)}
                      style={{ width: 90 }}
                      min={1}
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      id={`rpm-${row.language}`}
                      value={getVal(row, 'translation_rate_per_min')}
                      onChange={e => setRow(row.language, 'translation_rate_per_min', e.target.value)}
                      style={{ width: 90 }}
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
