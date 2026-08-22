import React, { useState, useRef } from 'react'

const DEFAULT_ACCEPT = 'video/*,audio/*,video/mp4,video/x-matroska,video/quicktime,video/x-msvideo,video/webm,.mp4,.mkv,.avi,.mov,.webm,.mp3,.wav,.ogg,.m4a,.flac,.aac,.opus,.3gp,.amr,.caf,.wma,.txt,.pdf,.docx,.csv'
const ICONS   = { video: '🎬', audio: '🎙️', text: '📄' }

function detectType(name) {
  const s = name.split('.').pop().toLowerCase()
  if (['mp4','mkv','avi','mov','webm'].includes(s)) return 'video'
  if (['mp3','wav','ogg','m4a','flac','aac','opus','3gp','amr','caf','wma'].includes(s)) return 'audio'
  return 'text'
}

export default function DragDropZone({ onFile, accept }) {
  const inputRef = useRef()
  const [dragging, setDragging] = useState(false)
  const [selected, setSelected] = useState(null)
  const acceptTypes = accept || DEFAULT_ACCEPT

  const handle = (file) => {
    setSelected(file)
    onFile(file)
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handle(file)
  }

  const fmtSize = (b) => b > 1e6 ? `${(b/1e6).toFixed(1)} MB` : `${(b/1e3).toFixed(0)} KB`

  return (
    <div
      className={`drop-zone ${dragging ? 'drag-over' : ''}`}
      onDragOver={e => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      onClick={() => inputRef.current && inputRef.current.click()}
      role="button"
      id="file-drop-zone"
      tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && inputRef.current && inputRef.current.click()}
      style={{
        position: 'relative',
        overflow: 'hidden',
        background: 'linear-gradient(180deg, #0B1120 0%, #080D18 100%)',
        border: dragging ? '2px dashed #10B981' : '1.5px dashed rgba(255, 255, 255, 0.2)',
        borderRadius: 16,
        padding: '36px 20px',
        textAlign: 'center',
        cursor: 'pointer',
        boxShadow: dragging ? '0 0 30px rgba(16, 185, 129, 0.35)' : 'inset 0 2px 6px rgba(0, 0, 0, 0.7), 0 1px 0 rgba(255, 255, 255, 0.08)',
        transition: 'all 0.25s cubic-bezier(0.16, 1, 0.3, 1)'
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept={acceptTypes}
        style={{ display: 'none' }}
        onChange={e => e.target.files[0] && handle(e.target.files[0])}
        id="file-input"
      />

      {/* Moving Acoustic Scanner Beam */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '40%',
        background: 'linear-gradient(180deg, rgba(16, 185, 129, 0.12) 0%, transparent 100%)',
        animation: 'radarSweep 4s ease-in-out infinite',
        pointerEvents: 'none'
      }} />

      {selected ? (
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{
            fontSize: 44,
            marginBottom: 10,
            animation: 'iconBob 3.5s ease-in-out infinite',
            filter: 'drop-shadow(0 0 14px #10B981)'
          }}>
            {ICONS[detectType(selected.name)]}
          </div>
          <p style={{ fontWeight: 800, color: '#F8FAFC', fontSize: 15, margin: 0 }}>
            {selected.name}
          </p>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            marginTop: 8,
            background: 'rgba(16, 185, 129, 0.2)',
            border: '1px solid rgba(52, 211, 153, 0.4)',
            borderRadius: 20,
            padding: '3px 12px',
            fontSize: 12,
            color: '#86EFAC',
            fontWeight: 700
          }}>
            <span>✓ {fmtSize(selected.size)}</span>
            <span>·</span>
            <span>Click or Drop to Replace</span>
          </div>
        </div>
      ) : (
        <div style={{ position: 'relative', zIndex: 1 }}>
          {/* Animated 3D Floating Upload Icon */}
          <div style={{
            width: 58,
            height: 58,
            borderRadius: 18,
            background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.25) 0%, rgba(16, 185, 129, 0.3) 100%)',
            border: '1.5px solid rgba(245, 158, 11, 0.5)',
            boxShadow: '0 8px 24px rgba(245, 158, 11, 0.3)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 28,
            marginBottom: 14,
            animation: 'iconBob 3.5s ease-in-out infinite'
          }}>
            📁
          </div>

          <p style={{ fontSize: 14.5, color: '#F8FAFC', fontWeight: 700, margin: '0 0 6px 0' }}>
            Drag & drop your agricultural advisory, or <span style={{ color: '#F59E0B', textDecoration: 'underline' }}>browse</span>
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 12, fontSize: 12, color: '#94A3B8', fontWeight: 600, marginTop: 4 }}>
            <span>🎬 HD Video</span>
            <span>·</span>
            <span>🎙️ Field Audio</span>
            <span>·</span>
            <span>📄 Advisory Text</span>
            <span>·</span>
            <span>⚡ Max 2 GB</span>
          </div>
        </div>
      )}
    </div>
  )
}
