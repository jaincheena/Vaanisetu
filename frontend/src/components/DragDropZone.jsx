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
    >
      <input
        ref={inputRef}
        type="file"
        accept={acceptTypes}
        style={{ display: 'none' }}
        onChange={e => e.target.files[0] && handle(e.target.files[0])}
        id="file-input"
      />

      {selected ? (
        <div>
          <div className="drop-icon">{ICONS[detectType(selected.name)]}</div>
          <p style={{ fontWeight: 600, color: 'var(--text)' }}>{selected.name}</p>
          <p className="drop-hint mt-2">{fmtSize(selected.size)} · Click to change</p>
        </div>
      ) : (
        <div>
          <div className="drop-icon">📁</div>
          <p>Drag & drop your file here, or <span style={{ color: 'var(--green-accent)' }}>browse</span></p>
          <p className="drop-hint">Video · Audio · Text · Max 2 GB</p>
          <p className="drop-hint">Works offline — no internet required</p>
        </div>
      )}
    </div>
  )
}
