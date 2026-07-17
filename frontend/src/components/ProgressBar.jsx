import React from 'react'

const STAGES = ['queued', 'validating', 'extracting', 'transcribing', 'translating', 'generating', 'packaging']

export default function ProgressBar({ stage, pct, message }) {
  const stageIdx = STAGES.indexOf(stage)

  return (
    <div className="progress-container">
      <div className="progress-stages">
        {STAGES.map((s, i) => {
          let cls = ''
          if (i < stageIdx)       cls = 'done'
          else if (i === stageIdx) cls = 'current'
          return <div key={s} className={`stage-dot ${cls}`} title={s} />
        })}
      </div>

      <div className="progress-bar-wrap">
        <div
          className="progress-bar-fill"
          style={{ width: `${Math.max(pct, 0)}%` }}
        />
      </div>

      <div className="progress-label">
        <span style={{ textTransform: 'capitalize' }}>
          {stage === 'heartbeat' ? 'Processing…' : stage}
        </span>
        <span>{pct >= 0 ? `${pct}%` : ''}</span>
      </div>

      {message && (
        <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
          {message}
        </p>
      )}
    </div>
  )
}
