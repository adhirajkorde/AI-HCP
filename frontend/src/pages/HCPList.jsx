import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { Plus, Users, Stethoscope, Building, Star, Mail, Phone, Loader2, ArrowRight } from 'lucide-react';
import { fetchHCPs, createHCP } from '../features/hcpSlice';
import { TableSkeleton } from '../components/Skeleton';
import { useToast } from '../components/ToastContext';

export const HCPList = () => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [name, setName] = useState('');
  const [specialty, setSpecialty] = useState('Cardiology');
  const [hospitalClinic, setHospitalClinic] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [productPreference, setProductPreference] = useState('CardioPlus');

  const dispatch = useDispatch();
  const { showToast } = useToast();
  const { list: hcpList, loading } = useSelector((state) => state.hcps);

  useEffect(() => {
    dispatch(fetchHCPs());
  }, [dispatch]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim() || !hospitalClinic.trim()) {
      showToast('Please enter both name and facility.', 'warning');
      return;
    }

    const payload = {
      name,
      specialty,
      hospital_clinic: hospitalClinic,
      email: email || null,
      phone: phone || null,
      product_preference: productPreference
    };

    dispatch(createHCP(payload))
      .unwrap()
      .then(() => {
        showToast(`Dr. ${name} added successfully!`, 'success');
        resetForm();
        setShowAddForm(false);
      })
      .catch((err) => {
        showToast(err || 'Failed to add HCP', 'error');
      });
  };

  const resetForm = () => {
    setName('');
    setHospitalClinic('');
    setEmail('');
    setPhone('');
  };

  if (loading && hcpList.length === 0) {
    return (
      <div className="hcp-list-page">
        <div className="page-header">
          <div>
            <h1 className="page-title">Healthcare Professionals (HCPs)</h1>
            <p className="page-subtitle">Loading clinical representative directory...</p>
          </div>
        </div>
        <TableSkeleton rows={5} />
      </div>
    );
  }

  return (
    <div className="hcp-list-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Healthcare Professionals Directory</h1>
          <p className="page-subtitle">View profiles, contact details, product alignments, and past timelines.</p>
        </div>
        <button 
          onClick={() => setShowAddForm(!showAddForm)} 
          className="btn btn-primary"
        >
          <Plus size={16} />
          <span>Add New HCP</span>
        </button>
      </div>

      {showAddForm && (
        <div className="card add-hcp-card fade-in">
          <h3 className="widget-title">Register New Medical Professional</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Doctor Name</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="e.g. Sarah Jenkins"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required 
                />
              </div>

              <div className="form-group">
                <label className="form-label">Specialty Area</label>
                <select 
                  className="form-input"
                  value={specialty}
                  onChange={(e) => setSpecialty(e.target.value)}
                >
                  <option value="Cardiology">Cardiology</option>
                  <option value="Neurology">Neurology</option>
                  <option value="Endocrinology">Endocrinology</option>
                  <option value="Gastroenterology">Gastroenterology</option>
                  <option value="Immunology">Immunology</option>
                  <option value="General Medicine">General Medicine</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Hospital / Facility</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="e.g. Metro Heart Clinic"
                  value={hospitalClinic}
                  onChange={(e) => setHospitalClinic(e.target.value)}
                  required 
                />
              </div>

              <div className="form-group">
                <label className="form-label">Preferred Product</label>
                <select 
                  className="form-input"
                  value={productPreference}
                  onChange={(e) => setProductPreference(e.target.value)}
                >
                  <option value="CardioPlus">CardioPlus</option>
                  <option value="LipoCare">LipoCare</option>
                  <option value="NeuroZest">NeuroZest</option>
                  <option value="GastroShield">GastroShield</option>
                  <option value="Immunex">Immunex</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Email address (Optional)</label>
                <input 
                  type="email" 
                  className="form-input" 
                  placeholder="name@clinic.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Phone contact (Optional)</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="555-xxxx"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </div>
            </div>
            
            <div className="form-actions" style={{ marginTop: '1rem' }}>
              <button 
                type="button" 
                className="btn btn-secondary" 
                onClick={() => setShowAddForm(false)}
                style={{ marginRight: '0.75rem' }}
              >
                Cancel
              </button>
              <button type="submit" className="btn btn-primary">
                Confirm Registration
              </button>
            </div>
          </form>
        </div>
      )}

      {hcpList.length === 0 ? (
        <div className="card empty-state">
          <Users size={48} className="empty-icon" />
          <h3>No doctors registered yet</h3>
          <p>Get started by clicking the "Add New HCP" button to register your medical representative directory.</p>
        </div>
      ) : (
        <div className="hcp-directory-grid">
          {hcpList.map((hcp) => (
            <div key={hcp.id} className="card hcp-item-card">
              <div className="avatar-header-row">
                <div className="hcp-avatar">
                  {hcp.name.substring(0, 2).toUpperCase()}
                </div>
                <div>
                  <h4 className="hcp-card-name">Dr. {hcp.name}</h4>
                  <div className="hcp-card-specialty">
                    <Stethoscope size={12} />
                    <span>{hcp.specialty}</span>
                  </div>
                </div>
              </div>

              <div className="hcp-card-body">
                <div className="card-detail-item">
                  <Building size={14} />
                  <span>{hcp.hospital_clinic}</span>
                </div>
                {hcp.email && (
                  <div className="card-detail-item">
                    <Mail size={14} />
                    <span>{hcp.email}</span>
                  </div>
                )}
                {hcp.phone && (
                  <div className="card-detail-item">
                    <Phone size={14} />
                    <span>{hcp.phone}</span>
                  </div>
                )}
                <div className="card-detail-item align-tag">
                  <Star size={14} className="star-highlight" />
                  <span>Aligns: <strong>{hcp.product_preference || 'None'}</strong></span>
                </div>
              </div>

              <div className="hcp-card-footer">
                <Link to={`/hcps/${hcp.id}`} className="btn btn-secondary full-width">
                  <span>View Timeline</span>
                  <ArrowRight size={14} />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      <style>{`
        .add-hcp-card {
          margin-bottom: 2rem;
        }

        .hcp-directory-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 1.5rem;
        }

        .hcp-item-card {
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          padding: 1.25rem 1.5rem;
        }

        .avatar-header-row {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 1rem;
          padding-bottom: 0.75rem;
          border-bottom: 1px solid var(--border-light);
        }

        .hcp-avatar {
          width: 42px;
          height: 42px;
          border-radius: var(--radius-full);
          background: var(--primary-light);
          color: var(--primary);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 0.9375rem;
        }

        .hcp-card-name {
          font-size: 0.9375rem;
          font-weight: 700;
          color: var(--text-main);
        }

        .hcp-card-specialty {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 0.75rem;
          color: var(--text-muted);
          margin-top: 0.125rem;
        }

        .hcp-card-body {
          display: flex;
          flex-direction: column;
          gap: 0.625rem;
          margin-bottom: 1.25rem;
        }

        .card-detail-item {
          display: flex;
          align-items: center;
          gap: 0.625rem;
          font-size: 0.8125rem;
          color: var(--text-muted);
        }

        .card-detail-item.align-tag {
          color: var(--text-main);
          font-weight: 500;
        }

        .star-highlight {
          color: var(--secondary);
          fill: var(--secondary);
        }

        .hcp-card-footer {
          margin-top: auto;
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

        .empty-state p {
          font-size: 0.875rem;
          max-width: 400px;
        }
      `}</style>
    </div>
  );
};

export default HCPList;
