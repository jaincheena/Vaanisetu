import React, { useState, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const NAV = [
  { to: '/upload',   icon: '⬆️',  label: 'Upload' },
  { to: '/history',  icon: '📋',  label: 'History' },
  { to: '/review',   icon: '🔍',  label: 'Review Queue', badge: 'review_pending' },
  { to: '/impact',   icon: '📊',  label: 'Impact Ledger' },
  { to: '/glossary', icon: '📖',  label: 'Glossary' },
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
        <NavLink to="/upload" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">⬆️</span>
          <span>Upload</span>
        </NavLink>
        <NavLink to="/history" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">📋</span>
          <span>History</span>
        </NavLink>
        <NavLink to="/review" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">🔍</span>
          <span>Review Queue</span>
          {reviewPending > 0 && <span className="nav-badge">{reviewPending}</span>}
        </NavLink>
        {role === 'admin' && (
          <NavLink to="/impact" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">📊</span>
            <span>Impact Ledger</span>
          </NavLink>
        )}
        <NavLink to="/glossary" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">📖</span>
          <span>Glossary</span>
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <button onClick={logout} className="nav-item" style={{ width: '100%', cursor: 'pointer', border: 'none', background: 'none', textAlign: 'left', color: 'var(--red)' }}>
          Logout
        </button>
        <div style={{ marginTop: 16 }}>VaaniSetu v1.0</div>
        <div style={{ marginTop: 4 }}>Port 8765 · CPU-only</div>
      </div>
    </aside>
  )
}
