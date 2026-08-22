import React, { useState, useEffect } from 'react'

const CATEGORIES = [
  { id: 'all', label: 'All Terms' },
  { id: 'crop', label: '🌾 Crop Protection & Pests' },
  { id: 'soil', label: '🧪 Fertilizers & Soil' },
  { id: 'water', label: '💧 Irrigation & Water' },
  { id: 'dairy', label: '🐄 Livestock & Dairy' },
  { id: 'scheme', label: '🏛️ Govt Schemes' },
]

export default function Glossary() {
  const [terms, setTerms] = useState([])
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('all')
  const [loading, setLoading] = useState(true)
  const [allLangs, setAllLangs] = useState([])
  const [showAddModal, setShowAddModal] = useState(false)
  const [feedback, setFeedback] = useState(null)

  // New Term Form State
  const [newTerm, setNewTerm] = useState({
    source_text: '',
    source_lang: 'English',
    target_lang: 'Hindi',
    translated_text: '',
  })

  const load = (q = '') => {
    fetch(`/api/glossary?search=${encodeURIComponent(q)}`)
      .then(r => r.json())
      .then(data => {
        setTerms(Array.isArray(data) ? data : [])
        const langs = new Set()
        if (Array.isArray(data)) {
          data.forEach(t => Object.keys(t.translations || {}).forEach(l => langs.add(l)))
        }
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

  const handleAddTerm = async (e) => {
    e.preventDefault()
    if (!newTerm.source_text || !newTerm.translated_text) return

    try {
      const res = await fetch('/api/glossary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTerm),
      })
      const data = await res.json()
      if (data.success) {
        setShowAddModal(false)
        setNewTerm({ source_text: '', source_lang: 'English', target_lang: 'Hindi', translated_text: '' })
        setFeedback(`✓ Added '${newTerm.source_text}' to verified AgriShield™ Glossary!`)
        setTimeout(() => setFeedback(null), 4000)
        load()
      }
    } catch (err) {
      console.error(err)
    }
  }
  
  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this term?")) return;
    
    try {
      const res = await fetch(`/api/glossary/${id}`, { method: "DELETE" });
      if (res.ok) 
      {
        setTerms(terms.filter(t => t.id !== id));
        setFeedback(`✗ Deleted term with ID ${id}`);
        setTimeout(() => setFeedback(null), 4000);
      } 
      else {
      console.error("Failed to delete term");
   }
  } catch (err) {
    console.error(err);
  }
};

  const filteredTerms = terms.filter(t => {
    if (category === 'all') return true
    const src = t.source_text.toLowerCase()
    if (category === 'crop') return src.includes('rust') || src.includes('pesticide') || src.includes('propiconazole') || src.includes('bollworm') || src.includes('oil') || src.includes('disease')
    if (category === 'soil') return src.includes('urea') || src.includes('dap') || src.includes('fertilizer') || src.includes('soil') || src.includes('testing')
    if (category === 'water') return src.includes('drip') || src.includes('irrigation') || src.includes('emitter') || src.includes('acid') || src.includes('flushing')
    if (category === 'dairy') return src.includes('lumpy') || src.includes('cattle') || src.includes('dairy') || src.includes('vaccine') || src.includes('goat')
    if (category === 'scheme') return src.includes('kisan') || src.includes('yojana') || src.includes('pm-') || src.includes('card')
    return true
  })

  return (
    <div>
      <div className="page-header flex items-center justify-between">
        <div>
          <h2>AgriShield™ Domain Glossary <span style={{ color: '#D97706', fontSize: 18, fontWeight: 700 }}>(वाणीसेतु सुरक्षित शब्दावली)</span></h2>
          <p>120+ verified agricultural formulations, fertilizers, cattle vaccines, and government schemes protected in 14 Indic scripts</p>
        </div>
        <div className="flex gap-2">
          <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
            ➕ Add Term
          </button>
          <a
            className="btn btn-secondary"
            href="/api/glossary/export/docx"
            download
            id="btn-export-docx"
          >
            📄 Export DOCX
          </a>
        </div>
      </div>

      {feedback && (
        <div className="card mb-4" style={{ background: 'rgba(82, 196, 135, 0.12)', borderColor: 'var(--green)', color: 'var(--green)', padding: '12px 16px', fontSize: 13, fontWeight: 500 }}>
          {feedback}
        </div>
      )}

      {/* Category Pills & Search */}
      <div className="card mb-4">
        <div style={{ display: 'flex', gap: 8, marginBottom: 14, overflowX: 'auto', paddingBottom: 4 }}>
          {CATEGORIES.map(c => (
            <button
              key={c.id}
              type="button"
              className={`btn btn-sm ${category === c.id ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setCategory(c.id)}
            >
              {c.label}
            </button>
          ))}
        </div>

        <div className="search-box">
          <input
            id="glossary-search"
            type="text"
            className="text-input"
            style={{ marginBottom: 0 }}
            placeholder="Search agricultural chemical, disease, fertilizer, or scheme terms…"
            value={search}
            onChange={handleSearch}
          />
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          Loading glossary…
        </div>
      ) : filteredTerms.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <p>No glossary terms found matching your filter.</p>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Agricultural Entity / Term</th>
                  <th>Source</th>
                  <th>Confidence</th>
                  {allLangs.map(l => <th key={l}>{l}</th>)}
                  <th>Actions</th> {/* New column header */}
                </tr>
              </thead>
              <tbody>
                {filteredTerms.map((term, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: 600, color: 'var(--text)' }}>
                      🌱 {term.source_text}
                    </td>
                    <td>
                      <span className="badge grey">{term.source_lang}</span>
                    </td>
                    <td>
                      <span className="badge green">{(term.confidence * 100).toFixed(0)}% ✓</span>
                    </td>
                    {allLangs.map(l => (
                      <td key={l} style={{ fontSize: 13, color: term.translations?.[l] ? 'var(--text)' : 'var(--text-muted)' }}>
                        {term.translations?.[l] || <span style={{ color: 'var(--text-dim)' }}>—</span>}
                      </td>
                    ))}
                    <td>
                       <button
                         className="btn btn-danger btn-sm"
                         onClick={() => handleDelete(term.id)}
                       >
                         🗑 Delete
                       </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add Term Modal */}
      {showAddModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(15, 23, 42, 0.4)', backdropFilter: 'blur(3px)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 9999, padding: 20
        }}>
          <div className="card" style={{ width: '100%', maxWidth: 480, background: '#111C30', border: '1.5px solid rgba(245, 158, 11, 0.4)', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.8)' }}>
            <h3 style={{ margin: '0 0 16px 0', fontSize: 18, color: '#F8FAFC', fontWeight: 800 }}>➕ Add Verified Agricultural Term</h3>
            <form onSubmit={handleAddTerm}>
              <div className="mb-3">
                <label>Source Term (e.g. English chemical or disease name)</label>
                <input
                  type="text"
                  className="text-input"
                  required
                  placeholder="e.g. Imidacloprid 17.8% SL"
                  value={newTerm.source_text}
                  onChange={e => setNewTerm({ ...newTerm, source_text: e.target.value })}
                />
              </div>

              <div className="grid-2 mb-3">
                <div>
                  <label>Source Language</label>
                  <select
                    value={newTerm.source_lang}
                    onChange={e => setNewTerm({ ...newTerm, source_lang: e.target.value })}
                  >
                    <option value="English">English</option>
                    <option value="Hindi">Hindi</option>
                    <option value="Marathi">Marathi</option>
                  </select>
                </div>
                <div>
                  <label>Target Language</label>
                  <select
                    value={newTerm.target_lang}
                    onChange={e => setNewTerm({ ...newTerm, target_lang: e.target.value })}
                  >
                    <option value="Hindi">Hindi</option>
                    <option value="Marathi">Marathi</option>
                    <option value="Gujarati">Gujarati</option>
                    <option value="Telugu">Telugu</option>
                    <option value="Bengali">Bengali</option>
                    <option value="Kannada">Kannada</option>
                  </select>
                </div>
              </div>

              <div className="mb-4">
                <label>Verified Localized Translation</label>
                <input
                  type="text"
                  className="text-input"
                  required
                  placeholder="e.g. इमिडाक्लोप्रिड 17.8% एसएल (कीटनाशक)"
                  value={newTerm.translated_text}
                  onChange={e => setNewTerm({ ...newTerm, translated_text: e.target.value })}
                />
              </div>

              <div className="flex justify-end gap-2">
                <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save to AgriShield™
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
