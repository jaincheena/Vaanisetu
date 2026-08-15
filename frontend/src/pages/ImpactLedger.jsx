import React, { useState, useEffect } from 'react'

export default function ImpactLedger() {
  const [summary, setSummary] = useState(null)
  const [config, setConfig] = useState([])
  const [editRows, setEditRows] = useState({})
  const [saving, setSaving] = useState({})
  const [loading, setLoading] = useState(true)

  // Interactive ROI Calculator State for Judges
  const [calcVideos, setCalcVideos] = useState(25)
  const [calcDuration, setCalcDuration] = useState(12)
  const [calcLangs, setCalcLangs] = useState(6)
  const [calcRate, setCalcRate] = useState(850)

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

  // Calculator computations
  const totalMinsMonth = calcVideos * calcDuration * calcLangs
  const monthlyCostSaved = totalMinsMonth * calcRate
  const annualCostSaved = monthlyCostSaved * 12
  const monthlyFarmers = (totalMinsMonth / 60) * 120
  const annualFarmers = monthlyFarmers * 12

  if (loading) return (
    <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
      Loading impact data…
    </div>
  )

  return (
    <div>
      <div className="page-header flex items-center justify-between">
        <div>
          <h2>Social Impact & Financial ROI Ledger</h2>
          <p>Real-time analytics of agricultural outreach, cost savings, and scale</p>
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
        <div className="stat-grid mb-6">
          <div className="stat-tile">
            <div className="stat-label">Hours Translated</div>
            <div className="stat-value">{summary.total_hours.toFixed(1)} hrs</div>
            <div className="stat-sub">across completed jobs</div>
          </div>
          <div className="stat-tile">
            <div className="stat-label">Financial Savings</div>
            <div className="stat-value">₹{(summary.total_cost_saved/1000).toFixed(1)}K</div>
            <div className="stat-sub">vs ₹850/min agency rate</div>
          </div>
          <div className="stat-tile">
            <div className="stat-label">Farmers Reached</div>
            <div className="stat-value">{Number(summary.total_farmers_reachable).toLocaleString('en-IN')}</div>
            <div className="stat-sub">smallholder beneficiaries</div>
          </div>
          <div className="stat-tile">
            <div className="stat-label">Completed Jobs</div>
            <div className="stat-value">{summary.job_count}</div>
            <div className="stat-sub">multi-format packages</div>
          </div>
        </div>
      )}

      {/* ── Interactive ROI Impact Calculator for Judges ── */}
      <div className="card mb-6" style={{
        background: 'linear-gradient(135deg, rgba(232, 109, 31, 0.08) 0%, var(--bg-card) 100%)',
        border: '1px solid var(--accent)'
      }}>
        <div className="card-title" style={{ color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: 8 }}>
          <span>🧮</span>
          <span>Interactive BAIF Scale & Financial Projection Model</span>
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>
          Adjust the sliders below to simulate organization-wide deployment across BAIF's 12 regional field offices.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 20, marginBottom: 24 }}>
          <div>
            <label style={{ fontSize: 12, fontWeight: 600 }}>Training Videos / Month: <strong>{calcVideos}</strong></label>
            <input
              type="range"
              min="5"
              max="100"
              value={calcVideos}
              onChange={e => setCalcVideos(+e.target.value)}
              style={{ width: '100%', accentColor: 'var(--accent)' }}
            />
          </div>

          <div>
            <label style={{ fontSize: 12, fontWeight: 600 }}>Avg Video Length: <strong>{calcDuration} mins</strong></label>
            <input
              type="range"
              min="2"
              max="45"
              value={calcDuration}
              onChange={e => setCalcDuration(+e.target.value)}
              style={{ width: '100%', accentColor: 'var(--accent)' }}
            />
          </div>

          <div>
            <label style={{ fontSize: 12, fontWeight: 600 }}>Target Languages: <strong>{calcLangs} langs</strong></label>
            <input
              type="range"
              min="1"
              max="12"
              value={calcLangs}
              onChange={e => setCalcLangs(+e.target.value)}
              style={{ width: '100%', accentColor: 'var(--accent)' }}
            />
          </div>

          <div>
            <label style={{ fontSize: 12, fontWeight: 600 }}>Agency Translation Rate: <strong>₹{calcRate}/min</strong></label>
            <input
              type="range"
              min="400"
              max="1500"
              step="50"
              value={calcRate}
              onChange={e => setCalcRate(+e.target.value)}
              style={{ width: '100%', accentColor: 'var(--accent)' }}
            />
          </div>
        </div>

        {/* Projection Results */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: 12,
          background: 'var(--bg-input)',
          padding: 16,
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border)'
        }}>
          <div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Monthly Output Generated</div>
            <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--text)' }}>
              {(totalMinsMonth / 60).toFixed(0)} Hours
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-dim)' }}>{totalMinsMonth.toLocaleString('en-IN')} audio mins</div>
          </div>

          <div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Monthly Agency Cost</div>
            <div style={{ fontSize: 18, fontWeight: 700, color: '#f87171' }}>
              ₹{(monthlyCostSaved / 100000).toFixed(2)} Lakhs
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-dim)' }}>Commercial outsourcing bill</div>
          </div>

          <div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>VaaniSetu Annual Savings</div>
            <div style={{ fontSize: 20, fontWeight: 800, color: '#4ade80' }}>
              ₹{(annualCostSaved / 10000000).toFixed(2)} Crores
            </div>
            <div style={{ fontSize: 10, color: '#4ade80' }}>100% saved via offline AI</div>
          </div>

          <div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Annual Farmer Reach</div>
            <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--accent)' }}>
              {annualFarmers.toLocaleString('en-IN')}
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-dim)' }}>Farmers trained across India</div>
          </div>
        </div>
      </div>

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
          <span className="text-small text-muted">Multipliers used for official audit reporting</span>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Language</th>
                <th>Farmers Reached / Hour</th>
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
