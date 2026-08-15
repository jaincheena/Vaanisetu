import React from 'react'

export default function WhatsAppSimulator({ text, langName, audioSrc }) {
  const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

  return (
    <div style={{
      background: '#0b141a',
      borderRadius: 16,
      border: '2px solid #202c33',
      maxWidth: 380,
      margin: '0 auto',
      overflow: 'hidden',
      boxShadow: '0 12px 32px rgba(0,0,0,0.5)',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      color: '#e9edef'
    }}>
      {/* Header */}
      <div style={{
        background: '#202c33',
        padding: '10px 14px',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        borderBottom: '1px solid rgba(255,255,255,0.06)'
      }}>
        <div style={{
          width: 38,
          height: 38,
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #25D366, #128C7E)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 18
        }}>
          🌱
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 14, fontWeight: 600, color: '#e9edef' }}>
            BAIF Krishi Salah Kendra
          </div>
          <div style={{ fontSize: 11, color: '#8696a0' }}>
            Official Advisory · {langName}
          </div>
        </div>
        <div style={{ fontSize: 16, color: '#8696a0' }}>⋮</div>
      </div>

      {/* Chat Body */}
      <div style={{
        background: '#0b141a',
        backgroundImage: 'radial-gradient(circle at 50% 50%, #111b21 0%, #0b141a 100%)',
        padding: '16px 12px',
        minHeight: 280,
        display: 'flex',
        flexDirection: 'column',
        gap: 10
      }}>
        {/* Date chip */}
        <div style={{
          alignSelf: 'center',
          background: '#182229',
          color: '#8696a0',
          fontSize: 11,
          padding: '4px 10px',
          borderRadius: 8,
          marginBottom: 4
        }}>
          TODAY
        </div>

        {/* Audio Message Bubble if present */}
        {audioSrc && (
          <div style={{
            background: '#005c4b',
            borderRadius: '8px 8px 8px 0px',
            padding: '10px 12px',
            maxWidth: '90%',
            alignSelf: 'flex-start',
            boxShadow: '0 1px 2px rgba(0,0,0,0.3)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
              <span style={{ fontSize: 18 }}>🎙️</span>
              <span style={{ fontSize: 12, fontWeight: 600, color: '#e9edef' }}>
                Voice Note ({langName})
              </span>
            </div>
            <audio controls src={audioSrc} style={{ width: 240, height: 32 }} />
            <div style={{
              textAlign: 'right',
              fontSize: 10,
              color: '#8696a0',
              marginTop: 4
            }}>
              {currentTime} ✓✓
            </div>
          </div>
        )}

        {/* Text Advisory Bubble */}
        <div style={{
          background: '#005c4b',
          borderRadius: '8px 8px 8px 0px',
          padding: '10px 12px',
          maxWidth: '92%',
          alignSelf: 'flex-start',
          boxShadow: '0 1px 2px rgba(0,0,0,0.3)'
        }}>
          <div style={{
            fontSize: 12,
            fontWeight: 700,
            color: '#25D366',
            marginBottom: 4,
            display: 'flex',
            alignItems: 'center',
            gap: 4
          }}>
            <span>📢</span> BAIF KISAN BULLETIN
          </div>
          <p style={{
            fontSize: 13,
            lineHeight: 1.45,
            margin: '0 0 6px 0',
            color: '#e9edef',
            whiteSpace: 'pre-wrap'
          }}>
            {text || 'No translated text available.'}
          </p>
          <div style={{
            fontSize: 11,
            color: 'rgba(255,255,255,0.7)',
            borderTop: '1px solid rgba(255,255,255,0.1)',
            paddingTop: 4,
            marginTop: 6
          }}>
            📞 Kisan Toll-Free Help: 1800-180-1551
          </div>
          <div style={{
            textAlign: 'right',
            fontSize: 10,
            color: 'rgba(255,255,255,0.5)',
            marginTop: 4
          }}>
            {currentTime} ✓✓
          </div>
        </div>
      </div>
    </div>
  )
}
