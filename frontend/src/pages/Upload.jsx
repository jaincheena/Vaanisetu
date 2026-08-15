import React, { useState, useRef, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import DragDropZone from '../components/DragDropZone'
import LangChipGrid from '../components/LangChipGrid'
import ProgressBar from '../components/ProgressBar'
import ConfidenceBadge from '../components/ConfidenceBadge'
import VoiceRecorder from '../components/VoiceRecorder'
import WhatsAppSimulator from '../components/WhatsAppSimulator'
import IVRSimulator from '../components/IVRSimulator'

const SOURCE_LANGS = [
  'Marathi', 'Hindi', 'Gujarati', 'English', 'Telugu', 'Kannada',
  'Bengali', 'Tamil', 'Malayalam', 'Punjabi', 'Odia', 'Urdu', 'Assamese', 'Nepali',
]

const OUTPUT_FORMATS = [
  { key: 'dubbed_mp4', label: '🎬 Localized Video (.mp4)', desc: 'HD video with voiceover & burned subtitles for WhatsApp & TV', size: 'large', default: true, group: 'video' },
  { key: 'mp3', label: '🎧 AI Voice Audio (.mp3)', desc: 'High-quality audio for WhatsApp voice notes & community radio', size: 'medium', default: true, group: 'audio' },
  { key: 'ivr_wav', label: '📞 Telecom IVR Audio (.wav)', desc: '8kHz Mono for automated voice calls to ₹1,000 keypad feature phones', size: 'small', default: true, group: 'audio' },
  { key: 'docx', label: '📄 Bilingual Advisory Doc (.docx)', desc: 'Printable prescription handout for field extension officers', size: 'small', default: true, group: 'text' },
  { key: 'srt', label: '📝 Subtitles SRT (.srt)', desc: 'VLC media player, video editing, and YouTube subtitles', size: 'tiny', default: true, group: 'text' },
  { key: 'txt', label: '📱 SMS & Plain Text (.txt)', desc: 'SMS broadcasting, farmer portal updates, and text logs', size: 'tiny', default: true, group: 'text' },
  { key: 'vtt', label: '🌐 Web Subtitles VTT (.vtt)', desc: 'HTML5 web video player subtitle tracks', size: 'tiny', default: false, group: 'text' },
  { key: 'whatsapp', label: '📦 WhatsApp 60s Chunks (.mp4)', desc: 'Auto-split clips (<15MB) for WhatsApp status broadcast', size: 'medium', default: false, group: 'video' },
]

const DELIVERY_BUNDLES = [
  { id: 'all', label: '🌟 All-in-One Multi-Channel Pack (Recommended)', formats: ['dubbed_mp4', 'mp3', 'ivr_wav', 'docx', 'srt', 'txt', 'vtt'] },
  { id: 'mobile', label: '📱 WhatsApp & Mobile Pack', formats: ['dubbed_mp4', 'mp3', 'docx', 'txt'] },
  { id: 'ivr', label: '📞 Feature Phone IVR & SMS Pack', formats: ['ivr_wav', 'txt'] },
  { id: 'print', label: '📄 Field Officer Handout Pack', formats: ['docx', 'srt', 'txt'] },
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
  const [targetLangs, setTargetLangs] = useState(['Marathi', 'Hindi'])
  const [file, setFile] = useState(null)
  const [farmerCtx, setFarmerCtx] = useState('')
  const [resourceSaver, setResourceSaver] = useState(false)
  const [bypassCache, setBypassCache] = useState(false)
  const [qualityMode, setQualityMode] = useState('draft') // Default to draft for fast responsiveness
  const [selectedFormats, setSelectedFormats] = useState(DEFAULT_FORMATS)
  const [showFormats, setShowFormats] = useState(false)
  const [activeBundle, setActiveBundle] = useState('all')

  // Scenarios state
  const [scenarios, setScenarios] = useState([])
  const [activeScenarioId, setActiveScenarioId] = useState(null)

  // Job state
  const [submitting, setSubmitting] = useState(false)
  const [jobId, setJobId] = useState(null)
  const [progress, setProgress] = useState(null)
  const [result, setResult] = useState(null)
  const [previewData, setPreviewData] = useState(null)
  const [activePreviewTab, setActivePreviewTab] = useState('bilingual') // 'bilingual' | 'audio' | 'video' | 'whatsapp' | 'ivr' | 'files'
  const [previewLang, setPreviewLang] = useState('Marathi')
  const [error, setError] = useState(null)
  const [showVisualTour, setShowVisualTour] = useState(false)
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false)
  const location = useLocation()

  useEffect(() => {
    fetch('/api/jobs/scenarios')
      .then(r => r.json())
      .then(data => {
        setScenarios(data)
        if (location.state?.autoLoadScenarioId) {
          const match = data.find(s => s.id === location.state.autoLoadScenarioId)
          if (match) loadScenario(match)
        }
      })
      .catch(() => {})
  }, [location.state])

  const applyBundle = (bundle) => {
    setActiveBundle(bundle.id)
    setSelectedFormats(bundle.formats)
  }

  const loadScenario = (s) => {
    setActiveScenarioId(s.id)
    setMode(s.mode)
    setSourceLang(s.source_lang)
    setTargetLangs(s.target_langs)
    setQualityMode(s.quality_mode || 'draft')
    setFarmerCtx(s.farmer_context || '')
    setSelectedFormats(s.output_formats || DEFAULT_FORMATS)
    setInputType('text')
    setTextContent(s.sample_text)
    if (s.target_langs.length > 0) {
      setPreviewLang(s.target_langs[0])
    }
  }

  const toggleFormat = (key) => {
    setSelectedFormats(prev => {
      const next = prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
      setActiveBundle('custom')
      return next
    })
  }

  const effectiveFormats = selectedFormats

  const canSubmit = (inputType === 'file' ? file : (inputType === 'mic' ? file : textContent.trim()))
    && targetLangs.length > 0 && !submitting

  const fetchPreview = async (id) => {
    try {
      const r = await fetch(`/api/jobs/${id}/preview`)
      if (r.ok) {
        const d = await r.json()
        setPreviewData(d)
        if (d.job?.target_langs?.length) {
          setPreviewLang(d.job.target_langs[0])
        }
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

      {/* ── 3-Step Field Advisory Guide Banner ── */}
      {!result && !submitting && (
        <div className="card mb-4" style={{
          background: 'linear-gradient(135deg, rgba(82, 196, 135, 0.08) 0%, rgba(30, 41, 59, 0.5) 100%)',
          borderColor: 'rgba(82, 196, 135, 0.3)',
          padding: '14px 18px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ fontSize: 24 }}>💡</span>
              <div>
                <strong style={{ fontSize: 14, color: 'var(--text)' }}>
                  3-Step Advisory Localization Guide
                </strong>
                <p style={{ margin: 0, fontSize: 12, color: 'var(--text-muted)' }}>
                  Translate advisories, veterinary guides, and farmer voice queries in 3 simple steps
                </p>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <button
                type="button"
                className="btn btn-sm btn-secondary"
                onClick={() => navigate('/docs')}
                style={{ fontSize: 12 }}
              >
                📖 Platform Manual
              </button>
              <button
                type="button"
                className="btn btn-sm btn-secondary"
                onClick={() => setShowVisualTour(v => !v)}
                style={{ fontSize: 12, fontWeight: 600 }}
              >
                {showVisualTour ? '▲ Hide Steps' : '▼ Quick Steps'}
              </button>
            </div>
          </div>

          {showVisualTour && (
            <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid rgba(255,255,255,0.08)' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
                <div style={{ background: 'var(--bg-input)', padding: '12px 14px', borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: 20, marginBottom: 4 }}>1️⃣ Choose Input</div>
                  <strong style={{ fontSize: 13, color: 'var(--text)' }}>Upload or Pick Field Preset</strong>
                  <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: '4px 0 0 0', lineHeight: 1.4 }}>
                    Pick a 1-Click Scenario Preset below, drop an MP4 video / MP3 audio, or paste raw text.
                  </p>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '12px 14px', borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: 20, marginBottom: 4 }}>2️⃣ Select Languages & Pack</div>
                  <strong style={{ fontSize: 13, color: 'var(--text)' }}>Pick Regional Targets</strong>
                  <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: '4px 0 0 0', lineHeight: 1.4 }}>
                    Choose Marathi 🚩, Hindi, Gujarati, etc. and select your delivery channel preset (WhatsApp, IVR, Print).
                  </p>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '12px 14px', borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: 20, marginBottom: 4 }}>3️⃣ Localize & Export</div>
                  <strong style={{ fontSize: 13, color: 'var(--text)' }}>Preview & Download</strong>
                  <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: '4px 0 0 0', lineHeight: 1.4 }}>
                    Click "Start AI Localization". Play audio/video, simulate WhatsApp/IVR, and download the full ZIP!
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

          {/* ── Delivery Channel Packs & Format Selector ── */}
          <div className="card mb-4">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
              <div>
                <strong style={{ fontSize: 14, color: 'var(--text)' }}>
                  📦 Delivery Channel Preset
                </strong>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                  Select the rural distribution channels for this advisory
                </div>
              </div>
              <span className="badge green" style={{ fontSize: 11 }}>
                {selectedFormats.length} formats active
              </span>
            </div>

            {/* Quick Bundle Pills */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 8, marginBottom: 14 }}>
              {DELIVERY_BUNDLES.map(b => (
                <button
                  key={b.id}
                  type="button"
                  onClick={() => applyBundle(b)}
                  style={{
                    padding: '8px 12px',
                    borderRadius: 6,
                    border: `1px solid ${activeBundle === b.id ? 'var(--accent)' : 'var(--border)'}`,
                    background: activeBundle === b.id ? 'rgba(74, 158, 122, 0.15)' : 'var(--bg-input)',
                    color: activeBundle === b.id ? 'var(--accent)' : 'var(--text)',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: 12,
                    fontWeight: activeBundle === b.id ? 600 : 400,
                    transition: 'all 0.15s ease',
                  }}
                >
                  {b.label}
                </button>
              ))}
            </div>

            {/* Optional Advanced Format Customization */}
            <div
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', paddingTop: 8, borderTop: '1px solid var(--border)' }}
              onClick={() => setShowAdvancedSettings(s => !s)}
            >
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                ⚙️ {showAdvancedSettings ? 'Hide Individual Format Toggles' : 'Customize Individual Formats & Hardware Controls'}
              </span>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                {showAdvancedSettings ? '▲' : '▼'}
              </span>
            </div>

            {showAdvancedSettings && (
              <div style={{ marginTop: 14, paddingTop: 12, borderTop: '1px dashed var(--border)' }}>
                {/* Format Grid */}
                <div style={{ marginBottom: 16 }}>
                  {['video', 'audio', 'text'].map(group => {
                    const groupFormats = OUTPUT_FORMATS.filter(f => f.group === group)
                    const groupLabels = { video: '🎥 Video Formats (WhatsApp & TV)', audio: '🔊 Audio & Telecom (Radio & IVR)', text: '📝 Text & Subtitles (Print & SMS)' }
                    return (
                      <div key={group} style={{ marginBottom: 14 }}>
                        <div className="section-label" style={{ fontSize: 11, marginBottom: 6 }}>{groupLabels[group]}</div>
                        <div className="format-grid">
                          {groupFormats.map(fmt => {
                            const isSelected = selectedFormats.includes(fmt.key)
                            return (
                              <label
                                key={fmt.key}
                                className={`format-item ${isSelected ? 'selected' : ''}`}
                                style={{ cursor: 'pointer' }}
                              >
                                <input
                                  type="checkbox"
                                  checked={isSelected}
                                  onChange={() => toggleFormat(fmt.key)}
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
              <div style={{ fontSize: 36, marginBottom: 8 }}>🎧</div>
              <h4 style={{ margin: '0 0 6px 0', fontSize: 16 }}>
                AI Synthetic Voice Track ({previewLang})
              </h4>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
                Natural speech synthesized via Indic Neural TTS · Ready for WhatsApp voice notes & community radio
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 }}>
                <audio
                  key={`audio-${jobId}-${previewLang}`}
                  controls
                  src={`/api/jobs/${jobId}/audio/${previewLang}`}
                  style={{ width: '100%', maxWidth: 480, height: 44 }}
                />
                <a
                  className="btn btn-sm btn-secondary"
                  href={`/api/jobs/${jobId}/audio/${previewLang}`}
                  download={`audio_${previewLang}.mp3`}
                >
                  ⬇️ Download {previewLang} Audio (.mp3)
                </a>
              </div>
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
              <div style={{ fontSize: 36, marginBottom: 6 }}>🎬</div>
              <h4 style={{ margin: '0 0 6px 0', fontSize: 16 }}>
                Dubbed & Advisory Video ({previewLang})
              </h4>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
                High-definition localized video with translated voiceover track & synchronized captions
              </p>
              <div style={{ maxWidth: 640, margin: '0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 }}>
                <video
                  key={`video-${jobId}-${previewLang}`}
                  controls
                  src={`/api/jobs/${jobId}/video/${previewLang}`}
                  style={{ width: '100%', borderRadius: 8, background: '#000', maxHeight: 380 }}
                />
                <a
                  className="btn btn-sm btn-secondary"
                  href={`/api/jobs/${jobId}/video/${previewLang}`}
                  download={`video_advisory_${previewLang}.mp4`}
                >
                  ⬇️ Download {previewLang} Video (.mp4)
                </a>
              </div>
            </div>
          )}

          {/* 4. WhatsApp Simulator Tab */}
          {activePreviewTab === 'whatsapp' && (
            <div>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', textAlign: 'center', marginBottom: 12 }}>
                💬 Simulating how rural smartphone farmers receive this multi-lingual audio note & advisory on WhatsApp.
              </p>
              <WhatsAppSimulator
                key={`wa-${jobId}-${previewLang}`}
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
                key={`ivr-${jobId}-${previewLang}`}
                audioSrc={`/api/jobs/${jobId}/ivr/${previewLang}`}
                langName={previewLang}
              />
            </div>
          )}

          {/* 6. Output Files Tab */}
          {activePreviewTab === 'files' && (
            <div>
              <div style={{ marginBottom: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div className="section-label">Generated Multi-Channel Packages & Artifacts</div>
                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  {previewData?.files?.length || 0} files ready
                </span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 10 }}>
                {[
                  { name: `video_advisory_${previewLang}.mp4`, channel: '📺 WhatsApp Video & KVK Screens', desc: 'HD video with audio voiceover & burned subtitles', url: `/api/jobs/${jobId}/video/${previewLang}` },
                  { name: `audio_${previewLang}.mp3`, channel: '🎧 WhatsApp Audio & Community Radio', desc: '44.1kHz stereo MP3 for smartphones & radio', url: `/api/jobs/${jobId}/audio/${previewLang}` },
                  { name: `ivr_audio_${previewLang}.wav`, channel: '📞 Feature Phone IVR Broadcast', desc: '8kHz Mono telecom audio for outbound voice calls', url: `/api/jobs/${jobId}/ivr/${previewLang}` },
                  { name: `bilingual_doc_${previewLang}.docx`, channel: '📄 Field Officer Prescription Slip', desc: 'Printable formatted Word document for physical handouts', url: null },
                  { name: `subtitles_${previewLang}.srt`, channel: '📝 Video Subtitles (SRT)', desc: 'Synchronized subtitle captions for VLC & YouTube', url: null },
                  { name: `translation_${previewLang}.txt`, channel: '📱 SMS & Digital Records', desc: 'Plain UTF-8 text for bulk SMS & agronomist ERP', url: null },
                ].map(item => (
                  <div
                    key={item.name}
                    style={{
                      background: 'var(--bg-input)',
                      border: '1px solid var(--border)',
                      borderRadius: 6,
                      padding: '12px 14px',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 4
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: 12, fontFamily: 'monospace', fontWeight: 600, color: 'var(--text)' }}>
                        📄 {item.name}
                      </span>
                      <span style={{ fontSize: 10, color: 'var(--accent)' }}>✓ Ready</span>
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--accent)', fontWeight: 500 }}>
                      {item.channel}
                    </div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                      {item.desc}
                    </div>
                    {item.url && (
                      <div style={{ marginTop: 6, paddingTop: 6, borderTop: '1px dashed var(--border)' }}>
                        <a
                          href={item.url}
                          download={item.name}
                          style={{ fontSize: 11, color: 'var(--accent)', textDecoration: 'none', fontWeight: 600 }}
                        >
                          ⬇️ Direct Download
                        </a>
                      </div>
                    )}
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
              ⬇️ Download Complete Multi-Channel ZIP Package
            </a>
            <button className="btn btn-secondary" onClick={reset} id="btn-new-job">
              ➕ New Advisory
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
