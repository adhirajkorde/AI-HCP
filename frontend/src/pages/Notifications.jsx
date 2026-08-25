import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
  Bell, 
  BellOff, 
  Filter, 
  CheckCircle, 
  X, 
  Loader2,
  AlertTriangle,
  Info,
  Shield,
  Clock,
  Mail
} from 'lucide-react';
import { fetchNotifications, markNotificationRead, markAllNotificationsRead } from '../features/automationSlice';
import { useToast } from '../components/ToastContext';

export const Notifications = () => {
  const dispatch = useDispatch();
  const { showToast } = useToast();
  const { notifications, loading, unreadCount } = useSelector((state) => state.automation);
  const [filter, setFilter] = useState('all'); // all, unread, read
  const [activeTab, setActiveTab] = useState('notifications'); // notifications, alerts

  useEffect(() => {
    dispatch(fetchNotifications());
    // Refresh every 30 seconds
    const interval = setInterval(() => dispatch(fetchNotifications()), 30000);
    return () => clearInterval(interval);
  }, [dispatch]);

  const filteredNotifications = notifications?.filter((n) => {
    if (filter === 'unread') return !n.read;
    if (filter === 'read') return n.read;
    return true;
  }) || [];

  const handleMarkRead = (notificationId) => {
    dispatch(markNotificationRead(notificationId))
      .unwrap()
      .catch((err) => showToast(err || 'Failed to mark as read', 'error'));
  };

  const handleMarkAllRead = () => {
    dispatch(markAllNotificationsRead())
      .unwrap()
      .then(() => showToast('All notifications marked as read', 'success'))
      .catch((err) => showToast(err || 'Failed to mark all as read', 'error'));
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return <AlertTriangle size={16} className="text-danger" />;
      case 'high': return <Shield size={16} className="text-warning" />;
      case 'warning': return <AlertTriangle size={16} className="text-warning" />;
      case 'info': return <Info size={16} className="text-primary" />;
      default: return <Bell size={16} className="text-muted" />;
    }
  };

  const getSeverityClass = (severity) => {
    switch (severity) {
      case 'critical': return 'severity-critical';
      case 'high': return 'severity-high';
      case 'warning': return 'severity-warning';
      case 'info': return 'severity-info';
      default: return '';
    }
  };

  if (loading && !notifications) {
    return (
      <div className="notifications-page">
        <div className="page-header">
          <h1 className="page-title">Notifications</h1>
          <p className="page-subtitle">Loading notifications...</p>
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
          <Loader2 className="animate-spin" size={32} />
        </div>
      </div>
    );
  }

  return (
    <div className="notifications-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <Bell size={24} />
            <span>Notifications</span>
          </h1>
          <p className="page-subtitle">
            {unreadCount > 0 ? `${unreadCount} unread notification${unreadCount > 1 ? 's' : ''}` : 'All caught up'}
          </p>
        </div>
        <div className="header-actions">
          {unreadCount > 0 && (
            <button onClick={handleMarkAllRead} className="btn btn-secondary">
              <CheckCircle size={16} />
              <span>Mark All Read</span>
            </button>
          )}
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="filter-tab-bar card">
        <button 
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          <span>All</span>
          <span className="count-badge">{notifications?.length || 0}</span>
        </button>
        <button 
          className={`filter-btn ${filter === 'unread' ? 'active' : ''}`}
          onClick={() => setFilter('unread')}
        >
          <Bell size={16} />
          <span>Unread</span>
          <span className="count-badge unread">{unreadCount}</span>
        </button>
        <button 
          className={`filter-btn ${filter === 'read' ? 'active' : ''}`}
          onClick={() => setFilter('read')}
        >
          <BellOff size={16} />
          <span>Read</span>
          <span className="count-badge">{(notifications?.filter(n => n.read).length || 0)}</span>
        </button>
      </div>

      {/* Notification List */}
      {filteredNotifications.length === 0 ? (
        <div className="card empty-state">
          <BellOff size={48} className="empty-icon" />
          <h3>No notifications</h3>
          <p>{filter === 'unread' ? 'All caught up! No unread notifications.' : 'No notifications yet.'}</p>
        </div>
      ) : (
        <div className="notifications-list">
          {filteredNotifications.map((notification) => (
            <div 
              key={notification.id} 
              className={`card notification-item ${!notification.read ? 'unread' : ''} ${getSeverityClass(notification.severity)}`}
            >
              <div className="notification-content">
                <div className="notification-header">
                  <div className="notification-icon">
                    {getSeverityIcon(notification.severity)}
                  </div>
                  <div className="notification-title-row">
                    <h4 className="notification-title">{notification.title}</h4>
                    <span className="notification-time">
                      {new Date(notification.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>
                
                <p className="notification-message">{notification.message}</p>
                
                {notification.event_type && (
                  <span className="notification-event-type">{notification.event_type}</span>
                )}
              </div>
              
              <div className="notification-actions">
                {!notification.read && (
                  <button 
                    onClick={() => handleMarkRead(notification.id)}
                    className="btn btn-primary btn-sm"
                    title="Mark as read"
                  >
                    <CheckCircle size={14} />
                    <span>Mark Read</span>
                  </button>
                )}
                {notification.action_url && (
                  <a href={notification.action_url} className="btn btn-secondary btn-sm">
                    <span>View</span>
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <style>{`
        .header-actions {
          display: flex;
          gap: 0.75rem;
        }

        .filter-tab-bar {
          display: flex;
          padding: 0.5rem;
          gap: 0.5rem;
          margin-bottom: 1.5rem;
          background: rgba(255, 255, 255, 0.7);
        }

        .filter-btn {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1.25rem;
          border: none;
          background: none;
          cursor: pointer;
          font-weight: 600;
          font-size: 0.875rem;
          color: var(--text-muted);
          border-radius: var(--radius-sm);
          transition: all var(--transition-fast);
        }

        .filter-btn:hover {
          color: var(--primary);
          background: rgba(255, 255, 255, 0.6);
        }

        .filter-btn.active {
          color: var(--primary);
          background: white;
          box-shadow: var(--shadow-sm);
        }

        .count-badge {
          font-size: 0.7rem;
          font-weight: 700;
          padding: 0.125rem 0.5rem;
          border-radius: var(--radius-full);
        }

        .count-badge.unread { background: var(--warning-light); color: var(--warning); }

        .notifications-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .notification-item {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 1.5rem;
          padding: 1.25rem 1.5rem;
          border-left: 4px solid var(--border-light);
          transition: all var(--transition-fast);
        }

        .notification-item:hover {
          transform: translateX(4px);
          box-shadow: var(--shadow-md);
        }

        .notification-item.unread {
          background: var(--primary-light);
          border-left-color: var(--primary);
        }

        .notification-item.severity-critical { border-left-color: var(--danger); }
        .notification-item.severity-high { border-left-color: var(--warning); }
        .notification-item.severity-warning { border-left-color: var(--warning); }
        .notification-item.severity-info { border-left-color: var(--primary); }

        .notification-content {
          flex: 1;
          min-width: 0;
        }

        .notification-header {
          display: flex;
          align-items: flex-start;
          gap: 0.75rem;
          margin-bottom: 0.5rem;
        }

        .notification-icon {
          width: 36px;
          height: 36px;
          border-radius: var(--radius-full);
          background: var(--primary-light);
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .notification-title-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 1rem;
          flex: 1;
          min-width: 0;
        }

        .notification-title {
          font-size: 0.9375rem;
          font-weight: 700;
          color: var(--text-main);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .notification-time {
          font-size: 0.75rem;
          color: var(--text-light);
          white-space: nowrap;
          flex-shrink: 0;
        }

        .notification-message {
          color: var(--text-muted);
          font-size: 0.875rem;
          line-height: 1.5;
          margin-bottom: 0.5rem;
        }

        .notification-event-type {
          display: inline-block;
          font-size: 0.7rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: var(--primary);
          background: var(--primary-light);
          padding: 0.125rem 0.5rem;
          border-radius: var(--radius-full);
        }

        .notification-actions {
          display: flex;
          gap: 0.5rem;
          flex-shrink: 0;
          align-self: flex-start;
        }

        .btn-sm {
          padding: 0.5rem 1rem;
          font-size: 0.8125rem;
        }

        .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
          padding: 3rem 1.5rem;
          color: var(--text-muted);
        }

        .empty-icon {
          color: var(--text-light);
          margin-bottom: 1rem;
          stroke-width: 1.5;
        }

        .empty-state h3 {
          font-size: 1.125rem;
          font-weight: 700;
          color: var(--text-main);
          margin-bottom: 0.5rem;
        }

        @media (max-width: 768px) {
          .notification-item {
            flex-direction: column;
          }
          
          .notification-actions {
            width: 100%;
            justify-content: flex-end;
          }
        }
      `}</style>
    </div>
  );
};

export default Notifications;