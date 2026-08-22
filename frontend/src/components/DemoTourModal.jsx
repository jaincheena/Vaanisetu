import React, { useState } from 'react'

export default function DemoTourModal({ onClose, onSelectScenario }) {
  const [activeTab, setActiveTab] = useState('tour') // 'tour' | 'agrishield' | 'formats'
  const [step, setStep] = useState(1)

  const steps = [
    {
      num: 1,
      title: 'Step 1: Select Input Media or Advisory Script',
      icon: '📁',
      desc: 'Drag & drop any BAIF training video (.mp4), audio voice note (.mp3/.wav), field document (.docx/.pdf), or type directly into the text box. You can also click any 1-Click Realistic Agricultural Scenario on the dashboard.',
      highlight: 'Works 100% offline — zero cloud upload required.'
    },
    {
      num: 2,
      title: 'Step 2: Choose Target Regional Languages',
      icon: '🌐',
      desc: 'Select one or more regional Indian languages (Hindi, Marathi, Gujarati, Bengali, Telugu, Kannada, etc.). VaaniSetu translates across all languages concurrently with cached English pivot processing.',
      highlight: 'Ultra-fast INT8 pipeline optimized for basic field laptops (<650MB RAM).'
    },
    {
      num: 3,
      title: 'Step 3: AI Translation with AgriShield™ Protection',
      icon: '🛡️',
      desc: 'The AI pipeline transcribes with Whisper, shields 120+ agricultural entities (schemes, chemical dosages, cattle breeds), and generates synthetic audio with natural Indian pronunciation using Piper ONNX.',
      highlight: 'Critical terms like PM-KISAN, DAP, and Urea are guaranteed never to be mistranslated.'
    },
    {
      num: 4,
      title: 'Step 4: Interactive Review & Multi-Format Export',
      icon: '📦',
      desc: 'Listen to the audio directly in your browser, compare bilingual transcripts side-by-side, verify confidence badges (🟢/🟡), and download ready-to-share packages for WhatsApp, IVR keypad phones, and village handouts.',
      highlight: 'One click generates WhatsApp video chunks (<15MB), 8kHz IVR audio, Word docs, and subtitles.'
    }
  ]

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(15, 23, 42, 0.45)',
      backdropFilter: 'blur(6px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: 20
    }}>
      <div style={{
        background: '#111C30',
        border: '1.5px solid rgba(245, 158, 11, 0.4)',
        borderRadius: 'var(--radius)',
        maxWidth: 760,
        width: '100%',
        maxHeight: '90vh',
        overflowY: 'auto',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.8)',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Header */}
        <div style={{
          padding: '18px 24px',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: '#0B1120'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="brand-3d-emblem" style={{ width: 40, height: 40, fontSize: 20, borderRadius: 10 }}>
              <span>🌱</span>
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: 17, fontWeight: 800, color: '#F8FAFC', display: 'flex', alignItems: 'center', gap: 8 }}>
                <span>VaaniSetu</span>
                <span className="brand-3d-devanagari">वाणीसेतु</span>
                <span style={{ fontSize: 12, fontWeight: 600, color: '#94A3B8' }}>— Field Trainer Guide</span>
              </h3>
              <p style={{ margin: '2px 0 0', fontSize: 11.5, color: '#34D399', fontWeight: 700, letterSpacing: '0.4px' }}>
                BAIF AGRO VOICE BRIDGE · INTERACTIVE PLATFORM TOUR
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              fontSize: 20,
              cursor: 'pointer'
            }}
          >
            ✕
          </button>
        </div>

        {/* Navigation Tabs */}
        <div style={{
          display: 'flex',
          borderBottom: '1px solid var(--border)',
          background: 'var(--bg-input)'
        }}>
          {[
            ['tour', '🎬 4-Step Field Walkthrough'],
            ['agrishield', '🛡️ AgriShield™ & Quality Control'],
            ['formats', '📦 Multiformat Delivery Formats']
          ].map(([tab, label]) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                flex: 1,
                padding: '12px',
                border: 'none',
                background: activeTab === tab ? 'var(--bg-card)' : 'transparent',
                color: activeTab === tab ? 'var(--accent)' : 'var(--text-muted)',
                fontWeight: activeTab === tab ? 700 : 500,
                borderBottom: activeTab === tab ? '2px solid var(--accent)' : 'none',
                cursor: 'pointer',
                fontSize: 13
              }}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Body Content */}
        <div style={{ padding: 24, flex: 1 }}>
          {activeTab === 'tour' && (
            <div>
              {/* Stepper Header */}
              <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
                {steps.map(s => (
                  <div
                    key={s.num}
                    onClick={() => setStep(s.num)}
                    style={{
                      flex: 1,
                      textAlign: 'center',
                      padding: '8px 4px',
                      borderRadius: 'var(--radius-sm)',
                      background: step === s.num ? 'rgba(245,158,11,0.2)' : 'var(--bg-input)',
                      border: `1px solid ${step === s.num ? 'var(--accent)' : 'var(--border)'}`,
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                  >
                    <div style={{ fontSize: 16 }}>{s.icon}</div>
                    <div style={{ fontSize: 11, fontWeight: 600, color: step === s.num ? 'var(--accent)' : 'var(--text-dim)' }}>
                      Step {s.num}
                    </div>
                  </div>
                ))}
              </div>

              {/* Step Card */}
              {(() => {
                const cur = steps[step - 1]
                return (
                  <div style={{
                    background: 'var(--bg-input)',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius-sm)',
                    padding: 20
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                      <span style={{ fontSize: 28 }}>{cur.icon}</span>
                      <div>
                        <h4 style={{ margin: 0, fontSize: 17, color: 'var(--text)' }}>{cur.title}</h4>
                        <span style={{ fontSize: 12, color: 'var(--accent)', fontWeight: 600 }}>Step {cur.num} of 4</span>
                      </div>
                    </div>
                    <p style={{ fontSize: 14, lineHeight: 1.6, color: 'var(--text-muted)', marginBottom: 16 }}>
                      {cur.desc}
                    </p>
                    <div style={{
                      background: 'rgba(16, 185, 129, 0.2)',
                      border: '1px solid rgba(16, 185, 129, 0.4)',
                      borderRadius: 6,
                      padding: '10px 14px',
                      color: '#34D399',
                      fontSize: 13,
                      fontWeight: 700
                    }}>
                      ✓ Field Benefit: {cur.highlight}
                    </div>
                  </div>
                )
              })()}

              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 24 }}>
                <button
                  className="btn btn-secondary"
                  disabled={step === 1}
                  onClick={() => setStep(s => s - 1)}
                >
                  ← Previous Step
                </button>
                {step < 4 ? (
                  <button
                    className="btn btn-primary"
                    onClick={() => setStep(s => s + 1)}
                  >
                    Next Step →
                  </button>
                ) : (
                  <button
                    className="btn btn-primary"
                    onClick={() => {
                      onClose()
                      if (onSelectScenario) onSelectScenario('scenario_wheat_rust')
                    }}
                  >
                    🚀 Try Scenario 1 (Crop Alert)
                  </button>
                )}
              </div>
            </div>
          )}

          {activeTab === 'agrishield' && (
            <div>
              <h4 style={{ margin: '0 0 12px 0', fontSize: 16, color: 'var(--text)' }}>
                🛡️ AgriShield™ Domain Entity Preservation
              </h4>
              <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 16 }}>
                In agriculture, mistranslating chemical dosages, crop diseases, or government scheme names can cause severe crop loss. AgriShield™ uses automated token wrapping to guarantee accuracy.
              </p>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                <div style={{ background: 'var(--bg-input)', padding: 14, borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--accent)', marginBottom: 6 }}>1. Protected Scheme Names</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    PM-KISAN, PMFBY, Soil Health Card, KCC, NABARD are never altered into incorrect literal translations.
                  </div>
                </div>
                <div style={{ background: 'var(--bg-input)', padding: 14, borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--accent)', marginBottom: 6 }}>2. Chemical & Dosage Safeguards</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    DAP, Urea, Propiconazole 25% EC, 1ml/L dosages remain exact across all regional scripts.
                  </div>
                </div>
                <div style={{ background: 'var(--bg-input)', padding: 14, borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--accent)', marginBottom: 6 }}>3. Cattle & Crop Varieties</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    Gir, Sahiwal, Murrah, HD-2967, Desi Cotton varieties are preserved verbatim.
                  </div>
                </div>
                <div style={{ background: 'var(--bg-input)', padding: 14, borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--accent)', marginBottom: 6 }}>4. Confidence Review Gate</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    Any sentence with confidence &lt;80% is flagged 🟡 Amber for quick 1-click review by field staff.
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'formats' && (
            <div>
              <h4 style={{ margin: '0 0 12px 0', fontSize: 16, color: 'var(--text)' }}>
                📦 Multiformat Field Distribution Matrix
              </h4>
              <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 16 }}>
                Every farmer is reached regardless of smartphone ownership or 2G/3G connectivity:
              </p>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <div style={{ background: 'var(--bg-input)', padding: 12, borderRadius: 8, border: '1px solid var(--border)', display: 'flex', gap: 12, alignItems: 'center' }}>
                  <span style={{ fontSize: 24 }}>💬</span>
                  <div>
                    <strong style={{ fontSize: 13, color: 'var(--text)' }}>WhatsApp Video Chunks (&lt;15 MB)</strong>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Automatically splits videos into compressed clips for easy forwarding across rural 2G/3G groups.</div>
                  </div>
                </div>
                <div style={{ background: 'var(--bg-input)', padding: 12, borderRadius: 8, border: '1px solid var(--border)', display: 'flex', gap: 12, alignItems: 'center' }}>
                  <span style={{ fontSize: 24 }}>📞</span>
                  <div>
                    <strong style={{ fontSize: 13, color: 'var(--text)' }}>8kHz Keypad Phone IVR (.wav)</strong>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Optimized downsampled audio for automated voice broadcast calls to ₹1,000 basic feature phones.</div>
                  </div>
                </div>
                <div style={{ background: 'var(--bg-input)', padding: 12, borderRadius: 8, border: '1px solid var(--border)', display: 'flex', gap: 12, alignItems: 'center' }}>
                  <span style={{ fontSize: 24 }}>📄</span>
                  <div>
                    <strong style={{ fontSize: 13, color: 'var(--text)' }}>Bilingual Word Handouts (.docx)</strong>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Printable side-by-side advisory sheets for village panchayat meetings and farmer group discussions.</div>
                  </div>
                </div>
                <div style={{ background: 'var(--bg-input)', padding: 12, borderRadius: 8, border: '1px solid var(--border)', display: 'flex', gap: 12, alignItems: 'center' }}>
                  <span style={{ fontSize: 24 }}>📝</span>
                  <div>
                    <strong style={{ fontSize: 13, color: 'var(--text)' }}>Subtitle Tracks (.srt / .vtt)</strong>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Synchronized subtitles for BAIF video portal, YouTube, and field training projectors.</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '14px 24px',
          borderTop: '1px solid var(--border)',
          display: 'flex',
          justifyContent: 'flex-end',
          background: 'var(--bg-card-hover)'
        }}>
          <button className="btn btn-secondary" onClick={onClose}>
            Close Guide
          </button>
        </div>
      </div>
    </div>
  )
}
