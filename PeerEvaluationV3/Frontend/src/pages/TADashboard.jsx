import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProfileMenu from '../components/User/ProfileMenu';

export default function TADashboard() {
  const [activeTab, setActiveTab] = useState('home');
  const [user, setUser] = useState({ name: '', email: '', role: '' });
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Remove body background, handled by container now
    document.body.style.background = '';
    document.body.style.margin = '0';
    document.body.style.minHeight = '100vh';
    return () => {
      document.body.style.margin = '';
      document.body.style.minHeight = '';
    };
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return navigate('/login');

    fetch('http://localhost:5000/api/auth/profile', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(res => res.json())
      .then(data => {
        if (data?._id) setUser(data);
        else navigate('/login');
      })
      .catch(() => navigate('/login'));
  }, [navigate]);

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/login');
  };

  const handleSidebarToggle = () => setSidebarOpen(open => !open);

  return (
    <div
      className={`ta-dashboard-bg${sidebarOpen ? ' sidebar-open' : ''}`}
      style={{
        minHeight: '100vh',
        width: '100vw',
        background: 'linear-gradient(135deg, #ece9f7 0%, #c3cfe2 100%)',
        display: 'flex',
        flexDirection: 'row',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        boxSizing: 'border-box',
        overflow: 'hidden',
      }}
    >
      {/* Profile Icon Dropdown Top Right */}
      <div style={{
        position: 'fixed',
        top: 24,
        right: 36,
        zIndex: 2000,
        display: 'flex',
        alignItems: 'center',
      }}>
        <ProfileMenu user={user} onLogout={logout} onProfile={() => setActiveTab('profile')} />
      </div>

      {/* Sidebar Toggle Button */}
      <button
        className="sidebar-toggle-btn"
        style={{
          position: 'absolute',
          top: '1rem',
          left: '1rem',
          zIndex: 1100,
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          padding: '0.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.3rem',
          alignItems: 'center',
        }}
        onClick={handleSidebarToggle}
        aria-label="Toggle sidebar"
      >
        <span style={{ width: '30px', height: '3px', background: 'white', borderRadius: '2px' }}></span>
        <span style={{ width: '30px', height: '3px', background: 'white', borderRadius: '2px' }}></span>
        <span style={{ width: '30px', height: '3px', background: 'white', borderRadius: '2px' }}></span>
      </button>

      {/* Sidebar (collapsible) */}
      <div
        className={`ta-dashboard-sidebar${sidebarOpen ? ' open' : ' collapsed'}`}
        style={{
          ...sidebarStyle,
          position: 'relative',
          height: 'auto',
          minHeight: '100vh',
          zIndex: 1,
          width: sidebarOpen ? '250px' : '60px',
          transition: 'width 0.3s ease',
        }}
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        <h2 style={{ fontSize: sidebarOpen ? '1.6rem' : '0', fontWeight: 'bold', marginBottom: sidebarOpen ? '1rem' : '0', overflow: 'hidden', whiteSpace: 'nowrap' }}>TA Panel</h2>
        {sidebarOpen && (
          <>
            <button onClick={() => setActiveTab('home')} style={buttonStyle(activeTab === 'home')}>🏠 Home</button>
            <button onClick={() => setActiveTab('role')} style={buttonStyle(activeTab === 'role')}>🧑‍💼 Role Manager</button>
            <button onClick={() => setActiveTab('course')} style={buttonStyle(activeTab === 'course')}>📚 Add Course</button>
            <button onClick={logout} style={{ marginTop: 'auto', ...buttonStyle(false) }}>🚪 Logout</button>
          </>
        )}
      </div>

      {/* Main Content */}
      <main
        className={`ta-dashboard-main${sidebarOpen ? ' sidebar-open' : ''}`}
        style={{
          ...mainStyle,
          marginLeft: 0,
          alignItems: 'stretch',
          justifyContent: 'center',
        }}
      >
        <div className="ta-dashboard-content" style={{
          ...contentStyle,
          background: 'rgba(255,255,255,0.92)', // subtle card background
          boxShadow: '0 8px 32px rgba(60,60,120,0.18)', // slightly stronger shadow
          border: '1.5px solid #e3e6f0', // soft border for contrast
          maxWidth: 'none',
          width: '100%',
          height: '80vh',
          minHeight: '500px',
          margin: 'auto',
          display: 'block',
          padding: '3rem 4rem',
        }}>
          {activeTab === 'home' && (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#3f3d56' }}>
              <h2>Welcome to the TA Dashboard</h2>
            </div>
          )}
          {activeTab === 'profile' && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', color: '#2d3559', height: '100%' }}>
              <h2 style={{ ...sectionHeading, marginTop: 0, marginBottom: '2rem', textAlign: 'left', color: '#3f3d56' }}>Profile</h2>
              <p style={{ fontSize: '1.2rem', margin: '0.5rem 0', color: '#3f3d56' }}><strong>Name:</strong> {user.name}</p>
              <p style={{ fontSize: '1.2rem', margin: '0.5rem 0', color: '#3f3d56' }}><strong>Email:</strong> {user.email}</p>
              <p style={{ fontSize: '1.2rem', margin: '0.5rem 0', color: '#3f3d56' }}>
                <strong>Role:</strong> {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
              </p>
              <div style={{ marginTop: 'auto' }}>
                <button
                  onClick={() => navigate('/change-password')}
                  style={{
                    background: ' #5c5470',
                    // background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                    border: 'none',
                    color: '#fff',
                    fontWeight: 600,
                    fontSize: '1rem',
                    padding: '0.85rem 1.5rem',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    boxShadow: '0 2px 8px rgba(60,60,120,0.12)',
                    transition: 'background 0.2s',
                  }}
                >
                  Change Password
                </button>
              </div>
            </div>
          )}

          {activeTab === 'role' && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', color: '#2d3559' }}>
              <h2 style={{ ...sectionHeading, marginTop: 0, marginBottom: '2rem', textAlign: 'left', color: '#3f3d56' }}>Role Manager</h2>
              <p style={{ color: '#3f3d56' }}>Implement role update functionality here.</p>
            </div>
          )}
          {activeTab === 'course' && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', color: '#2d3559' }}>
              <h2 style={{ ...sectionHeading, marginTop: 0, marginBottom: '2rem', textAlign: 'left', color: '#3f3d56' }}>Add New Course</h2>
              <p style={{ color: '#3f3d56' }}>Implement course creation form here.</p>
            </div>
          )}
        </div>
      </main>

      {/* Responsive styles */}
      <style>
        {`
        html, body, #root {
          height: 100%;
          width: 100%;
          margin: 0;
          padding: 0;
          box-sizing: border-box;
          background: none !important;
          overflow: hidden !important;
        }
        body {
          background: none !important;
        }
        .ta-dashboard-bg {
          min-height: 100vh;
          width: 100vw;
          background: linear-gradient(135deg, #ece9f7 0%, #c3cfe2 100%);
          display: flex;
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          box-sizing: border-box;
          overflow: hidden;
        }
        .ta-dashboard-container {
          display: flex;
          min-height: 100vh;
          width: 100%;
          position: relative;
        }
        .ta-dashboard-sidebar {
          position: relative;
          top: 0;
          left: 0;
          height: auto;
          min-height: 100vh;
          z-index: 1;
        }
        .sidebar-toggle-btn {
          display: none;
        }
        .ta-dashboard-main {
          flex: 1;
          margin-left: 0;
          transition: margin-left 0.3s;
        }
        @media (max-width: 900px) {
          .ta-dashboard-sidebar {
            width: 220px;
            padding: 1.5rem 0.75rem;
          }
          .ta-dashboard-main {
            margin-left: 220px;
            padding: 1rem;
          }
        }
        @media (max-width: 700px) {
          .ta-dashboard-sidebar {
            left: -260px;
            width: 220px;
            border-radius: 0 20px 20px 0;
            box-shadow: 4px 0 12px rgba(0,0,0,0.1);
            transition: left 0.3s;
          }
          .ta-dashboard-sidebar.open {
            left: 0;
          }
          .sidebar-toggle-btn {
            display: block;
            position: fixed;
            top: 1.2rem;
            left: 1.2rem;
            z-index: 1100;
            background: #3f3d56;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 0.8rem;
            cursor: pointer;
          }
          .ta-dashboard-main {
            margin-left: 0;
            padding: 1rem;
            transition: margin-left 0.3s;
          }
          .ta-dashboard-main.sidebar-open {
            /* Optionally add overlay effect or dim background */
          }
        }
        @media (max-width: 600px) {
          .ta-dashboard-content {
            padding: 1rem;
            max-width: 100%;
          }
          .ta-dashboard-sidebar {
            padding: 1rem 0.5rem;
            width: 180px;
          }
        }
      `}
      </style>
    </div>
  );
}


