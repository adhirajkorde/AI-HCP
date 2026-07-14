import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { 
  Users, 
  PhoneCall, 
  CalendarClock, 
  Cpu, 
  ArrowRight,
  TrendingUp,
  Activity,
  Smile,
  Compass,
  Frown,
  ExternalLink
} from 'lucide-react';
import { fetchDashboardData } from '../features/analyticsSlice';
import { StatsSkeleton, TableSkeleton } from '../components/Skeleton';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export const Dashboard = () => {
  const dispatch = useDispatch();
  const { dashboard, loading, error } = useSelector((state) => state.analytics);

  useEffect(() => {
    dispatch(fetchDashboardData());
  }, [dispatch]);

  if (loading || !dashboard) {
    return (
      <div className="dashboard-page">
        <div className="page-header">
          <div>
            <h1 className="page-title">Field Representative Dashboard</h1>
            <p className="page-subtitle">Loading metrics and AI summaries...</p>
          </div>
        </div>
        <StatsSkeleton />
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem', marginTop: '2rem' }}>
          <TableSkeleton rows={3} />
          <TableSkeleton rows={3} />
        </div>
      </div>
    );
  }

  const { total_hcps, total_interactions, upcoming_followups, ai_insights_summary, recent_activities } = dashboard;
  
  // Custom mock analytics monthly trends dataset if no historical logs group exists yet
  const chartData = [
    { name: 'Feb', contacts: 1 },
    { name: 'Mar', contacts: 2 },
    { name: 'Apr', contacts: 4 },
    { name: 'May', contacts: 5 },
    { name: 'Jun', contacts: 9 },
    { name: 'Jul', contacts: total_interactions }
  ];

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Field Representative Dashboard</h1>
          <p className="page-subtitle">Real-time HCP metrics, follow-ups, and pharmaceutical logs.</p>
        </div>
        <Link to="/log-interaction" className="btn btn-primary">
          <span>Log Interaction</span>
          <ArrowRight size={16} />
        </Link>
      </div>

      {/* KPI Stats widgets */}
      <div className="stats-grid">
        <div className="card stat-card">
          <div className="stat-icon-wrapper blue">
            <Users size={22} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Total HCPs</span>
            <h3 className="stat-value">{total_hcps}</h3>
          </div>
        </div>

        <div className="card stat-card">
          <div className="stat-icon-wrapper teal">
            <PhoneCall size={22} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Total Interactions</span>
            <h3 className="stat-value">{total_interactions}</h3>
          </div>
        </div>

        <div className="card stat-card">
          <div className="stat-icon-wrapper warning">
            <CalendarClock size={22} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Upcoming Follow-ups</span>
            <h3 className="stat-value">{upcoming_followups}</h3>
          </div>
        </div>

        <div className="card stat-card">
          <div className="stat-icon-wrapper purple">
            <Cpu size={22} />
          </div>
          <div className="stat-content">
            <span className="stat-label">HCP Engagement Index</span>
            <h3 className="stat-value">{ai_insights_summary.average_engagement_score}%</h3>
          </div>
        </div>
      </div>

      {/* Main dashboard body grids */}
      <div className="dashboard-grid">
        {/* Contact Trends Area Chart */}
        <div className="card chart-card">
          <h3 className="widget-title">
            <TrendingUp size={18} />
            <span>Weekly Contact History</span>
          </h3>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorContacts" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.25}/>
                    <stop offset="95%" stopColor="var(--primary)" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-light)" />
                <XAxis dataKey="name" stroke="var(--text-light)" fontSize={12} tickLine={false} />
                <YAxis stroke="var(--text-light)" fontSize={12} tickLine={false} />
                <Tooltip />
                <Area type="monotone" dataKey="contacts" stroke="var(--primary)" strokeWidth={2.5} fillOpacity={1} fill="url(#colorContacts)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Insight Sentiment Widget */}
        <div className="card sentiment-widget">
          <h3 className="widget-title">
            <Cpu size={18} className="ai-icon" />
            <span>AI Insights Sentiment</span>
          </h3>
          
          <div className="sentiment-bars">
            <div className="sentiment-bar-row">
              <span className="sentiment-row-label">
                <Smile size={16} className="text-success" />
                <span>Positive</span>
              </span>
              <div className="progress-bar-container">
                <div 
                  className="progress-bar bg-success" 
                  style={{ width: `${(ai_insights_summary.sentiment_distribution.Positive / Math.max(total_hcps, 1)) * 100}%` }}
                />
              </div>
              <span className="sentiment-row-value">{ai_insights_summary.sentiment_distribution.Positive}</span>
            </div>

            <div className="sentiment-bar-row">
              <span className="sentiment-row-label">
                <Compass size={16} className="text-primary" />
                <span>Neutral</span>
              </span>
              <div className="progress-bar-container">
                <div 
                  className="progress-bar bg-primary" 
                  style={{ width: `${(ai_insights_summary.sentiment_distribution.Neutral / Math.max(total_hcps, 1)) * 100}%` }}
                />
              </div>
              <span className="sentiment-row-value">{ai_insights_summary.sentiment_distribution.Neutral}</span>
            </div>

            <div className="sentiment-bar-row">
              <span className="sentiment-row-label">
                <Frown size={16} className="text-danger" />
                <span>Negative</span>
              </span>
              <div className="progress-bar-container">
                <div 
                  className="progress-bar bg-danger" 
                  style={{ width: `${(ai_insights_summary.sentiment_distribution.Negative / Math.max(total_hcps, 1)) * 100}%` }}
                />
              </div>
              <span className="sentiment-row-value">{ai_insights_summary.sentiment_distribution.Negative}</span>
            </div>
          </div>

          <div className="sentiment-summary-footer">
            <p>Engagement calculations suggest positive sentiments toward <strong>CardioPlus</strong> and <strong>NeuroZest</strong>.</p>
          </div>
        </div>

        {/* Recent Activity Feed */}
        <div className="card activity-card">
          <h3 className="widget-title">
            <Activity size={18} />
            <span>Recent Activity Feed</span>
          </h3>

          <div className="activity-feed">
            {recent_activities.length === 0 ? (
              <div className="empty-state">
                <p>No interactions logged recently.</p>
              </div>
            ) : (
              recent_activities.map((act) => (
                <div key={act.id} className="activity-item">
                  <div className="activity-indicator" />
                  <div className="activity-content">
                    <div className="activity-header">
                      <Link to={`/hcps/${act.hcp_id}`} className="activity-hcp-link">
                        <span>Dr. {act.hcp_name}</span>
                        <ExternalLink size={12} />
                      </Link>
                      <span className="activity-date">
                        {new Date(act.date_time).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                      </span>
                    </div>
                    <p className="activity-desc">
                      Logged <strong>{act.interaction_type}</strong> regarding <strong>{act.product_discussed}</strong>. 
                      Outcome: <em>"{act.outcome || 'No outcome recorded.'}"</em>
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <style>{`
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .stat-card {
          display: flex;
          align-items: center;
          gap: 1.25rem;
          padding: 1.25rem 1.5rem;
        }

        .stat-icon-wrapper {
          width: 48px;
          height: 48px;
          border-radius: var(--radius-md);
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .stat-icon-wrapper.blue { background: hsl(215, 85%, 94%); color: hsl(215, 80%, 45%); }
        .stat-icon-wrapper.teal { background: hsl(160, 84%, 94%); color: hsl(160, 84%, 35%); }
        .stat-icon-wrapper.warning { background: hsl(38, 92%, 94%); color: hsl(38, 92%, 40%); }
        .stat-icon-wrapper.purple { background: hsl(270, 80%, 94%); color: hsl(270, 75%, 45%); }

        .stat-label {
          font-size: 0.8125rem;
          font-weight: 600;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .stat-value {
          font-size: 1.5rem;
          font-weight: 700;
          color: var(--text-main);
          margin-top: 0.125rem;
        }

        .dashboard-grid {
          display: grid;
          grid-template-columns: 2fr 1fr;
          gap: 2rem;
        }

        @media (max-width: 1024px) {
          .dashboard-grid {
            grid-template-columns: 1fr;
          }
        }

        .chart-card {
          grid-column: span 1;
        }

        .widget-title {
          font-size: 1.0625rem;
          font-weight: 700;
          color: var(--text-main);
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 1.5rem;
          padding-bottom: 0.75rem;
          border-bottom: 1px solid var(--border-light);
        }

        .ai-icon {
          color: var(--primary);
        }

        .sentiment-widget {
          display: flex;
          flex-direction: column;
          justify-content: space-between;
        }

        .sentiment-bars {
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
          margin: 1rem 0;
        }

        .sentiment-bar-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 1rem;
        }

        .sentiment-row-label {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.875rem;
          font-weight: 600;
          width: 90px;
        }

        .progress-bar-container {
          flex: 1;
          height: 8px;
          background: var(--primary-light);
          border-radius: var(--radius-full);
          overflow: hidden;
        }

        .progress-bar {
          height: 100%;
          border-radius: var(--radius-full);
          transition: width 1s ease-in-out;
        }

        .bg-success { background-color: var(--success); }
        .bg-primary { background-color: var(--primary); }
        .bg-danger { background-color: var(--danger); }
        
        .text-success { color: var(--success); }
        .text-primary { color: var(--primary); }
        .text-danger { color: var(--danger); }

        .sentiment-row-value {
          font-size: 0.875rem;
          font-weight: 700;
          color: var(--text-main);
          width: 20px;
          text-align: right;
        }

        .sentiment-summary-footer {
          background: var(--primary-light);
          border-radius: var(--radius-sm);
          padding: 0.75rem 1rem;
          font-size: 0.8125rem;
          color: var(--text-muted);
          line-height: 1.4;
          border-left: 3px solid var(--primary);
        }

        .activity-card {
          grid-column: span 1;
          display: flex;
          flex-direction: column;
        }

        @media (min-width: 1025px) {
          .activity-card {
            grid-column: span 2;
          }
        }

        .activity-feed {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .activity-item {
          display: flex;
          gap: 1rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid var(--border-light);
        }

        .activity-item:last-child {
          border-bottom: none;
          padding-bottom: 0;
        }

        .activity-indicator {
          width: 8px;
          height: 8px;
          border-radius: var(--radius-full);
          background: var(--primary);
          margin-top: 6px;
          box-shadow: 0 0 0 3px var(--primary-glow);
        }

        .activity-content {
          flex: 1;
        }

        .activity-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.25rem;
        }

        .activity-hcp-link {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--primary);
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .activity-hcp-link:hover {
          text-decoration: underline;
        }

        .activity-date {
          font-size: 0.75rem;
          color: var(--text-light);
        }

        .activity-desc {
          font-size: 0.875rem;
          color: var(--text-main);
          line-height: 1.4;
        }
      `}</style>
    </div>
  );
};

export default Dashboard;
