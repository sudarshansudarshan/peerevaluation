import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaChalkboardTeacher, FaBook, FaUserGraduate } from 'react-icons/fa';
import '../styles/Admin/AdminDashboard.css'; // Assuming you have a CSS file for styles
import { containerStyle, sidebarStyle, mainStyle, contentStyle, sectionHeading, buttonStyle } from '../styles/Admin/AdminDashboardStyles'; // Import styles
import { showMessage } from '../utils/Message'; // Assuming you have a utility for showing messages
import { AppContext } from '../utils/AppContext';
import { useContext } from 'react';
import ProfileMenu from '../components/User/ProfileMenu'; // Assuming you have a ProfileMenu component

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('home');
  const [user, setUser] = useState({ name: '', email: '', role: '' });
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const [instructors, setInstructors] = useState([]);
  const [courses, setCourses] = useState([]); // New state for courses
  const [courseDetails, setCourseDetails] = useState({
      courseId: '',
      courseName: '',
      openCourse: false,
      startDate: '',
      endDate: ''
  });
  const [batchDetails, setBatchDetails] = useState({
    batchId: '',
    instructor: '',
    course: '' // Updated batchDetails state to include course field
});
  const [counts, setCounts] = useState({ teachers: 0, courses: 0, students: 0 });
  const { setRefreshApp } = useContext(AppContext);
  const [courseId, setCourseId] = useState('');
  const [selectedBatchId, setSelectedBatchId] = useState('');
  const [batches, setBatches] = useState([]);



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

  // Responsive sidebar toggle for mobile
  const handleSidebarToggle = () => setSidebarOpen(open => !open);

  // Added functionality to handle the role update request.
  const handleRoleUpdate = async (event) => {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const role = document.getElementById('role').value;

    if (!email || !role) {
      showMessage('Please provide both email and role.', 'error');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/admin/update-role', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ email, role }),
      });

      const data = await response.json();

      if (response.ok) {
        showMessage('Role updated successfully!', 'success');
        // Optionally, you can reset the form fields after successful update
        document.getElementById('email').value = '';
        document.getElementById('role').value = '';
        setTimeout(() => setRefreshApp(true), 1000); // Adds a 1-second delay before refreshing the app
      } else {
        showMessage(`Error! ${data.message || 'Failed to update role.'}`, 'error');
      }
    } catch (error) {
      showMessage('An error occurred while updating the role.', 'error');
      console.error(error);
    }
  };

useEffect(() => {
  const fetchInstructors = async () => {
      try {
          const token = localStorage.getItem('token');
          const response = await fetch('http://localhost:5000/api/admin/teachers', {
            method: 'GET',
              headers: {
                  Authorization: `Bearer ${token}`,
              },
          });
          const data = await response.json();
          setInstructors(data);
      } catch (error) {
          console.error('Failed to fetch instructors:', error);
      }
  };

  fetchInstructors();
}, []);

useEffect(() => {
  const fetchCourses = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/admin/courses', {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await response.json();
      // Map backend fields to expected frontend fields
      const mappedCourses = Array.isArray(data)
        ? data.map(course => ({
            id: course._id || course.id,
            courseId: course.courseId,
            name: course.courseName || course.name,
          }))
        : [];
      setCourses(mappedCourses);
    } catch (error) {
      console.error('Failed to fetch courses:', error);
    }
  };

  fetchCourses();
}, []);

useEffect(() => {
  const fetchBatches = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/admin/batches', {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await response.json();
      if (response.ok) {
        setBatches(data);
      } else {
        console.error('Failed to fetch batches:', data.message);
      }
    } catch (error) {
      console.error('Error fetching batches:', error);
    }
  };

  fetchBatches();
}, []);


