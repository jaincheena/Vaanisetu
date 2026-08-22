import React from 'react'

export default function AnimatedAgriBackground() {
  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      pointerEvents: 'none',
      zIndex: 0,
      overflow: 'hidden'
    }}>
      {/* 1. Soft Amber Ambient Light (Top-Right) */}
      <div style={{
        position: 'absolute',
        top: '-15%',
        right: '-5%',
        width: 550,
        height: 550,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(245, 158, 11, 0.08) 0%, rgba(217, 119, 6, 0.02) 50%, transparent 70%)',
        animation: 'sunGlow 12s ease-in-out infinite'
      }} />

      {/* 2. Soft Emerald Neon Glow (Bottom-Left) */}
      <div style={{
        position: 'absolute',
        bottom: '-15%',
        left: '10%',
        width: 600,
        height: 600,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(16, 185, 129, 0.08) 0%, rgba(5, 150, 105, 0.02) 55%, transparent 70%)',
        animation: 'floatSlow 16s ease-in-out infinite'
      }} />

      {/* ─────────────────────────────────────────────────────────────
          🌊 REAL-TIME WATER FLOW STREAM (Gentle Ambient Background River)
          Calibrated to be completely non-intrusive behind all UI elements
          ───────────────────────────────────────────────────────────── */}
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: 100,
        overflow: 'hidden',
        opacity: 0.35,
        pointerEvents: 'none',
        zIndex: 0
      }}>
        {/* Deep Current Wave Layer (Back) - Gentle 22s Left-to-Right */}
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          width: '200%',
          height: 80,
          display: 'flex',
          animation: 'waterWaveFlowRight 22s linear infinite',
          willChange: 'transform'
        }}>
          <svg viewBox="0 0 1440 80" preserveAspectRatio="none" style={{ width: '50%', height: '100%', flexShrink: 0 }}>
            <path
              d="M0,25 C320,55 480,5 720,30 C960,55 1120,8 1440,28 L1440,80 L0,80 Z"
              fill="url(#deepWaterGradient)"
            />
            <defs>
              <linearGradient id="deepWaterGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="rgba(5, 150, 105, 0.12)" />
                <stop offset="50%" stopColor="rgba(14, 165, 233, 0.15)" />
                <stop offset="100%" stopColor="rgba(5, 150, 105, 0.12)" />
              </linearGradient>
            </defs>
          </svg>
          <svg viewBox="0 0 1440 80" preserveAspectRatio="none" style={{ width: '50%', height: '100%', flexShrink: 0 }}>
            <path
              d="M0,25 C320,55 480,5 720,30 C960,55 1120,8 1440,28 L1440,80 L0,80 Z"
              fill="url(#deepWaterGradient)"
            />
          </svg>
        </div>

        {/* Mid-Stream Aqua Wave Layer (Middle) - Gentle 14s Left-to-Right */}
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          width: '200%',
          height: 65,
          display: 'flex',
          animation: 'waterWaveFlowRight 14s linear infinite',
          willChange: 'transform'
        }}>
          <svg viewBox="0 0 1440 65" preserveAspectRatio="none" style={{ width: '50%', height: '100%', flexShrink: 0 }}>
            <path
              d="M0,20 C360,50 540,5 720,25 C900,50 1080,8 1440,22 L1440,65 L0,65 Z"
              fill="url(#midWaterGradient)"
            />
            <defs>
              <linearGradient id="midWaterGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="rgba(56, 189, 248, 0.15)" />
                <stop offset="50%" stopColor="rgba(52, 211, 153, 0.18)" />
                <stop offset="100%" stopColor="rgba(56, 189, 248, 0.15)" />
              </linearGradient>
            </defs>
          </svg>
          <svg viewBox="0 0 1440 65" preserveAspectRatio="none" style={{ width: '50%', height: '100%', flexShrink: 0 }}>
            <path
              d="M0,20 C360,50 540,5 720,25 C900,50 1080,8 1440,22 L1440,65 L0,65 Z"
              fill="url(#midWaterGradient)"
            />
          </svg>
        </div>

        {/* Crest Surface Shimmer Layer - Gentle 9s Left-to-Right */}
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          width: '200%',
          height: 45,
          display: 'flex',
          animation: 'waterWaveFlowRight 9s linear infinite',
          willChange: 'transform'
        }}>
          <svg viewBox="0 0 1440 45" preserveAspectRatio="none" style={{ width: '50%', height: '100%', flexShrink: 0 }}>
            <path
              d="M0,12 C240,30 480,4 720,16 C960,30 1200,6 1440,14 L1440,45 L0,45 Z"
              fill="url(#crestWaterGradient)"
            />
            <defs>
              <linearGradient id="crestWaterGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="rgba(245, 158, 11, 0.1)" />
                <stop offset="35%" stopColor="rgba(16, 185, 129, 0.2)" />
                <stop offset="70%" stopColor="rgba(56, 189, 248, 0.2)" />
                <stop offset="100%" stopColor="rgba(245, 158, 11, 0.1)" />
              </linearGradient>
            </defs>
          </svg>
          <svg viewBox="0 0 1440 45" preserveAspectRatio="none" style={{ width: '50%', height: '100%', flexShrink: 0 }}>
            <path
              d="M0,12 C240,30 480,4 720,16 C960,30 1200,6 1440,14 L1440,45 L0,45 Z"
              fill="url(#crestWaterGradient)"
            />
          </svg>
        </div>

        {/* Soft Micro Water Ripples Streaming Left to Right */}
        <div style={{
          position: 'absolute',
          bottom: 25,
          left: 0,
          width: 8,
          height: 8,
          borderRadius: '50%',
          background: 'radial-gradient(circle, #38BDF8 0%, rgba(56, 189, 248, 0) 75%)',
          boxShadow: '0 0 8px #38BDF8',
          opacity: 0.35,
          animation: 'waterParticleStream 12s cubic-bezier(0.4, 0, 0.6, 1) infinite'
        }} />

        <div style={{
          position: 'absolute',
          bottom: 40,
          left: 0,
          width: 10,
          height: 10,
          borderRadius: '50%',
          background: 'radial-gradient(circle, #34D399 0%, rgba(52, 211, 153, 0) 75%)',
          boxShadow: '0 0 10px #34D399',
          opacity: 0.35,
          animation: 'waterParticleStream 16s cubic-bezier(0.4, 0, 0.6, 1) infinite 4s'
        }} />
      </div>

      {/* 3. Subtle Floating Bioluminescent Leaves */}
      <div style={{
        position: 'absolute',
        top: '10%',
        right: '5%',
        fontSize: 20,
        animation: 'floatSlow 8s ease-in-out infinite',
        opacity: 0.35,
        filter: 'drop-shadow(0 0 6px rgba(52, 211, 153, 0.3))'
      }}>
        🍃
      </div>

      <div style={{
        position: 'absolute',
        bottom: '20%',
        left: '3%',
        fontSize: 18,
        animation: 'floatReverse 10s ease-in-out infinite',
        opacity: 0.3,
        filter: 'drop-shadow(0 0 6px rgba(251, 191, 36, 0.25))'
      }}>
        🌿
      </div>

      {/* 4. Bottom-Right Swaying Wheat Silhouette */}
      <div style={{
        position: 'absolute',
        bottom: 0,
        right: 30,
        display: 'flex',
        alignItems: 'flex-end',
        gap: 6,
        opacity: 0.2,
        userSelect: 'none',
        filter: 'drop-shadow(0 0 8px rgba(245, 158, 11, 0.15))',
        zIndex: 1
      }}>
        <span className="wheat-sway-1" style={{ fontSize: 52 }}>🌾</span>
        <span className="wheat-sway-2" style={{ fontSize: 64 }}>🌾</span>
        <span className="wheat-sway-3" style={{ fontSize: 56 }}>🌾</span>
      </div>

      {/* 5. Bottom-Left Swaying Wheat Silhouette */}
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 20,
        display: 'flex',
        alignItems: 'flex-end',
        gap: 6,
        opacity: 0.18,
        userSelect: 'none',
        filter: 'drop-shadow(0 0 8px rgba(16, 185, 129, 0.15))',
        zIndex: 1
      }}>
        <span className="wheat-sway-2" style={{ fontSize: 44 }}>🌾</span>
        <span className="wheat-sway-1" style={{ fontSize: 54 }}>🌾</span>
      </div>
    </div>
  )
}
