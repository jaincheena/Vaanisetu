import React, { Component } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import TopBanner from './components/TopBanner'
import Overview from './pages/Overview'
import Upload from './pages/Upload'
import History from './pages/History'
import ReviewQueue from './pages/ReviewQueue'
import ImpactLedger from './pages/ImpactLedger'
import Glossary from './pages/Glossary'
import TrainingHub from './pages/TrainingHub'
import Documentation from './pages/Documentation'
import { AuthProvider, useAuth } from './context/AuthContext'

// Safe fetch interceptor with proper window binding
if (typeof window !== 'undefined' && window.fetch) {
  const nativeFetch = window.fetch.bind(window);
  window.fetch = async (url, options = {}) => {
    try {
      const token = localStorage.getItem('vaani_token');
      if (token && typeof url === 'string' && url.startsWith('/api')) {
        const headers = new Headers(options.headers || {});
        if (!headers.has('Authorization')) {
          headers.set('Authorization', `Bearer ${token}`);
        }
        options = { ...options, headers };
      }
    } catch (e) {
      // Ignore localStorage access errors
    }
    return nativeFetch(url, options);
  };
}

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error("UI Render Error:", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 40, color: '#f87171', background: '#0C0E14', minHeight: '100vh', fontFamily: 'sans-serif' }}>
          <h2>⚠️ Interface Initialization Notice</h2>
          <p style={{ color: '#94a3b8' }}>{this.state.error?.toString()}</p>
          <button 
            onClick={() => window.location.reload()} 
            style={{ padding: '8px 16px', background: '#e8924a', border: 'none', borderRadius: 6, color: '#fff', cursor: 'pointer', marginTop: 12 }}
          >
            Reload Interface
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

function ProtectedRoute({ children, adminOnly = false }) {
  const auth = useAuth();
  if (adminOnly && auth?.role !== 'admin') return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <AppContent />
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  );
}

function AppContent() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-area">
        <TopBanner />
        <main className="page-content">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
            <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
            <Route path="/review" element={<ProtectedRoute><ReviewQueue /></ProtectedRoute>} />
            <Route path="/impact" element={<ProtectedRoute adminOnly><ImpactLedger /></ProtectedRoute>} />
            <Route path="/glossary" element={<ProtectedRoute><Glossary /></ProtectedRoute>} />
            <Route path="/training" element={<ProtectedRoute><TrainingHub /></ProtectedRoute>} />
            <Route path="/docs" element={<Documentation />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
