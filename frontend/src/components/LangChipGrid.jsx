import React from 'react'

const ALL_LANGS = [
  'Hindi','Bengali','Telugu','Marathi','Tamil','Gujarati',
  'Urdu','Kannada','Odia','Malayalam','Punjabi','Assamese',
  'Maithili','Sanskrit','Konkani','Sindhi','Dogri','Kashmiri',
  'Manipuri','Nepali','Bodo','Santhali',
]

export default function LangChipGrid({ selected, onChange, exclude = [] }) {
  const langs = ALL_LANGS.filter(l => !exclude.includes(l))

  const toggle = (lang) => {
    if (selected.includes(lang)) {
      onChange(selected.filter(l => l !== lang))
    } else {
      onChange([...selected, lang])
    }
  }

  const selectAll = () => onChange(langs)
  const clearAll  = () => onChange([])

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-small text-muted">
          {selected.length}/{langs.length} selected
        </span>
        <div className="flex gap-2">
          <button className="btn btn-sm btn-secondary" onClick={selectAll} type="button">
            All
          </button>
          <button className="btn btn-sm btn-danger" onClick={clearAll} type="button">
            Clear
          </button>
        </div>
      </div>
      <div className="chip-grid">
        {langs.map(lang => (
          <div
            key={lang}
            className={`chip ${selected.includes(lang) ? 'selected' : ''}`}
            onClick={() => toggle(lang)}
            role="checkbox"
            aria-checked={selected.includes(lang)}
            tabIndex={0}
            onKeyDown={e => e.key === 'Enter' && toggle(lang)}
          >
            {lang}
          </div>
        ))}
      </div>
    </div>
  )
}
