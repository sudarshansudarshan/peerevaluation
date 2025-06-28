import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ProfileMenu from '../components/User/ProfileMenu';
import '../styles/Student/StudentDashboard.css';
import EnrolledCoursesSection from '../components/Student/EnrolledCoursesSection';
import EnrollmentRequestSection from '../components/Student/EnrollmentRequestSection';
import StudentExamsTab from '../components/Student/StudentExamsTab';
import { containerStyle, sidebarStyle, mainStyle, contentStyle, sidebarToggleBtnStyle, buttonStyle, sectionHeading } from '../styles/Student/StudentDashboard.js'
import { FaBook, FaClipboardList, FaLaptopCode } from 'react-icons/fa';
import { showMessage } from '../utils/Message';

export default function StudentDashboard() {
  const [activeTab, setActiveTab] = useState('home');
  const [user, setUser] = useState({ name: '', email: '', role: '', isTA: false });
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [taBatchInfo, setTaBatchInfo] = useState(null);
  const [selectedTABatch, setSelectedTABatch] = useState('');
  const [dashboardStats, setDashboardStats] = useState({ courses: 0, pendingEvaluations: 0, activeExams: 0 });
  const [enrolledCourses, setEnrolledCourses] = useState([]);
  const [availableCourses, setAvailableCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [availableBatches, setAvailableBatches] = useState([]);
  const [selectedBatch, setSelectedBatch] = useState('');
  const [studentBatches, setStudentBatches] = useState([]);
  const [selectedBatchForExam, setSelectedBatchForExam] = useState('');
  const [batchExams, setBatchExams] = useState([]);
  const [examFileMap, setExamFileMap] = useState({});
  const fileInputRefs = useRef({});
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

  useEffect(() => {
    const fetchTABatchInfo = async () => {
      const token = localStorage.getItem('token');
      if (!token || !user.isTA) return;
      try {
        const res = await fetch('http://localhost:5000/api/ta/my-batches', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        const data = await res.json();
        if (res.ok && data) {
          // Ensure taBatchInfo is always an array
          setTaBatchInfo(Array.isArray(data) ? data : [data]);
        }
      } catch (error) {
        console.error("Failed to fetch TA batch info:", error);
      }
    };

    fetchTABatchInfo();
  }, [user.isTA]);

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/login');
  };

  useEffect(() => {
    const fetchDashboardStats = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:5000/api/student/dashboard-stats', {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        const data = await response.json();

        if (
          typeof data === 'object' &&
          data !== null &&
          'coursesEnrolled' in data &&
          'pendingEvaluations' in data &&
          'activeExams' in data
        ) {
          setDashboardStats({
            courses: data.coursesEnrolled,
            pendingEvaluations: data.pendingEvaluations,
            activeExams: data.activeExams,
          });
        } else {
          console.error('Invalid dashboard stats response:', data);
          setDashboardStats({ courses: 0, pendingEvaluations: 0, activeExams: 0 });
        }
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error);
        setDashboardStats({ courses: 0, pendingEvaluations: 0, activeExams: 0 });
      }
    };

    fetchDashboardStats();
  }, []);

  // Fetch enrolled courses and available courses on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;
    // Fetch enrolled courses
    fetch('http://localhost:5000/api/student/enrolled-courses', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.json())
      .then(data => setEnrolledCourses(Array.isArray(data) ? data : []))
      .catch(() => setEnrolledCourses([]));
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;
    // Fetch all available courses
    fetch('http://localhost:5000/api/student/available-courses', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.json())
      .then(data => setAvailableCourses(Array.isArray(data) ? data : []))
      .catch(() => setAvailableCourses([]));
  }, []);

  // Fetch batches for selected course
  useEffect(() => {
    if (!selectedCourse) {
      setAvailableBatches([]);
      setSelectedBatch('');
      return;
    }
    const token = localStorage.getItem('token');
    fetch(`http://localhost:5000/api/student/course-batches/${selectedCourse}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.json())
      .then(data => setAvailableBatches(Array.isArray(data) ? data : []))
      .catch(() => setAvailableBatches([]));
  }, [selectedCourse]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;
    // Fetch all batches student is enrolled in
    fetch('http://localhost:5000/api/student/enrolled-batches', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.json())
      .then(data => setStudentBatches(Array.isArray(data) ? data : []))
      .catch(() => setStudentBatches([]));
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;
    // Fetch all exams for the student (optionally filter by batch)
    let url = 'http://localhost:5000/api/student/all-exams';
    if (selectedBatchForExam) url += `?batchId=${selectedBatchForExam}`;
    fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.json())
      .then(data => setBatchExams(Array.isArray(data) ? data : []))
      .catch(() => setBatchExams([]));
  }, [selectedBatchForExam]);

  // Handle enrollment request
  const handleEnrollmentRequest = async (e) => {
    e.preventDefault();
    // console.log('Enrollment request:', selectedCourse, selectedBatch);
    if (!selectedCourse || !selectedBatch) {
      showMessage('Please select both course and batch.');
      return;
    }
    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://localhost:5000/api/student/request-enrollment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ courseId: selectedCourse, batchId: selectedBatch }),
      });
      const data = await response.json();
      if (response.ok) {
        showMessage(data.message, 'success');
      } else {
        showMessage(data.message || 'Failed to send enrollment request.', 'error');
      }
    } catch (error) {
      showMessage('Failed to send enrollment request.', 'error');
    }
    setSelectedCourse('');
    setSelectedBatch('');
  };

  const handleExamFileChange = (examId, file) => {
    setExamFileMap(prev => ({ ...prev, [examId]: file }));
  };

  const handleExamFileUpload = async (examId) => {
    const file = examFileMap[examId];
    if (!file) return;
    const token = localStorage.getItem('token');
    const formData = new FormData();
    formData.append('file', file);
    formData.append('examId', examId);

    try {
      const response = await fetch('http://localhost:5000/api/student/upload-exam-document', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      const data = await response.json();
      if (response.ok) {
        showMessage(data.message, 'success');
      }
      else if (response.status === 409) {
        showMessage(data.message, 'info');
      } else {
        showMessage(data.message || 'Upload failed!', 'error');
      }
    } catch {
      showMessage('Upload failed!', 'error');
    }
    setExamFileMap(prev => ({ ...prev, [examId]: null }));
    if (fileInputRefs.current[examId]) {
      fileInputRefs.current[examId].value = "";
    }
  };

  const handleSidebarToggle = () => setSidebarOpen(open => !open);

  return (
    <div
      className={`student-dashboard-bg${sidebarOpen ? ' sidebar-open' : ''}`}
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
        minWidth: '500px',
        overflowX: 'auto',
        overflowY: 'auto',
        scrollbarWidth: 'thin',
        scrollbarColor: ' #4b3c70 transparent',
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
        className={`student-dashboard-sidebar${sidebarOpen ? ' open' : ' collapsed'}`}
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
        <h2 style={{ fontSize: sidebarOpen ? '1.6rem' : '0', fontWeight: 'bold', marginBottom: sidebarOpen ? '1rem' : '0', overflow: 'hidden', whiteSpace: 'nowrap' }}>Student Panel</h2>
        {sidebarOpen && (
          <>
            <button onClick={() => setActiveTab('home')} style={buttonStyle(activeTab === 'home')}>🏠 Home</button>
            <button onClick={() => setActiveTab('course')} style={buttonStyle(activeTab === 'course')}>📚 Courses & Enrollment</button>
            <button onClick={() => setActiveTab('exam')} style={buttonStyle(activeTab === 'exam')}>📋 Exams</button>
            <button onClick={() => setActiveTab('evaluation')} style={buttonStyle(activeTab === 'evaluation')}>📝 Evaluations</button>
            {user.isTA && (
              <button onClick={() => setActiveTab('ta')} style={buttonStyle(activeTab === 'ta')}>🧑‍🏫 TA Panel</button>
            )}
            <button onClick={logout} style={{ marginTop: 'auto', ...buttonStyle(false) }}>🚪 Logout</button>
          </>
        )}
      </div>

      {/* Main Content */}
      <main
        className={`student-dashboard-main${sidebarOpen ? ' sidebar-open' : ''}`}
        style={{
          ...mainStyle,
          marginLeft: 0,
          alignItems: 'stretch',
          justifyContent: 'center',
        }}
      >
        <div className="student-dashboard-content" style={{
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
          minWidth: '950px',
          overflowX: 'auto',
          scrollbarWidth: 'thin',
          scrollbarColor: ' #4b3c70 transparent',
        }}>
          {activeTab === 'home' && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', color: '#3f3d56' }}>
              <h2 style={{ ...sectionHeading, textAlign: 'center', marginBottom: '2rem' }}>
                Welcome to the Student Dashboard
              </h2>
              <div style={{ display: 'flex', justifyContent: 'space-around', width: '100%' }}>
                {/* Courses Enrolled Card */}
                <div style={{ textAlign: 'center', padding: '1rem', borderRadius: '12px', background: 'linear-gradient(135deg, #667eea, #764ba2)', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', width: '200px', color: '#fff' }}>
                  <FaBook size={40} style={{ marginBottom: '0.5rem' }} />
                  <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Courses Enrolled</h3>
                  <p style={{ fontWeight: 'bold', fontSize: '1.2rem' }}> {dashboardStats.courses} </p>
                </div>
                {/* Pending Evaluations Card */}
                <div style={{ textAlign: 'center', padding: '1rem', borderRadius: '12px', background: 'linear-gradient(135deg, #32cd32, #125e12)', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', width: '230px', color: '#fff' }}>
                  <FaClipboardList size={40} style={{ marginBottom: '0.5rem' }} />
                  <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Pending Evaluations</h3>
                  <p style={{ fontWeight: 'bold', fontSize: '1.2rem' }}> {dashboardStats.pendingEvaluations} </p>
                </div>
                {/* Active Exams Card */}
                <div style={{ textAlign: 'center', padding: '1rem', borderRadius: '12px', background: 'linear-gradient(135deg, #43cea2, #185a9d)', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', width: '200px', color: '#fff' }}>
                  <FaLaptopCode size={40} style={{ marginBottom: '0.5rem' }} />
                  <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Active Exams</h3>
                  <p style={{ fontWeight: 'bold', fontSize: '1.2rem' }}> {dashboardStats.activeExams} </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'profile' && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', color: '#2d3559', height: '100%' }}>
              <h2 style={{ ...sectionHeading, marginTop: 0, marginBottom: '2rem', textAlign: 'left' }}>Profile</h2>
              <p style={{ fontSize: '1.2rem', margin: '0.5rem 0' }}><strong>Name:</strong> {user.name}</p>
              <p style={{ fontSize: '1.2rem', margin: '0.5rem 0' }}><strong>Email:</strong> {user.email}</p>
              <p style={{ fontSize: '1.2rem', margin: '0.5rem 0' }}>
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

          {activeTab === 'course' && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', color: '#2d3559', width: '100%' }}>
              <h2 style={{ ...sectionHeading, marginTop: 0, marginBottom: '2rem', textAlign: 'center', color: ' #4b3c70', width: '100%' }}>
                Courses & Enrollment
              </h2>

              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '1rem',
                justifyContent: 'center',
                width: '100%'
              }}>
                {/* Enrolled Courses Section */}
                <EnrolledCoursesSection enrolledCourses={enrolledCourses} />

                {/* Enrollment Request Section */}
                <EnrollmentRequestSection
                  availableCourses={availableCourses}
                  selectedCourse={selectedCourse}
                  setSelectedCourse={setSelectedCourse}
                  availableBatches={availableBatches}
                  selectedBatch={selectedBatch}
                  setSelectedBatch={setSelectedBatch}
                  handleEnrollmentRequest={handleEnrollmentRequest}
                />
              </div>
            </div>
          )}
          
          {activeTab === 'exam' && (
            <StudentExamsTab
              sectionHeading={sectionHeading}
              studentBatches={studentBatches}
              selectedBatchForExam={selectedBatchForExam}
              setSelectedBatchForExam={setSelectedBatchForExam}
              batchExams={batchExams}
              fileInputRefs={fileInputRefs}
              handleExamFileChange={handleExamFileChange}
              handleExamFileUpload={handleExamFileUpload}
              examFileMap={examFileMap}
            />
          )}

          {activeTab === 'evaluation' && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', color: '#2d3559' }}>
            <h2 style={{ ...sectionHeading, marginTop: 0, marginBottom: '2rem', color: '#3f3d56' }}>Evaluations</h2>
          </div>
          )}

          {activeTab === 'ta' && user.isTA && (
            <div style={{ display: 'flex', flexDirection: 'column', color: '#2d3559', width: '100%' }}>
              <div style={{ alignItems: 'center' }}>
                <h2 style={{ ...sectionHeading, marginTop: 0, marginBottom: '2rem', textAlign: 'center', color: '#3f3d56' }}>TA Panel</h2>
              </div>
              {/* Filter Dropdown */}
              <div style={{ marginBottom: '1rem', alignItems: 'left', width: '100%' }}>
                <label style={{ fontSize: '1rem', fontWeight: 500, textAlign: 'left' }}>Filter by Batch/Course: </label>
                <select
                  value={selectedTABatch || ''}
                  onChange={e => setSelectedTABatch(e.target.value)}
                  style={{
                    minWidth: 180,
                    padding: '0.6rem 1.2rem',
                    borderRadius: '8px',
                    border: '1.5px solid #4b3c70',
                    fontSize: '1rem',
                    background: '#fff',
                    color: '#000',
                    fontWeight: 500,
                    transition: 'background 0.2s',
                    outline: 'none',
                    cursor: 'pointer'
                  }}
                >
                  <option value="">All Batches</option>
                  {taBatchInfo && taBatchInfo.map((assignment, idx) => (
                    <option key={idx} value={assignment.batchId}>
                      {assignment.courseName} - {assignment.batchId}
                    </option>
                  ))}
                </select>
              </div>
              {/* Table */}
              <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px #4b3c70' }}>
                <thead style={{ backgroundColor: '#4b3c70', color: '#ffffff', position: 'sticky', top: 0, zIndex: 1 }}>
                  <tr>
                    <th style={{ padding: '12px', textAlign: 'center' }}>Course Name</th>
                    <th style={{ padding: '12px', textAlign: 'center' }}>Course ID</th>
                    <th style={{ padding: '12px', textAlign: 'center' }}>Batch ID</th>
                    <th style={{ padding: '12px', textAlign: 'center' }}>Instructor</th>
                  </tr>
                </thead>
                <tbody>
                  {taBatchInfo && taBatchInfo.length > 0 ? (
                    (selectedTABatch
                      ? taBatchInfo.filter(a => a.batchId === selectedTABatch)
                      : taBatchInfo
                    ).map((assignment, idx) => (
                      <tr key={idx}>
                        <td style={{ padding: '12px', textAlign: 'center', fontWeight: 500 }}>{assignment.courseName}</td>
                        <td style={{ padding: '12px', textAlign: 'center', fontWeight: 500 }}>{assignment.courseId}</td>
                        <td style={{ padding: '12px', textAlign: 'center', fontWeight: 500 }}>{assignment.batchId}</td>
                        <td style={{ padding: '12px', textAlign: 'center', fontWeight: 500 }}>{assignment.instructorName}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} style={{ textAlign: 'center', padding: '1rem' }}>Loading your assigned TA batch info...</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

        </div>
      </main>
    </div>
  );
}