const containerStyle = {
  position: 'fixed',
  top: 0,
  left: 0,
  minHeight: '100vh',
  minWidth: '100vw',
  height: '100vh',
  width: '100vw',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: 'linear-gradient(135deg, #ece9f7 0%, #c3cfe2 100%)',
  padding: '2rem',
  boxSizing: 'border-box',
  zIndex: 0
};

const sidebarStyle = {
  width: '250px',
  // background: '#3f3d56',
  background: 'linear-gradient(90deg, #3f3d56 0%, #5c5470 100%)',
  color: 'white',
  padding: '2rem 1rem',
  borderTopRightRadius: '20px',
  borderBottomRightRadius: '20px',
  boxShadow: '4px 0 12px rgba(0,0,0,0.1)',
  display: 'flex',
  flexDirection: 'column',
  gap: '1.25rem',
  minWidth: 0,
  boxSizing: 'border-box',
  height: '100vh',
  position: 'fixed',
  top: 0,
  left: 0,
  zIndex: 1000,
};

const mainStyle = {
  flex: 1,
  padding: '3rem 2rem',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'flex-start',
  minWidth: 0,
  boxSizing: 'border-box',
  marginLeft: '250px',
  transition: 'margin-left 0.3s',
};

const contentStyle = {
  background: '#ffffff',
  borderRadius: '20px',
  boxShadow: '0 8px 32px rgba(60,60,120,0.12)',
  padding: '2rem',
  width: '100%',
  height: '80vh',
  minHeight: '500px',
  margin: 'auto',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  boxSizing: 'border-box',
};

const sidebarToggleBtnStyle = {
  display: 'none', // will be overridden by CSS media queries
};

function buttonStyle(active) {
  return {
    background: active ? '#4a4e69' : 'transparent',
    color: 'white',
    padding: '0.75rem 1rem',
    textAlign: 'left',
    border: 'none',
    cursor: 'pointer',
    fontWeight: 500,
    borderRadius: '8px',
    transition: 'background 0.2s ease',
    fontSize: '1rem',
    textTransform: 'capitalize',
    width: '100%',
    boxSizing: 'border-box'
  };
}

const sectionHeading = {
  fontSize: '1.8rem',
  fontWeight: 'bold',
  color: '#3f3d56',
  marginBottom: '1.25rem'
};
