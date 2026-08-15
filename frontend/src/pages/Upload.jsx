import React, { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import DragDropZone from '../components/DragDropZone'
import LangChipGrid from '../components/LangChipGrid'
import ProgressBar from '../components/ProgressBar'
import ConfidenceBadge from '../components/ConfidenceBadge'

// Source language options for the dropdown
const SOURCE_LANGS = [
  'English', 'Hindi', 'Bengali', 'Telugu', 'Marathi', 'Tamil',
  'Gujarati', 'Urdu', 'Kannada', 'Odia', 'Malayalam', 'Punjabi', 'Assamese', 'Nepali',
]

// Output format definitions with size indicators and descriptions
const OUTPUT_FORMATS = [
  {
    key: 'txt',
    label: 'Plain Text (.txt)',
    desc: 'SMS, app content, offline reading',
    size: 'tiny',
    default: true,
    group: 'text',
  },
  {
    key: 'docx',
    label: 'Bilingual Doc (.docx)',
    desc: 'Printed handout for field officers',
    size: 'small',
    default: true,
    group: 'text',
  },
  {
    key: 'srt',
    label: 'Subtitles SRT (.srt)',
    desc: 'VLC player, video editors, YouTube',
    size: 'tiny',
    default: true,
    group: 'text',
  },
  {
    key: 'vtt',
    label: 'Subtitles VTT (.vtt)',
    desc: 'Web embed, BAIF portal upload',
    size: 'tiny',
    default: false,
    group: 'text',
  },
  {
    key: 'mp3',
    label: 'Audio MP3 (.mp3)',
    desc: 'Community radio, WhatsApp audio',
    size: 'medium',
    default: true,
    group: 'audio',
  },
  {
    key: 'ivr_wav',
    label: 'IVR Audio (.wav)',
    desc: '8kHz for IVR / feature phones',
    size: 'small',
    default: false,
    group: 'audio',
  },
  {
    key: 'dubbed_mp4',
    label: 'Dubbed Video (.mp4)',
    desc: 'Video with translated voice-over',
    size: 'large',
    default: false,
    group: 'video',
    fullOnly: true,
  },
  {
    key: 'captioned_mp4',
    label: 'Captioned Video (.mp4)',
    desc: 'Burned subtitles for social media',
    size: 'large',
    default: false,
    group: 'video',
    fullOnly: true,
  },
  {
    key: 'whatsapp',
    label: 'WhatsApp Chunks (.mp4)',
    desc: 'Auto-split <15MB for delivery',
    size: 'medium',
    default: false,
    group: 'video',
    fullOnly: true,
  },
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
  const [inputType, setInputType] = useState('file')
  const [textContent, setTextContent] = useState('')
  const [targetLangs, setTargetLangs] = useState(['Hindi'])
  const [file, setFile] = useState(null)
  const [farmerCtx, setFarmerCtx] = useState('')
  const [resourceSaver, setResourceSaver] = useState(false)
  const [bypassCache, setBypassCache] = useState(false)
  const [qualityMode, setQualityMode] = useState('full')
  const [selectedFormats, setSelectedFormats] = useState(DEFAULT_FORMATS)
  const [showFormats, setShowFormats] = useState(false)

  // Job state
  const [submitting, setSubmitting] = useState(false)
  const [jobId, setJobId] = useState(null)
  const [progress, setProgress] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const esRef = useRef(null)

  const canSubmit = (inputType === 'file' ? file : textContent.trim())
    && targetLangs.length > 0 && !submitting

  const toggleFormat = (key) => {
    setSelectedFormats(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    )
  }

  // In draft mode, video formats are unavailable
  const effectiveFormats = qualityMode === 'draft'
    ? selectedFormats.filter(f => !OUTPUT_FORMATS.find(o => o.key === f)?.fullOnly)
    : selectedFormats

  const submit = async () => {
    if (!canSubmit) return
    setSubmitting(true)
    setError(null)
    setProgress({ stage: 'queued', pct: 0, message: 'Queuing job…' })

    if (Notification.permission === 'default') {
      Notification.requestPermission()
    }

    let uploadFile = file
    if (inputType === 'text' && textContent.trim()) {
      const blob = new Blob([textContent], { type: 'text/plain' })
      uploadFile = new File([blob], 'short_text.txt', { type: 'text/plain' })
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
      if (d.status === 'completed') { setResult(d); setSubmitting(false) }
      else if (d.status === 'failed') { setError(d.error_log || 'Job failed'); setSubmitting(false) }
      else setTimeout(poll, 3000)
    }
    poll()
  }

  const reset = () => {
    setFile(null); setTextContent(''); setJobId(null); setProgress(null)
    setResult(null); setError(null); setSubmitting(false)
    if (esRef.current) { esRef.current.close(); esRef.current = null }
  }

  return (
    <div>
      <div className="page-header">
        <h2>New Translation Job</h2>
        <p>Upload a video, audio, or document to translate into Indian languages</p>
      </div>

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
            📤 Translate Content
          </button>
          <button
            className={mode === 'reverse_bridge' ? 'active' : ''}
            onClick={() => setMode('reverse_bridge')}
            type="button"
            id="mode-reverse"
          >
            🎙️ Farmer Voice → HQ
          </button>
        </div>

        {mode === 'reverse_bridge' && (
          <div style={{ marginTop: 16 }}>
            <div className="alert alert-indigo mb-3" style={{ background: 'var(--indigo-soft)', color: 'var(--indigo)', borderColor: 'rgba(124,131,208,0.2)' }}>
              Farmer audio is transcribed, translated to English, and forwarded to HQ experts.
            </div>
            <label>Field Context (optional)</label>
            <textarea
              id="farmer-context"
              value={farmerCtx}
              onChange={e => setFarmerCtx(e.target.value)}
              rows={3}
              placeholder="E.g. crop disease query from Maharashtra, Kharif 2024…"
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
                  <option value="Auto-Detect">🔍 Auto-Detect</option>
                  {SOURCE_LANGS.map(l => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
                <p style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 6 }}>
                  Auto-Detect works for all Indian languages
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
                  File
                </button>
                <button
                  type="button"
                  className={`btn btn-sm ${inputType === 'text' ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setInputType('text')}
                >
                  Text
                </button>
              </div>
            </div>

            {inputType === 'file' ? (
              <>
                <DragDropZone onFile={setFile} accept="audio/*,video/*,.txt,.pdf,.docx,.csv" />
                <div style={{ marginTop: 12, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                  {[
                    ['🎬 Video', '.mp4 .mkv · Max 15 min, 200 MB'],
                    ['🎙️ Audio', '.mp3 .wav .m4a · Max 30 min'],
                    ['📄 Docs', '.pdf .docx .txt .csv'],
                    ['📊 Sheets', '.csv (data/survey)'],
                  ].map(([icon, desc]) => (
                    <div key={icon} style={{ fontSize: 11, color: 'var(--text-dim)', display: 'flex', gap: 6 }}>
                      <span>{icon}</span>
                      <span>{desc}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <textarea
                value={textContent}
                onChange={e => setTextContent(e.target.value)}
                placeholder="Paste or type text here for translation…"
                rows={8}
                className="text-input"
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
                <div className="quality-option-title">Draft</div>
                <div className="quality-option-desc">
                  Text + subtitles + audio only. 1–5 minutes. Best for quick review.
                </div>
                <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-dim)' }}>
                  Piper TTS · 2-beam translation
                </div>
              </div>
              <div
                className={`quality-option ${qualityMode === 'full' ? 'selected' : ''}`}
                onClick={() => setQualityMode('full')}
                id="quality-full"
              >
                <span className="quality-option-icon">🎬</span>
                <div className="quality-option-title">Full Quality</div>
                <div className="quality-option-desc">
                  All outputs incl. dubbed & captioned video. 15–90 min.
                </div>
                <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-dim)' }}>
                  XTTS voice cloning · 4-beam translation
                </div>
              </div>
            </div>
          </div>

          {/* ── Output Format Selector ── */}
          <div className="card mb-4">
            <div
              className="collapsible-header"
              onClick={() => setShowFormats(v => !v)}
              style={{ cursor: 'pointer' }}
            >
              <div className="card-title" style={{ marginBottom: 0 }}>
                <span className="card-title-icon">📦</span>
                Output Formats
                <span style={{ fontSize: 11, fontWeight: 400, color: 'var(--text-dim)', marginLeft: 6 }}>
                  ({effectiveFormats.length} selected)
                </span>
              </div>
              <span className={`collapsible-arrow ${showFormats ? 'open' : ''}`}>▾</span>
            </div>

            {showFormats && (
              <div style={{ marginTop: 16 }}>
                {['text', 'audio', 'video'].map(group => {
                  const groupFormats = OUTPUT_FORMATS.filter(f => f.group === group)
                  const groupLabels = { text: '📝 Text & Subtitles', audio: '🔊 Audio', video: '🎥 Video (Full Quality only)' }
                  return (
                    <div key={group} style={{ marginBottom: 16 }}>
                      <div className="section-label">{groupLabels[group]}</div>
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
                <p style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 4 }}>
                  Deselecting LARGE video files significantly reduces processing time and ZIP size.
                </p>
              </div>
            )}
          </div>

          {/* ── Advanced Options ── */}
          <div className="card mb-4">
            <div className="card-title">
              <span className="card-title-icon">🛠️</span> Advanced Options
            </div>
            <div className="toggle-row">
              <div className="toggle-row-info">
                <strong>🐢 Resource Saver</strong>
                <p>Limits CPU usage so the computer stays responsive during processing.</p>
              </div>
              <Toggle checked={resourceSaver} onChange={setResourceSaver} />
            </div>
            <div className="toggle-row">
              <div className="toggle-row-info">
                <strong>🔄 Force Re-run (Bypass Cache)</strong>
                <p>Ignore cached translations and re-run the full pipeline. Use after editing Translation Memory.</p>
              </div>
              <Toggle checked={bypassCache} onChange={setBypassCache} />
            </div>
          </div>

          {error && (
            <div className="alert alert-red mb-4">⚠️ {error}</div>
          )}

          <button
            className="btn btn-primary btn-lg"
            onClick={submit}
            disabled={!canSubmit}
            id="btn-submit"
            style={{ width: '100%', justifyContent: 'center' }}
          >
            🚀 Start Translation
          </button>
        </>
      )}

      {/* ── Progress View ── */}
      {(submitting || (progress && !result)) && (
        <div className="card mt-6">
          <div className="card-title">
            <span className="card-title-icon">⚙️</span> Processing…
          </div>
          {progress && (
            <ProgressBar
              stage={progress.stage}
              pct={progress.pct}
              message={progress.message}
            />
          )}
          <p style={{ marginTop: 16, fontSize: 12, color: 'var(--text-dim)' }}>
            You can close this tab — the job continues on the server. Check History when it's done.
          </p>
        </div>
      )}

      {/* ── Result View ── */}
      {result && (
        <div className="card mt-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: 18, fontWeight: 700 }}>
                ✅ Translation Complete
              </h3>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                Job ID: <span className="font-mono">{jobId?.slice(0, 8)}…</span>
              </p>
            </div>
            <ConfidenceBadge
              level={result.confidence_level}
              score={result.avg_confidence}
            />
          </div>

          {result.confidence_level === 'amber' && (
            <div className="alert alert-amber mb-4" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span>⚠️ Some segments have amber confidence — review before distributing.</span>
              <button
                className="btn btn-sm btn-amber"
                style={{ marginLeft: 12, flexShrink: 0 }}
                onClick={() => navigate('/review')}
              >
                Review Queue →
              </button>
            </div>
          )}

          {result.confidence_level === 'red' && (
            <div className="alert alert-red mb-4">
              🔴 Low confidence — a bilingual expert must review before distribution.
            </div>
          )}

          {result.distribution_clearance === 'cleared' ? (
            <div className="alert alert-green mb-4">✓ All segments cleared — safe to distribute.</div>
          ) : (
            <div className="alert alert-amber mb-4">⚠️ Pending review — distribution on hold.</div>
          )}

          <div className="result-actions">
            <a
              className="btn btn-primary btn-lg"
              href={`/api/jobs/${jobId}/download?token=${localStorage.getItem('vaani_token')}`}
              download
              id="btn-download"
            >
              ⬇️ Download ZIP
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
