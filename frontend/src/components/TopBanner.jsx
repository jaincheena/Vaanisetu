import React, { useState, useEffect } from 'react'
import DemoTourModal from './DemoTourModal'

export default function TopBanner() {
  const [health, setHealth] = useState(null)
  const [showTour, setShowTour] = useState(false)
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

  const allModelsLoaded = health?.models_ready || health?.jit_mode || (
    health?.models_loaded &&
    health.models_loaded.whisper &&
    health.models_loaded.en_indic
  )

  return (
    <>
      <div className="top-banner" style={{ justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
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
                    <span style={{ color: 'var(--green)', fontWeight: 700 }}>Ready (AgriShield™ ON)</span>
                  ) : (
                    <span style={{ color: 'var(--amber)', fontWeight: 700 }}>Loading…</span>
                  )}
                </span>
              </div>

              {health.queue_depth > 0 && (
                <div className="banner-chip">
                  <span className="dot amber" />
                  <span>Queue: <strong>{health.queue_depth}</strong> job(s)</span>
                </div>
              )}

              {health.review_pending > 0 && (
                <div className="banner-chip">
                  <span className="dot amber" />
                  <span><strong style={{ color: '#DC2626' }}>{health.review_pending}</strong> segment(s) need review</span>
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

        <div>
          <button
            onClick={() => setShowTour(true)}
            style={{
              background: 'linear-gradient(135deg, #D97706 0%, #B45309 100%)',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: 20,
              padding: '7px 16px',
              fontSize: 12.5,
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              boxShadow: '0 2px 8px rgba(217, 119, 6, 0.3)',
              transition: 'transform 0.15s ease, box-shadow 0.15s ease'
            }}
          >
            <span>💡</span>
            <span>BAIF User Guide & Tour</span>
          </button>
        </div>

        {/* Subtle Ambient Real-Time Water Stream Flow */}
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 1.5,
          overflow: 'hidden',
          background: 'rgba(255, 255, 255, 0.03)',
          pointerEvents: 'none',
          opacity: 0.5
        }}>
          <div style={{
            width: '200%',
            height: '100%',
            background: 'linear-gradient(90deg, transparent 0%, #059669 20%, #10B981 35%, #38BDF8 50%, #F59E0B 65%, #10B981 80%, transparent 100%)',
            backgroundSize: '50% 100%',
            animation: 'waterStreamShimmer 5s linear infinite'
          }} />
        </div>
      </div>

      {showTour && (
        <DemoTourModal
          onClose={() => setShowTour(false)}
          onSelectScenario={(scId) => {
            setShowTour(false)
          }}
        />
      )}
    </>
  )
}
