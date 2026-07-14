import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  FileText, 
  Send, 
  Check, 
  Loader2, 
  User, 
  Building, 
  Stethoscope, 
  Info,
  Calendar,
  MessageCircle,
  ThumbsUp,
  AlertTriangle
} from 'lucide-react';
import { fetchHCPs } from '../features/hcpSlice';
import { 
  logStructuredInteraction, 
  analyzeConversationalText, 
  confirmAIInteraction, 
  clearAIExtraction 
} from '../features/interactionSlice';
import { useToast } from '../components/ToastContext';

export const LogInteraction = () => {
  const [activeTab, setActiveTab] = useState('structured'); // structured or aiChat
  
  // Structured form states
  const [hcpId, setHcpId] = useState('');
  const [interactionType, setInteractionType] = useState('In-Person Meeting');
  const [dateTime, setDateTime] = useState(() => {
    const d = new Date();
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    return d.toISOString().slice(0, 16);
  });
  const [productDiscussed, setProductDiscussed] = useState('CardioPlus');
  const [notes, setNotes] = useState('');
  const [outcome, setOutcome] = useState('');
  const [followUpDate, setFollowUpDate] = useState('');

  // AI chat states
  const [rawText, setRawText] = useState('');
  const [editableEntities, setEditableEntities] = useState(null);

  const dispatch = useDispatch();
  const { showToast } = useToast();
  
  const { list: hcpList } = useSelector((state) => state.hcps);
  const { loading, aiLoading, aiExtraction } = useSelector((state) => state.interactions);

  useEffect(() => {
    dispatch(fetchHCPs());
    dispatch(clearAIExtraction());
  }, [dispatch]);

  // Autofill specialty/hospital if HCP is selected in Structured Form
  const selectedHCPDetails = hcpList.find(h => h.id === parseInt(hcpId));

  // Initialize editable entities once AI analysis returns results
  useEffect(() => {
    if (aiExtraction && aiExtraction.success) {
      const ent = aiExtraction.entities;
      // Pre-resolve doctor in our local HCP list if possible
      let matchedHcpId = '';
      if (ent.hcp_name) {
        const cleanedName = ent.hcp_name.toLowerCase().replace('dr.', '').trim();
        const found = hcpList.find(h => h.name.toLowerCase().includes(cleanedName));
        if (found) matchedHcpId = found.id;
      }

      setEditableEntities({
        hcp_id: matchedHcpId,
        hcp_name: ent.hcp_name || 'Dr. Sharma',
        specialty: ent.specialty || 'General Medicine',
        hospital_clinic: ent.hospital_clinic || 'General Clinic',
        interaction_type: ent.interaction_type || 'In-Person Meeting',
        product_discussed: ent.product_discussed || 'CardioPlus',
        notes: ent.notes || rawText,
        outcome: ent.outcome || 'Discussed trials.',
        follow_up_date: ent.follow_up_date ? new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10) : '',
        sentiment: aiExtraction.sentiment || 'Neutral',
        engagement_score: aiExtraction.engagement_score || 50
      });
    }
  }, [aiExtraction, hcpList, rawText]);

  // Log Structured interaction handler
  const handleStructuredSubmit = (e) => {
    e.preventDefault();
    if (!hcpId) {
      showToast('Please select a healthcare professional.', 'warning');
      return;
    }
    if (!notes.trim()) {
      showToast('Please enter clinical interaction notes.', 'warning');
      return;
    }

    const payload = {
      hcp_id: parseInt(hcpId),
      interaction_type,
      date_time: new Date(dateTime).toISOString(),
      product_discussed,
      notes,
      outcome: outcome || 'Discussion complete.',
      follow_up_date: followUpDate ? new Date(followUpDate).toISOString() : null
    };

    dispatch(logStructuredInteraction(payload))
      .unwrap()
      .then(() => {
        showToast('Interaction logged successfully!', 'success');
        resetStructuredForm();
      })
      .catch((err) => {
        showToast(err || 'Failed to log interaction', 'error');
      });
  };

  const resetStructuredForm = () => {
    setHcpId('');
    setNotes('');
    setOutcome('');
    setFollowUpDate('');
  };

  // Run LangGraph AI Parser handler
  const handleAISubmit = (e) => {
    e.preventDefault();
    if (!rawText.trim()) {
      showToast('Please input conversational notes for the agent to parse.', 'warning');
      return;
    }

    dispatch(analyzeConversationalText(rawText))
      .unwrap()
      .then(() => {
        showToast('Text parsed successfully. Review extracted data below.', 'success');
      })
      .catch((err) => {
        showToast(err || 'Failed to parse text.', 'error');
      });
  };

  // Confirm and Commit AI parsed details handler
  const handleSyncToCRM = () => {
    if (!editableEntities.hcp_id) {
      showToast('Please map the extracted doctor to a profile or create one first.', 'warning');
      return;
    }

    const payload = {
      hcp_id: parseInt(editableEntities.hcp_id),
      interaction_type: editableEntities.interaction_type,
      date_time: new Date().toISOString(),
      product_discussed: editableEntities.product_discussed,
      notes: editableEntities.notes,
      outcome: editableEntities.outcome,
      follow_up_date: editableEntities.follow_up_date ? new Date(editableEntities.follow_up_date).toISOString() : null
    };

    dispatch(confirmAIInteraction(payload))
      .unwrap()
      .then(() => {
        showToast('AI-parsed record synced to CRM!', 'success');
        setRawText('');
        setEditableEntities(null);
      })
      .catch((err) => {
        showToast(err || 'Sync failed.', 'error');
      });
  };

  const handleEntityChange = (field, value) => {
    setEditableEntities(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="log-interaction-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Log HCP Interaction</h1>
          <p className="page-subtitle">Log representative touches via structured form inputs or conversational AI.</p>
        </div>
      </div>

      {/* Tabs Selector */}
      <div className="tab-control card">
        <button 
          className={`tab-btn ${activeTab === 'structured' ? 'active' : ''}`}
          onClick={() => setActiveTab('structured')}
        >
          <FileText size={18} />
          <span>Structured Form</span>
        </button>
        <button 
          className={`tab-btn ${activeTab === 'aiChat' ? 'active' : ''}`}
          onClick={() => setActiveTab('aiChat')}
        >
          <Sparkles size={18} className="ai-accent" />
          <span>Conversational AI Assistant</span>
        </button>
      </div>

      {/* TAB A: Structured Form */}
      {activeTab === 'structured' && (
        <div className="card log-card-form fade-in">
          <form onSubmit={handleStructuredSubmit} className="structured-form">
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">HCP Name</label>
                <select 
                  className="form-input" 
                  value={hcpId} 
                  onChange={(e) => setHcpId(e.target.value)}
                  required
                >
                  <option value="">-- Select Doctor --</option>
                  {hcpList.map(h => (
                    <option key={h.id} value={h.id}>{h.name} ({h.specialty})</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Specialty</label>
                <div className="input-autofill-box">
                  <Stethoscope size={16} />
                  <span>{selectedHCPDetails ? selectedHCPDetails.specialty : 'Select Doctor to Autofill'}</span>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Hospital/Clinic</label>
                <div className="input-autofill-box">
                  <Building size={16} />
                  <span>{selectedHCPDetails ? selectedHCPDetails.hospital_clinic : 'Select Doctor to Autofill'}</span>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Interaction Type</label>
                <select 
                  className="form-input" 
                  value={interactionType}
                  onChange={(e) => setInteractionType(e.target.value)}
                >
                  <option value="In-Person Meeting">In-Person Meeting</option>
                  <option value="Call">Phone Call</option>
                  <option value="Email">Email Check-in</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Date & Time</label>
                <input 
                  type="datetime-local" 
                  className="form-input" 
                  value={dateTime}
                  onChange={(e) => setDateTime(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Product Discussed</label>
                <select 
                  className="form-input"
                  value={productDiscussed}
                  onChange={(e) => setProductDiscussed(e.target.value)}
                >
                  <option value="CardioPlus">CardioPlus</option>
                  <option value="LipoCare">LipoCare</option>
                  <option value="NeuroZest">NeuroZest</option>
                  <option value="GastroShield">GastroShield</option>
                  <option value="Immunex">Immunex</option>
                </select>
              </div>
            </div>

            <div className="form-group full-width">
              <label className="form-label">Clinical Interaction Notes</label>
              <textarea 
                className="form-input textarea-notes" 
                rows="5"
                placeholder="Enter detailed summary notes of clinical details discussed, questions asked by the HCP, patient feedback..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                required
              />
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Follow-up Date (Optional)</label>
                <input 
                  type="date" 
                  className="form-input" 
                  value={followUpDate}
                  onChange={(e) => setFollowUpDate(e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Meeting Outcome (Optional)</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="e.g. Requested samples, interested in trial data"
                  value={outcome}
                  onChange={(e) => setOutcome(e.target.value)}
                />
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-primary btn-submit" disabled={loading}>
                {loading ? <Loader2 className="animate-spin" size={18} /> : null}
                <span>Commit Interaction</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* TAB B: Conversational AI Assistant */}
      {activeTab === 'aiChat' && (
        <div className="ai-tab-wrapper fade-in">
          {/* Chat prompt container */}
          <div className="card prompt-card">
            <h3 className="widget-title">
              <Sparkles size={18} className="ai-icon" />
              <span>LangGraph Conversational Logging</span>
            </h3>
            
            <form onSubmit={handleAISubmit} className="ai-input-form">
              <textarea
                className="form-input ai-textarea"
                rows="4"
                placeholder="Describe your meeting in natural language. For example:
'Emailed Dr Sarah Jenkins today regarding CardioPlus. She is highly interested in the cardiology trial slides and wants a follow up meeting in 2 weeks.'"
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                disabled={aiLoading}
              />
              
              <div className="ai-form-bar">
                <div className="ai-hint">
                  <Info size={14} />
                  <span>The agent will automatically extract HCP profiles, product discussed, sentiment index, and register follow-ups.</span>
                </div>
                <button type="submit" className="btn btn-teal" disabled={aiLoading || !rawText.trim()}>
                  {aiLoading ? (
                    <>
                      <Loader2 className="animate-spin" size={16} />
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <Send size={16} />
                      <span>Parse with Agent</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* AI Loader Skeleton */}
          {aiLoading && (
            <div className="card loading-skeleton-card fade-in">
              <div className="skeleton pulse-header" />
              <div className="skeleton-rows">
                <div className="skeleton pulse-row" style={{ width: '40%' }} />
                <div className="skeleton pulse-row" style={{ width: '70%' }} />
                <div className="skeleton pulse-row" style={{ width: '55%' }} />
              </div>
            </div>
          )}

          {/* AI Extraction Outputs & Confirmation */}
          {editableEntities && (
            <div className="ai-results-panel fade-in">
              <div className="ai-insights-grid">
                {/* Visual results summary */}
                <div className="card ai-kpi-card">
                  <h4 className="card-sub-title">Extraction Insights</h4>
                  
                  <div className="extraction-metrics">
                    <div className="metric-row">
                      <span>Sentiment:</span>
                      <span className={`sentiment-badge ${editableEntities.sentiment.toLowerCase()}`}>
                        {editableEntities.sentiment}
                      </span>
                    </div>

                    <div className="metric-row">
                      <span>Engagement Index:</span>
                      <span className="metric-score-value">{editableEntities.engagement_score}%</span>
                    </div>
                    
                    <div className="metric-progress-container">
                      <div 
                        className={`metric-progress-bar ${editableEntities.sentiment.toLowerCase()}`}
                        style={{ width: `${editableEntities.engagement_score}%` }}
                      />
                    </div>
                  </div>

                  <div className="raw-summary-block">
                    <h5>Agent Narrative Summary</h5>
                    <p>{aiExtraction?.summary}</p>
                  </div>
                </div>

                {/* Edit Form */}
                <div className="card ai-edit-card">
                  <h4 className="card-sub-title">Verify & Map Fields</h4>
                  
                  <div className="confirm-fields-form">
                    <div className="form-group">
                      <label className="form-label">Identified Doctor (HCP)</label>
                      <select
                        className="form-input highlighted"
                        value={editableEntities.hcp_id}
                        onChange={(e) => handleEntityChange('hcp_id', e.target.value)}
                      >
                        <option value="">-- Match Doctor Profile --</option>
                        {hcpList.map(h => (
                          <option key={h.id} value={h.id}>{h.name} ({h.specialty})</option>
                        ))}
                      </select>
                      {!editableEntities.hcp_id && (
                        <span className="mapping-warning">
                          <AlertTriangle size={12} />
                          <span>HCP '{editableEntities.hcp_name}' not found. Please match manually.</span>
                        </span>
                      )}
                    </div>

                    <div className="form-grid-2">
                      <div className="form-group">
                        <label className="form-label">Interaction Channel</label>
                        <select
                          className="form-input"
                          value={editableEntities.interaction_type}
                          onChange={(e) => handleEntityChange('interaction_type', e.target.value)}
                        >
                          <option value="In-Person Meeting">In-Person Meeting</option>
                          <option value="Call">Call</option>
                          <option value="Email">Email</option>
                        </select>
                      </div>

                      <div className="form-group">
                        <label className="form-label">Product Discussed</label>
                        <select
                          className="form-input"
                          value={editableEntities.product_discussed}
                          onChange={(e) => handleEntityChange('product_discussed', e.target.value)}
                        >
                          <option value="CardioPlus">CardioPlus</option>
                          <option value="LipoCare">LipoCare</option>
                          <option value="NeuroZest">NeuroZest</option>
                          <option value="GastroShield">GastroShield</option>
                          <option value="Immunex">Immunex</option>
                        </select>
                      </div>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Outcome Summary</label>
                      <input
                        type="text"
                        className="form-input"
                        value={editableEntities.outcome}
                        onChange={(e) => handleEntityChange('outcome', e.target.value)}
                      />
                    </div>

                    <div className="form-grid-2">
                      <div className="form-group">
                        <label className="form-label">Follow-up Action</label>
                        <input
                          type="text"
                          className="form-input"
                          value={aiExtraction?.follow_up_action || 'None'}
                          disabled
                        />
                      </div>

                      <div className="form-group">
                        <label className="form-label">Follow-up Date</label>
                        <input
                          type="date"
                          className="form-input"
                          value={editableEntities.follow_up_date}
                          onChange={(e) => handleEntityChange('follow_up_date', e.target.value)}
                        />
                      </div>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Refined Log Notes</label>
                      <textarea
                        className="form-input"
                        rows="3"
                        value={editableEntities.notes}
                        onChange={(e) => handleEntityChange('notes', e.target.value)}
                      />
                    </div>

                    <div className="confirm-actions">
                      <button onClick={handleSyncToCRM} className="btn btn-teal full-width" disabled={loading}>
                        {loading ? <Loader2 className="animate-spin" size={16} /> : <Check size={16} />}
                        <span>Confirm & Sync to CRM</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <style>{`
        .tab-control {
          display: flex;
          padding: 0.5rem;
          gap: 0.5rem;
          margin-bottom: 2rem;
          background: rgba(255, 255, 255, 0.7);
        }

        .tab-btn {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          padding: 0.875rem;
          border: none;
          background: none;
          cursor: pointer;
          font-weight: 600;
          font-size: 0.9375rem;
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

        .ai-accent {
          color: var(--secondary);
        }

        .form-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 1.5rem;
        }

        .input-autofill-box {
          height: 42px;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0 1rem;
          background: var(--primary-light);
          border: 1px solid var(--border-light);
          border-radius: var(--radius-sm);
          font-size: 0.875rem;
          color: var(--text-muted);
        }

        .full-width {
          grid-column: 1 / -1;
          margin-top: 0.5rem;
        }

        .textarea-notes {
          resize: vertical;
          min-height: 120px;
        }

        .form-actions {
          margin-top: 1.5rem;
          display: flex;
          justify-content: flex-end;
        }

        .btn-submit {
          padding: 0.75rem 2rem;
          font-size: 0.9375rem;
          font-weight: 600;
        }

        /* AI Prompt page css */
        .prompt-card {
          margin-bottom: 2rem;
        }

        .ai-textarea {
          resize: vertical;
          min-height: 90px;
          padding: 1rem;
          line-height: 1.5;
          margin-bottom: 1rem;
        }

        .ai-form-bar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 1rem;
        }

        .ai-hint {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.8125rem;
          color: var(--text-light);
        }

        .loading-skeleton-card {
          display: flex;
          flex-direction: column;
          gap: 1rem;
          padding: 2rem;
          min-height: 150px;
        }

        .pulse-header {
          height: 20px;
          width: 25%;
        }

        .skeleton-rows {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .pulse-row {
          height: 14px;
        }

        /* AI Results panels */
        .ai-insights-grid {
          display: grid;
          grid-template-columns: 1fr 2fr;
          gap: 2rem;
        }

        @media (max-width: 1024px) {
          .ai-insights-grid {
            grid-template-columns: 1fr;
          }
        }

        .card-sub-title {
          font-size: 1rem;
          font-weight: 700;
          color: var(--text-main);
          margin-bottom: 1.25rem;
          padding-bottom: 0.5rem;
          border-bottom: 1px solid var(--border-light);
        }

        .extraction-metrics {
          background: hsl(210, 20%, 99%);
          border-radius: var(--radius-sm);
          padding: 1rem;
          border: 1px solid var(--border-light);
          margin-bottom: 1.5rem;
        }

        .metric-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--text-muted);
          margin-bottom: 0.75rem;
        }

        .sentiment-badge {
          padding: 0.25rem 0.75rem;
          border-radius: var(--radius-full);
          font-size: 0.75rem;
          font-weight: 700;
          text-transform: uppercase;
        }

        .sentiment-badge.positive { background: var(--success-light); color: var(--success); }
        .sentiment-badge.neutral { background: var(--primary-light); color: var(--primary); }
        .sentiment-badge.negative { background: var(--danger-light); color: var(--danger); }

        .metric-score-value {
          font-size: 1.125rem;
          font-weight: 800;
          color: var(--text-main);
        }

        .metric-progress-container {
          height: 6px;
          background: var(--border-light);
          border-radius: var(--radius-full);
          overflow: hidden;
        }

        .metric-progress-bar {
          height: 100%;
          border-radius: var(--radius-full);
        }

        .metric-progress-bar.positive { background: var(--success); }
        .metric-progress-bar.neutral { background: var(--primary); }
        .metric-progress-bar.negative { background: var(--danger); }

        .raw-summary-block h5 {
          font-size: 0.8125rem;
          font-weight: 700;
          text-transform: uppercase;
          color: var(--text-light);
          margin-bottom: 0.5rem;
          letter-spacing: 0.5px;
        }

        .raw-summary-block p {
          font-size: 0.875rem;
          color: var(--text-main);
          line-height: 1.5;
        }

        .confirm-fields-form {
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
        }

        .form-grid-2 {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }

        .form-input.highlighted {
          border-color: var(--primary);
          background-color: var(--primary-light);
        }

        .mapping-warning {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 0.75rem;
          color: var(--warning);
          font-weight: 600;
          margin-top: 0.25rem;
        }

        .confirm-actions {
          margin-top: 1rem;
        }

        .animate-spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LogInteraction;
