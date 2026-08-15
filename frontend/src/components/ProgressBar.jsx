import React from 'react'

const STAGES = [
  { key: 'queued',      label: 'Queue' },
  { key: 'validating',  label: 'Validate' },
  { key: 'extracting',  label: 'Extract' },
  { key: 'transcribing',label: 'Transcribe' },
  { key: 'translating', label: 'Translate' },
  { key: 'generating',  label: 'Generate' },
  { key: 'packaging',   label: 'Package' },
]

export default function ProgressBar({ stage, pct, message }) {
  const stageIdx = STAGES.findIndex(s => s.key === stage)

  return (
    <div className="progress-container">
      {/* Stage dots with names */}
      <div className="progress-stages">
        {STAGES.map((s, i) => {
          let cls = ''
          if (i < stageIdx)        cls = 'done'
          else if (i === stageIdx) cls = 'current'
          return (
            <div key={s.key} className="stage-step">
              <div className={`stage-dot ${cls}`} />
              <div className={`stage-name ${cls}`}>{s.label}</div>
            </div>
          )
        })}
      </div>

      {/* Progress bar */}
      <div className="progress-bar-wrap">
        <div
          className="progress-bar-fill"
          style={{ width: `${Math.max(pct ?? 0, 0)}%` }}
        />
      </div>

      {/* Label row */}
      <div className="progress-label">
        <span>
          <strong>
            {stage === 'heartbeat' ? 'Processing…' : STAGES.find(s => s.key === stage)?.label ?? stage}
          </strong>
        </span>
        <span>{pct >= 0 ? `${pct}%` : ''}</span>
      </div>

      {message && (
        <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6 }}>
          {message}
        </p>
      )}
    </div>
  )
}
