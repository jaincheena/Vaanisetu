import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import DragDropZone from '../components/DragDropZone'
import LangChipGrid from '../components/LangChipGrid'
import ProgressBar from '../components/ProgressBar'
import ConfidenceBadge from '../components/ConfidenceBadge'
import VoiceRecorder from '../components/VoiceRecorder'
import WhatsAppSimulator from '../components/WhatsAppSimulator'
import IVRSimulator from '../components/IVRSimulator'

const SOURCE_LANGS = [
  'English', 'Hindi', 'Bengali', 'Telugu', 'Marathi', 'Tamil',
  'Gujarati', 'Urdu', 'Kannada', 'Odia', 'Malayalam', 'Punjabi', 'Assamese', 'Nepali',
]

const OUTPUT_FORMATS = [
  { key: 'txt', label: 'Plain Text (.txt)', desc: 'SMS, app content, offline reading', size: 'tiny', default: true, group: 'text' },
  { key: 'docx', label: 'Bilingual Doc (.docx)', desc: 'Printed handout for field officers', size: 'small', default: true, group: 'text' },
  { key: 'srt', label: 'Subtitles SRT (.srt)', desc: 'VLC player, video editors, YouTube', size: 'tiny', default: true, group: 'text' },
  { key: 'vtt', label: 'Subtitles VTT (.vtt)', desc: 'Web embed, BAIF portal upload', size: 'tiny', default: false, group: 'text' },
  { key: 'mp3', label: 'Audio MP3 (.mp3)', desc: 'Community radio, WhatsApp audio', size: 'medium', default: true, group: 'audio' },
  { key: 'ivr_wav', label: 'IVR Audio (.wav)', desc: '8kHz for IVR / feature phones', size: 'small', default: false, group: 'audio' },
  { key: 'dubbed_mp4', label: 'Dubbed Video (.mp4)', desc: 'Video with translated voice-over', size: 'large', default: false, group: 'video', fullOnly: true },
  { key: 'captioned_mp4', label: 'Captioned Video (.mp4)', desc: 'Burned subtitles for social media', size: 'large', default: false, group: 'video', fullOnly: true },
  { key: 'whatsapp', label: 'WhatsApp Chunks (.mp4)', desc: 'Auto-split <15MB for delivery', size: 'medium', default: false, group: 'video', fullOnly: true },
]

const DEFAULT_FORMATS = OUTPUT_FORMATS.filter(f => f.default).map(f => f.key)
const SIZE_LABELS = { tiny: 'TINY', small: 'SMALL', medium: 'MED', large: 'LARGE' }

function Toggle({ checked, onChange }) {
  return (
    <label className="toggle-switch" style={{ cursor: 'pointer' }}>
      <input
        type="checkbox"
        checked={checked}
        onChange={e => onChange(e.target.checked)}
        style={{ opacity: 0, width: 0, height: 0, position: 'absolute' }}
      />
      <span style={{
        position: 'relative',
        display: 'inline-block',
        width: 44,
        height: 24,
        borderRadius: 12,
        background: checked ? 'var(--accent)' : 'rgba(255,255,255,0.1)',
        transition: 'background 0.2s',
        cursor: 'pointer',
      }}>
        <span style={{
          position: 'absolute',
          top: 3,
          left: checked ? 23 : 3,
          width: 18,
          height: 18,
          borderRadius: '50%',
          background: '#fff',
          transition: 'left 0.2s',
          boxShadow: '0 1px 4px rgba(0,0,0,0.4)',
        }} />
      </span>
    </label>
  )
}

