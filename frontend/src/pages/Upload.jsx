import React, { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import DragDropZone from '../components/DragDropZone'
import LangChipGrid from '../components/LangChipGrid'
import ProgressBar from '../components/ProgressBar'
import ConfidenceBadge from '../components/ConfidenceBadge'

const SOURCE_LANGS = [
  'English','Hindi','Bengali','Telugu','Marathi','Tamil','Gujarati',
  'Urdu','Kannada','Odia','Malayalam','Punjabi','Assamese','Nepali',
]

export default function Upload() {
  const navigate = useNavigate()
  const [mode, setMode] = useState('translate')
  const [sourceLang, setSourceLang] = useState('English')
  const [inputType, setInputType] = useState('file')
  const [textContent, setTextContent] = useState('')
  const [targetLangs, setTargetLangs] = useState(['Hindi'])
  const [file, setFile] = useState(null)
  const [farmerCtx, setFarmerCtx] = useState('')
  const [resourceSaver, setResourceSaver] = useState(false)
  const [bypassCache, setBypassCache] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [jobId, setJobId] = useState(null)
  const [progress, setProgress] = useState(null)   // {stage, pct, message}
  const [result, setResult] = useState(null)        // {confidence_level, avg_confidence, ...}
  const [error, setError] = useState(null)
  const esRef = useRef(null)

  const canSubmit = (inputType === 'file' ? file : textContent.trim()) && targetLangs.length > 0 && !submitting

  const submit = async () => {
    if (!canSubmit) return
    setSubmitting(true)
    setError(null)
    setProgress({ stage: 'queued', pct: 0, message: 'Queuing job…' })

    // Request notification permission if not yet decided
    if (Notification.permission === 'default') {
      Notification.requestPermission();
    }

    let uploadFile = file;
    if (inputType === 'text' && textContent.trim()) {
      const blob = new Blob([textContent], { type: 'text/plain' });
      uploadFile = new File([blob], 'short_text.txt', { type: 'text/plain' });
    }

    const fd = new FormData()
    fd.append('file', uploadFile)
    fd.append('target_langs', JSON.stringify(targetLangs))
    fd.append('source_lang', sourceLang)
    fd.append('mode', mode)
    fd.append('farmer_context', farmerCtx)
    fd.append('resource_saver', resourceSaver)
    fd.append('bypass_cache', bypassCache)

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

    // SSE stream
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
        
        // Trigger browser notification
        if (Notification.permission === 'granted') {
          new Notification('VaaniSetu: Translation Complete', {
            body: `Job completed with ${ev.confidence_level} confidence.`,
            icon: '/favicon.ico'
          });
        }
      }
      if (ev.stage === 'failed') {
        setError(ev.message || 'Job failed')
        setSubmitting(false)
        es.close()
      }
    }

    es.onerror = () => {
      es.close()
      // fallback poll
      pollStatus(id)
    }
  }

  const pollStatus = async (id) => {
    const poll = async () => {
      const r = await fetch(`/api/jobs/${id}/status`)
      const d = await r.json()
      if (d.status === 'completed') {
        setResult(d)
        setSubmitting(false)
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
    setResult(null); setError(null); setSubmitting(false)
    if (esRef.current) { esRef.current.close(); esRef.current = null }
  }

  return (
    <div>
      <div className="page-header">
        <h2>Submit Translation Job</h2>
        <p>Upload a video, audio, or text file for AI translation into multiple Indian languages</p>
      </div>

      {/* Mode toggle */}
      <div className="card mb-4">
        <div className="card-title">Translation Mode</div>
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
            🎙️ Reverse Bridge (Farmer Voice)
          </button>
        </div>
        {mode === 'reverse_bridge' && (
          <div className="mt-4">
            <div className="alert alert-green" style={{ marginBottom: 12 }}>
              ℹ️ Farmer audio → English transcript + translation for HQ experts.
            </div>
            <label>Context (optional)</label>
            <textarea
              id="farmer-context"
              value={farmerCtx}
              onChange={e => setFarmerCtx(e.target.value)}
              rows={3}
              placeholder="E.g. crop disease query from Maharashtra, Kharif 2024..."
            />
          </div>
        )}
      </div>

      {!result && !submitting && (
        <>
          {/* Language selection */}
          <div className="card mb-4">
            <div className="card-title">Language Settings</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 20 }}>
              <div>
                <label>Source Language</label>
                <select
                  value={sourceLang}
                  onChange={e => setSourceLang(e.target.value)}
                  className="text-input"
                >
                  <option value="Auto-Detect">Auto-Detect</option>
                  {SOURCE_LANGS.map(l => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
              </div>
              <div>
                <label>Target Languages ({targetLangs.length} selected)</label>
                <LangChipGrid
                  selected={targetLangs}
                  onChange={setTargetLangs}
                  exclude={[sourceLang]}
                />
              </div>
            </div>
          </div>

          {/* File/Text input */}
          <div className="card mb-4">
            <div className="card-title flex items-center justify-between">
              Input Content
              <div className="flex gap-2">
                <button
                  type="button"
                  className={`btn btn-sm ${inputType === 'file' ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setInputType('file')}
                >
                  📁 Upload File
                </button>
                <button
                  type="button"
                  className={`btn btn-sm ${inputType === 'text' ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setInputType('text')}
                >
                  ✍️ Short Text
                </button>
              </div>
            </div>

            {inputType === 'file' ? (
              <>
                <DragDropZone onFile={setFile} accept="audio/*,video/*,.txt,.pdf,.docx,.csv" />
                <p style={{ margin: '14px 0 0 0', fontSize: '13px', color: 'var(--text-muted)' }}>
                  <strong>Video:</strong> .mp4, .mkv (Max 15 min, 200MB)<br/>
                  <strong>Audio:</strong> .mp3, .wav (Max 30 min, 150MB uncompressed / 50MB compressed)<br/>
                  <strong>Documents (MVP Selection):</strong> .pdf, .docx, .csv, .txt (Note: .pptx and .xlsx support coming soon)
                </p>
              </>
            ) : (
              <textarea
                value={textContent}
                onChange={e => setTextContent(e.target.value)}
                placeholder="Paste or type short text here for translation..."
                rows={8}
                style={{ width: '100%', padding: '12px', border: '1px solid var(--border)', borderRadius: '8px', background: 'var(--bg-card)' }}
              />
            )}
          </div>

          {error && (
            <div className="alert alert-red mb-4">⚠️ {error}</div>
          )}

          <div className="card mb-4" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '15px 20px', background: 'var(--bg-card)' }}>
            <div>
              <strong>🐢 Resource Saver Mode</strong>
              <p style={{ margin: '4px 0 0', fontSize: '13px', color: 'var(--text-muted)' }}>
                Limits AI CPU usage so your computer won't freeze while doing background translations.
              </p>
            </div>
            <label className="toggle-switch" style={{ position: 'relative', display: 'inline-block', width: '40px', height: '24px' }}>
              <input type="checkbox" checked={resourceSaver} onChange={e => setResourceSaver(e.target.checked)} style={{ opacity: 0, width: 0, height: 0 }} />
              <span style={{ position: 'absolute', cursor: 'pointer', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: resourceSaver ? '#4CAF50' : '#ccc', transition: '.4s', borderRadius: '34px' }}>
                <span style={{ position: 'absolute', content: '""', height: '18px', width: '18px', left: resourceSaver ? '19px' : '3px', bottom: '3px', backgroundColor: 'white', transition: '.4s', borderRadius: '50%' }}></span>
              </span>
            </label>
          </div>

          <div className="card mb-4" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '15px 20px', background: 'var(--bg-card)' }}>
            <div>
              <strong>🔄 Force Re-run (Bypass Cache)</strong>
              <p style={{ margin: '4px 0 0', fontSize: '13px', color: 'var(--text-muted)' }}>
                Ignore previously cached translations and re-run the pipeline to apply new edits from the Translation Memory.
              </p>
            </div>
            <label className="toggle-switch" style={{ position: 'relative', display: 'inline-block', width: '40px', height: '24px' }}>
              <input type="checkbox" checked={bypassCache} onChange={e => setBypassCache(e.target.checked)} style={{ opacity: 0, width: 0, height: 0 }} />
              <span style={{ position: 'absolute', cursor: 'pointer', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: bypassCache ? '#4CAF50' : '#ccc', transition: '.4s', borderRadius: '34px' }}>
                <span style={{ position: 'absolute', content: '""', height: '18px', width: '18px', left: bypassCache ? '19px' : '3px', bottom: '3px', backgroundColor: 'white', transition: '.4s', borderRadius: '50%' }}></span>
              </span>
            </label>
          </div>

          <button
            className="btn btn-primary btn-lg"
            onClick={submit}
            disabled={!canSubmit}
            id="btn-submit"
          >
            🚀 Start Translation
          </button>
        </>
      )}

      {/* Progress view */}
      {(submitting || (progress && !result)) && (
        <div className="card mt-4">
          <div className="card-title">Processing…</div>
          {progress && (
            <ProgressBar
              stage={progress.stage}
              pct={progress.pct}
              message={progress.message}
            />
          )}
        </div>
      )}

      {/* Result view */}
      {result && (
        <div className="card mt-4">
          <div className="flex items-center justify-between mb-4">
            <h3>✅ Translation Complete</h3>
            <ConfidenceBadge
              level={result.confidence_level}
              score={result.avg_confidence}
            />
          </div>

          {result.confidence_level === 'amber' && (
            <div className="alert alert-amber mb-4">
              ⚠️ Some segments have amber confidence. Review before distributing.{' '}
              <button
                className="btn btn-sm btn-amber"
                style={{ marginLeft: 8 }}
                onClick={() => navigate('/review')}
              >
                Go to Review Queue →
              </button>
            </div>
          )}

          {result.distribution_clearance === 'cleared' ? (
            <div className="alert alert-green mb-4">
              ✓ All segments cleared — safe to distribute.
            </div>
          ) : (
            <div className="alert alert-amber mb-4">
              ⚠️ Pending review items — distribution holds.
            </div>
          )}

          <div className="flex gap-3 mt-4">
            <a
              className="btn btn-primary"
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
              📋 View History
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
