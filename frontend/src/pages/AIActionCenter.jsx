import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
  Clock, 
  AlertTriangle, 
  Mail, 
  CheckCircle, 
  XCircle, 
  RefreshCw, 
  Zap,
  Shield,
  Inbox,
  Send,
  History,
  Loader2
} from 'lucide-react';
import { fetchAIActionCenter, approveRequest, rejectRequest } from '../features/automationSlice';
import { useToast } from '../components/ToastContext';

export const AIActionCenter = () => {
  const dispatch = useDispatch();
  const { showToast } = useToast();
  const { actionCenter, loading, error } = useSelector((state) => state.automation);
  const [activeTab, setActiveTab] = useState('approvals');

  useEffect(() => {
    dispatch(fetchAIActionCenter());
  }, [dispatch]);

  const handleApprove = (item) => {
    if (item.approval_request_id) {
      dispatch(approveRequest({ id: item.approval_request_id, decision_reason: 'Approved via AI Action Center' }))
        .unwrap()
        .then(() => {
          showToast(`${item.type} approved`, 'success');
          dispatch(fetchAIActionCenter());
        })
        .catch((err) => showToast(err || 'Failed to approve', 'error'));
    }
  };

  const handleReject = (item) => {
    if (item.approval_request_id) {
      dispatch(rejectRequest({ id: item.approval_request_id, decision_reason: 'Rejected via AI Action Center' }))
        .unwrap()
        .then(() => {
          showToast(`${item.type} rejected`, 'success');
          dispatch(fetchAIActionCenter());
        })
        .catch((err) => showToast(err || 'Failed to reject', 'error'));
    }
  };

  const getPriorityClass = (priority) => {
    switch (priority) {
      case 'high': return 'priority-high';
      case 'medium': return 'priority-medium';
      case 'low': return 'priority-low';
      default: return '';
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'pending': return 'status-pending';
      case 'approved': return 'status-approved';
      case 'rejected': return 'status-rejected';
      case 'completed': return 'status-completed';
      case 'failed': return 'status-failed';
      default: return '';
    }
  };

  const tabs = [
    { id: 'approvals', label: 'Pending Approvals', icon: Shield, count: actionCenter?.pending_approvals?.length || 0 },
    { id: 'followups', label: 'Generated Follow-ups', icon: Clock, count: actionCenter?.generated_followups?.length || 0 },
    { id: 'emails', label: 'Email Drafts', icon: Mail, count: actionCenter?.email_drafts?.length || 0 },
    { id: 'upcoming', label: 'Upcoming Actions', icon: Zap, count: actionCenter?.upcoming_actions?.length || 0 },
    { id: 'failed', label: 'Failed Automations', icon: AlertTriangle, count: actionCenter?.failed_automations?.length || 0 },
    { id: 'history', label: 'Recent Decisions', icon: History, count: actionCenter?.recent_decisions?.length || 0 },
  ];

  const getItemsForTab = (tabId) => {
    switch (tabId) {
      case 'approvals': return actionCenter?.pending_approvals || [];
      case 'followups': return actionCenter?.generated_followups || [];
      case 'emails': return actionCenter?.email_drafts || [];
      case 'upcoming': return actionCenter?.upcoming_actions || [];
      case 'failed': return actionCenter?.failed_automations || [];
      case 'history': return actionCenter?.recent_decisions || [];
      default: return [];
    }
  };

  const getIconForType = (type) => {
    switch (type) {
      case 'approval': return <Shield size={16} className="text-primary" />;
      case 'followup': return <Clock size={16} className="text-teal" />;
      case 'email_draft': return <Mail size={16} className="text-secondary" />;
      case 'automation': return <Zap size={16} className="text-warning" />;
      case 'decision': return <CheckCircle size={16} className="text-success" />;
      default: return <Inbox size={16} className="text-muted" />;
    }
  };

  if (loading && !actionCenter) {
    return (
      <div className="ai-action-center-page">
        <div className="page-header">
          <h1 className="page-title">AI Action Center</h1>
          <p className="page-subtitle">Loading AI-generated actions...</p>
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
          <Loader2 className="animate-spin" size={32} />
        </div>
      </div>
    );
  }

  return (
    <div className="ai-action-center-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">AI Action Center</h1>
          <p className="page-subtitle">Review and approve AI-generated actions, follow-ups, and email drafts.</p>
        </div>
        <button 
          onClick={() => dispatch(fetchAIActionCenter())} 
          className="btn btn-secondary"
          disabled={loading}
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="tab-control card">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <tab.icon size={18} />
            <span>{tab.label}</span>
            {tab.count > 0 && <span className="count-badge">{tab.count}</span>}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="action-center-content">
        {getItemsForTab(activeTab).length === 0 ? (
          <div className="card empty-state">
            {activeTab === 'approvals' && <Shield size={48} className="empty-icon" />}
            {activeTab === 'followups' && <Clock size={48} className="empty-icon" />}
            {activeTab === 'emails' && <Mail size={48} className="empty-icon" />}
            {activeTab === 'upcoming' && <Zap size={48} className="empty-icon" />}
            {activeTab === 'failed' && <AlertTriangle size={48} className="empty-icon" />}
            {activeTab === 'history' && <History size={48} className="empty-icon" />}
            <h3>No {tabs.find(t => t.id === activeTab)?.label.toLowerCase()}</h3>
            <p>All caught up! No items requiring attention in this category.</p>
          </div>
        ) : (
          <div className="action-items-list">
            {getItemsForTab(activeTab).map((item) => (
              <div key={item.id} className={`card action-item ${getPriorityClass(item.priority)}`}>
                <div className="action-item-header">
                  <div className="action-item-icon">
                    {getIconForType(item.type)}
                  </div>
                  <div className="action-item-title">
                    <h4>{item.title}</h4>
                    {item.hcp_name && <span className="hcp-name">Dr. {item.hcp_name}</span>}
                  </div>
                  <div className="action-item-meta">
                    <span className={`priority-badge ${getPriorityClass(item.priority)}`}>
                      {item.priority.toUpperCase()}
                    </span>
                    <span className={`status-badge ${getStatusClass(item.status)}`}>
                      {item.status.toUpperCase()}
                    </span>
                  </div>
                </div>

                <p className="action-item-description">{item.description}</p>

                <div className="action-item-footer">
                  <span className="action-item-time">
                    {new Date(item.created_at).toLocaleString()}
                  </span>
                  
                  {item.requires_approval && activeTab === 'approvals' && (
                    <div className="action-item-actions">
                      <button 
                        onClick={() => handleApprove(item)} 
                        className="btn btn-success btn-sm"
                        disabled={loading}
                      >
                        <CheckCircle size={14} />
                        <span>Approve</span>
                      </button>
                      <button 
                        onClick={() => handleReject(item)} 
                        className="btn btn-danger btn-sm"
                        disabled={loading}
                      >
                        <XCircle size={14} />
                        <span>Reject</span>
                      </button>
                    </div>
                  )}
                  
                  {item.requires_approval && activeTab === 'emails' && (
                    <div className="action-item-actions">
                      <button className="btn btn-primary btn-sm" disabled>
                        <Send size={14} />
                        <span>Review & Send</span>
                      </button>
                    </div>
                  )}

                  {activeTab === 'failed' && (
                    <button className="btn btn-secondary btn-sm">
                      <RefreshCw size={14} />
                      <span>Retry</span>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <style>{`
        .tab-control {
          display: flex;
          flex-wrap: wrap;
          padding: 0.5rem;
          gap: 0.5rem;
          margin-bottom: 2rem;
          background: rgba(255, 255, 255, 0.7);
        }

        .tab-btn {
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

        .tab-btn:hover {
          color: var(--primary);
          background: rgba(255, 255, 255, 0.6);
        }

        .tab-btn.active {
          color: var(--primary);
          background: white;
          box-shadow: var(--shadow-sm);
        }

        .count-badge {
          font-size: 0.7rem;
          font-weight: 700;
          padding: 0.125rem 0.5rem;
          border-radius: var(--radius-full);
          background: var(--primary-light);
          color: var(--primary);
        }

        .action-center-content {
          margin-top: 1rem;
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

        .action-items-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .action-item {
          padding: 1.5rem;
          border-left: 4px solid var(--border-light);
        }

        .action-item.priority-high { border-left-color: var(--danger); }
        .action-item.priority-medium { border-left-color: var(--warning); }
        .action-item.priority-low { border-left-color: var(--primary); }

        .action-item-header {
          display: flex;
          align-items: flex-start;
          gap: 1rem;
          margin-bottom: 0.75rem;
        }

        .action-item-icon {
          width: 40px;
          height: 40px;
          border-radius: var(--radius-md);
          background: var(--primary-light);
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .action-item-title {
          flex: 1;
        }

        .action-item-title h4 {
          font-size: 1rem;
          font-weight: 700;
          color: var(--text-main);
          margin-bottom: 0.25rem;
        }

        .hcp-name {
          font-size: 0.875rem;
          color: var(--primary);
          font-weight: 500;
        }

        .action-item-meta {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          flex-shrink: 0;
        }

        .priority-badge {
          font-size: 0.7rem;
          font-weight: 700;
          text-transform: uppercase;
          padding: 0.25rem 0.625rem;
          border-radius: var(--radius-full);
        }

        .priority-high { background: var(--danger-light); color: var(--danger); }
        .priority-medium { background: var(--warning-light); color: var(--warning); }
        .priority-low { background: var(--primary-light); color: var(--primary); }

        .status-badge {
          font-size: 0.7rem;
          font-weight: 600;
          text-transform: uppercase;
          padding: 0.25rem 0.625rem;
          border-radius: var(--radius-full);
        }

        .status-pending { background: var(--warning-light); color: var(--warning); }
        .status-approved { background: var(--success-light); color: var(--success); }
        .status-rejected { background: var(--danger-light); color: var(--danger); }
        .status-completed { background: var(--primary-light); color: var(--primary); }
        .status-failed { background: var(--danger-light); color: var(--danger); }

        .action-item-description {
          color: var(--text-main);
          line-height: 1.5;
          margin-bottom: 1rem;
          font-size: 0.9375rem;
        }

        .action-item-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding-top: 1rem;
          border-top: 1px solid var(--border-light);
        }

        .action-item-time {
          font-size: 0.75rem;
          color: var(--text-light);
        }

        .action-item-actions {
          display: flex;
          gap: 0.5rem;
        }

        .btn-sm {
          padding: 0.5rem 1rem;
          font-size: 0.8125rem;
        }

        .btn-success {
          background: var(--success);
          color: white;
        }

        .btn-success:hover {
          background: hsl(142, 70%, 38%);
        }

        @media (max-width: 768px) {
          .action-item-header {
            flex-direction: column;
            align-items: flex-start;
          }
          
          .action-item-meta {
            width: 100%;
            justify-content: space-between;
          }
          
          .action-item-footer {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.75rem;
          }
        }
      `}</style>
    </div>
  );
};

export default AIActionCenter;