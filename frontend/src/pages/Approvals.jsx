import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
  Shield, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle, 
  FileText,
  Loader2,
  User,
  MoreVertical,
  Eye
} from 'lucide-react';
import { fetchApprovals, approveRequest, rejectRequest } from '../features/automationSlice';
import { useToast } from '../components/ToastContext';

export const Approvals = () => {
  const dispatch = useDispatch();
  const { showToast } = useToast();
  const { approvals, loading } = useSelector((state) => state.automation);
  const [filter, setFilter] = useState('pending');
  const [selectedApproval, setSelectedApproval] = useState(null);

  useEffect(() => {
    dispatch(fetchApprovals());
  }, [dispatch]);

  const filteredApprovals = approvals?.filter((a) => {
    if (filter === 'pending') return a.status === 'pending';
    if (filter === 'approved') return a.status === 'approved';
    if (filter === 'rejected') return a.status === 'rejected';
    return true;
  }) || [];

  const handleApprove = (approval) => {
    dispatch(approveRequest({ id: approval.id, decision_reason: 'Approved via Approvals page' }))
      .unwrap()
      .then(() => {
        showToast('Approval request approved', 'success');
        setSelectedApproval(null);
      })
      .catch((err) => showToast(err || 'Failed to approve', 'error'));
  };

  const handleReject = (approval) => {
    const reason = prompt('Please provide a reason for rejection:');
    if (!reason) return;
    
    dispatch(rejectRequest({ id: approval.id, decision_reason: reason }))
      .unwrap()
      .then(() => {
        showToast('Approval request rejected', 'success');
        setSelectedApproval(null);
      })
      .catch((err) => showToast(err || 'Failed to reject', 'error'));
  };

  const handleViewDetails = (approval) => {
    setSelectedApproval(approval);
  };

  const getRiskClass = (risk) => {
    switch (risk) {
      case 'critical': return 'risk-critical';
      case 'high': return 'risk-high';
      case 'medium': return 'risk-medium';
      case 'low': return 'risk-low';
      default: return '';
    }
  };

  const getRiskIcon = (risk) => {
    switch (risk) {
      case 'critical': return <AlertTriangle size={14} className="text-danger" />;
      case 'high': return <Shield size={14} className="text-warning" />;
      case 'medium': return <AlertTriangle size={14} className="text-warning" />;
      case 'low': return <Info size={14} className="text-primary" />;
      default: return <Shield size={14} className="text-muted" />;
    }
  };

  const getSourceIcon = (type) => {
    switch (type) {
      case 'email_draft': return <Mail size={16} />;
      case 'hcp': return <User size={16} />;
      case 'interaction': return <Clock size={16} />;
      case 'followup': return <Clock size={16} />;
      case 'webhook': return <Zap size={16} />;
      default: return <FileText size={16} />;
    }
  };

  if (loading && !approvals) {
    return (
      <div className="approvals-page">
        <div className="page-header">
          <h1 className="page-title">Approval Requests</h1>
          <p className="page-subtitle">Loading approval requests...</p>
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
          <Loader2 className="animate-spin" size={32} />
        </div>
      </div>
    );
  }

  return (
    <div className="approvals-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <Shield size={24} />
            <span>Approval Requests</span>
          </h1>
          <p className="page-subtitle">
            Review and decide on AI-generated actions requiring human approval.
          </p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="filter-tab-bar card">
        <button 
          className={`filter-btn ${filter === 'pending' ? 'active' : ''}`}
          onClick={() => setFilter('pending')}
        >
          <Shield size={16} />
          <span>Pending</span>
          <span className="count-badge">{approvals?.filter(a => a.status === 'pending').length || 0}</span>
        </button>
        <button 
          className={`filter-btn ${filter === 'approved' ? 'active' : ''}`}
          onClick={() => setFilter('approved')}
        >
          <CheckCircle size={16} />
          <span>Approved</span>
          <span className="count-badge">{approvals?.filter(a => a.status === 'approved').length || 0}</span>
        </button>
        <button 
          className={`filter-btn ${filter === 'rejected' ? 'active' : ''}`}
          onClick={() => setFilter('rejected')}
        >
          <XCircle size={16} />
          <span>Rejected</span>
          <span className="count-badge">{approvals?.filter(a => a.status === 'rejected').length || 0}</span>
        </button>
        <button 
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          <span>All</span>
        </button>
      </div>

      {/* Approval List */}
      {filteredApprovals.length === 0 ? (
        <div className="card empty-state">
          <Shield size={48} className="empty-icon" />
          <h3>No approval requests</h3>
          <p>{filter === 'pending' ? 'No pending approval requests.' : `No ${filter} approval requests.`}</p>
        </div>
      ) : (
        <div className="approvals-list">
          {filteredApprovals.map((approval) => (
            <div 
              key={approval.id} 
              className={`card approval-item ${approval.status === 'pending' ? 'pending' : ''}`}
              onClick={() => handleViewDetails(approval)}
            >
              <div className="approval-header">
                <div className="approval-icon">
                  {getSourceIcon(approval.source_type)}
                </div>
                <div className="approval-title-section">
                  <h4 className="approval-title">{approval.title}</h4>
                  <div className="approval-meta">
                    <span className={`risk-badge ${getRiskClass(approval.risk_level)}`}>
                      {getRiskIcon(approval.risk_level)}
                      {approval.risk_level.toUpperCase()} RISK
                    </span>
                    <span className="approval-type">{approval.request_type.replace(/_/g, ' ')}</span>
                    <span className="approval-time">
                      {new Date(approval.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>
                <div className="approval-status">
                  <span className={`status-badge status-${approval.status}`}>
                    {approval.status.toUpperCase()}
                  </span>
                </div>
              </div>

              <p className="approval-description">{approval.description}</p>

              {approval.input_data && (
                <details className="approval-details">
                  <summary>View Details</summary>
                  <pre>{JSON.stringify(approval.input_data, null, 2)}</pre>
                </details>
              )}

              {approval.status === 'pending' && (
                <div className="approval-actions">
                  <button 
                    onClick={(e) => { e.stopPropagation(); handleApprove(approval); }}
                    className="btn btn-success"
                  >
                    <CheckCircle size={16} />
                    <span>Approve</span>
                  </button>
                  <button 
                    onClick={(e) => { e.stopPropagation(); handleReject(approval); }}
                    className="btn btn-danger"
                  >
                    <XCircle size={16} />
                    <span>Reject</span>
                  </button>
                </div>
              )}

              {approval.status !== 'pending' && approval.decided_by && (
                <div className="approval-decision">
                  <span className="decision-info">
                    {approval.status === 'approved' ? <CheckCircle size={14} className="text-success" /> : <XCircle size={14} className="text-danger" />}
                    {approval.status.charAt(0).toUpperCase() + approval.status.slice(1)} by user {approval.decided_by}
                    {approval.decided_at && ` on ${new Date(approval.decided_at).toLocaleString()}`}
                  </span>
                  {approval.decision_reason && (
                    <span className="decision-reason">Reason: {approval.decision_reason}</span>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Detail Modal */}
      {selectedApproval && (
        <div className="modal-overlay" onClick={() => setSelectedApproval(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedApproval.title}</h3>
              <button onClick={() => setSelectedApproval(null)} className="modal-close">
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <div className="modal-field">
                <label>Type</label>
                <span>{selectedApproval.request_type}</span>
              </div>
              <div className="modal-field">
                <label>Risk Level</label>
                <span className={`risk-badge ${getRiskClass(selectedApproval.risk_level)}`}>
                  {getRiskIcon(selectedApproval.risk_level)}
                  {selectedApproval.risk_level.toUpperCase()}
                </span>
              </div>
              <div className="modal-field">
                <label>Source</label>
                <span>{selectedApproval.source_type} #{selectedApproval.source_id}</span>
              </div>
              <div className="modal-field">
                <label>Description</label>
                <p>{selectedApproval.description}</p>
              </div>
              {selectedApproval.input_data && (
                <div className="modal-field">
                  <label>Input Data</label>
                  <pre>{JSON.stringify(selectedApproval.input_data, null, 2)}</pre>
                </div>
              )}
              {selectedApproval.decision_reason && (
                <div className="modal-field">
                  <label>Decision Reason</label>
                  <p>{selectedApproval.decision_reason}</p>
                </div>
              )}
            </div>
            {selectedApproval.status === 'pending' && (
              <div className="modal-footer">
                <button onClick={() => handleReject(selectedApproval)} className="btn btn-danger">
                  <XCircle size={16} />
                  <span>Reject</span>
                </button>
                <button onClick={() => handleApprove(selectedApproval)} className="btn btn-success">
                  <CheckCircle size={16} />
                  <span>Approve</span>
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      <style>{`
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
          background: var(--primary-light);
          color: var(--primary);
        }

        .approvals-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .approval-item {
          padding: 1.5rem;
          border-left: 4px solid var(--border-light);
          cursor: pointer;
          transition: all var(--transition-fast);
        }

        .approval-item:hover {
          transform: translateX(4px);
          box-shadow: var(--shadow-md);
        }

        .approval-item.pending {
          background: var(--warning-light);
          border-left-color: var(--warning);
        }

        .approval-header {
          display: flex;
          align-items: flex-start;
          gap: 1rem;
          margin-bottom: 0.75rem;
        }

        .approval-icon {
          width: 40px;
          height: 40px;
          border-radius: var(--radius-md);
          background: var(--primary-light);
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          color: var(--primary);
        }

        .approval-title-section {
          flex: 1;
        }

        .approval-title {
          font-size: 1rem;
          font-weight: 700;
          color: var(--text-main);
          margin-bottom: 0.5rem;
        }

        .approval-meta {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          gap: 0.75rem;
        }

        .risk-badge {
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.7rem;
          font-weight: 700;
          text-transform: uppercase;
          padding: 0.25rem 0.625rem;
          border-radius: var(--radius-full);
        }

        .risk-critical { background: var(--danger-light); color: var(--danger); }
        .risk-high { background: var(--warning-light); color: var(--warning); }
        .risk-medium { background: var(--warning-light); color: var(--warning); }
        .risk-low { background: var(--primary-light); color: var(--primary); }

        .approval-type {
          font-size: 0.75rem;
          color: var(--text-muted);
          text-transform: capitalize;
        }

        .approval-time {
          font-size: 0.75rem;
          color: var(--text-light);
        }

        .approval-status {
          flex-shrink: 0;
        }

        .status-badge {
          font-size: 0.75rem;
          font-weight: 700;
          text-transform: uppercase;
          padding: 0.375rem 0.875rem;
          border-radius: var(--radius-full);
        }

        .status-pending { background: var(--warning-light); color: var(--warning); }
        .status-approved { background: var(--success-light); color: var(--success); }
        .status-rejected { background: var(--danger-light); color: var(--danger); }
        .status-expired { background: var(--border-light); color: var(--text-light); }

        .approval-description {
          color: var(--text-muted);
          font-size: 0.875rem;
          line-height: 1.5;
          margin-bottom: 1rem;
        }

        .approval-details {
          margin-top: 1rem;
          padding: 1rem;
          background: var(--bg-main);
          border-radius: var(--radius-sm);
          border: 1px solid var(--border-light);
        }

        .approval-details summary {
          cursor: pointer;
          font-weight: 600;
          color: var(--primary);
          margin-bottom: 0.5rem;
        }

        .approval-details pre {
          font-size: 0.75rem;
          overflow-x: auto;
          max-height: 200px;
          overflow-y: auto;
        }

        .approval-actions {
          display: flex;
          gap: 0.75rem;
          margin-top: 1rem;
          padding-top: 1rem;
          border-top: 1px solid var(--border-light);
        }

        .approval-decision {
          margin-top: 1rem;
          padding-top: 1rem;
          border-top: 1px solid var(--border-light);
        }

        .decision-info {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          font-weight: 600;
          margin-bottom: 0.5rem;
        }

        .decision-reason {
          font-size: 0.875rem;
          color: var(--text-muted);
          font-style: italic;
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

        /* Modal */
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          backdrop-filter: blur(4px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 1rem;
        }

        .modal-content {
          background: white;
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-lg);
          max-width: 600px;
          width: 100%;
          max-height: 80vh;
          overflow-y: auto;
        }

        .modal-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 1.5rem;
          border-bottom: 1px solid var(--border-light);
        }

        .modal-header h3 {
          font-size: 1.125rem;
          font-weight: 700;
        }

        .modal-close {
          background: none;
          border: none;
          color: var(--text-light);
          cursor: pointer;
          padding: 0.25rem;
          border-radius: var(--radius-sm);
        }

        .modal-close:hover {
          background: var(--bg-main);
          color: var(--text-main);
        }

        .modal-body {
          padding: 1.5rem;
        }

        .modal-field {
          margin-bottom: 1.5rem;
        }

        .modal-field label {
          display: block;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
          color: var(--text-light);
          margin-bottom: 0.375rem;
        }

        .modal-field span {
          display: inline-flex;
          align-items: center;
          gap: 0.375rem;
        }

        .modal-field pre {
          font-size: 0.75rem;
          background: var(--bg-main);
          padding: 1rem;
          border-radius: var(--radius-sm);
          overflow-x: auto;
          max-height: 200px;
        }

        .modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 0.75rem;
          padding: 1.5rem;
          border-top: 1px solid var(--border-light);
        }

        @media (max-width: 768px) {
          .approval-header {
            flex-direction: column;
          }
          
          .approval-actions {
            flex-direction: column;
          }
          
          .modal-content {
            margin: 1rem;
            max-height: 90vh;
          }
        }
      `}</style>
    </div>
  );
};

export default Approvals;