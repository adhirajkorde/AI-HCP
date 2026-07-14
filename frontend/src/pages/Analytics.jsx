import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
  BarChart3, 
  TrendingUp, 
  Smile, 
  PieChart as PieIcon, 
  Activity,
  CheckCircle,
  HelpCircle
} from 'lucide-react';
import { fetchMetricsData } from '../features/analyticsSlice';
import { TableSkeleton } from '../components/Skeleton';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  CartesianGrid 
} from 'recharts';

export const Analytics = () => {
  const dispatch = useDispatch();
  const { metrics, metricsLoading, error } = useSelector((state) => state.analytics);

  useEffect(() => {
    dispatch(fetchMetricsData());
  }, [dispatch]);

  if (metricsLoading || !metrics) {
    return (
      <div className="analytics-page">
        <div className="page-header">
          <div>
            <h1 className="page-title">Interaction Analytics</h1>
            <p className="page-subtitle">Loading metrics, graphs and clinical charts...</p>
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          <TableSkeleton rows={4} />
          <TableSkeleton rows={4} />
        </div>
      </div>
    );
  }

  const { sentiment_trends, engagement_score_distribution, product_discussion_stats, followup_metrics, monthly_interaction_trends } = metrics;

  // Format Recharts Data
  const sentimentData = [
    { name: 'Positive', value: sentiment_trends.Positive, color: 'var(--success)' },
    { name: 'Neutral', value: sentiment_trends.Neutral, color: 'var(--primary)' },
    { name: 'Negative', value: sentiment_trends.Negative, color: 'var(--danger)' }
  ].filter(d => d.value > 0);

  const engagementData = [
    { name: 'Low (0-49)', value: engagement_score_distribution['Low (0-49)'], color: 'var(--danger)' },
    { name: 'Medium (50-79)', value: engagement_score_distribution['Medium (50-79)'], color: 'var(--primary)' },
    { name: 'High (80-100)', value: engagement_score_distribution['High (80-100)'], color: 'var(--secondary)' }
  ];

  // Primary colors list for products pie/bar
  const PRODUCT_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

  return (
    <div className="analytics-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Interaction Analytics</h1>
          <p className="page-subtitle">Comprehensive sentiment trends, product coverage metrics, and engagement stats.</p>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="analytics-summary-cards">
        <div className="card summary-card">
          <CheckCircle size={24} className="summary-card-icon success" />
          <div className="summary-card-details">
            <span className="summary-card-label">Follow-up Completion Rate</span>
            <h3 className="summary-card-val">{followup_metrics.completion_rate}%</h3>
            <p className="summary-card-desc">
              Completed {followup_metrics.completed} of {followup_metrics.total} scheduled tasks.
            </p>
          </div>
        </div>

        <div className="card summary-card">
          <Smile size={24} className="summary-card-icon positive" />
          <div className="summary-card-details">
            <span className="summary-card-label">Positive Sentiment Ratio</span>
            <h3 className="summary-card-val">
              {roundToDec(((sentiment_trends.Positive) / Math.max(sentiment_trends.Positive + sentiment_trends.Neutral + sentiment_trends.Negative, 1)) * 100)}%
            </h3>
            <p className="summary-card-desc">Based on AI-extracted clinical interaction notes.</p>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="analytics-charts-grid">
        {/* Sentiment Distribution */}
        <div className="card chart-widget-card">
          <h3 className="chart-widget-title">
            <Smile size={18} />
            <span>Doctor Sentiment Distribution</span>
          </h3>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {sentimentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Product Discussion Ratios */}
        <div className="card chart-widget-card">
          <h3 className="chart-widget-title">
            <PieIcon size={18} />
            <span>Product Discussion Shares</span>
          </h3>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={product_discussion_stats}
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                >
                  {product_discussion_stats.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PRODUCT_COLORS[index % PRODUCT_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Engagement Distributions */}
        <div className="card chart-widget-card">
          <h3 className="chart-widget-title">
            <Activity size={18} />
            <span>HCP Engagement Index Range</span>
          </h3>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={engagementData} margin={{ left: -20, top: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-light)" />
                <XAxis dataKey="name" stroke="var(--text-light)" fontSize={12} tickLine={false} />
                <YAxis stroke="var(--text-light)" fontSize={12} tickLine={false} />
                <Tooltip />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {engagementData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Monthly Activity History */}
        <div className="card chart-widget-card">
          <h3 className="chart-widget-title">
            <TrendingUp size={18} />
            <span>Monthly Log Volumes</span>
          </h3>
          <div className="chart-wrapper">
            {monthly_interaction_trends.length === 0 ? (
              <div className="empty-state">
                <p>No monthly logs historical details.</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <AreaChart data={monthly_interaction_trends} margin={{ left: -20, top: 10 }}>
                  <defs>
                    <linearGradient id="colorTrends" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--secondary)" stopOpacity={0.25}/>
                      <stop offset="95%" stopColor="var(--secondary)" stopOpacity={0.0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-light)" />
                  <XAxis dataKey="month" stroke="var(--text-light)" fontSize={12} tickLine={false} />
                  <YAxis stroke="var(--text-light)" fontSize={12} tickLine={false} />
                  <Tooltip />
                  <Area type="monotone" dataKey="count" stroke="var(--secondary)" strokeWidth={2.5} fillOpacity={1} fill="url(#colorTrends)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      <style>{`
        .analytics-summary-cards {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        @media (max-width: 768px) {
          .analytics-summary-cards {
            grid-template-columns: 1fr;
          }
        }

        .summary-card {
          display: flex;
          align-items: center;
          gap: 1.25rem;
          padding: 1.5rem;
        }

        .summary-card-icon {
          width: 48px;
          height: 48px;
          border-radius: var(--radius-sm);
          padding: 10px;
        }

        .summary-card-icon.success { background: var(--success-light); color: var(--success); }
        .summary-card-icon.positive { background: var(--secondary-light); color: var(--secondary); }

        .summary-card-label {
          font-size: 0.8125rem;
          font-weight: 700;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .summary-card-val {
          font-size: 1.75rem;
          font-weight: 800;
          color: var(--text-main);
          margin-top: 0.25rem;
        }

        .summary-card-desc {
          font-size: 0.8125rem;
          color: var(--text-light);
          margin-top: 0.125rem;
        }

        .analytics-charts-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(440px, 1fr));
          gap: 2rem;
        }

        @media (max-width: 480px) {
          .analytics-charts-grid {
            grid-template-columns: 1fr;
          }
        }

        .chart-widget-title {
          font-size: 0.9375rem;
          font-weight: 700;
          color: var(--text-main);
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 1.5rem;
          padding-bottom: 0.75rem;
          border-bottom: 1px solid var(--border-light);
        }
      `}</style>
    </div>
  );
};

// Quick math rounded decimals helper
function roundToDec(num) {
  return Math.round(num * 10) / 10 || 0;
}

export default Analytics;
