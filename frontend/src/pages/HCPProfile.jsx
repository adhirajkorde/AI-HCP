import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams, Link } from 'react-router-dom';
import { 
  User, 
  Stethoscope, 
  Building, 
  Mail, 
  Phone, 
  Star, 
  Cpu, 
  Clock, 
  Calendar, 
  CheckCircle2, 
  ArrowLeft,
  Loader2
} from 'lucide-react';
import { fetchHCPProfile, clearSelectedHCP } from '../features/hcpSlice';
import { CardSkeleton, TableSkeleton } from '../components/Skeleton';

export const HCPProfile = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const { selectedHCP, profileLoading, error } = useSelector((state) => state.hcps);

  useEffect(() => {
    dispatch(fetchHCPProfile(id));
    return () => {
      dispatch(clearSelectedHCP());
    };
  }, [dispatch, id]);

  if (profileLoading || !selectedHCP) {
    return (
      <div className="hcp-profile-page">
        <div className="page-header">
          <Link to="/" className="btn btn-secondary">
            <ArrowLeft size={16} />
            <span>Back</span>
          </Link>
        </div>
        <div className="profile-grid">
          <CardSkeleton />
          <TableSkeleton rows={4} />
        </div>
      </div>
    );
  }

  const { hcp, interactions, followups, ai_insight } = selectedHCP;

  return (
    <div className="hcp-profile-page fade-in">
      <div className="page-header">
        <Link to="/" className="btn btn-secondary">
          <ArrowLeft size={16} />
          <span>Back to Dashboard</span>
        </Link>
        <Link to="/log-interaction" className="btn btn-primary">
          <span>Log Interaction</span>
        </Link>
      </div>

      <div className="profile-grid">
        {/* Left Column: Profile Card & AI Insights */}
        <div className="profile-left-col">
          {/* Main Info */}
          <div className="card profile-info-card">
            <div className="avatar-header">
              <div className="profile-avatar">
                {hcp.name.substring(0, 2).toUpperCase()}
              </div>
              <div>
                <h2 className="profile-name">Dr. {hcp.name}</h2>
                <div className="profile-title-row">
                  <Stethoscope size={14} />
                  <span>{hcp.specialty}</span>
                </div>
              </div>
            </div>

            <div className="profile-details-list">
              <div className="detail-item">
                <Building size={16} className="detail-icon" />
                <div>
                  <div className="detail-label">Facility</div>
                  <div className="detail-value">{hcp.hospital_clinic}</div>
                </div>
              </div>

              <div className="detail-item">
                <Mail size={16} className="detail-icon" />
                <div>
                  <div className="detail-label">Email</div>
                  <div className="detail-value">{hcp.email || 'Not Provided'}</div>
                </div>
              </div>

              <div className="detail-item">
                <Phone size={16} className="detail-icon" />
                <div>
                  <div className="detail-label">Phone</div>
                  <div className="detail-value">{hcp.phone || 'Not Provided'}</div>
                </div>
              </div>

              <div className="detail-item">
                <Star size={16} className="detail-icon preferred" />
                <div>
                  <div className="detail-label">Product Preference</div>
                  <div className="detail-value text-primary font-semibold">{hcp.product_preference || 'None'}</div>
                </div>
              </div>
            </div>
          </div>

          {/* AI Insights Widget */}
          <div className="card profile-ai-insights">
            <h3 className="widget-title">
              <Cpu size={18} className="ai-icon" />
              <span>AI Doctor Profile Summary</span>
            </h3>

            {ai_insight ? (
              <div className="ai-insight-content">
                <div className="engagement-summary-box">
                  <div className="engagement-header">
                    <span className="label">Engagement Index</span>
                    <span className="value">{ai_insight.engagement_score}%</span>
                  </div>
                  <div className="progress-bar-container">
                    <div 
                      className={`progress-bar ${ai_insight.sentiment?.toLowerCase() || 'neutral'}`}
                      style={{ width: `${ai_insight.engagement_score}%` }}
                    />
                  </div>
                </div>

                <div className="ai-meta-rows">
                  <div className="meta-row">
                    <span className="meta-label">Overall Sentiment:</span>
                    <span className={`sentiment-badge ${ai_insight.sentiment?.toLowerCase() || 'neutral'}`}>
                      {ai_insight.sentiment || 'Neutral'}
                    </span>
                  </div>

                  <div className="meta-row">
                    <span className="meta-label">Clinical Interests:</span>
                    <span className="meta-value">{ai_insight.medical_interests || hcp.specialty}</span>
                  </div>

                  <div className="meta-row">
                    <span className="meta-label">Therapeutic Preferences:</span>
                    <span className="meta-value">{ai_insight.product_preferences || 'None'}</span>
                  </div>
                </div>

                <div className="ai-narrative-summary">
                  <h4>Clinical Rep Summary</h4>
                  <p>{ai_insight.summary}</p>
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <p>Insights have not been calculated yet. Log interactions to compile analysis.</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Timeline & Tasks */}
        <div className="profile-right-col">
          {/* Interaction Timeline */}
          <div className="card timeline-card">
            <h3 className="widget-title">
              <Clock size={18} />
              <span>Interaction Timeline</span>
            </h3>

            {interactions.length === 0 ? (
              <div className="empty-timeline">
                <div className="empty-indicator" />
                <p>No historical interactions registered. Use "Log Interaction" to populate details.</p>
              </div>
            ) : (
              <div className="profile-timeline">
                {interactions.map((inter) => (
                  <div key={inter.id} className="timeline-item">
                    <div className="timeline-node" />
                    <div className="timeline-content card">
                      <div className="timeline-header">
                        <span className="timeline-type-badge">{inter.interaction_type}</span>
                        <span className="timeline-date">
                          {new Date(inter.date_time).toLocaleDateString(undefined, { 
                            weekday: 'short', 
                            year: 'numeric', 
                            month: 'short', 
                            day: 'numeric' 
                          })}
                        </span>
                      </div>
                      
                      <div className="timeline-product-row">
                        <strong>Discussed:</strong> <span className="product-tag">{inter.product_discussed}</span>
                      </div>

                      <p className="timeline-notes">"{inter.notes}"</p>
                      
                      {inter.outcome && (
                        <div className="timeline-outcome-row">
                          <strong>Outcome:</strong> <span>{inter.outcome}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Upcoming Tasks */}
          <div className="card followups-mini-card">
            <h3 className="widget-title">
              <Calendar size={18} />
              <span>Upcoming Follow-ups</span>
            </h3>

            {followups.filter(f => f.status === 'Pending').length === 0 ? (
              <div className="empty-state">
                <p>No pending follow-ups scheduled for Dr. {hcp.name}.</p>
              </div>
            ) : (
              <div className="followups-mini-list">
                {followups.filter(f => f.status === 'Pending').map((f) => (
                  <div key={f.id} className={`mini-followup-item ${f.priority_level.toLowerCase()}`}>
                    <div className="mini-followup-header">
                      <span className="priority-label">{f.priority_level} Priority</span>
                      <span className="due-date">
                        Due {new Date(f.follow_up_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                      </span>
                    </div>
                    <p className="recommendation">"{f.ai_recommendation}"</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <style>{`
        .profile-grid {
          display: grid;
          grid-template-columns: 1fr 2fr;
          gap: 2rem;
        }

        @media (max-width: 1024px) {
          .profile-grid {
            grid-template-columns: 1fr;
          }
        }

        .avatar-header {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1.5rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid var(--border-light);
        }

        .profile-avatar {
          width: 56px;
          height: 56px;
          border-radius: var(--radius-full);
          background: var(--primary-light);
          color: var(--primary);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 800;
          font-size: 1.25rem;
        }

        .profile-name {
          font-size: 1.25rem;
          font-weight: 800;
          color: var(--text-main);
        }

        .profile-title-row {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.875rem;
          color: var(--text-muted);
          margin-top: 0.125rem;
        }

        .profile-details-list {
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
        }

        .detail-item {
          display: flex;
          align-items: flex-start;
          gap: 1rem;
        }

        .detail-icon {
          color: var(--text-light);
          margin-top: 2px;
        }

        .detail-icon.preferred {
          color: var(--secondary);
        }

        .detail-label {
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
          color: var(--text-light);
          letter-spacing: 0.5px;
        }

        .detail-value {
          font-size: 0.9375rem;
          color: var(--text-main);
          font-weight: 500;
          margin-top: 0.125rem;
        }

        .profile-left-col {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .profile-right-col {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .engagement-summary-box {
          background: hsl(210, 20%, 99%);
          border: 1px solid var(--border-light);
          border-radius: var(--radius-sm);
          padding: 1rem;
          margin-bottom: 1.5rem;
        }

        .engagement-header {
          display: flex;
          justify-content: space-between;
          font-size: 0.8125rem;
          font-weight: 700;
          color: var(--text-muted);
          margin-bottom: 0.5rem;
          text-transform: uppercase;
        }

        .ai-meta-rows {
          display: flex;
          flex-direction: column;
          gap: 0.875rem;
          margin-bottom: 1.5rem;
        }

        .meta-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 0.875rem;
        }

        .meta-label {
          font-weight: 600;
          color: var(--text-muted);
        }

        .meta-value {
          color: var(--text-main);
          font-weight: 500;
        }

        .ai-narrative-summary h4 {
          font-size: 0.8125rem;
          font-weight: 700;
          text-transform: uppercase;
          color: var(--text-light);
          margin-bottom: 0.5rem;
          letter-spacing: 0.5px;
        }

        .ai-narrative-summary p {
          font-size: 0.875rem;
          color: var(--text-main);
          line-height: 1.5;
        }

        /* Timeline page styles */
        .profile-timeline {
          position: relative;
          padding-left: 2rem;
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .profile-timeline::before {
          content: '';
          position: absolute;
          left: 7px;
          top: 8px;
          bottom: 8px;
          width: 2px;
          background: var(--border-light);
        }

        .timeline-item {
          position: relative;
        }

        .timeline-node {
          position: absolute;
          left: -29px;
          top: 14px;
          width: 14px;
          height: 14px;
          border-radius: var(--radius-full);
          background: white;
          border: 3px solid var(--primary);
          box-shadow: 0 0 0 3px var(--primary-glow);
        }

        .timeline-content {
          box-shadow: var(--shadow-sm);
          border: 1px solid var(--border-light);
          padding: 1.25rem;
        }

        .timeline-content:hover {
          transform: none; /* Disable timeline cards shifting */
        }

        .timeline-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.75rem;
        }

        .timeline-type-badge {
          background: var(--primary-light);
          color: var(--primary);
          font-size: 0.75rem;
          font-weight: 700;
          padding: 0.25rem 0.625rem;
          border-radius: var(--radius-full);
          text-transform: uppercase;
        }

        .timeline-date {
          font-size: 0.8125rem;
          color: var(--text-light);
        }

        .timeline-product-row {
          font-size: 0.875rem;
          color: var(--text-main);
          margin-bottom: 0.5rem;
        }

        .product-tag {
          font-weight: 700;
          color: var(--primary);
        }

        .timeline-notes {
          font-size: 0.875rem;
          color: var(--text-main);
          line-height: 1.5;
          margin-bottom: 0.75rem;
          font-style: italic;
        }

        .timeline-outcome-row {
          background: hsl(210, 20%, 99%);
          border-radius: var(--radius-sm);
          padding: 0.5rem 0.75rem;
          font-size: 0.8125rem;
          color: var(--text-muted);
          border-left: 3px solid var(--secondary);
        }

        .followups-mini-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .mini-followup-item {
          padding: 1rem;
          border-radius: var(--radius-sm);
          border: 1px solid var(--border-light);
          border-left-width: 4px;
        }

        .mini-followup-item.high { border-left-color: var(--danger); background: var(--danger-light); }
        .mini-followup-item.medium { border-left-color: var(--warning); background: var(--warning-light); }
        .mini-followup-item.low { border-left-color: var(--primary); background: var(--primary-light); }

        .mini-followup-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 0.375rem;
        }

        .priority-label {
          font-size: 0.75rem;
          font-weight: 700;
          text-transform: uppercase;
        }

        .due-date {
          font-size: 0.75rem;
          color: var(--text-muted);
          font-weight: 500;
        }

        .recommendation {
          font-size: 0.875rem;
          color: var(--text-main);
          line-height: 1.4;
        }
      `}</style>
    </div>
  );
};

export default HCPProfile;
