import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { checkAuthStatus } from './features/authSlice';

// Components & Layout
import Sidebar from './components/Sidebar';
import ProtectedRoute from './components/ProtectedRoute';
import { ToastProvider } from './components/ToastContext';

// Pages
import Dashboard from './pages/Dashboard';
import LogInteraction from './pages/LogInteraction';
import HCPList from './pages/HCPList';
import HCPProfile from './pages/HCPProfile';
import FollowUps from './pages/FollowUps';
import Analytics from './pages/Analytics';
import Login from './pages/Login';

function App() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const dispatch = useDispatch();
  const { isAuthenticated } = useSelector((state) => state.auth);

  useEffect(() => {
    dispatch(checkAuthStatus());
  }, [dispatch]);

  return (
    <ToastProvider>
      <Router>
        <div className="app-container">
          {isAuthenticated && (
            <Sidebar mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />
          )}

          <main className={isAuthenticated ? 'main-content' : 'auth-main-content'}>
            <Routes>
              {/* Authenticated Routes */}
              <Route path="/" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />
              
              <Route path="/log-interaction" element={
                <ProtectedRoute>
                  <LogInteraction />
                </ProtectedRoute>
              } />
              
              <Route path="/hcps" element={
                <ProtectedRoute>
                  <HCPList />
                </ProtectedRoute>
              } />
              
              <Route path="/hcps/:id" element={
                <ProtectedRoute>
                  <HCPProfile />
                </ProtectedRoute>
              } />
              
              <Route path="/followups" element={
                <ProtectedRoute>
                  <FollowUps />
                </ProtectedRoute>
              } />
              
              <Route path="/analytics" element={
                <ProtectedRoute>
                  <Analytics />
                </ProtectedRoute>
              } />

              {/* Login Portal Route */}
              <Route path="/login" element={<Login />} />

              {/* Catch-all Fallback Redirect */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </Router>

      <style>{`
        .auth-main-content {
          flex: 1;
          width: 100%;
        }
      `}</style>
    </ToastProvider>
  );
}

export default App;