const handleCourseSubmit = async (event) => {
  event.preventDefault();

  // Prepare the course data to send (ensure correct field names)
  const courseData = {
    courseId: courseDetails.courseId,
    courseName: courseDetails.courseName,
    openCourse: courseDetails.openCourse,
    startDate: courseDetails.startDate,
    endDate: courseDetails.endDate,
  };

  try {
    const token = localStorage.getItem('token');
    const response = await fetch('http://localhost:5000/api/admin/add-course', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(courseData),
    });

    if (response.ok) {
      showMessage('Course added successfully!', 'success');
      setCourseDetails({
        courseId: '',
        courseName: '',
        openCourse: false,
        startDate: '',
        endDate: ''
      });
      setTimeout(() => setRefreshApp(true), 500); // Adds a 500ms delay before refreshing the app
    } else {
      const data = await response.json();
      showMessage(`Error: ${data.message || 'Failed to add course.'}`, 'error');
    }
  } catch (error) {
    showMessage('An error occurred while adding the course.', 'error');
    console.error(error);
  }
};

const handleCourseDelete = async (event) => {
  event.preventDefault();
  // console.log('Selected courseId:', courseId); // Debugging
  const courseData = {
    courseId: courseId,
  };

  if (!courseData.courseId) {
    showMessage('Please select a course to delete.', 'error');
    return;
  }

  try {
    const token = localStorage.getItem('token');
    const response = await fetch(`http://localhost:5000/api/admin/delete-course/${courseData.courseId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      showMessage(data.message, 'success');
      setCourses(courses.filter(course => course.id !== courseData.courseId));
    } else {
      const data = await response.json();
      showMessage(`Error: ${data.message || 'Failed to delete course.'}`, 'error');
    }
  } catch (error) {
    showMessage('An error occurred while deleting the course.', 'error');
    // console.error(error);
  }
};

const handleBatchSubmit = async (event) => {
  event.preventDefault();

  // Prepare the batch data to send (ensure correct field names)
  const batchData = {
    batchId: batchDetails.batchId,
    instructor: batchDetails.instructor,
    course: batchDetails.course,
  };

  try {
    const token = localStorage.getItem('token');
    const response = await fetch('http://localhost:5000/api/admin/add-batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(batchData),
    });

    if (response.ok) {
      showMessage('Batch added successfully!', 'success');
      setBatchDetails({
        batchId: '',
        instructor: '',
        course: '' // Reset course field
      });
      setTimeout(() => setRefreshApp(true), 500); // Adds a 500ms delay before refreshing the app
    } else {
      const data = await response.json();
      showMessage(`Error! ${data.message || 'Failed to add batch.'}`, 'error');
    }
  } catch (error) {
    showMessage('An error occurred while adding the batch.', 'error');
    console.error(error);
  }
};

const handleBatchDelete = async () => {
  // console.log('Selected batchId:', selectedBatchId); // Debugging
  if (!selectedBatchId) {
    showMessage('Please select a batch to delete.', 'error');
    return;
  }

  try {
    const token = localStorage.getItem('token');
    const response = await fetch(`http://localhost:5000/api/admin/delete-batch/${selectedBatchId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();
    if (response.ok) {
      showMessage(data.message, 'success');
      setBatches(batches.filter(batch => batch._id !== selectedBatchId));
      setSelectedBatchId('');
    } else {
      showMessage(data.message || 'Failed to delete batch.', 'error');
    }
  } catch (error) {
    showMessage('An error occurred while deleting the batch.', 'error');
  }
};


useEffect(() => {
  const fetchCounts = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/admin/dashboard-counts', {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setCounts(data);
    } catch (error) {
      console.error('Error fetching dashboard counts:', error);
    }
  };
  if (activeTab === 'home') {
      fetchCounts();
    }
}, [activeTab]);


  return (
    <div
      className={`admin-dashboard-bg${sidebarOpen ? ' sidebar-open' : ''}`}
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
        className={`admin-dashboard-sidebar${sidebarOpen ? ' open' : ' collapsed'}`}
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
        <h2 style={{ fontSize: sidebarOpen ? '1.6rem' : '0', fontWeight: 'bold', marginBottom: sidebarOpen ? '1rem' : '0', overflow: 'hidden', whiteSpace: 'nowrap' }}>Admin Panel</h2>
        {sidebarOpen && (
          <>
            <button onClick={() => setActiveTab('home')} style={buttonStyle(activeTab === 'home')}>🏠 Home</button>
            <button onClick={() => setActiveTab('role')} style={buttonStyle(activeTab === 'role')}>🧑‍💼 Role Manager</button>
            <button onClick={() => setActiveTab('course')} style={buttonStyle(activeTab === 'course')}>📚 Course Manager</button>
            <button onClick={() => setActiveTab('batch')} style={buttonStyle(activeTab === 'batch')}>📘 Batch Manager</button>
            <button onClick={logout} style={{ marginTop: 'auto', ...buttonStyle(false) }}>🚪 Logout</button>
          </>
        )}
      </div>

      {/* Main Content */}
      <main
        className={`admin-dashboard-main${sidebarOpen ? ' sidebar-open' : ''}`}
        style={{
          ...mainStyle,
          marginLeft: 0,
          alignItems: 'stretch',
          justifyContent: 'center',
        }}
      >
        <div className="admin-dashboard-content" style={{
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
              <h2 style={{ ...sectionHeading, marginBottom: '2rem' }}>Welcome to the Admin Dashboard</h2>
              <div style={{ display: 'flex', justifyContent: 'space-around', width: '100%' }}>
                <div style={{ textAlign: 'center', padding: '1rem', borderRadius: '12px', background: 'linear-gradient(135deg, #667eea, #764ba2)', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', width: '200px', color: '#fff' }}>
                  <FaChalkboardTeacher size={40} style={{ marginBottom: '0.5rem' }} />
                  <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Teachers</h3>
                  <p style={{ fontSize: '1.2rem' }}>{counts.teachers}</p>
                </div>
                <div style={{ textAlign: 'center', padding: '1rem', borderRadius: '12px', background: 'linear-gradient(135deg, #32cd32, #125e12)', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', width: '200px', color: '#fff' }}>
                  <FaBook size={40} style={{ marginBottom: '0.5rem' }} />
                  <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Courses</h3>
                  <p style={{ fontSize: '1.2rem' }}>{counts.courses}</p>
                </div>
                <div style={{ textAlign: 'center', padding: '1rem', borderRadius: '12px', background: 'linear-gradient(135deg, #43cea2, #185a9d)', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', width: '200px', color: '#fff' }}>
                  <FaUserGraduate size={40} style={{ marginBottom: '0.5rem' }} />
                  <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Students</h3>
                  <p style={{ fontSize: '1.2rem' }}>{counts.students}</p>
                </div>
              </div>
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
            <div style={{ display: 'flex', flexDirection: 'column', color: '#2d3559' }}>
              <h2 style={{ ...sectionHeading, marginTop: 0, marginBottom: '2rem', textAlign: 'center', color: '#3f3d56' }}>Role Manager</h2>
              <p style={{textAlign: 'left', color: '#3f3d56' }}>Update the role of a user by providing their email ID and selecting a role.</p>
              <form onSubmit={handleRoleUpdate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', width: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '100%' }}>
                  <label style={{ color: '#3f3d56', fontWeight: 'bold', whiteSpace: 'nowrap', width: '150px', textAlign: 'left' }} htmlFor="email">Email ID</label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    placeholder="Enter user email ID"
                    style={{
                      padding: '0.5rem',
                      borderRadius: '12px',
                      border: '1px solid  #5c5470',
                      fontSize: '1rem',
                      width: '300px', // Reduced width
                      boxSizing: 'border-box',
                      background: '#ffffff',
                      color: ' #4b3c70', // Ensured text color is black
                    }}
                  />
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '100%' }}>
                  <label style={{ color: '#3f3d56', fontWeight: 'bold', whiteSpace: 'nowrap', width: '150px', textAlign: 'left' }} htmlFor="role">Select Role</label>
                  <select
                    id="role"
                    name="role"
                    style={{
                      padding: '0.5rem',
                      borderRadius: '12px',
                      border: '1px solid #5c5470',
                      fontSize: '1rem',
                      width: '300px', // Reduced width
                      boxSizing: 'border-box',
                      background: '#ffffff',
                      color: ' #4b3c70', // Ensured text color is black
                    }}
                  >
                    <option value="admin">Admin</option>
                    <option value="teacher">Teacher</option>
                    <option value="student">Student</option>
                  </select>
                </div>

                <div style={{ display: 'flex', width: '100%', marginLeft: '150px' }}>
                  <button
                    type="submit"
                    style={{
                      background: '#5c5470',
                      border: 'none',
                      color: '#fff',
                      fontWeight: 600,
                      fontSize: '1rem',
                      padding: '0.5rem 1rem',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      boxShadow: '0 2px 8px rgba(60,60,120,0.12)',
                      transition: 'background 0.2s',
                    }}
                  >
                    Update Role
                  </button>
                </div>
              </form>
            </div>
          )}
          
          {/* Add a Delete Course section aligned to the right */}
          {activeTab === 'course' && (
            <div className="course-manager" style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
              <div className="add-course" style={{ width: '48%' }}>
                <h2 style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '2rem', textAlign: 'left', color: '#3f3d56' }}>Add New Course</h2>
                <form onSubmit={handleCourseSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', width: '100%' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '100%' }}>
                        <label style={{ color: '#3f3d56', fontWeight: 'bold', whiteSpace: 'nowrap', width: '150px' }} htmlFor="courseId">Course ID</label>
                        <input
                            type="text"
                            id="courseId"
                            name="courseId"
                            placeholder="Enter course ID"
                            value={courseDetails.courseId}
                            onChange={(e) => setCourseDetails({ ...courseDetails, courseId: e.target.value })}
                            style={{
                                padding: '0.5rem',
                                borderRadius: '12px',
                                border: '1px solid  #5c5470',
                                fontSize: '1rem',
                                width: '300px',
                                boxSizing: 'border-box',
                                background: '#ffffff',
                                color: ' #4b3c70',
                            }}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '100%' }}>
                        <label style={{ color: '#3f3d56', fontWeight: 'bold', whiteSpace: 'nowrap', width: '150px' }} htmlFor="courseName">Course Name</label>
                        <input
                            type="text"
                            id="courseName"
                            name="courseName"
                            placeholder="Enter course name"
                            value={courseDetails.courseName}
                            onChange={(e) => setCourseDetails({ ...courseDetails, courseName: e.target.value })}
                            style={{
                                padding: '0.5rem',
                                borderRadius: '12px',
                                border: '1px solid  #5c5470',
                                fontSize: '1rem',
                                width: '300px',
                                boxSizing: 'border-box',
                                background: '#ffffff',
                                color: ' #4b3c70',
                            }}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '100%' }}>
                        <label style={{ color: '#3f3d56', fontWeight: 'bold', whiteSpace: 'nowrap', width: '150px' }} htmlFor="openCourse">Open Course</label>
                        <input
                            type="checkbox"
                            id="openCourse"
                            name="openCourse"
                            checked={courseDetails.openCourse || false}
                            onChange={(e) => setCourseDetails({ ...courseDetails, openCourse: e.target.checked })}
                            style={{
                                width: '20px',
                                height: '20px',
                                cursor: 'pointer',
                                background: '#f0f0f0',
                                border: '1px solid #5c5470',
                                borderRadius: '4px',
                            }}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '100%' }}>
                        <label style={{ color: '#3f3d56', fontWeight: 'bold', whiteSpace: 'nowrap', width: '150px' }} htmlFor="startDate">Course Start Date</label>
                        <input
                            type="date"
                            id="startDate"
                            name="startDate"
                            value={courseDetails.startDate || ''}
                            onChange={(e) => setCourseDetails({ ...courseDetails, startDate: e.target.value })}
                            style={{
                                padding: '0.5rem',
                                borderRadius: '12px',
                                border: '1px solid  #5c5470',
                                fontSize: '1rem',
                                width: '300px',
                                boxSizing: 'border-box',
                                background: '#ffffff',
                                color: ' #4b3c70',
                                position: 'relative',
                                zIndex: 9999,
                            }}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '100%' }}>
                        <label style={{ color: '#3f3d56', fontWeight: 'bold', whiteSpace: 'nowrap', width: '150px' }} htmlFor="endDate">Course End Date</label>
                        <input
                            type="date"
                            id="endDate"
                            name="endDate"
                            value={courseDetails.endDate || ''}
                            onChange={(e) => setCourseDetails({ ...courseDetails, endDate: e.target.value })}
                            style={{
                                padding: '0.5rem',
                                borderRadius: '12px',
                                border: '1px solid  #5c5470',
                                fontSize: '1rem',
                                width: '300px',
                                boxSizing: 'border-box',
                                background: '#ffffff',
                                color: ' #4b3c70',
                                position: 'relative',
                                zIndex: 9999,
                            }}
                        />
                    </div>

                    <div style={{ display: 'flex', width: '100%', marginLeft: '150px' }}>
                        <button
                            type="submit"
                            style={{
                                background: '#5c5470',
                                border: 'none',
                                color: '#fff',
                                fontWeight: 600,
                                fontSize: '1rem',
                                padding: '0.5rem 1rem',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                boxShadow: '0 2px 8px rgba(60,60,120,0.12)',
                                transition: 'background 0.2s',
                            }}
                        >
                            Add Course
                        </button>
                    </div>
                </form>
              </div>

              <div className="delete-course" style={{ width: '48%', textAlign: 'right' }}>
                <h2 style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '2rem', textAlign: 'right', color: '#3f3d56' }}>Delete Course</h2>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '1rem', width: '100%' }}>
                  <select
                    value={courseId}
                    onChange={(e) => setCourseId(e.target.value)}
                    style={{
                      padding: '0.5rem',
                      borderRadius: '12px',
                      border: '1px solid #5c5470',
                      fontSize: '1rem',
                      width: '300px',
                      boxSizing: 'border-box',
                      background: '#ffffff',
                      color: ' #4b3c70',
                    }}
                  >
                    <option value="">Select Course</option>
                    {courses.map((course) => (
                      <option key={course.id} value={course.id}>
                        {course.courseId} - {course.name}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={handleCourseDelete}
                    style={{
                      background: '#5c5470',
                      border: 'none',
                      color: '#fff',
                      fontWeight: 600,
                      fontSize: '1rem',
                      padding: '0.5rem 1rem',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      boxShadow: '0 2px 8px rgba(60,60,120,0.12)',
                      transition: 'background 0.2s',
                    }}
                  >
                    Delete Course
                  </button>
                </div>
              </div>
            </div>
        )}


        {activeTab === 'batch' && (
          <div className="batch-manager" style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
            
            {/* Add Batch Section */}
            <div className="add-batch" style={{ width: '48%' }}>
              <h2 style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '2rem', textAlign: 'left', color: '#3f3d56' }}>Add New Batch</h2>
              <form onSubmit={handleBatchSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', width: '100%' }}>
                
                {/* Batch ID */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '100%' }}>
                  <label style={{ color: '#3f3d56', fontWeight: 'bold', whiteSpace: 'nowrap', width: '150px' }} htmlFor="batchId">Batch ID</label>
                  <input
                    type="text"
                    id="batchId"
                    name="batchId"
                    placeholder="Enter batch ID"
                    value={batchDetails.batchId}
                    onChange={(e) => setBatchDetails({ ...batchDetails, batchId: e.target.value })}
                    style={{
                      padding: '0.5rem',
                      borderRadius: '12px',
                      border: '1px solid  #5c5470',
                      fontSize: '1rem',
                      width: '282px',
                      background: '#ffffff',
                      color: ' #4b3c70',
                    }}
                  />
                </div>

                {/* Instructor */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '100%' }}>
                  <label style={{ color: '#3f3d56', fontWeight: 'bold', whiteSpace: 'nowrap', width: '150px' }} htmlFor="instructor">Instructor</label>
                  <select
                    id="instructor"
                    name="instructor"
                    value={batchDetails.instructor}
                    onChange={(e) => setBatchDetails({ ...batchDetails, instructor: e.target.value })}
                    style={{
                      padding: '0.5rem',
                      borderRadius: '12px',
                      border: '1px solid #5c5470',
                      fontSize: '1rem',
                      width: '300px',
                      background: '#ffffff',
                      color: ' #4b3c70',
                    }}
                  >
                    <option value="">Select Instructor</option>
                    {instructors.map((instructor) => (
                      <option key={instructor.id} value={instructor.id}>{instructor.name}</option>
                    ))}
                  </select>
                </div>

                {/* Course */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '100%' }}>
                  <label style={{ color: '#3f3d56', fontWeight: 'bold', whiteSpace: 'nowrap', width: '150px' }} htmlFor="course">Course</label>
                  <select
                    id="course"
                    name="course"
                    value={batchDetails.course}
                    onChange={(e) => setBatchDetails({ ...batchDetails, course: e.target.value })}
                    style={{
                      padding: '0.5rem',
                      borderRadius: '12px',
                      border: '1px solid #5c5470',
                      fontSize: '1rem',
                      width: '300px',
                      background: '#ffffff',
                      color: ' #4b3c70',
                    }}
                  >
                    <option value="">Select Course</option>
                    {courses.map((course) => (
                      <option key={course.id} value={course.id}> {course.courseId} - {course.name}</option>
                    ))}
                  </select>
                </div>

                {/* Submit Button */}
                <div style={{ display: 'flex', width: '100%', marginLeft: '150px' }}>
                  <button
                    type="submit"
                    style={{
                      background: '#5c5470',
                      border: 'none',
                      color: '#fff',
                      fontWeight: 600,
                      fontSize: '1rem',
                      padding: '0.5rem 1rem',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      boxShadow: '0 2px 8px rgba(60,60,120,0.12)',
                      transition: 'background 0.2s',
                    }}
                  >
                    Add Batch
                  </button>
                </div>
              </form>
            </div>

            {/* Delete Batch Section */}
            <div className="delete-batch" style={{ width: '48%', textAlign: 'right' }}>
              <h2 style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '2rem', textAlign: 'right', color: '#3f3d56' }}>Delete Batch</h2>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '1rem', width: '100%' }}>
                <select
                  value={selectedBatchId}
                  onChange={(e) => setSelectedBatchId(e.target.value)}
                  style={{
                    padding: '0.5rem',
                    borderRadius: '12px',
                    border: '1px solid #5c5470',
                    fontSize: '1rem',
                    width: '300px',
                    background: '#ffffff',
                    color: ' #4b3c70',
                  }}
                >
                  <option value="">Select Batch</option>
                  {batches.map((batch) => (
                    <option key={batch._id} value={batch._id}>
                      {batch.batchId} - {batch.course.courseName} ({batch.instructor.name})
                    </option>
                  ))}
                </select>
                <button
                  onClick={handleBatchDelete}
                  style={{
                    background: '#5c5470',
                    border: 'none',
                    color: '#fff',
                    fontWeight: 600,
                    fontSize: '1rem',
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    boxShadow: '0 2px 8px rgba(60,60,120,0.12)',
                    transition: 'background 0.2s',
                  }}
                >
                  Delete Batch
                </button>
              </div>
            </div>

          </div>
        )}

        </div>
      </main>
    </div>
  );
}
