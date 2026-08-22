import React, { useState, useEffect } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const NAV = [
  { to: '/',         icon: <svg width="19" height="19" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>, label: 'Overview' },
  { to: '/upload',   icon: <svg width="19" height="19" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>,  label: 'Advisory Studio' },
  { to: '/review',   icon: <svg width="19" height="19" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 12h4l2-9 5 18 3-9h4"/></svg>,  label: 'Review Queue' },
  { to: '/history',  icon: <svg width="19" height="19" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>,  label: 'History & Audit' },
  { to: '/glossary', icon: <svg width="19" height="19" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>,  label: 'Agri-Glossary' },
  { to: '/training', icon: <svg width="19" height="19" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>,  label: 'Training Academy' },
  { to: '/impact',   icon: <svg width="19" height="19" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>,  label: 'Impact Ledger' },
  { to: '/docs',     icon: <svg width="19" height="19" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>, label: 'Platform Manual' },
]

export default function Sidebar() {
  const [reviewPending, setReviewPending] = useState(0)
  const [mobileOpen, setMobileOpen] = useState(false)
  const { role, logout } = useAuth()
  const location = useLocation()

  useEffect(() => { setMobileOpen(false) }, [location.pathname])

  useEffect(() => {
    const fetch_ = () =>
      fetch('/api/health')
        .then(r => r.json())
        .then(d => setReviewPending(d.review_pending || 0))
        .catch(() => {})
    fetch_()
    const id = setInterval(fetch_, 30000)
    return () => clearInterval(id)
  }, [])

  return (
    <>
      <button
        type="button"
        className="sidebar-toggle"
        aria-label={mobileOpen ? 'Close navigation' : 'Open navigation'}
        aria-expanded={mobileOpen}
        onClick={() => setMobileOpen(o => !o)}
      >
        {mobileOpen ? '✕' : '☰'}
      </button>
      {mobileOpen && (
        <div className="sidebar-scrim" onClick={() => setMobileOpen(false)} />
      )}
      <aside className={`sidebar ${mobileOpen ? 'is-open' : ''}`}>
        <div className="sidebar-logo">
          <div className="brand-3d-container">
            <div className="brand-3d-emblem" style={{
              background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.35) 0%, rgba(16, 185, 129, 0.4) 100%)',
              border: '1px solid rgba(245, 158, 11, 0.6)',
              boxShadow: '0 4px 14px rgba(245, 158, 11, 0.3)'
            }}>
              <span>🌱</span>
            </div>
            <div className="brand-3d-text-block">
              <div className="brand-3d-title">
                <span style={{
                  background: 'linear-gradient(135deg, #FFFFFF 30%, #FDE68A 70%, #34D399 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  fontWeight: 900
                }}>
                  VaaniSetu
                </span>
                <span className="brand-3d-devanagari" style={{ fontSize: 10, padding: '1px 6px', fontWeight: 800 }}>वाणीसेतु</span>
              </div>
              <div className="brand-3d-subtitle" style={{ fontSize: 9.5, padding: '2px 7px', fontWeight: 800 }}>
                BAIF AI VOICE PLATFORM
              </div>
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {NAV.map(item => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <span className="nav-icon">
                {item.icon}
              </span>
              <span style={{ flex: 1 }}>{item.label}</span>
              {item.to === '/review' && reviewPending > 0 && (
                <span className="nav-badge">{reviewPending}</span>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div>
            <div style={{ fontWeight: 700, color: '#F8FAFC', fontSize: 11.5 }}>VaaniSetu v2.0</div>
            <div style={{ color: '#34D399', fontWeight: 600, fontSize: 10.5, marginTop: 1 }}>● Air-Gapped Mode</div>
          </div>
          <span className="badge green" style={{ fontSize: 10, padding: '2px 6px' }}>OFFLINE</span>
        </div>
      </aside>
    </>
  )
}
