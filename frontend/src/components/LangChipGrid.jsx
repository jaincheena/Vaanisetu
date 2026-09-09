import React from 'react'

// All 22 official Indian languages + English with native script representation
const ALL_LANGS = [
  { key: 'Marathi', name: 'Marathi', native: 'मराठी', region: 'Maharashtra' },
  { key: 'Hindi', name: 'Hindi', native: 'हिन्दी', region: 'North Hub' },
  { key: 'Gujarati', name: 'Gujarati', native: 'ગુજરાતી', region: 'Gujarat' },
  { key: 'English', name: 'English', native: 'English', region: 'All-India' },
  { key: 'Telugu', name: 'Telugu', native: 'తెలుగు', region: 'AP & Telangana' },
  { key: 'Kannada', name: 'Kannada', native: 'ಕನ್ನಡ', region: 'Karnataka' },
  { key: 'Bengali', name: 'Bengali', native: 'বাংলা', region: 'West Bengal' },
  { key: 'Tamil', name: 'Tamil', native: 'தமிழ்', region: 'Tamil Nadu' },
  { key: 'Malayalam', name: 'Malayalam', native: 'മലയാളം', region: 'Kerala' },
  { key: 'Punjabi', name: 'Punjabi', native: 'ਪੰਜਾਬੀ', region: 'Punjab' },
  { key: 'Odia', name: 'Odia', native: 'ଓଡ଼ିଆ', region: 'Odisha' },
  { key: 'Urdu', name: 'Urdu', native: 'اردو', region: 'All-India' },
  { key: 'Assamese', name: 'Assamese', native: 'অসমীয়া', region: 'Assam' },
  { key: 'Nepali', name: 'Nepali', native: 'नेपाली', region: 'Sikkim/WB' },
  { key: 'Maithili', name: 'Maithili', native: 'मैथिली', region: 'Bihar' },
  { key: 'Sanskrit', name: 'Sanskrit', native: 'संस्कृतम्', region: 'Classical' },
  { key: 'Konkani', name: 'Konkani', native: 'कोंकणी', region: 'Goa/Konkan' },
  { key: 'Sindhi', name: 'Sindhi', native: 'سنڌي', region: 'Western' },
  { key: 'Dogri', name: 'Dogri', native: 'डोगरी', region: 'J&K' },
  { key: 'Kashmiri', name: 'Kashmiri', native: 'کٲشُر', region: 'Kashmir' },
  { key: 'Manipuri', name: 'Manipuri', native: 'মৈতৈলোন্', region: 'Manipur' },
  { key: 'Bodo', name: 'Bodo', native: 'बर’', region: 'Assam' },
  { key: 'Santhali', name: 'Santhali', native: 'ᱥᱟᱱᱛᱟᱲᱤ', region: 'Jharkhand' },
]

export const ACTIVE_LANGS = new Set([
  'Marathi', 'Hindi', 'Gujarati', 'Kannada', 'Bengali'
])

export default function LangChipGrid({ selected, onChange, exclude = [] }) {
  const langs = ALL_LANGS.filter(l => !exclude.includes(l.key))
  const active = langs.filter(l => ACTIVE_LANGS.has(l.key)).map(l => l.key)

  const toggle = (langKey) => {
    if (!ACTIVE_LANGS.has(langKey)) return
    if (selected.includes(langKey)) {
      onChange(selected.filter(l => l !== langKey))
    } else {
      onChange([...selected, langKey])
    }
  }

  const selectActive = () => onChange(active)
  const selectMaharashtra = () => onChange(['Marathi', 'Hindi'])
  const selectWestern = () => onChange(['Marathi', 'Hindi', 'Gujarati'])
  const selectSouth = () => onChange(['Kannada'])
  const clearAll = () => onChange([])

  return (
    <div>
      <div className="chip-grid-actions" style={{ flexWrap: 'wrap', gap: 8 }}>
        <span className="chip-count">
          <strong>{selected.length}</strong> of {active.length} active Indic languages selected
        </span>
        <div className="flex gap-2" style={{ flexWrap: 'wrap' }}>
          <button className="btn btn-sm btn-secondary" onClick={selectMaharashtra} type="button" title="Pune HQ & Maharashtra field blocks">
            🚩 Maharashtra (MR + HI)
          </button>
          <button className="btn btn-sm btn-secondary" onClick={selectWestern} type="button" title="Maharashtra, Gujarat, MP">
            🌾 Western India
          </button>
          <button className="btn btn-sm btn-secondary" onClick={selectSouth} type="button">
            🌴 South Hub
          </button>
          <button className="btn btn-sm btn-secondary" onClick={selectActive} type="button">
            All 5 Active
          </button>
          <button className="btn btn-sm btn-danger" onClick={clearAll} type="button">
            Clear
          </button>
        </div>
      </div>

      <div className="chip-grid">
        {langs.map(l => {
          const isActive = ACTIVE_LANGS.has(l.key)
          const isSelected = selected.includes(l.key)
          return (
            <div
              key={l.key}
              className={`chip ${isSelected ? 'selected' : ''} ${!isActive ? 'disabled' : ''}`}
              onClick={() => isActive && toggle(l.key)}
              role="checkbox"
              aria-checked={isSelected}
              aria-disabled={!isActive}
              tabIndex={isActive ? 0 : -1}
              onKeyDown={e => e.key === 'Enter' && isActive && toggle(l.key)}
              data-tooltip={!isActive ? 'Pipeline in training' : undefined}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '8px 10px',
                minHeight: 48
              }}
            >
              <span style={{ fontSize: 13, fontWeight: 700 }}>
                {l.native}
              </span>
              <span style={{ fontSize: 11, opacity: 0.8, fontWeight: 500 }}>
                {l.name}
              </span>
            </div>
          )
        })}
      </div>

      <p style={{ fontSize: 11.5, color: '#64748B', marginTop: 10, fontWeight: 500 }}>
        ✦ Selected Indic languages receive synthesized voiceovers in native regional dialects.
      </p>
    </div>
  )
}
