import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle2, AlertCircle, AlertTriangle, X } from 'lucide-react';

const ToastContext = createContext(null);

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message, type = 'success', duration = 4000) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);

    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle2 size={18} className="toast-icon-success" />;
      case 'error':
        return <AlertCircle size={18} className="toast-icon-error" />;
      case 'warning':
        return <AlertTriangle size={18} className="toast-icon-warning" />;
      default:
        return null;
    }
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="toast-container">
        {toasts.map((toast) => (
          <div key={toast.id} className={`toast ${toast.type}`}>
            <span className="toast-icon-wrapper">{getIcon(toast.type)}</span>
            <div className="toast-content">{toast.message}</div>
            <button className="toast-close-btn" onClick={() => removeToast(toast.id)}>
              <X size={14} />
            </button>
          </div>
        ))}
      </div>
      <style>{`
        .toast-icon-success { color: var(--success); }
        .toast-icon-error { color: var(--danger); }
        .toast-icon-warning { color: var(--warning); }
        .toast-icon-wrapper {
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .toast-content {
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--text-main);
          flex: 1;
        }
        .toast-close-btn {
          background: none;
          border: none;
          color: var(--text-light);
          cursor: pointer;
          display: flex;
          align-items: center;
          padding: 2px;
          border-radius: 4px;
        }
        .toast-close-btn:hover {
          color: var(--text-muted);
          background: rgba(0, 0, 0, 0.05);
        }
      `}</style>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};
