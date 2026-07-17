import React, { useState, useEffect } from 'react'

export default function TopBanner() {
  const [health, setHealth] = useState(null)
  const ip = window.location.hostname

  useEffect(() => {
    const fetch_ = () =>
      fetch('/api/health')
        .then(r => r.json())
        .then(setHealth)
        .catch(() => setHealth(null))
    fetch_()
    const id = setInterval(fetch_, 30000)
    return () => clearInterval(id)
  }, [])

  const allModelsLoaded = health?.models_loaded &&
    health.models_loaded.whisper &&
    health.models_loaded.en_indic &&
    health.models_loaded.indic_en

  return (
    <div className="top-banner">
      <div className="banner-chip">
        <span className="dot pulse" />
        <span>LAN: <strong>{ip}:8765</strong></span>
      </div>

      {health ? (
        <>
          <div className="banner-chip">
            <span className="dot" />
            <span>RAM: {health.ram_free_gb}GB free / {health.ram_gb}GB</span>
          </div>

          <div className="banner-chip">
            <span className="dot" />
            <span>Disk: {health.disk_free_gb}GB free</span>
          </div>

          <div className="banner-chip">
            <span className={`dot ${allModelsLoaded ? '' : 'amber'}`} />
            <span>
              Models: {allModelsLoaded ? (
                <span style={{ color: 'var(--green-accent)' }}>Ready</span>
              ) : (
                <span style={{ color: 'var(--amber)' }}>Loading…</span>
              )}
            </span>
          </div>

          {health.queue_depth > 0 && (
            <div className="banner-chip">
              <span className="dot amber" />
              <span>Queue: {health.queue_depth} job(s)</span>
            </div>
          )}

          {health.review_pending > 0 && (
            <div className="banner-chip">
              <span className="dot amber" />
              <span>{health.review_pending} segment(s) need review</span>
            </div>
          )}
        </>
      ) : (
        <div className="banner-chip">
          <span className="dot red" />
          <span style={{ color: 'var(--text-dim)' }}>Connecting…</span>
        </div>
      )}
    </div>
  )
}