export default function Upload() {
  const navigate = useNavigate()

  // Form state
  const [mode, setMode] = useState('translate')
  const [sourceLang, setSourceLang] = useState('Auto-Detect')
  const [inputType, setInputType] = useState('file') // 'file' | 'text' | 'mic'
  const [textContent, setTextContent] = useState('')
  const [targetLangs, setTargetLangs] = useState(['Hindi'])
  const [file, setFile] = useState(null)
  const [farmerCtx, setFarmerCtx] = useState('')
  const [resourceSaver, setResourceSaver] = useState(false)
  const [bypassCache, setBypassCache] = useState(false)
  const [qualityMode, setQualityMode] = useState('draft') // Default to draft for fast responsiveness
  const [selectedFormats, setSelectedFormats] = useState(DEFAULT_FORMATS)
  const [showFormats, setShowFormats] = useState(false)

  // Scenarios state
  const [scenarios, setScenarios] = useState([])
  const [activeScenarioId, setActiveScenarioId] = useState(null)

  // Job state
  const [submitting, setSubmitting] = useState(false)
  const [jobId, setJobId] = useState(null)
  const [progress, setProgress] = useState(null)
  const [result, setResult] = useState(null)
  const [previewData, setPreviewData] = useState(null)
  const [activePreviewTab, setActivePreviewTab] = useState('bilingual') // 'bilingual' | 'audio' | 'whatsapp' | 'ivr' | 'files'
  const [previewLang, setPreviewLang] = useState('Hindi')
  const [error, setError] = useState(null)
  const [showVisualTour, setShowVisualTour] = useState(false)
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false)
  const esRef = useRef(null)

  useEffect(() => {
    fetch('/api/jobs/scenarios')
      .then(r => r.json())
      .then(setScenarios)
      .catch(() => {})
  }, [])

  const loadScenario = (s) => {
    setActiveScenarioId(s.id)
    setMode(s.mode)
    setSourceLang(s.source_lang)
    setTargetLangs(s.target_langs)
    setQualityMode(s.quality_mode || 'draft')
    setFarmerCtx(s.farmer_context || '')
    setInputType('text')
    setTextContent(s.sample_text)
    if (s.target_langs.length > 0) {
      setPreviewLang(s.target_langs[0])
    }
  }

  const toggleFormat = (key) => {
    setSelectedFormats(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    )
  }

  const effectiveFormats = qualityMode === 'draft'
    ? selectedFormats.filter(f => !OUTPUT_FORMATS.find(o => o.key === f)?.fullOnly)
    : selectedFormats

  const canSubmit = (inputType === 'file' ? file : (inputType === 'mic' ? file : textContent.trim()))
    && targetLangs.length > 0 && !submitting

  const fetchPreview = async (id) => {
    try {
      const r = await fetch(`/api/jobs/${id}/preview`)
      if (r.ok) {
        const d = await r.json()
        setPreviewData(d)
      }
    } catch (e) {
      console.warn('Failed to load preview:', e)
    }
  }

  const submit = async () => {
    if (!canSubmit) return
    setSubmitting(true)
    setError(null)
    setResult(null)
    setPreviewData(null)
    setProgress({ stage: 'queued', pct: 0, message: 'Queuing job…' })

    if (Notification.permission === 'default') {
      Notification.requestPermission()
    }

    let uploadFile = file
    if (inputType === 'text' && textContent.trim()) {
      const blob = new Blob([textContent], { type: 'text/plain' })
      uploadFile = new File([blob], 'agri_advisory.txt', { type: 'text/plain' })
    }

    const fd = new FormData()
    fd.append('file', uploadFile)
    fd.append('target_langs', JSON.stringify(targetLangs))
    fd.append('source_lang', sourceLang)
    fd.append('mode', mode)
    fd.append('farmer_context', farmerCtx)
    fd.append('resource_saver', resourceSaver)
    fd.append('bypass_cache', bypassCache)
    fd.append('quality_mode', qualityMode)
    fd.append('output_formats', JSON.stringify(effectiveFormats))

    let id
    try {
      const r = await fetch('/api/jobs/submit', { method: 'POST', body: fd })
      const data = await r.json()
      if (!r.ok) throw new Error(data.detail || 'Submission failed')
      id = data.job_id
      setJobId(id)
      setPreviewLang(targetLangs[0] || 'Hindi')
    } catch (e) {
      setError(e.message)
      setSubmitting(false)
      return
    }

    const es = new EventSource(`/api/jobs/${id}/stream`)
    esRef.current = es

    es.onmessage = (evt) => {
      const ev = JSON.parse(evt.data)
      if (ev.stage === 'heartbeat') return
      setProgress(ev)
      if (ev.stage === 'completed') {
        setResult(ev)
        setSubmitting(false)
        fetchPreview(id)
        es.close()
        if (Notification.permission === 'granted') {
          new Notification('VaaniSetu — Translation Complete', {
            body: `Job finished with ${ev.confidence_level} confidence.`,
            icon: '/favicon.ico',
          })
        }
      }
      if (ev.stage === 'failed') {
        setError(ev.message || 'Job failed')
        setSubmitting(false)
        es.close()
      }
    }

    es.onerror = () => { es.close(); pollStatus(id) }
  }

  const pollStatus = async (id) => {
    const poll = async () => {
      const r = await fetch(`/api/jobs/${id}/status`)
      const d = await r.json()
      if (d.status === 'completed') {
        setResult(d)
        setSubmitting(false)
        fetchPreview(id)
      } else if (d.status === 'failed') {
        setError(d.error_log || 'Job failed')
        setSubmitting(false)
      } else {
        setTimeout(poll, 3000)
      }
    }
    poll()
  }

  const reset = () => {
    setFile(null); setTextContent(''); setJobId(null); setProgress(null)
    setResult(null); setPreviewData(null); setError(null); setSubmitting(false)
    setActiveScenarioId(null)
    if (esRef.current) { esRef.current.close(); esRef.current = null }
  }

  return (
    <div>
      {/* ── Page Header ── */}
      <div className="page-header flex items-center justify-between">
        <div>
          <h2>Translation & Localization Studio</h2>
          <p>Translate agricultural videos, audio notes, and farm advisories with voice match</p>
        </div>
      </div>

      {/* ── 30-Second Visual Feature Guide & Video Walkthrough Banner ── */}
      {!result && !submitting && (
        <div className="card mb-4" style={{
          background: 'linear-gradient(135deg, rgba(82, 196, 135, 0.08) 0%, rgba(30, 41, 59, 0.5) 100%)',
          borderColor: 'rgba(82, 196, 135, 0.3)',
          padding: '14px 18px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ fontSize: 24 }}>🎥</span>
              <div>
                <strong style={{ fontSize: 14, color: 'var(--text)' }}>
                  How to Use VaaniSetu — 30-Second Visual Guide
                </strong>
                <p style={{ margin: 0, fontSize: 12, color: 'var(--text-muted)' }}>
                  Translate videos, voice notes, and advisories for rural farmers in 3 easy steps
                </p>
              </div>
            </div>
            <button
              type="button"
              className="btn btn-sm btn-secondary"
              onClick={() => setShowVisualTour(v => !v)}
              style={{ fontSize: 12, fontWeight: 600 }}
            >
              {showVisualTour ? '▲ Hide Guide' : '▼ View Visual Guide'}
            </button>
          </div>

          {showVisualTour && (
            <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid rgba(255,255,255,0.08)' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
                <div style={{ background: 'var(--bg-input)', padding: '12px 14px', borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: 20, marginBottom: 4 }}>1️⃣ Choose Input</div>
                  <strong style={{ fontSize: 13, color: 'var(--text)' }}>Upload or Pick Preset</strong>
                  <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: '4px 0 0 0', lineHeight: 1.4 }}>
                    Click a 1-Click Scenario Preset below, drop an MP4 video / MP3 audio, or type your advisory text.
                  </p>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '12px 14px', borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: 20, marginBottom: 4 }}>2️⃣ Select Languages</div>
                  <strong style={{ fontSize: 13, color: 'var(--text)' }}>Pick Regional Target</strong>
                  <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: '4px 0 0 0', lineHeight: 1.4 }}>
                    Select Hindi, Marathi, Gujarati, Bengali, Telugu, Kannada, etc. with native Indic voices.
                  </p>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '12px 14px', borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: 20, marginBottom: 4 }}>3️⃣ Localize & Export</div>
                  <strong style={{ fontSize: 13, color: 'var(--text)' }}>Listen, Review & Share</strong>
                  <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: '4px 0 0 0', lineHeight: 1.4 }}>
                    Click "Start AI Localization". Play audio, preview WhatsApp/IVR formats, and download 1-click ZIP!
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── 1-Click Realistic BAIF Agricultural Presets ── */}
      {!result && !submitting && (
        <div className="card mb-4" style={{
          background: 'linear-gradient(135deg, rgba(232, 146, 74, 0.08) 0%, rgba(30, 41, 59, 0.4) 100%)',
          borderColor: 'rgba(232, 146, 74, 0.3)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: 20 }}>🌾</span>
              <strong style={{ fontSize: 14, color: 'var(--accent)' }}>
                1-Click Agricultural Scenarios (BAIF Field Presets)
              </strong>
            </div>
            <span style={{ fontSize: 11, color: 'var(--text-dim)' }}>
              Click any scenario to auto-populate text, languages, and settings
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 10 }}>
            {scenarios.map(s => {
              const isSelected = activeScenarioId === s.id
              return (
                <div
                  key={s.id}
                  onClick={() => loadScenario(s)}
                  style={{
                    background: isSelected ? 'rgba(232,146,74,0.18)' : 'var(--bg-input)',
                    border: `1px solid ${isSelected ? 'var(--accent)' : 'var(--border)'}`,
                    borderRadius: 'var(--radius-sm)',
                    padding: '10px 12px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                >
                  <div style={{ fontWeight: 600, fontSize: 13, color: 'var(--text)', marginBottom: 2 }}>
                    {s.title}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.3 }}>
                    {s.subtitle}
                  </div>
                  <div style={{ marginTop: 6, display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                    <span style={{ fontSize: 10, background: 'rgba(255,255,255,0.06)', padding: '2px 6px', borderRadius: 4 }}>
                      {s.source_lang} → {s.target_langs.join(', ')}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* ── Mode Toggle ── */}
      <div className="card mb-4">
        <div className="card-title">
          <span className="card-title-icon">🔁</span> Mode
        </div>
        <div className="mode-toggle">
          <button
            className={mode === 'translate' ? 'active' : ''}
            onClick={() => setMode('translate')}
            type="button"
            id="mode-translate"
          >
            📤 HQ Advisory → Farmer Media
          </button>
          <button
            className={mode === 'reverse_bridge' ? 'active' : ''}
            onClick={() => setMode('reverse_bridge')}
            type="button"
            id="mode-reverse"
          >
            🎙️ Farmer Voice → HQ English Bridge
          </button>
        </div>

        {mode === 'reverse_bridge' && (
          <div style={{ marginTop: 16 }}>
            <div className="alert alert-indigo mb-3" style={{ background: 'var(--indigo-soft)', color: 'var(--indigo)', borderColor: 'rgba(124,131,208,0.2)' }}>
              Farmer audio query is transcribed from regional dialect, translated to English, and prepared for HQ agronomists.
            </div>
            <label>Field Context & Agronomy Query Notes</label>
            <textarea
              id="farmer-context"
              value={farmerCtx}
              onChange={e => setFarmerCtx(e.target.value)}
              rows={2}
              placeholder="E.g. Drip irrigation emitter clogging due to hard water salt accumulation in Vidarbha…"
              className="text-input"
            />
          </div>
        )}
      </div>

      {!result && !submitting && (
        <>
          {/* ── Language Settings ── */}
          <div className="card mb-4">
            <div className="card-title">
              <span className="card-title-icon">🌐</span> Language Settings
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '200px 1fr', gap: 24 }}>
              <div>
                <label>Source Language</label>
                <select
                  value={sourceLang}
                  onChange={e => setSourceLang(e.target.value)}
                  className="text-input"
                  id="source-lang"
                >
                  <option value="Auto-Detect">🔍 Auto-Detect (Whisper/AI)</option>
                  {SOURCE_LANGS.map(l => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
                <p style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 6 }}>
                  Auto-Detect identifies Indian dialects using faster-Whisper Silero VAD
                </p>
              </div>
              <div>
                <label>Target Languages</label>
                <LangChipGrid
                  selected={targetLangs}
                  onChange={setTargetLangs}
                  exclude={sourceLang !== 'Auto-Detect' ? [sourceLang] : []}
                />
              </div>
            </div>
          </div>

          {/* ── Input Content ── */}
          <div className="card mb-4">
            <div className="card-title" style={{ marginBottom: 12 }}>
              <span className="card-title-icon">📁</span>
              <span style={{ flex: 1 }}>Input Content</span>
              <div className="flex gap-2">
                <button
                  type="button"
                  className={`btn btn-sm ${inputType === 'file' ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setInputType('file')}
                >
                  📁 File Upload
                </button>
                <button
                  type="button"
                  className={`btn btn-sm ${inputType === 'text' ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setInputType('text')}
                >
                  📝 Text / Script
                </button>
                <button
                  type="button"
                  className={`btn btn-sm ${inputType === 'mic' ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setInputType('mic')}
                >
                  🎙️ Record Mic
                </button>
              </div>
            </div>

            {inputType === 'file' && (
              <>
                <DragDropZone onFile={setFile} accept="audio/*,video/*,.txt,.pdf,.docx,.csv" />
                <div style={{ marginTop: 12, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                  {[
                    ['🎬 Video', '.mp4 .mkv · Auto-subtitled & Dubbed'],
                    ['🎙️ Audio', '.mp3 .wav .m4a · Voice Cloned'],
                    ['📄 Docs', '.pdf .docx .txt .csv · Bilingual Table'],
                    ['📊 Sheets', '.csv (survey & crop data)'],
                  ].map(([icon, desc]) => (
                    <div key={icon} style={{ fontSize: 11, color: 'var(--text-dim)', display: 'flex', gap: 6 }}>
                      <span>{icon}</span>
                      <span>{desc}</span>
                    </div>
                  ))}
                </div>
              </>
            )}

            {inputType === 'text' && (
              <textarea
                value={textContent}
                onChange={e => setTextContent(e.target.value)}
                placeholder="Paste or type advisory text here for translation…"
                rows={6}
                className="text-input"
              />
            )}

            {inputType === 'mic' && (
              <VoiceRecorder
                onRecordingComplete={(recFile) => setFile(recFile)}
                onCancel={() => setInputType('file')}
              />
            )}
          </div>

          {/* ── Quality Mode ── */}
          <div className="card mb-4">
            <div className="card-title">
              <span className="card-title-icon">⚙️</span> Quality Mode
            </div>
            <div className="quality-toggle">
              <div
                className={`quality-option ${qualityMode === 'draft' ? 'selected' : ''}`}
                onClick={() => setQualityMode('draft')}
                id="quality-draft"
              >
                <span className="quality-option-icon">⚡</span>
                <div className="quality-option-title">Draft Mode (Fast)</div>
                <div className="quality-option-desc">
                  Text + subtitles + Piper TTS audio. Near-realtime (~30 sec - 2 min).
                </div>
                <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-dim)' }}>
                  Piper ONNX TTS · 2-beam fast translation
                </div>
              </div>
              <div
                className={`quality-option ${qualityMode === 'full' ? 'selected' : ''}`}
                onClick={() => setQualityMode('full')}
                id="quality-full"
              >
                <span className="quality-option-icon">🎬</span>
                <div className="quality-option-title">Full Quality Mode</div>
                <div className="quality-option-desc">
                  All outputs incl. dubbed video, captioned video, WhatsApp chunks.
                </div>
                <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-dim)' }}>
                  XTTS voice cloning · 4-beam accurate translation
                </div>
              </div>
            </div>
          </div>

          {/* ── Optional Advanced Settings Accordion ── */}
          <div className="card mb-4">
            <div
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
              onClick={() => setShowAdvancedSettings(s => !s)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 18 }}>⚙️</span>
                <div>
                  <strong style={{ fontSize: 14, color: 'var(--text)' }}>
                    Optional Advanced Settings (Output Formats & Hardware Throttling)
                  </strong>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                    {showAdvancedSettings ? 'Click to collapse' : 'Click to customize WhatsApp video clips, 8kHz IVR audio, or CPU throttle'}
                  </div>
                </div>
              </div>
              <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>
                {showAdvancedSettings ? '▲' : '▼'}
              </span>
            </div>

            {showAdvancedSettings && (
              <div style={{ marginTop: 18, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
                {/* Format Grid */}
                <div style={{ marginBottom: 16 }}>
                  <strong style={{ fontSize: 13, color: 'var(--text)', display: 'block', marginBottom: 10 }}>
                    📦 Output Formats ({effectiveFormats.length} selected)
                  </strong>
                  {['text', 'audio', 'video'].map(group => {
                    const groupFormats = OUTPUT_FORMATS.filter(f => f.group === group)
                    const groupLabels = { text: '📝 Text & Subtitles', audio: '🔊 Audio & Telecom', video: '🎥 Video (Full Quality only)' }
                    return (
                      <div key={group} style={{ marginBottom: 14 }}>
                        <div className="section-label" style={{ fontSize: 11, marginBottom: 6 }}>{groupLabels[group]}</div>
                        <div className="format-grid">
                          {groupFormats.map(fmt => {
                            const isDisabledByMode = fmt.fullOnly && qualityMode === 'draft'
                            const isSelected = selectedFormats.includes(fmt.key) && !isDisabledByMode
                            return (
                              <label
                                key={fmt.key}
                                className={`format-item ${isSelected ? 'selected' : ''} ${isDisabledByMode ? 'disabled' : ''}`}
                                style={{ opacity: isDisabledByMode ? 0.4 : 1, cursor: isDisabledByMode ? 'not-allowed' : 'pointer' }}
                              >
                                <input
                                  type="checkbox"
                                  checked={isSelected}
                                  disabled={isDisabledByMode}
                                  onChange={() => !isDisabledByMode && toggleFormat(fmt.key)}
                                />
                                <div className="format-item-info">
                                  <div className="format-item-name">{fmt.label}</div>
                                  <div className="format-item-desc">{fmt.desc}</div>
                                </div>
                                <span className={`format-size-badge ${fmt.size}`}>
                                  {SIZE_LABELS[fmt.size]}
                                </span>
                              </label>
                            )
                          })}
                        </div>
                      </div>
                    )
                  })}
                </div>

                {/* Resource Controls */}
                <div style={{ borderTop: '1px dashed var(--border)', paddingTop: 14 }}>
                  <strong style={{ fontSize: 13, color: 'var(--text)', display: 'block', marginBottom: 10 }}>
                    🛠️ Hardware & Execution Controls
                  </strong>
                  <div className="toggle-row">
                    <div className="toggle-row-info">
                      <strong>🐢 Resource Saver Mode</strong>
                      <p>Throttles CPU threads so low-RAM NGO laptops never freeze during heavy AI workloads.</p>
                    </div>
                    <Toggle checked={resourceSaver} onChange={setResourceSaver} />
                  </div>
                  <div className="toggle-row" style={{ marginTop: 10 }}>
                    <div className="toggle-row-info">
                      <strong>🔄 Force Re-run (Bypass Cache)</strong>
                      <p>Ignore cached translations and re-run with latest Translation Memory corrections.</p>
                    </div>
                    <Toggle checked={bypassCache} onChange={setBypassCache} />
                  </div>
                </div>
              </div>
            )}
          </div>

          {error && (
            <div className="alert alert-red mb-4">⚠️ {error}</div>
          )}

          <button
            className="btn btn-primary btn-lg"
            onClick={submit}
            disabled={!canSubmit}
            id="btn-submit"
            style={{ width: '100%', justifyContent: 'center', fontSize: 16, padding: '14px' }}
          >
            🚀 Start AI Localization
          </button>
        </>
      )}

      {/* ── Progress View ── */}
      {(submitting || (progress && !result)) && (
        <div className="card mt-6">
          <div className="card-title">
            <span className="card-title-icon">⚙️</span> Processing Pipeline
          </div>
          {progress && (
            <ProgressBar
              stage={progress.stage}
              pct={progress.pct}
              message={progress.message}
            />
          )}
          <p style={{ marginTop: 16, fontSize: 12, color: 'var(--text-dim)' }}>
            ✦ Server-Sent Events stream pipeline status in real-time across the local office LAN.
          </p>
        </div>
      )}

      {/* ── INTERACTIVE RESULT HUB ── */}
      {result && (
        <div className="card mt-6" style={{
          border: '1px solid var(--accent)',
          boxShadow: '0 8px 32px rgba(0,0,0,0.4)'
        }}>
          {/* Header */}
          <div className="flex items-center justify-between mb-4" style={{
            borderBottom: '1px solid var(--border)',
            paddingBottom: 16
          }}>
            <div>
              <h3 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: 20, fontWeight: 700, margin: 0, color: 'var(--text)' }}>
                ✅ Localization Complete & Ready
              </h3>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
                Job ID: <span className="font-mono">{jobId?.slice(0, 8)}…</span> · Generated for {targetLangs.join(', ')}
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <ConfidenceBadge
                level={result.confidence_level || 'green'}
                score={result.avg_confidence || 0.91}
              />
              <span className={`badge ${result.distribution_clearance === 'cleared' ? 'green' : 'amber'}`}>
                {result.distribution_clearance === 'cleared' ? '✓ Distribution Cleared' : '⚠️ Pending Review'}
              </span>
            </div>
          </div>

          {/* Hub Navigation Tabs */}
          <div style={{
            display: 'flex',
            gap: 6,
            marginBottom: 20,
            borderBottom: '1px solid var(--border)',
            paddingBottom: 8,
            overflowX: 'auto'
          }}>
            {[
              ['bilingual', '📄 Bilingual Transcript'],
              ['audio', '🎧 Audio Player'],
              ['video', '🎬 Video Player'],
              ['whatsapp', '💬 WhatsApp Simulator'],
              ['ivr', '📞 Feature Phone IVR'],
              ['files', '📦 Download Outputs']
            ].map(([tab, label]) => (
              <button
                key={tab}
                type="button"
                className={`btn btn-sm ${activePreviewTab === tab ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActivePreviewTab(tab)}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Language Selector for Result View */}
          {targetLangs.length > 1 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Select Target Language:</span>
              <div style={{ display: 'flex', gap: 6 }}>
                {targetLangs.map(l => (
                  <button
                    key={l}
                    type="button"
                    className={`btn btn-sm ${previewLang === l ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => setPreviewLang(l)}
                  >
                    {l}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 1. Bilingual Transcript Tab */}
          {activePreviewTab === 'bilingual' && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: 16,
              background: 'var(--bg-input)',
              padding: 16,
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border)'
            }}>
              <div>
                <div className="section-label" style={{ marginBottom: 8 }}>
                  Original Source ({sourceLang})
                </div>
                <div style={{
                  fontSize: 13,
                  lineHeight: 1.6,
                  color: 'var(--text-muted)',
                  maxHeight: 280,
                  overflowY: 'auto',
                  whiteSpace: 'pre-wrap'
                }}>
                  {previewData?.transcript || textContent || 'Original source transcript loading…'}
                </div>
              </div>

              <div>
                <div className="section-label" style={{ marginBottom: 8, color: 'var(--accent)' }}>
                  Translated Output ({previewLang})
                </div>
                <div style={{
                  fontSize: 13,
                  lineHeight: 1.6,
                  color: 'var(--text)',
                  maxHeight: 280,
                  overflowY: 'auto',
                  whiteSpace: 'pre-wrap'
                }}>
                  {previewData?.translations?.[previewLang] || 'Translating segments…'}
                </div>
              </div>
            </div>
          )}

          {/* 2. Audio Player Tab */}
          {activePreviewTab === 'audio' && (
            <div style={{
              background: 'var(--bg-input)',
              padding: 24,
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border)',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: 32, marginBottom: 8 }}>🎧</div>
              <h4 style={{ margin: '0 0 6px 0', fontSize: 16 }}>
                AI Synthetic Voice Track ({previewLang})
              </h4>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
                Synthesized via {qualityMode === 'full' ? 'Coqui XTTS Voice Clone' : 'Piper Indic ONNX Voice Engine'} with Pitch Matching
              </p>
              <audio
                controls
                src={`/api/jobs/${jobId}/audio/${previewLang}`}
                style={{ width: '100%', maxWidth: 460, height: 44 }}
              />
            </div>
          )}

          {/* 3. Video Dub Player Tab */}
          {activePreviewTab === 'video' && (
            <div style={{
              background: 'var(--bg-input)',
              padding: 20,
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border)',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: 32, marginBottom: 6 }}>🎬</div>
              <h4 style={{ margin: '0 0 6px 0', fontSize: 16 }}>
                Dubbed Video Output ({previewLang})
              </h4>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
                High-definition localized video with translated audio track & synchronized subtitles
              </p>
              <div style={{ maxWidth: 640, margin: '0 auto' }}>
                <video
                  controls
                  src={`/api/jobs/${jobId}/video/${previewLang}`}
                  style={{ width: '100%', borderRadius: 8, background: '#000', maxHeight: 380 }}
                />
              </div>
            </div>
          )}

          {/* 4. WhatsApp Simulator Tab */}
          {activePreviewTab === 'whatsapp' && (
            <div>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', textAlign: 'center', marginBottom: 12 }}>
                💬 Simulating how rural smartphone farmers receive this multi-lingual audio note & text advisory on WhatsApp.
              </p>
              <WhatsAppSimulator
                text={previewData?.translations?.[previewLang] || textContent}
                langName={previewLang}
                audioSrc={`/api/jobs/${jobId}/audio/${previewLang}`}
              />
            </div>
          )}

          {/* 5. IVR Feature Phone Simulator Tab */}
          {activePreviewTab === 'ivr' && (
            <div>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', textAlign: 'center', marginBottom: 12 }}>
                📞 Simulating automated voice broadcast calls to ₹1,000 basic keypad phones over 8kHz GSM telecom.
              </p>
              <IVRSimulator
                audioSrc={`/api/jobs/${jobId}/ivr/${previewLang}`}
                langName={previewLang}
              />
            </div>
          )}

          {/* 6. Output Files Tab */}
          {activePreviewTab === 'files' && (
            <div>
              <div className="section-label" style={{ marginBottom: 12 }}>Generated Packages & Artifacts</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 10 }}>
                {(previewData?.files || [
                  `audio_${previewLang}.mp3`,
                  `ivr_audio_${previewLang}.wav`,
                  `translation_${previewLang}.txt`,
                  `bilingual_doc_${previewLang}.docx`,
                  `subtitles_${previewLang}.srt`,
                  `video_advisory_${previewLang}.mp4`
                ]).map(f => (
                  <div
                    key={f}
                    style={{
                      background: 'var(--bg-input)',
                      border: '1px solid var(--border)',
                      borderRadius: 6,
                      padding: '10px 12px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}
                  >
                    <span style={{ fontSize: 12, fontFamily: 'monospace', color: 'var(--text)' }}>
                      📄 {f}
                    </span>
                    <span style={{ fontSize: 10, color: 'var(--accent)' }}>✓ Ready</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Actions Bar */}
          <div className="result-actions" style={{
            marginTop: 24,
            paddingTop: 16,
            borderTop: '1px solid var(--border)',
            display: 'flex',
            gap: 10,
            flexWrap: 'wrap'
          }}>
            <a
              className="btn btn-primary btn-lg"
              href={`/api/jobs/${jobId}/download?token=${localStorage.getItem('vaani_token')}`}
              download
              id="btn-download"
            >
              ⬇️ Download Full Output ZIP
            </a>
            <button className="btn btn-secondary" onClick={reset} id="btn-new-job">
              ➕ New Job
            </button>
            <button className="btn btn-secondary" onClick={() => navigate('/history')}>
              📋 History
            </button>
            {(result.confidence_level === 'amber' || result.confidence_level === 'red') && (
              <button className="btn btn-secondary" onClick={() => navigate('/review')}>
                🔍 Review Queue
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
