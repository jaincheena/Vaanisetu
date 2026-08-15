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
        marginBottom: 12,
        padding: '12px 16px',
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-sm)',
        flexShrink: 0
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontSize: 24 }}>📖</span>
          <div>
            <h2 style={{ fontSize: 16, fontWeight: 700, margin: 0, color: 'var(--text)' }}>
              Platform Manual & Architecture Hub
            </h2>
            <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: '2px 0 0 0' }}>
              100% Offline AI Reference Guide · Complete Technical & Field Operations Handover
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button
            type="button"
            className="btn btn-sm btn-secondary"
            onClick={reloadIframe}
            title="Reload Documentation"
          >
            🔄 Refresh
          </button>
          <button
            type="button"
            className="btn btn-sm btn-primary"
            onClick={openExternal}
            title="Open interactive manual in dedicated browser tab"
          >
            ↗️ Open Fullscreen Tab
          </button>
        </div>
      </div>

      {/* Embedded Interactive Documentation Viewport */}
      <div style={{
        flex: 1,
        background: '#fff',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-sm)',
        overflow: 'hidden',
        boxShadow: '0 4px 12px rgba(0,0,0,0.08)'
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
