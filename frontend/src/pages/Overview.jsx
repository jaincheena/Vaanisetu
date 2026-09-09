import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const INDIC_SCRIPTS = [
  { script: 'मराठी', lang: 'Marathi', icon: '🚩', color: '#FBBF24' },
  { script: 'हिन्दी', lang: 'Hindi', icon: '🌾', color: '#34D399' },
  { script: 'ગુજરાતી', lang: 'Gujarati', icon: '🌱', color: '#F59E0B' },
  { script: 'ಕನ್ನಡ', lang: 'Kannada', icon: '🌴', color: '#34D399' },
  { script: 'বাংলা', lang: 'Bengali', icon: '🌊', color: '#67E8F9' },
  { script: 'English', lang: 'English', icon: '🌐', color: '#CBD5E1' },
]

export default function Overview() {
  const navigate = useNavigate()
  const [health, setHealth] = useState(null)
  const [scenarios, setScenarios] = useState([])

  useEffect(() => {
    fetch('/api/health')
      .then(r => r.json())
      .then(setHealth)
      .catch(() => {})

    fetch('/api/jobs/scenarios')
      .then(r => r.json())
      .then(setScenarios)
      .catch(() => {})
  }, [])

  return (
    <div className="overview-page" style={{ maxWidth: 1200, margin: '0 auto', paddingBottom: 80, position: 'relative' }}>
      {/* ── 1. Enhanced Visual Dark Hero Banner ── */}
      <div style={{
        background: 'linear-gradient(135deg, #0B1120 0%, #0F1A2E 50%, #05261F 100%)',
        border: '1.5px solid rgba(245, 158, 11, 0.4)',
        borderRadius: 24,
        padding: '38px 42px 34px',
        marginBottom: 44,
        boxShadow: '0 20px 50px -15px rgba(0, 0, 0, 0.8), inset 0 1px 0 rgba(255, 255, 255, 0.15)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Subtle Ambient Glow */}
        <div style={{ position: 'absolute', top: -30, right: 30, pointerEvents: 'none', zIndex: 0 }}>
          <div className="ambient-particle-1" style={{ width: 220, height: 220, opacity: 0.25, animation: 'sunGlow 7s ease-in-out infinite' }} />
        </div>
        <div style={{ position: 'absolute', bottom: -20, left: 30, pointerEvents: 'none', zIndex: 0 }}>
          <div className="ambient-particle-2" style={{ width: 220, height: 220, opacity: 0.2 }} />
        </div>

        {/* Top Badges Bar */}
        <div style={{ position: 'relative', zIndex: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
            <span className="badge green" style={{ fontSize: 11.5, letterSpacing: 0.5, fontWeight: 800, padding: '6px 16px', borderRadius: 20 }}>
              🌾 BHARATIYA AGRO INDUSTRIES FOUNDATION (BAIF)
            </span>
            <span className="badge amber" style={{ fontSize: 11.5, fontWeight: 800, padding: '6px 16px', borderRadius: 20 }}>
              ⚡ 100% OFFLINE AIR-GAPPED AI · NO INTERNET
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#34D399', fontWeight: 700, background: 'rgba(16, 185, 129, 0.15)', padding: '5px 14px', borderRadius: 20, border: '1px solid rgba(16, 185, 129, 0.3)' }}>
            <span className="status-dot green" />
            <span>Pune Central HQ & 16 State Centers</span>
          </div>
        </div>

        {/* Hero Grid */}
        <div style={{ position: 'relative', zIndex: 1, display: 'grid', gridTemplateColumns: 'minmax(0, 1.3fr) minmax(0, 0.9fr)', gap: 36, alignItems: 'center' }}>
          {/* Left Hero Content */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 18, marginBottom: 18 }}>
              {/* Illuminated Glassmorphic 3D Emblem */}
              <div style={{
                position: 'relative',
                width: 68,
                height: 68,
                borderRadius: 20,
                background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.3) 0%, rgba(16, 185, 129, 0.35) 100%)',
                border: '1.5px solid rgba(245, 158, 11, 0.6)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 36,
                boxShadow: '0 12px 32px -4px rgba(245, 158, 11, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.4)',
                flexShrink: 0
              }}>
                <span style={{ filter: 'drop-shadow(0 2px 10px rgba(245, 158, 11, 0.6))' }}>🌱</span>
                {/* Animated Bioluminescent Pulse Ring */}
                <div style={{
                  position: 'absolute',
                  inset: -4,
                  borderRadius: 24,
                  border: '1.5px solid rgba(52, 211, 153, 0.5)',
                  animation: 'pulse 3s ease-in-out infinite',
                  pointerEvents: 'none'
                }} />
              </div>

              <div>
                <h1 style={{
                  fontSize: 42,
                  fontWeight: 900,
                  margin: 0,
                  letterSpacing: '-1px',
                  lineHeight: 1.15,
                  fontFamily: "'Plus Jakarta Sans', sans-serif",
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12,
                  flexWrap: 'wrap'
                }}>
                  <span style={{
                    background: 'linear-gradient(135deg, #FFFFFF 20%, #FDE68A 60%, #34D399 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    filter: 'drop-shadow(0 2px 12px rgba(245, 158, 11, 0.25))'
                  }}>
                    VaaniSetu
                  </span>
                  <span style={{
                    fontSize: 18,
                    fontWeight: 800,
                    color: '#FDE68A',
                    background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.3) 0%, rgba(217, 119, 6, 0.4) 100%)',
                    border: '1.5px solid rgba(245, 158, 11, 0.6)',
                    padding: '4px 14px',
                    borderRadius: 10,
                    boxShadow: '0 4px 14px rgba(245, 158, 11, 0.35)',
                    letterSpacing: '0.4px',
                    verticalAlign: 'middle'
                  }}>
                    वाणीसेतु
                  </span>
                </h1>

                {/* Illuminated High-Tech Subtitle Pill */}
                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 10,
                  background: 'rgba(11, 17, 32, 0.85)',
                  border: '1px solid rgba(52, 211, 153, 0.35)',
                  borderRadius: 30,
                  padding: '5px 16px',
                  marginTop: 8,
                  boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span className="status-dot green" style={{ width: 8, height: 8 }} />
                    <span style={{ fontSize: 11.5, fontWeight: 800, color: '#94A3B8', letterSpacing: '0.8px', textTransform: 'uppercase' }}>
                      BAIF AI VOICE PLATFORM
                    </span>
                  </div>
                  <span style={{ color: '#F59E0B', fontSize: 14, fontWeight: 900 }}>✦</span>
                  <span style={{
                    fontSize: 13,
                    fontWeight: 800,
                    background: 'linear-gradient(135deg, #FBBF24 0%, #34D399 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    letterSpacing: '0.3px'
                  }}>
                    आवाज़ से खेत तक
                  </span>
                </div>
              </div>
            </div>

            <p style={{
              fontSize: 15,
              color: '#CBD5E1',
              lineHeight: 1.7,
              marginBottom: 24,
              fontWeight: 500
            }}>
              Multi-lingual voice translation & neural localization platform built for BAIF field extension. Translate agricultural advisories, veterinary handbooks, and farmer voice queries across 14 Indic languages on laptops without internet.
            </p>

            {/* Action Buttons */}
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <button
                type="button"
                className="btn btn-primary btn-lg"
                onClick={() => navigate('/upload')}
                style={{
                  fontSize: 14.5,
                  padding: '13px 26px',
                  fontWeight: 800,
                  borderRadius: 10,
                  boxShadow: '0 4px 16px rgba(245, 158, 11, 0.4)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8
                }}
              >
                <span>🚀</span> Open Advisory Studio
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-lg"
                onClick={() => navigate('/docs')}
                style={{ fontSize: 14.5, padding: '13px 20px', fontWeight: 600, borderRadius: 10 }}
              >
                📖 Platform Manual
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-lg"
                onClick={() => navigate('/training')}
                style={{ fontSize: 14.5, padding: '13px 20px', fontWeight: 600, borderRadius: 10 }}
              >
                🎓 Training Academy
              </button>
            </div>
          </div>

          {/* Right Visual Graphic Card: Dynamic Moving Neural Engine */}
          <div style={{
            background: 'linear-gradient(145deg, #0B1120 0%, #0F172A 50%, #032019 100%)',
            border: '1.5px solid rgba(255, 255, 255, 0.16)',
            borderRadius: 22,
            padding: '24px 26px',
            boxShadow: '0 24px 48px -10px rgba(0, 0, 0, 0.8), 0 0 30px rgba(16, 185, 129, 0.15), inset 0 1.5px 0 rgba(255, 255, 255, 0.25)',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {/* Ambient Background Wave Gradient */}
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '100%',
              background: 'radial-gradient(ellipse at 80% 20%, rgba(52, 211, 153, 0.12) 0%, transparent 60%)',
              pointerEvents: 'none'
            }} />

            {/* Header: Live Spectrum Equalizer */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18, borderBottom: '1px solid rgba(255, 255, 255, 0.1)', paddingBottom: 14 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ fontSize: 22, filter: 'drop-shadow(0 0 8px #10B981)' }}>🎙️</span>
                <div>
                  <strong style={{ fontSize: 14.5, color: '#F8FAFC', fontWeight: 800, letterSpacing: '0.2px', display: 'block' }}>
                    Live Neural Voice Stream
                  </strong>
                  <span style={{ fontSize: 11, color: '#34D399', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 5 }}>
                    <span className="status-dot green" style={{ width: 6, height: 6 }} /> REAL-TIME TRANSLATION MATRIX
                  </span>
                </div>
              </div>

              {/* Sleek Contained Audio Wave Capsule */}
              <div className="audio-wave-capsule">
                <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <span className="status-dot green" style={{ width: 7, height: 7, animation: 'pulse 2s infinite' }} />
                  <span style={{ fontSize: 10.5, fontWeight: 800, color: '#34D399', letterSpacing: '0.6px' }}>
                    16kHz VAD
                  </span>
                </div>
                <div className="audio-wave" style={{ height: 16 }}>
                  <span className="audio-wave-bar" />
                  <span className="audio-wave-bar" />
                  <span className="audio-wave-bar" />
                  <span className="audio-wave-bar" />
                  <span className="audio-wave-bar" />
                </div>
              </div>
            </div>

            {/* ── REAL-TIME MOVING NEURAL PIPELINE FLOW ── */}
            <div style={{
              background: '#080D18',
              borderRadius: 14,
              padding: '14px 16px',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              marginBottom: 16,
              boxShadow: 'inset 0 2px 6px rgba(0, 0, 0, 0.7)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'relative' }}>
                {/* Connecting Moving Flow Line */}
                <div style={{
                  position: 'absolute',
                  top: '50%',
                  left: 24,
                  right: 24,
                  height: 3,
                  background: 'rgba(255, 255, 255, 0.08)',
                  transform: 'translateY(-50%)',
                  zIndex: 0,
                  borderRadius: 2,
                  overflow: 'hidden'
                }}>
                  {/* Moving Left-to-Right Signal Packet */}
                  <div style={{
                    position: 'absolute',
                    top: 0,
                    width: 40,
                    height: '100%',
                    background: 'linear-gradient(90deg, transparent, #10B981, #F59E0B, transparent)',
                    animation: 'neuralFlowPulse 2.4s ease-in-out infinite',
                    boxShadow: '0 0 10px #10B981'
                  }} />
                </div>

                {/* Node 1: Input Voice */}
                <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                  <div style={{
                    width: 36,
                    height: 36,
                    borderRadius: 10,
                    background: 'linear-gradient(135deg, #1E293B, #0F172A)',
                    border: '1.5px solid #38BDF8',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 16,
                    boxShadow: '0 0 12px rgba(56, 189, 248, 0.3)'
                  }}>
                    🎙️
                  </div>
                  <span style={{ fontSize: 10.5, fontWeight: 800, color: '#38BDF8' }}>Voice ASR</span>
                </div>

                {/* Node 2: AgriShield Validator */}
                <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                  <div style={{
                    width: 36,
                    height: 36,
                    borderRadius: 10,
                    background: 'linear-gradient(135deg, #1E293B, #0F172A)',
                    border: '1.5px solid #10B981',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 16,
                    boxShadow: '0 0 12px rgba(16, 185, 129, 0.4)',
                    animation: 'pulse 2.5s ease-in-out infinite'
                  }}>
                    🛡️
                  </div>
                  <span style={{ fontSize: 10.5, fontWeight: 800, color: '#34D399' }}>AgriShield™</span>
                </div>

                {/* Node 3: 14 Indic Dialects */}
                <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                  <div style={{
                    width: 36,
                    height: 36,
                    borderRadius: 10,
                    background: 'linear-gradient(135deg, #1E293B, #0F172A)',
                    border: '1.5px solid #F59E0B',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 16,
                    boxShadow: '0 0 12px rgba(245, 158, 11, 0.35)'
                  }}>
                    🌐
                  </div>
                  <span style={{ fontSize: 10.5, fontWeight: 800, color: '#FBBF24' }}>14 Dialects</span>
                </div>
              </div>
            </div>

            {/* Live Moving Simulated Translation Preview Stream */}
            <div style={{
              background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(245, 158, 11, 0.12) 100%)',
              border: '1px solid rgba(52, 211, 153, 0.35)',
              borderRadius: 12,
              padding: '12px 14px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: 12
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, minWidth: 0 }}>
                <span style={{ fontSize: 18, animation: 'iconBob 3s ease-in-out infinite' }}>⚡</span>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontSize: 11, color: '#34D399', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.4px' }}>
                    100% Offline AI Inference
                  </div>
                  <div style={{ fontSize: 12.5, color: '#F8FAFC', fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    मराठी (Marathi) · हिन्दी · ગુજરાતી · తెలుగు
                  </div>
                </div>
              </div>
              <span className="badge green" style={{ fontSize: 10.5, fontWeight: 800, padding: '3px 8px', flexShrink: 0 }}>
                0ms Internet
              </span>
            </div>
          </div>
        </div>

        {/* Supported Languages Interactive Pill Matrix */}
        <div style={{ position: 'relative', zIndex: 1, marginTop: 26, paddingTop: 20, borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 12, fontWeight: 800, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.6px' }}>
              Supported Regional Languages:
            </span>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {INDIC_SCRIPTS.map(s => (
                <div
                  key={s.script}
                  style={{
                    background: 'linear-gradient(180deg, #131E35 0%, #0B1120 100%)',
                    border: '1.5px solid rgba(255, 255, 255, 0.14)',
                    color: '#F8FAFC',
                    fontSize: 12,
                    fontWeight: 700,
                    padding: '6px 14px',
                    borderRadius: 10,
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 6,
                    boxShadow: '0 4px 10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.15)',
                    transition: 'all 0.22s cubic-bezier(0.16, 1, 0.3, 1)',
                    cursor: 'default',
                    transform: 'perspective(600px) translateZ(0)'
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.transform = 'perspective(600px) translateY(-3px) translateZ(8px)'
                    e.currentTarget.style.borderColor = s.color
                    e.currentTarget.style.boxShadow = `0 8px 20px rgba(0, 0, 0, 0.7), 0 0 14px ${s.color}35`
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.transform = 'perspective(600px) translateZ(0)'
                    e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.14)'
                    e.currentTarget.style.boxShadow = '0 4px 10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.15)'
                  }}
                >
                  <span style={{ fontSize: 13, filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.4))' }}>{s.icon}</span>
                  <span style={{ fontWeight: 800, color: s.color }}>{s.script}</span>
                  <span style={{ fontSize: 11, color: '#94A3B8', fontWeight: 600 }}>({s.lang})</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── 2. Platform Capabilities ── */}
      <div style={{ marginBottom: 44 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20, flexWrap: 'wrap', gap: 8 }}>
          <div>
            <h2 style={{ fontSize: 20, fontWeight: 800, margin: 0, color: '#F8FAFC', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              🏛️ Platform Capabilities Built for Field Operations
            </h2>
            <p style={{ fontSize: 13, color: '#94A3B8', margin: '4px 0 0', fontWeight: 500 }}>
              Engineered specifically for rural grassroots extension without external internet requirements
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 20 }}>
          {/* Card 1 */}
          <div className="card" style={{ background: '#111C30', padding: '26px 24px', borderRadius: 18 }}>
            <div style={{
              width: 52,
              height: 52,
              borderRadius: 14,
              background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.3) 0%, rgba(217, 119, 6, 0.4) 100%)',
              border: '1.5px solid rgba(245, 158, 11, 0.6)',
              boxShadow: '0 8px 20px rgba(245, 158, 11, 0.35)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 24,
              marginBottom: 16,
              animation: 'iconBob 4s ease-in-out infinite'
            }}>
              📢
            </div>
            <h3 style={{ fontSize: 16.5, fontWeight: 700, color: '#F8FAFC', marginBottom: 8 }}>
              Multi-Format Broadcast
            </h3>
            <p style={{ fontSize: 13.5, color: '#CBD5E1', lineHeight: 1.6, margin: 0, fontWeight: 500 }}>
              Synthesizes training advisories into video, audio voice notes, phone calls, printed slips, and subtitles all at once.
            </p>
            <div style={{ marginTop: 16, paddingTop: 12, borderTop: '1px solid rgba(255, 255, 255, 0.08)', display: 'flex', gap: 6 }}>
              <span className="badge grey" style={{ fontSize: 11, fontWeight: 700 }}>🎬 HD MP4</span>
              <span className="badge grey" style={{ fontSize: 11, fontWeight: 700 }}>📞 8kHz IVR</span>
              <span className="badge grey" style={{ fontSize: 11, fontWeight: 700 }}>📄 DOCX</span>
            </div>
          </div>

          {/* Card 2 */}
          <div className="card" style={{ background: '#111C30', padding: '26px 24px', borderRadius: 18 }}>
            <div style={{
              width: 52,
              height: 52,
              borderRadius: 14,
              background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(79, 70, 229, 0.4) 100%)',
              border: '1.5px solid rgba(99, 102, 241, 0.6)',
              boxShadow: '0 8px 20px rgba(99, 102, 241, 0.35)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 24,
              marginBottom: 16,
              animation: 'iconBob 4.5s ease-in-out infinite 0.5s'
            }}>
              🎙️
            </div>
            <h3 style={{ fontSize: 16.5, fontWeight: 700, color: '#F8FAFC', marginBottom: 8 }}>
              Farmer Voice Assistant
            </h3>
            <p style={{ fontSize: 13.5, color: '#CBD5E1', lineHeight: 1.6, margin: 0, fontWeight: 500 }}>
              Captures field voice queries from farmers in Marathi, Hindi, or Gujarati, and transcribes them for Pune HQ agronomists.
            </p>
            <div style={{ marginTop: 16, paddingTop: 12, borderTop: '1px solid rgba(255, 255, 255, 0.08)', display: 'flex', gap: 6 }}>
              <span className="badge grey" style={{ fontSize: 11, fontWeight: 700 }}>Whisper INT8</span>
              <span className="badge grey" style={{ fontSize: 11, fontWeight: 700 }}>VAD Detection</span>
            </div>
          </div>

          {/* Card 3 */}
          <div className="card" style={{ background: '#111C30', padding: '26px 24px', borderRadius: 18 }}>
            <div style={{
              width: 52,
              height: 52,
              borderRadius: 14,
              background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.3) 0%, rgba(5, 150, 105, 0.4) 100%)',
              border: '1.5px solid rgba(16, 185, 129, 0.6)',
              boxShadow: '0 8px 20px rgba(16, 185, 129, 0.35)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 24,
              marginBottom: 16,
              animation: 'iconBob 3.8s ease-in-out infinite 1s'
            }}>
              🛡️
            </div>
            <h3 style={{ fontSize: 16.5, fontWeight: 700, color: '#F8FAFC', marginBottom: 8 }}>
              Confidence Review Gate
            </h3>
            <p style={{ fontSize: 13.5, color: '#CBD5E1', lineHeight: 1.6, margin: 0, fontWeight: 500 }}>
              Holds back uncertain translations — chemical dosages, drug formulations, and fertilizer ratios — for human expert clearance.
            </p>
            <div style={{ marginTop: 16, paddingTop: 12, borderTop: '1px solid rgba(255, 255, 255, 0.08)', display: 'flex', gap: 6 }}>
              <span className="badge green" style={{ fontSize: 11, fontWeight: 700 }}>&gt;98% Accuracy</span>
              <span className="badge amber" style={{ fontSize: 11, fontWeight: 700 }}>Review Queue</span>
            </div>
          </div>

          {/* Card 4 */}
          <div className="card" style={{ background: '#111C30', padding: '26px 24px', borderRadius: 18 }}>
            <div style={{
              width: 52,
              height: 52,
              borderRadius: 14,
              background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.3) 0%, rgba(185, 28, 28, 0.4) 100%)',
              border: '1.5px solid rgba(239, 68, 68, 0.6)',
              boxShadow: '0 8px 20px rgba(239, 68, 68, 0.35)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 24,
              marginBottom: 16,
              animation: 'iconBob 4.2s ease-in-out infinite 1.5s'
            }}>
              📚
            </div>
            <h3 style={{ fontSize: 16.5, fontWeight: 700, color: '#F8FAFC', marginBottom: 8 }}>
              Protected Farm Glossary
            </h3>
            <p style={{ fontSize: 13.5, color: '#CBD5E1', lineHeight: 1.6, margin: 0, fontWeight: 500 }}>
              Protects 120+ verified fertilizers, crop medicines, cattle vaccines, and government schemes from AI mistranslation.
            </p>
            <div style={{ marginTop: 16, paddingTop: 12, borderTop: '1px solid rgba(255, 255, 255, 0.08)', display: 'flex', gap: 6 }}>
              <span className="badge grey" style={{ fontSize: 11, fontWeight: 700 }}>14 Scripts</span>
              <span className="badge grey" style={{ fontSize: 11, fontWeight: 700 }}>Memory Sync</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── 3. 1-Click Field Demonstration Scenarios ── */}
      <div style={{ marginBottom: 48 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20, flexWrap: 'wrap', gap: 8 }}>
          <div>
            <h2 style={{ fontSize: 20, fontWeight: 800, margin: 0, color: '#F8FAFC', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              🧪 1-Click Field Demonstration Scenarios
            </h2>
            <p style={{ fontSize: 13.5, color: '#94A3B8', margin: '4px 0 0', fontWeight: 500 }}>
              Select any pre-configured BAIF advisory to test end-to-end multi-lingual synthesis
            </p>
          </div>
          <span className="badge green" style={{ fontSize: 11.5, padding: '6px 14px', fontWeight: 700 }}>
            ✓ Verified &gt;98% Precision
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
          {scenarios.map((sc, idx) => (
            <div
              key={sc.id}
              className="card"
              style={{
                background: '#111C30',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                borderRadius: 16,
                padding: '24px',
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <strong style={{ fontSize: 15.5, color: '#F8FAFC', fontWeight: 700 }}>{sc.title}</strong>
                  <span className="badge amber" style={{ fontSize: 11, fontWeight: 700 }}>
                    Scenario {idx + 1}
                  </span>
                </div>
                <p style={{ fontSize: 13, color: '#F59E0B', fontWeight: 600, marginBottom: 10 }}>
                  {sc.subtitle}
                </p>
                <div style={{ fontSize: 12.5, color: '#CBD5E1', marginBottom: 12, fontWeight: 500 }}>
                  <strong style={{ color: '#F8FAFC' }}>Routing:</strong> {sc.source_lang} → {sc.target_langs?.join(', ')}
                </div>
                <div style={{
                  fontSize: 12.5,
                  color: '#94A3B8',
                  background: '#0B1120',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  padding: '12px 14px',
                  borderRadius: 8,
                  maxHeight: 74,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  lineHeight: 1.55,
                  fontWeight: 500
                }}>
                  {sc.sample_text}
                </div>
              </div>

              <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid rgba(255, 255, 255, 0.08)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: 12, color: '#94A3B8', fontWeight: 600 }}>
                  📦 {sc.output_formats?.length || 6} Formats
                </span>
                <button
                  type="button"
                  className="btn btn-sm btn-primary"
                  onClick={() => navigate('/upload', { state: { autoLoadScenarioId: sc.id } })}
                  style={{ fontWeight: 800, padding: '8px 16px', borderRadius: 8 }}
                >
                  🚀 Run in Studio →
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── 4. Simple 3-Step Field Workflow ── */}
      <div className="card" style={{
        background: '#111C30',
        borderRadius: 18,
        padding: '30px 32px'
      }}>
        <div style={{ textAlign: 'center', marginBottom: 20 }}>
          <h3 style={{ fontSize: 18, fontWeight: 800, color: '#F8FAFC', margin: 0 }}>
            🌾 How VaaniSetu Operates in the Field
          </h3>
          <p style={{ fontSize: 13, color: '#94A3B8', marginTop: 3, fontWeight: 500 }}>
            Simple 3-step workflow from agronomy research to village farmers
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16 }}>
          <div style={{ background: '#0B1120', padding: '16px 18px', borderRadius: 12, border: '1px solid rgba(255, 255, 255, 0.08)' }}>
            <div style={{ fontSize: 26, marginBottom: 6 }}>1️⃣</div>
            <h4 style={{ fontSize: 14, fontWeight: 700, color: '#F8FAFC', margin: '0 0 4px 0' }}>
              Input Advisory or Voice
            </h4>
            <p style={{ fontSize: 12.5, color: '#94A3B8', lineHeight: 1.5, margin: 0, fontWeight: 500 }}>
              Enter advisory text, upload a video, or record raw farmer voice queries in village dialects.
            </p>
          </div>

          <div style={{ background: '#0B1120', padding: '16px 18px', borderRadius: 12, border: '1px solid rgba(255, 255, 255, 0.08)' }}>
            <div style={{ fontSize: 26, marginBottom: 6 }}>2️⃣</div>
            <h4 style={{ fontSize: 14, fontWeight: 700, color: '#F8FAFC', margin: '0 0 4px 0' }}>
              AI Synthesis & Safety Check
            </h4>
            <p style={{ fontSize: 12.5, color: '#94A3B8', lineHeight: 1.5, margin: 0, fontWeight: 500 }}>
              AgriShield™ protects dosages while offline AI translates and generates natural Indic voices.
            </p>
          </div>

          <div style={{ background: '#0B1120', padding: '16px 18px', borderRadius: 12, border: '1px solid rgba(255, 255, 255, 0.08)' }}>
            <div style={{ fontSize: 26, marginBottom: 6 }}>3️⃣</div>
            <h4 style={{ fontSize: 14, fontWeight: 700, color: '#F8FAFC', margin: '0 0 4px 0' }}>
              Multi-Channel Delivery
            </h4>
            <p style={{ fontSize: 12.5, color: '#94A3B8', lineHeight: 1.5, margin: 0, fontWeight: 500 }}>
              Outputs ready-to-share WhatsApp videos, automated phone IVR calls, and printed handouts.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
