import React, { useState } from 'react'

export default function DemoTourModal({ onClose, onSelectScenario }) {
  const [activeTab, setActiveTab] = useState('tour') // 'tour' | 'benchmark' | 'economics'
  const [step, setStep] = useState(1)

  const steps = [
    {
      num: 1,
      title: 'The Grassroots Problem',
      icon: '🌾',
      desc: 'BAIF produces high-yield agricultural training videos in English & Marathi, but 1.3+ billion rural farmers speak 22 regional languages. Commercial translation agencies charge ₹850/min ($10/min) with 2-week turnaround and zero offline access in remote tribal villages.',
      highlight: 'VaaniSetu delivers 100% offline, air-gapped, zero-cost localization in minutes.'
    },
    {
      num: 2,
      title: 'Full Pipeline Architecture & Voice Match',
      icon: '⚡',
      desc: '7-Stage pipelined engine with faster-Whisper (INT8 + Silero VAD) -> IndicTrans2 -> AgriShield™ Domain Dictionary -> Gender-Aware Pitch Analysis -> Piper/XTTS Voice Cloning. Target languages translate concurrently with cached English pivot.',
      highlight: '4-8x faster on basic CPU laptops, automatic CUDA GPU acceleration, and 100% private.'
    },
    {
      num: 3,
      title: 'Last-Mile Multiformat Delivery',
      icon: '📦',
      desc: 'One upload generates WhatsApp auto-split video chunks (<15MB), 8kHz IVR mono audio for ₹1,000 basic feature phones, synced SRT/VTT subtitles, and bilingual Word documentation for village field workers.',
      highlight: 'Every farmer reached regardless of smartphone ownership or 2G/3G connectivity.'
    },
    {
      num: 4,
      title: 'Human-in-the-Loop & Self-Learning TM',
      icon: '🧠',
      desc: 'Token log-probability confidence scores automatically route uncertain translations (Amber/Red) to bilingual extension officers. Approved edits dynamically update the persistent Translation Memory database.',
      highlight: 'System becomes smarter and more accurate with every agricultural season.'
    }
  ]

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0,0,0,0.8)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: 20
    }}>
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        maxWidth: 780,
        width: '100%',
        maxHeight: '90vh',
        overflowY: 'auto',
        boxShadow: '0 24px 48px rgba(0,0,0,0.6)',
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
          background: 'var(--bg-card-hover)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 24 }}>🏆</span>
            <div>
              <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: 'var(--text)' }}>
                VaaniSetu — Hackathon Presentation & Architecture Hub
              </h3>
              <p style={{ margin: 0, fontSize: 12, color: 'var(--text-muted)' }}>
                3-Minute Jury Guide · BAIF Agricultural Localization Platform
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
            ['tour', '🎬 4-Step Solution Tour'],
            ['benchmark', '📊 Why VaaniSetu Wins (Benchmark)'],
            ['economics', '💰 BAIF Financial ROI']
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
                      background: step === s.num ? 'rgba(232,109,31,0.15)' : 'var(--bg-input)',
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
                        <span style={{ fontSize: 12, color: 'var(--accent)', fontWeight: 600 }}>Phase {cur.num} of 4</span>
                      </div>
                    </div>
                    <p style={{ fontSize: 14, lineHeight: 1.6, color: 'var(--text-muted)', marginBottom: 16 }}>
                      {cur.desc}
                    </p>
                    <div style={{
                      background: 'rgba(34, 197, 94, 0.1)',
                      border: '1px solid rgba(34, 197, 94, 0.3)',
                      borderRadius: 6,
                      padding: '10px 14px',
                      color: '#4ade80',
                      fontSize: 13,
                      fontWeight: 600
                    }}>
                      ✓ Unfair Advantage: {cur.highlight}
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
                    🚀 Launch Live Scenario 1 (Crop Alert)
                  </button>
                )}
              </div>
            </div>
          )}

          {activeTab === 'benchmark' && (
            <div>
              <h4 style={{ margin: '0 0 12px 0', fontSize: 15 }}>
                Competitive Technical Benchmark (VaaniSetu vs Alternatives)
              </h4>
              <div style={{ overflowX: 'auto' }}>
                <table className="data-table" style={{ fontSize: 12 }}>
                  <thead>
                    <tr>
                      <th>Capability / Metric</th>
                      <th style={{ color: 'var(--accent)', fontWeight: 'bold' }}>🌱 VaaniSetu (Our Solution)</th>
                      <th>Cloud APIs (Google/Azure)</th>
                      <th>Vanilla Whisper + gTTS</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td><strong>Runtime Internet Requirement</strong></td>
                      <td><span style={{ color: '#4ade80' }}>✓ 100% Offline (Air-gapped)</span></td>
                      <td><span style={{ color: '#f87171' }}>✗ High Bandwidth Required</span></td>
                      <td><span style={{ color: '#fbbf24' }}>⚠️ gTTS Requires Internet</span></td>
                    </tr>
                    <tr>
                      <td><strong>Cost per Hour of Audio</strong></td>
                      <td><span style={{ color: '#4ade80' }}>✓ ₹0 (Zero Operating Cost)</span></td>
                      <td><span style={{ color: '#f87171' }}>✗ ₹1,200 - ₹2,500 / hr</span></td>
                      <td><span style={{ color: '#4ade80' }}>✓ ₹0</span></td>
                    </tr>
                    <tr>
                      <td><strong>Specialized Agri Domain Shield</strong></td>
                      <td><span style={{ color: '#4ade80' }}>✓ AgriShield™ (120+ entities)</span></td>
                      <td><span style={{ color: '#f87171' }}>✗ Generic (Mistranslates terms)</span></td>
                      <td><span style={{ color: '#f87171' }}>✗ Zero entity protection</span></td>
                    </tr>
                    <tr>
                      <td><strong>Voice Gender & Cloning</strong></td>
                      <td><span style={{ color: '#4ade80' }}>✓ Librosa pitch analysis + XTTS/Piper</span></td>
                      <td><span style={{ color: '#fbbf24' }}>⚠️ Generic robotic voices</span></td>
                      <td><span style={{ color: '#f87171' }}>✗ Female only hardcoded</span></td>
                    </tr>
                    <tr>
                      <td><strong>Feature Phone IVR Support</strong></td>
                      <td><span style={{ color: '#4ade80' }}>✓ Auto 8kHz Mono WAV generation</span></td>
                      <td><span style={{ color: '#f87171' }}>✗ Manual downsampling needed</span></td>
                      <td><span style={{ color: '#f87171' }}>✗ Not supported</span></td>
                    </tr>
                    <tr>
                      <td><strong>WhatsApp Delivery Splitter</strong></td>
                      <td><span style={{ color: '#4ade80' }}>✓ Auto-chunks &lt;15MB MP4 videos</span></td>
                      <td><span style={{ color: '#f87171' }}>✗ Manual video slicing needed</span></td>
                      <td><span style={{ color: '#f87171' }}>✗ Not supported</span></td>
                    </tr>
                    <tr>
                      <td><strong>Hardware Resilience</strong></td>
                      <td><span style={{ color: '#4ade80' }}>✓ Resource Saver + INT8 Quant</span></td>
                      <td><span style={{ color: '#8696a0' }}>N/A (Cloud)</span></td>
                      <td><span style={{ color: '#f87171' }}>✗ Freezes 16GB laptops</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'economics' && (
            <div>
              <h4 style={{ margin: '0 0 12px 0', fontSize: 15 }}>
                BAIF Real-World Social & Financial Impact
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
                <div style={{ background: 'var(--bg-input)', padding: 16, borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Commercial Translation Cost</div>
                  <div style={{ fontSize: 24, fontWeight: 700, color: '#f87171', margin: '4px 0' }}>₹850 / minute</div>
                  <div style={{ fontSize: 11, color: 'var(--text-dim)' }}>Standard rate charged by human translation agencies</div>
                </div>
                <div style={{ background: 'var(--bg-input)', padding: 16, borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>VaaniSetu Cost per 100 Hours</div>
                  <div style={{ fontSize: 24, fontWeight: 700, color: '#4ade80', margin: '4px 0' }}>₹0 Runtime</div>
                  <div style={{ fontSize: 11, color: 'var(--text-dim)' }}>Saves ₹51,00,000 (₹51 Lakhs) per 100 hrs of video</div>
                </div>
              </div>
              <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6 }}>
                By deploying on standard office PCs across BAIF's 12 state offices, VaaniSetu expands outreach to over <strong>4,50,000+ smallholder and tribal farmers</strong> across Maharashtra, Gujarat, Odisha, Bihar, and Karnataka at zero ongoing cloud expenditure.
              </p>
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
            Close Tour
          </button>
        </div>
      </div>
    </div>
  )
}
