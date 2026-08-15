import React, { useState, useRef, useEffect } from 'react'

export default function VoiceRecorder({ onRecordingComplete, onCancel }) {
  const [isRecording, setIsRecording] = useState(false)
  const [duration, setDuration] = useState(0)
  const [audioBlob, setAudioBlob] = useState(null)
  const [audioUrl, setAudioUrl] = useState(null)
  const mediaRecorderRef = useRef(null)
  const timerRef = useRef(null)
  const chunksRef = useRef([])

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
      if (audioUrl) URL.revokeObjectURL(audioUrl)
    }
  }, [audioUrl])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      chunksRef.current = []
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/wav' })
        const url = URL.createObjectURL(blob)
        setAudioBlob(blob)
        setAudioUrl(url)
        const file = new File([blob], `mic_recording_${Date.now()}.wav`, { type: 'audio/wav' })
        onRecordingComplete(file)
        stream.getTracks().forEach(t => t.stop())
      }

      mediaRecorder.start(200)
      setIsRecording(true)
      setDuration(0)
      timerRef.current = setInterval(() => {
        setDuration(d => d + 1)
      }, 1000)
    } catch (err) {
      alert('Microphone access denied or not available. Please check browser permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60)
    const s = secs % 60
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }

  return (
    <div style={{
      background: 'var(--bg-input)',
      border: '1px dashed var(--accent)',
      borderRadius: 'var(--radius)',
      padding: '24px',
      textAlign: 'center',
      marginTop: '12px',
    }}>
      <div style={{ fontSize: 32, marginBottom: 8 }}>
        {isRecording ? '🔴' : '🎙️'}
      </div>
      
      <h4 style={{ margin: '0 0 6px 0', fontSize: 16 }}>
        {isRecording ? 'Recording Live Audio…' : audioUrl ? 'Voice Recording Ready' : 'Direct Microphone Input'}
      </h4>
      
      <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: '0 0 16px 0' }}>
        {isRecording
          ? `Speaking... (${formatTime(duration)}) — Keep speaking clearly in your local dialect`
          : audioUrl
          ? `Recorded ${formatTime(duration)} audio clip ready for translation`
          : 'Record farmer field voice query or audio advisory directly from your microphone'}
      </p>

      {audioUrl && !isRecording && (
        <div style={{ marginBottom: 16 }}>
          <audio controls src={audioUrl} style={{ width: '100%', maxWidth: 360, height: 36 }} />
        </div>
      )}

      <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
        {!isRecording ? (
          <button
            type="button"
            className="btn btn-primary"
            onClick={startRecording}
            style={{ minWidth: 140 }}
          >
            {audioUrl ? '🔄 Re-record' : '🔴 Start Recording'}
          </button>
        ) : (
          <button
            type="button"
            className="btn btn-danger"
            onClick={stopRecording}
            style={{ minWidth: 140, animation: 'pulse 1.5s infinite' }}
          >
            ⏹️ Stop ({formatTime(duration)})
          </button>
        )}

        {onCancel && (
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  )
}
