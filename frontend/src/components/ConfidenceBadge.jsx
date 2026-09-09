import React from 'react'

const CONFIG = {
  green: { label: '✓ High Confidence', icon: '🟢' },
  amber: { label: '⚠ Review Needed',   icon: '🟡' },
  red:   { label: '✗ Low Confidence',  icon: '🔴' },
}

export default function ConfidenceBadge({ level, score, style, className }) {
  if (!level) return null
  const cfg = CONFIG[level] || { label: level, icon: '⚪' }

  return (
    <span className={`badge ${level} ${className || ''}`} style={style}>
      {cfg.icon} {cfg.label} {score !== undefined && `(${(score * 100).toFixed(0)}%)`}
    </span>
  )
}
