import React, { useState } from 'react'

export default function Documentation() {
  const [iframeKey, setIframeKey] = useState(0)

  const reloadIframe = () => setIframeKey(k => k + 1)
  const openExternal = () => window.open('/api/docs/html', '_blank')

  return (
    <div className="docs-page" style={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      {/* Top Controls Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 14,
        padding: '14px 20px',
        background: '#111C30',
        border: '1px solid var(--border)',
        borderRadius: 14,
        boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
        flexShrink: 0,
        flexWrap: 'wrap',
        gap: 12
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{
            width: 44,
            height: 44,
            borderRadius: 12,
            background: 'rgba(245, 158, 11, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 22,
            color: '#F59E0B'
          }}>
            📖
          </div>
          <div>
            <h2 style={{ fontSize: 17, fontWeight: 800, margin: 0, color: '#F8FAFC', display: 'flex', alignItems: 'center', gap: 8 }}>
              <span>Platform Manual & Architecture Hub</span>
              <span style={{ color: '#F59E0B', fontSize: 14, fontWeight: 700 }}>(मार्गदर्शिका और दस्तावेज़)</span>
            </h2>
            <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: '3px 0 0 0', fontWeight: 500 }}>
              100% Offline AI Reference Guide · Complete Technical & Field Operations Handover
            </p>
          </div>
        </div>

        {/* Action Tools */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
          <button
            type="button"
            className="btn btn-sm btn-secondary"
            onClick={reloadIframe}
            title="Reload Documentation"
            style={{ fontSize: 13, padding: '8px 14px', borderRadius: 8, fontWeight: 600 }}
          >
            🔄 Refresh Manual
          </button>
          <button
            type="button"
            className="btn btn-sm btn-primary"
            onClick={openExternal}
            title="Open interactive manual in dedicated browser tab"
            style={{ fontSize: 13, padding: '8px 16px', borderRadius: 8, fontWeight: 800 }}
          >
            ↗️ Open Fullscreen Tab
          </button>
        </div>
      </div>

      {/* Embedded Interactive Documentation Viewport */}
      <div style={{
        flex: 1,
        background: '#090E1A',
        border: '1px solid var(--border)',
        borderRadius: 16,
        overflow: 'hidden',
        boxShadow: '0 12px 36px rgba(0,0,0,0.6)'
      }}>
        <iframe
          key={iframeKey}
          src="/api/docs/html"
          title="VaaniSetu Complete Documentation"
          style={{
            width: '100%',
            height: '100%',
            border: 'none',
            display: 'block'
          }}
        />
      </div>
    </div>
  )
}
