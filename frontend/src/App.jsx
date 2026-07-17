import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import TopBanner from './components/TopBanner'
import Upload from './pages/Upload'
import History from './pages/History'
import ReviewQueue from './pages/ReviewQueue'
import ImpactLedger from './pages/ImpactLedger'
import Glossary from './pages/Glossary'

import Login from './pages/Login'
import { AuthProvider, useAuth } from './context/AuthContext'

// Global fetch interceptor to inject JWT token
const originalFetch = window.fetch;
window.fetch = async (url, options = {}) => {
  const token = localStorage.getItem('vaani_token');
  if (token && (typeof url === 'string' && url.startsWith('/api'))) {
    options.headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    };
  }
  return originalFetch(url, options);
};

function ProtectedRoute({ children, adminOnly = false }) {
  const { token, role } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  if (adminOnly && role !== 'admin') return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </AuthProvider>
  );
}

function AppContent() {
  const { token } = useAuth();

  if (!token) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <div className="app-shell">
        <Sidebar />
        <div className="main-area">
          <TopBanner />
          <main className="page-content">
            <Routes>
              <Route path="/" element={<Navigate to="/upload" replace />} />
              <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
              <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
              <Route path="/review" element={<ProtectedRoute><ReviewQueue /></ProtectedRoute>} />
              <Route path="/impact" element={<ProtectedRoute adminOnly><ImpactLedger /></ProtectedRoute>} />
              <Route path="/glossary" element={<ProtectedRoute><Glossary /></ProtectedRoute>} />
            </Routes>
          </main>
        </div>
      </div>
  )
}
