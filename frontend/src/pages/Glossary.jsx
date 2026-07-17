import React, { useState, useEffect } from 'react'

export default function Glossary() {
  const [terms, setTerms] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [allLangs, setAllLangs] = useState([])

  const load = (q = '') => {
    fetch(`/api/glossary?search=${encodeURIComponent(q)}`)
      .then(r => r.json())
      .then(data => {
        setTerms(data)
        // Derive all target languages present
        const langs = new Set()
        data.forEach(t => Object.keys(t.translations).forEach(l => langs.add(l)))
        setAllLangs([...langs].sort())
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleSearch = (e) => {
    setSearch(e.target.value)
    load(e.target.value)
  }

  return (
    <div>
      <div className="page-header flex items-center justify-between">
        <div>
          <h2>Glossary</h2>
          <p>High-confidence terms used 3+ times</p>
        </div>
        <a
          className="btn btn-secondary"
          href="/api/glossary/export/docx"
          download
          id="btn-export-docx"
        >
          📄 Export DOCX
        </a>
      </div>

      <div className="card mb-4">
        <div className="search-box">
          <input
            id="glossary-search"
            type="text"
            placeholder="Search terms…"
            value={search}
            onChange={handleSearch}
          />
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          Loading glossary…
        </div>
      ) : terms.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <p>No glossary terms yet.</p>
          <p className="text-small mt-2">Terms appear automatically after 3+ translations with ≥ 85% confidence.</p>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Source Term</th>
                  <th>Lang</th>
                  <th>Used</th>
                  <th>Confidence</th>
                  {allLangs.map(l => <th key={l}>{l}</th>)}
                </tr>
              </thead>
              <tbody>
                {terms.map((term, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: 600 }}>{term.source_text}</td>
                    <td>
                      <span className="badge grey">{term.source_lang}</span>
                    </td>
                    <td>
                      <span className="badge green">{term.times_used}×</span>
                    </td>
                    <td>
                      <span className="badge green">{(term.confidence * 100).toFixed(0)}%</span>
                    </td>
                    {allLangs.map(l => (
                      <td key={l}>
                        {term.translations[l] || (
                          <span style={{ color: 'var(--text-dim)' }}>—</span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
