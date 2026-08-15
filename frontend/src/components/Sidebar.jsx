import React, { useState, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const NAV = [
  { to: '/upload',   icon: <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>,  label: 'Upload' },
  { to: '/history',  icon: <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>,  label: 'History' },
  { to: '/review',   icon: <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 12h4l2-9 5 18 3-9h4"/></svg>,  label: 'Review Queue' },
  { to: '/impact',   icon: <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>,  label: 'Impact Ledger' },
  { to: '/glossary', icon: <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>,  label: 'Glossary' },
]

export default function Sidebar() {
  const [reviewPending, setReviewPending] = useState(0)
  const { role, logout } = useAuth()

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
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h1>🌱 VaaniSetu</h1>
        <p>AI Translation · BAIF</p>
      </div>

      <nav className="sidebar-nav">
        {NAV.map(item => (
          <NavLink key={item.to} to={item.to} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <span className="nav-icon" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {item.icon}
            </span>
            <span>{item.label}</span>
            {item.to === '/review' && reviewPending > 0 && <span className="nav-badge">{reviewPending}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button onClick={logout} className="nav-item" style={{ width: '100%', cursor: 'pointer', border: 'none', background: 'none', textAlign: 'left', color: 'var(--red)' }}>
          Logout
        </button>
        <div style={{ marginTop: 16 }}>VaaniSetu v2.0</div>
        <div style={{ marginTop: 4 }}>Port 8765</div>
      </div>
    </aside>
  )
}
