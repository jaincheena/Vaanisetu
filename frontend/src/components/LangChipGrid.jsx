import React from 'react'

// All 22 official Indian languages + English
const ALL_LANGS = [
  'Marathi', 'Hindi', 'Gujarati', 'English', 'Telugu', 'Kannada',
  'Bengali', 'Tamil', 'Malayalam', 'Punjabi', 'Odia', 'Urdu',
  'Assamese', 'Nepali', 'Maithili', 'Sanskrit', 'Konkani', 'Sindhi',
  'Dogri', 'Kashmiri', 'Manipuri', 'Bodo', 'Santhali',
]

// Languages with verified end-to-end translation and speech pipelines
export const ACTIVE_LANGS = new Set([
  'Marathi', 'Hindi', 'Gujarati', 'English', 'Telugu', 'Kannada',
  'Bengali', 'Tamil', 'Malayalam', 'Punjabi', 'Odia', 'Urdu',
  'Assamese', 'Nepali',
])

export default function LangChipGrid({ selected, onChange, exclude = [] }) {
  const langs = ALL_LANGS.filter(l => !exclude.includes(l))
  const active = langs.filter(l => ACTIVE_LANGS.has(l))

  const toggle = (lang) => {
    if (!ACTIVE_LANGS.has(lang)) return
    if (selected.includes(lang)) {
      onChange(selected.filter(l => l !== lang))
    } else {
      onChange([...selected, lang])
    }
  }

  const selectActive = () => onChange(active)
  const selectMaharashtra = () => onChange(['Marathi', 'Hindi'])
  const selectWestern = () => onChange(['Marathi', 'Hindi', 'Gujarati'])
  const selectSouth = () => onChange(['Telugu', 'Kannada', 'Tamil', 'Malayalam'])
  const clearAll = () => onChange([])

  return (
    <div>
      <div className="chip-grid-actions" style={{ flexWrap: 'wrap', gap: 8 }}>
        <span className="chip-count">
          {selected.length} of {active.length} active languages selected
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
            All Active
          </button>
          <button className="btn btn-sm btn-danger" onClick={clearAll} type="button">
            Clear
          </button>
        </div>
      </div>

      <div className="chip-grid">
        {langs.map(lang => {
          const isActive = ACTIVE_LANGS.has(lang)
          const isSelected = selected.includes(lang)
          return (
            <div
              key={lang}
              className={`chip ${isSelected ? 'selected' : ''} ${!isActive ? 'disabled' : ''}`}
              onClick={() => isActive && toggle(lang)}
              role="checkbox"
              aria-checked={isSelected}
              aria-disabled={!isActive}
              tabIndex={isActive ? 0 : -1}
              onKeyDown={e => e.key === 'Enter' && isActive && toggle(lang)}
              data-tooltip={!isActive ? 'Coming soon' : undefined}
            >
              {lang}
            </div>
          )
        })}
      </div>

      <p style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 10 }}>
        ✦ Greyed out languages are coming soon. Auto-detect works for all source languages.
      </p>
    </div>
  )
}
