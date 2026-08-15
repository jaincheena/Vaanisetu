import React, { useState } from 'react'

export default function IVRSimulator({ audioSrc, langName }) {
  const [calling, setCalling] = useState(false)
  const [callSecs, setCallSecs] = useState(0)

  const toggleCall = () => {
    setCalling(c => !c)
    setCallSecs(0)
  }

  return (
    <div style={{
      background: '#1e2022',
      borderRadius: 24,
      border: '4px solid #33383f',
      maxWidth: 280,
      margin: '0 auto',
      padding: '20px 16px',
      boxShadow: '0 16px 36px rgba(0,0,0,0.6)',
      fontFamily: 'monospace',
      color: '#e9edef'
    }}>
      {/* Screen */}
      <div style={{
        background: '#8ab489',
        color: '#112211',
        borderRadius: 8,
        padding: '12px 10px',
        textAlign: 'center',
        border: '2px solid #5a7b59',
        boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.3)',
        marginBottom: 16
      }}>
        <div style={{ fontSize: 10, fontWeight: 'bold', borderBottom: '1px dashed #5a7b59', paddingBottom: 4 }}>
          BAIF KISAN CALL 8kHz
        </div>
        <div style={{ fontSize: 14, fontWeight: 'bold', margin: '8px 0 4px 0' }}>
          {calling ? '📞 IN CALL…' : '🟢 READY'}
        </div>
        <div style={{ fontSize: 11 }}>
          {calling ? `Lang: ${langName}` : 'Toll-Free Broadcast'}
        </div>
        {calling && (
          <div style={{ marginTop: 8 }}>
            <audio autoPlay controls src={audioSrc} style={{ width: '100%', height: 28 }} />
          </div>
        )}
      </div>

      {/* Keypad */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: 8,
        marginBottom: 16
      }}>
        {['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#'].map(key => (
          <div
            key={key}
            style={{
              background: '#2b2f36',
              borderRadius: 6,
              padding: '10px 0',
              textAlign: 'center',
              fontSize: 14,
              fontWeight: 'bold',
              color: '#d1d7db',
              boxShadow: '0 2px 0 #181a1d',
              userSelect: 'none'
            }}
          >
            {key}
          </div>
        ))}
      </div>

      {/* Call Buttons */}
      <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
        <button
          type="button"
          onClick={toggleCall}
          style={{
            flex: 1,
            background: calling ? '#dc2626' : '#16a34a',
            color: '#fff',
            border: 'none',
            borderRadius: 8,
            padding: '10px',
            fontWeight: 'bold',
            fontSize: 13,
            cursor: 'pointer',
            boxShadow: '0 2px 0 rgba(0,0,0,0.4)'
          }}
        >
          {calling ? '🔴 End Call' : '📞 Answer Broadcast'}
        </button>
      </div>

      <div style={{ textAlign: 'center', fontSize: 10, color: '#8696a0', marginTop: 12 }}>
        Simulating 8kHz Downsampled GSM Audio for Feature Phones
      </div>
    </div>
  )
}
