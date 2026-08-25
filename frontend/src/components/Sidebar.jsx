import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { 
  LayoutDashboard, 
  ClipboardList, 
  Users, 
  CheckSquare, 
  BarChart3, 
  LogOut,
  Activity,
  Menu,
  X,
  Zap,
  Bell,
  Shield,
  Inbox
} from 'lucide-react';
import { logout } from '../features/authSlice';

export const Sidebar = ({ mobileOpen, setMobileOpen }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} /> },
    { name: 'Log Interaction', path: '/log-interaction', icon: <ClipboardList size={20} /> },
    { name: 'HCP Directory', path: '/hcps', icon: <Users size={20} /> },
    { name: 'Follow-ups', path: '/followups', icon: <CheckSquare size={20} /> },
    { name: 'Analytics & Insights', path: '/analytics', icon: <BarChart3 size={20} /> },
    { name: 'AI Action Center', path: '/ai-action-center', icon: <Zap size={20} /> },
    { name: 'Notifications', path: '/notifications', icon: <Bell size={20} /> },
    { name: 'Approvals', path: '/approvals', icon: <Shield size={20} /> },
  ];

  return (
    <>
      {/* Mobile top bar */}
      <header className="mobile-header">
        <div className="mobile-brand">
          <Activity className="brand-logo" />
          <span className="brand-title">MediConnect AI</span>
        </div>
        <button className="mobile-menu-btn" onClick={() => setMobileOpen(!mobileOpen)}>
          {mobileOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </header>

      {/* Sidebar navigation shell */}
      <aside className={`sidebar-aside ${mobileOpen ? 'mobile-active' : ''}`}>
        <div className="sidebar-brand">
          <Activity className="brand-logo" />
          <span className="brand-title">MediConnect AI</span>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setMobileOpen(false)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-name">{item.name}</span>
            </NavLink>
          ))}
        </nav>

        {user && (
          <div className="sidebar-footer">
            <div className="user-profile">
              <div className="user-avatar">
                {user.username.substring(0, 2).toUpperCase()}
              </div>
              <div className="user-info">
                <div className="user-name">{user.username}</div>
                <div className="user-role">Field Representative</div>
              </div>
            </div>
            <button className="logout-btn" onClick={handleLogout}>
              <LogOut size={18} />
              <span>Sign Out</span>
            </button>
          </div>
        )}
      </aside>

      {/* Dim overlay for mobile drawer */}
      {mobileOpen && (
        <div className="sidebar-overlay" onClick={() => setMobileOpen(false)} />
      )}

      <style>{`
        .mobile-header {
          display: none;
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          height: 60px;
          background: white;
          border-bottom: 1px solid var(--border-light);
          padding: 0 1rem;
          align-items: center;
          justify-content: space-between;
          z-index: 1000;
        }

        .mobile-brand {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: var(--primary);
        }

        .mobile-menu-btn {
          background: none;
          border: none;
          color: var(--text-main);
          cursor: pointer;
        }

        .sidebar-aside {
          position: fixed;
          top: 0;
          bottom: 0;
          left: 0;
          width: 260px;
          background: var(--bg-sidebar);
          border-right: 1px solid var(--border-light);
          display: flex;
          flex-direction: column;
          z-index: 1001;
          transition: transform var(--transition-normal);
        }

        .sidebar-brand {
          height: 80px;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0 1.5rem;
          color: var(--primary);
          border-bottom: 1px solid rgba(0, 0, 0, 0.02);
        }

        .brand-logo {
          color: var(--primary);
          stroke-width: 2.5;
        }

        .brand-title {
          font-weight: 800;
          font-size: 1.125rem;
          letter-spacing: -0.5px;
        }

        .sidebar-nav {
          flex: 1;
          padding: 1.5rem 1rem;
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
          overflow-y: auto;
        }

        .nav-item {
          display: flex;
          align-items: center;
          gap: 0.875rem;
          padding: 0.75rem 1rem;
          color: var(--text-muted);
          font-weight: 500;
          font-size: 0.9375rem;
          border-radius: var(--radius-sm);
        }

        .nav-item:hover {
          color: var(--primary);
          background-color: var(--primary-light);
        }

        .nav-item.active {
          color: var(--primary);
          background-color: var(--primary-light);
          font-weight: 600;
        }

        .nav-icon {
          display: flex;
          align-items: center;
        }

        .sidebar-footer {
          padding: 1.5rem;
          border-top: 1px solid var(--border-light);
          background: hsl(210, 20%, 99%);
        }

        .user-profile {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 1.25rem;
        }

        .user-avatar {
          width: 36px;
          height: 36px;
          border-radius: var(--radius-full);
          background: var(--primary);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 0.8125rem;
          box-shadow: 0 4px 10px var(--primary-glow);
        }

        .user-name {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--text-main);
          text-transform: capitalize;
        }

        .user-role {
          font-size: 0.75rem;
          color: var(--text-muted);
        }

        .logout-btn {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          padding: 0.625rem;
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--danger);
          background: var(--danger-light);
          border: none;
          border-radius: var(--radius-sm);
          cursor: pointer;
          transition: all var(--transition-fast);
        }

        .logout-btn:hover {
          background: hsl(354, 76%, 92%);
        }

        .sidebar-overlay {
          display: none;
        }

        @media (max-width: 1024px) {
          .sidebar-aside {
            width: 80px;
          }
          .brand-title, .nav-name, .user-info, .logout-btn span {
            display: none;
          }
          .sidebar-brand, .user-profile {
            justify-content: center;
            padding: 0;
          }
          .sidebar-brand {
            height: 70px;
          }
          .nav-item {
            justify-content: center;
            padding: 0.875rem 0;
          }
          .sidebar-footer {
            padding: 1rem 0.5rem;
            display: flex;
            flex-direction: column;
            align-items: center;
          }
          .logout-btn {
            padding: 0.625rem 0;
            width: 40px;
            height: 40px;
            border-radius: var(--radius-full);
          }
        }

        @media (max-width: 768px) {
          .mobile-header {
            display: flex;
          }
          .sidebar-aside {
            transform: translateX(-100%);
            width: 260px;
          }
          .brand-title, .nav-name, .user-info, .logout-btn span {
            display: inline;
          }
          .sidebar-brand, .user-profile {
            justify-content: flex-start;
            padding: 0 1.5rem;
          }
          .sidebar-brand {
            height: 80px;
          }
          .nav-item {
            justify-content: flex-start;
            padding: 0.75rem 1rem;
          }
          .sidebar-footer {
            padding: 1.5rem;
            width: 100%;
          }
          .logout-btn {
            width: 100%;
            height: auto;
            border-radius: var(--radius-sm);
          }
          .sidebar-aside.mobile-active {
            transform: translateX(0);
          }
          .sidebar-overlay {
            display: block;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(4px);
            z-index: 1000;
          }
        }
      `}</style>
    </>
  );
};

export default Sidebar;
