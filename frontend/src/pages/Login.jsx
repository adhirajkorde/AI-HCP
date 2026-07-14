import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Activity, Lock, User, AlertCircle, Loader2, Mail } from 'lucide-react';
import { login, register, clearError } from '../features/authSlice';
import { useToast } from '../components/ToastContext';

export const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const { loading, error, isAuthenticated } = useSelector((state) => state.auth);

  useEffect(() => {
    dispatch(clearError());
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate, dispatch]);

  const toggleMode = () => {
    setIsRegistering(!isRegistering);
    dispatch(clearError());
    setUsername('');
    setPassword('');
    setEmail('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isRegistering) {
      if (!username.trim() || !email.trim() || !password) {
        showToast('Please enter username, email, and password.', 'warning');
        return;
      }
      if (username.trim().length < 3) {
        showToast('Username must be at least 3 characters.', 'warning');
        return;
      }
      if (password.length < 6) {
        showToast('Password must be at least 6 characters.', 'warning');
        return;
      }
      dispatch(register({ username: username.trim(), email: email.trim(), password }))
        .unwrap()
        .then(() => {
          showToast('Account created successfully! Please sign in.', 'success');
          setIsRegistering(false);
          setPassword('');
        })
        .catch((err) => {
          showToast(err || 'Registration failed.', 'error');
        });
    } else {
      if (!username.trim() || !password) {
        showToast('Please enter both username and password.', 'warning');
        return;
      }
      dispatch(login({ username: username.trim(), password }))
        .unwrap()
        .then(() => {
          showToast('Welcome back to MediConnect AI!', 'success');
        })
        .catch((err) => {
          showToast(err || 'Failed to authenticate.', 'error');
        });
    }
  };

  const handleAutofill = () => {
    setUsername('rep1');
    setPassword('password123');
    showToast('Demo credentials autofilled.', 'success');
  };

  return (
    <div className="login-page">
      <div className="login-card card">
        <div className="login-header">
          <div className="login-logo-wrapper">
            <Activity className="login-logo" size={32} />
          </div>
          <h1 className="login-title">
            {isRegistering ? 'Create Account' : 'MediConnect AI'}
          </h1>
          <p className="login-subtitle">
            {isRegistering 
              ? 'Join MediConnect AI to log HCP interactions' 
              : 'AI-First HCP Interaction Log & CRM Portal'}
          </p>
        </div>

        {error && (
          <div className="error-alert">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label className="form-label" htmlFor="username">Username</label>
            <div className="input-with-icon">
              <User className="input-icon" size={18} />
              <input
                id="username"
                type="text"
                className="form-input"
                placeholder="Enter your representative username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={loading}
              />
            </div>
          </div>

          {isRegistering && (
            <div className="form-group">
              <label className="form-label" htmlFor="email">Email Address</label>
              <div className="input-with-icon">
                <Mail className="input-icon" size={18} />
                <input
                  id="email"
                  type="email"
                  className="form-input"
                  placeholder="Enter email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                />
              </div>
            </div>
          )}

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <div className="input-with-icon">
              <Lock className="input-icon" size={18} />
              <input
                id="password"
                type="password"
                className="form-input"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
              />
            </div>
          </div>

          <button type="submit" className="btn btn-primary login-submit-btn" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={18} />
                <span>{isRegistering ? 'Creating Account...' : 'Signing In...'}</span>
              </>
            ) : (
              <span>{isRegistering ? 'Create Account' : 'Sign In'}</span>
            )}
          </button>
        </form>

        {!isRegistering && (
          <>
            <div className="login-divider">
              <span>Demo Access</span>
            </div>

            <button 
              onClick={handleAutofill} 
              className="btn btn-secondary autofill-btn"
              disabled={loading}
            >
              Autofill Demo Representative (rep1)
            </button>
          </>
        )}

        <div className="login-footer">
          {isRegistering ? (
            <>
              Already have an account?
              <button onClick={toggleMode} className="login-footer-link" type="button" disabled={loading}>
                Sign In
              </button>
            </>
          ) : (
            <>
              Don't have an account?
              <button onClick={toggleMode} className="login-footer-link" type="button" disabled={loading}>
                Create Account
              </button>
            </>
          )}
        </div>
      </div>

      <style>{`
        .login-page {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 1.5rem;
          background-image: 
            radial-gradient(at 0% 0%, rgba(219, 234, 254, 0.5) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(243, 232, 255, 0.4) 0px, transparent 50%);
          background-attachment: fixed;
        }

        .login-card {
          width: 100%;
          max-width: 440px;
          padding: 2.5rem;
          background: rgba(255, 255, 255, 0.85);
          border: 1px solid rgba(255, 255, 255, 0.6);
          box-shadow: 0 20px 50px rgba(18, 38, 63, 0.08);
          border-radius: var(--radius-lg);
        }

        .login-card:hover {
          transform: none; /* Disable standard card lift for login */
        }

        .login-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .login-logo-wrapper {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 56px;
          height: 56px;
          border-radius: var(--radius-md);
          background: var(--primary-light);
          color: var(--primary);
          margin-bottom: 1.25rem;
          box-shadow: 0 8px 16px var(--primary-glow);
        }

        .login-logo {
          stroke-width: 2.5;
        }

        .login-title {
          font-size: 1.5rem;
          font-weight: 800;
          color: var(--text-main);
          letter-spacing: -0.5px;
        }

        .login-subtitle {
          font-size: 0.875rem;
          color: var(--text-muted);
          margin-top: 0.25rem;
        }

        .error-alert {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem 1rem;
          background: var(--danger-light);
          color: var(--danger);
          border-radius: var(--radius-sm);
          font-size: 0.8125rem;
          font-weight: 500;
          margin-bottom: 1.5rem;
          border: 1px solid rgba(239, 68, 68, 0.1);
        }

        .input-with-icon {
          position: relative;
        }

        .input-with-icon .form-input {
          padding-left: 2.75rem;
        }

        .input-icon {
          position: absolute;
          left: 1rem;
          top: 50%;
          transform: translateY(-50%);
          color: var(--text-light);
        }

        .login-submit-btn {
          width: 100%;
          padding: 0.75rem;
          font-size: 0.9375rem;
          font-weight: 600;
          border-radius: var(--radius-sm);
          margin-top: 0.5rem;
        }

        .login-divider {
          display: flex;
          align-items: center;
          text-align: center;
          margin: 1.5rem 0;
          color: var(--text-light);
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 1px;
        }

        .login-divider::before, .login-divider::after {
          content: '';
          flex: 1;
          border-bottom: 1px solid var(--border-light);
        }

        .login-divider span {
          padding: 0 0.75rem;
        }

        .autofill-btn {
          width: 100%;
          padding: 0.75rem;
          font-weight: 600;
          font-size: 0.875rem;
          border: 1px dashed var(--primary);
        }

        .autofill-btn:hover {
          border-style: solid;
        }

        .animate-spin {
          animation: spin 1s linear infinite;
        }

        .login-footer {
          margin-top: 1.5rem;
          text-align: center;
          font-size: 0.875rem;
          color: var(--text-muted);
        }

        .login-footer-link {
          color: var(--primary);
          font-weight: 600;
          cursor: pointer;
          margin-left: 0.25rem;
          text-decoration: none;
          background: none;
          border: none;
          padding: 0;
          font-size: inherit;
        }

        .login-footer-link:hover {
          text-decoration: underline;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default Login;
