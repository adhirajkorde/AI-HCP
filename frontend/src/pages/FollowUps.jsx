import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { CheckSquare, Calendar, Stethoscope, User, HelpCircle, ArrowRight, CheckCircle } from 'lucide-react';
import { fetchFollowUps, updateFollowUpStatus } from '../features/followupSlice';
import { fetchHCPs } from '../features/hcpSlice';
import { TableSkeleton } from '../components/Skeleton';
import { useToast } from '../components/ToastContext';

export const FollowUps = () => {
  const [filterStatus, setFilterStatus] = useState('Pending'); // All, Pending, Completed
  const dispatch = useDispatch();
  const { showToast } = useToast();
  
  const { list: followups, loading } = useSelector((state) => state.followups);
  const { list: hcpList } = useSelector((state) => state.hcps);

  useEffect(() => {
    dispatch(fetchFollowUps());
    dispatch(fetchHCPs());
  }, [dispatch]);

  const handleToggleStatus = (id, currentStatus) => {
    const nextStatus = currentStatus === 'Pending' ? 'Completed' : 'Pending';
    dispatch(updateFollowUpStatus({ id, status: nextStatus }))
      .unwrap()
      .then(() => {
        showToast(`Follow-up task marked as ${nextStatus.toLowerCase()}!`, 'success');
      })
      .catch((err) => {
        showToast(err || 'Failed to update status', 'error');
      });
  };

  const getHCPName = (hcpId) => {
    const hcp = hcpList.find(h => h.id === hcpId);
    return hcp ? hcp.name : 'Unknown Doctor';
  };

  const getHCPSpecialty = (hcpId) => {
    const hcp = hcpList.find(h => h.id === hcpId);
    return hcp ? hcp.specialty : '';
  };

  // Filter list
  const filteredList = followups.filter((item) => {
    if (filterStatus === 'All') return true;
    return item.status === filterStatus;
  });

  if (loading && followups.length === 0) {
    return (
      <div className="followups-page">
        <div className="page-header">
          <div>
            <h1 className="page-title">Follow-up Management</h1>
            <p className="page-subtitle">Loading clinical representative tasks...</p>
          </div>
        </div>
        <TableSkeleton rows={4} />
      </div>
    );
  }

  return (
    <div className="followups-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Follow-up Task Manager</h1>
          <p className="page-subtitle">Manage upcoming scheduled events, clinical callbacks, and AI strategies.</p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="filter-tab-bar card">
        <button 
          className={`filter-btn ${filterStatus === 'Pending' ? 'active' : ''}`}
          onClick={() => setFilterStatus('Pending')}
        >
          <span>Pending Actions</span>
          <span className="count-badge pending">
            {followups.filter(f => f.status === 'Pending').length}
          </span>
        </button>
        <button 
          className={`filter-btn ${filterStatus === 'Completed' ? 'active' : ''}`}
          onClick={() => setFilterStatus('Completed')}
        >
          <span>Completed Tasks</span>
          <span className="count-badge completed">
            {followups.filter(f => f.status === 'Completed').length}
          </span>
        </button>
        <button 
          className={`filter-btn ${filterStatus === 'All' ? 'active' : ''}`}
          onClick={() => setFilterStatus('All')}
        >
          <span>All Items</span>
        </button>
      </div>

      {filteredList.length === 0 ? (
        <div className="card empty-state">
          <CheckSquare size={48} className="empty-icon" />
          <h3>No tasks match criteria</h3>
          <p>You're all caught up! No follow-up tasks are registered under {filterStatus.toLowerCase()} status.</p>
        </div>
      ) : (
        <div className="followups-list">
          {filteredList.map((task) => (
            <div key={task.id} className={`card followup-item-card ${task.status.toLowerCase()} ${task.priority_level.toLowerCase()}`}>
              <div className="checkbox-col">
                <input 
                  type="checkbox" 
                  className="task-checkbox"
                  checked={task.status === 'Completed'}
                  onChange={() => handleToggleStatus(task.id, task.status)}
                />
              </div>

              <div className="details-col">
                <div className="doctor-header-info">
                  <Link to={`/hcps/${task.hcp_id}`} className="doctor-link">
                    <span>Dr. {getHCPName(task.hcp_id)}</span>
                    <Stethoscope size={13} />
                    <span className="specialty-label">{getHCPSpecialty(task.hcp_id)}</span>
                  </Link>

                  <div className="task-badges">
                    <span className={`priority-badge ${task.priority_level.toLowerCase()}`}>
                      {task.priority_level} Priority
                    </span>
                    <span className="due-date-badge">
                      <Calendar size={12} />
                      <span>
                        Due {new Date(task.follow_up_date).toLocaleDateString(undefined, { 
                          month: 'short', 
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </span>
                    </span>
                  </div>
                </div>

                <div className="ai-strategy-callout">
                  <div className="callout-header">
                    <HelpCircle size={14} className="info-icon" />
                    <span>AI Strategic Recommendation</span>
                  </div>
                  <p className="callout-body">"{task.ai_recommendation || 'Follow up with clinical trial findings or product detail leaflets.'}"</p>
                </div>
              </div>

              <div className="action-col">
                <Link to={`/hcps/${task.hcp_id}`} className="btn btn-secondary flex items-center gap-1">
                  <span>View Timeline</span>
                  <ArrowRight size={14} />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      <style>{`
        .filter-tab-bar {
          display: flex;
          padding: 0.5rem;
          gap: 0.5rem;
          margin-bottom: 2rem;
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
          font-size: 0.75rem;
          font-weight: 700;
          padding: 0.125rem 0.5rem;
          border-radius: var(--radius-full);
        }

        .count-badge.pending { background: var(--warning-light); color: var(--warning); }
        .count-badge.completed { background: var(--success-light); color: var(--success); }

        .followups-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .followup-item-card {
          display: grid;
          grid-template-columns: auto 1fr auto;
          gap: 1.5rem;
          align-items: center;
          padding: 1.25rem 1.5rem;
          border-left: 4px solid var(--border-light);
        }

        @media (max-width: 768px) {
          .followup-item-card {
            grid-template-columns: auto 1fr;
          }
          .action-col {
            grid-column: 2;
            justify-self: start;
            margin-top: 0.5rem;
          }
        }

        .followup-item-card.completed {
          opacity: 0.7;
          border-left-color: var(--success) !important;
        }

        .followup-item-card.completed .doctor-link span {
          text-decoration: line-through;
          color: var(--text-light);
        }

        .followup-item-card.completed .ai-strategy-callout {
          background: rgba(0, 0, 0, 0.01);
          border-color: var(--border-light);
        }

        /* Priority border left colors */
        .followup-item-card.high:not(.completed) { border-left-color: var(--danger); }
        .followup-item-card.medium:not(.completed) { border-left-color: var(--warning); }
        .followup-item-card.low:not(.completed) { border-left-color: var(--primary); }

        .task-checkbox {
          width: 20px;
          height: 20px;
          border-radius: 4px;
          border: 2px solid var(--text-light);
          cursor: pointer;
          accent-color: var(--success);
        }

        .doctor-header-info {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          gap: 1rem;
          margin-bottom: 0.75rem;
        }

        .doctor-link {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          font-weight: 700;
          font-size: 0.9375rem;
          color: var(--primary);
        }

        .doctor-link:hover {
          text-decoration: underline;
        }

        .specialty-label {
          font-size: 0.75rem;
          color: var(--text-muted);
          background: var(--primary-light);
          padding: 0.125rem 0.5rem;
          border-radius: var(--radius-full);
          font-weight: 500;
        }

        .task-badges {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .priority-badge {
          font-size: 0.75rem;
          font-weight: 700;
          text-transform: uppercase;
        }

        .priority-badge.high { color: var(--danger); }
        .priority-badge.medium { color: var(--warning); }
        .priority-badge.low { color: var(--primary); }

        .due-date-badge {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          font-size: 0.75rem;
          color: var(--text-light);
          font-weight: 600;
        }

        .ai-strategy-callout {
          background: var(--primary-light);
          border: 1px solid rgba(var(--primary-hue), var(--primary-sat), var(--primary-lightness), 0.1);
          border-radius: var(--radius-sm);
          padding: 0.875rem 1rem;
        }

        .callout-header {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.75rem;
          font-weight: 700;
          color: var(--primary);
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 0.25rem;
        }

        .callout-body {
          font-size: 0.875rem;
          color: var(--text-main);
          line-height: 1.45;
          font-style: italic;
        }
      `}</style>
    </div>
  );
};

export default FollowUps;
