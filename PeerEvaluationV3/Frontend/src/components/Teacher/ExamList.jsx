import React from 'react';
import { FaEdit, FaDownload, FaUpload, FaPaperPlane, FaTrashAlt, FaCheck } from 'react-icons/fa';

const ExamList = ({ exams, handleEditClick, handleDownloadPDF, handleBulkUploadClick, handleSendEvaluation, handleMarkAsDone, handleDeleteExam }) => {
  return (
    <div style={{ marginTop: '2rem', maxHeight: '350px', border: '1px solid #ddd', borderRadius: '12px' }}>
      <h3 style={{ color: '#3f3d56', fontWeight: 'bold', marginBottom: '1rem' }}>Exams</h3>
      <div style={{ maxHeight: '300px', overflowY: 'auto', overflowX: 'auto', scrollbarWidth: 'thin', scrollbarColor: ' #4b3c70 transparent' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', borderRadius: '12px' }}>
          <thead style={{ backgroundColor: '#4b3c70', color: '#ffffff', position: 'sticky', top: 0, zIndex: 1 }}>
            <tr>
              <th style={{ padding: '12px', textAlign: 'center' }}>Exam Name</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Batch</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Date</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Time</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>No. of questions</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Duration</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Total Marks</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>K</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Total Students</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Solutions</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {exams.length === 0 ? (
                <tr>
                  <td colSpan="11" style={{ padding: '16px', textAlign: 'center', color: '#3f3d56', fontStyle:'italic' }}>
                    No exam scheduled yet.
                  </td>
                </tr>
              ) : (
                exams.map((exam) => (
                  <tr key={exam._id} style={{ borderBottom: '1px solid #ddd' }}>
                    <td style={{ padding: '12px', color: '#3f3d56' }}>{exam.name}</td>
                    <td style={{ padding: '12px', color: '#3f3d56' }}>{exam.batch}</td>
                    <td style={{ padding: '12px', color: '#3f3d56' }}>
                      {new Date(exam.date).toLocaleDateString('en-IN', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                      })}
                    </td>
                    <td style={{ padding: '12px', color: '#3f3d56' }}>{exam.time}</td>
                    <td style={{ padding: '12px', color: '#3f3d56' }}>{exam.number_of_questions}</td>
                    <td style={{ padding: '12px', color: '#3f3d56' }}>{exam.duration} mins</td>
                    <td style={{ padding: '12px', color: '#3f3d56' }}>{exam.totalMarks}</td>
                    <td style={{ padding: '12px', color: '#3f3d56' }}>{exam.k}</td>
                    <td style={{ padding: '12px', color: '#3f3d56' }}>{exam.total_students}</td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      {typeof exam.solutions === 'string' && exam.solutions.trim() !== '' ? (
                        <a href={`http://localhost:5000/${exam.solutions}`} target="_blank" rel="noopener noreferrer">
                          View Solutions
                        </a>
                      ) : (
                        'No Solutions Available'
                      )}
                    </td>
                    <td style={{ padding: '12px', overflowX: 'auto' }}>
                      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                        <button
                          onClick={() => handleEditClick(exam)}
                          style={{
                            // padding: '0.5rem 1rem',
                            borderRadius: '8px',
                            color: '#ffffff',
                            background: 'none',
                            border: ' #006400 1px solid',
                            fontSize: '0.6rem',
                            fontWeight: 'bold',
                            cursor: 'pointer',
                          }}
                          title="Edit Exam"
                        >
                          <FaEdit style={{ color: ' #006400', fontSize: '1.2rem' }} />
                        </button>

                        <button
                          onClick={() => handleDownloadPDF(exam._id)} // Pass examId when clicking the button
                          style={{
                            // padding: '0.5rem 1rem',
                            borderRadius: '8px',
                            color: '#ffffff',
                            background: 'none',
                            border: ' #00008b 1px solid', // Indigo shade
                            fontSize: '0.6rem',
                            fontWeight: 'bold',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                          }}
                          title="Download PDF"
                        >
                          <FaDownload style={{ color: ' #00008b', fontSize: '1.2rem' }} /> {/* Indigo shade */}
                        </button>
                        
                        <button
                          onClick={() => handleBulkUploadClick(exam._id)} // Pass examId when clicking the button
                          style={{
                            // padding: '0.5rem 1rem',
                            borderRadius: '8px',
                            color: '#ffffff',
                            background: 'none',
                            border: ' #6a0dad 1px solid',
                            fontSize: '0.6rem',
                            fontWeight: 'bold',
                            cursor: 'pointer',
                          }}
                          title="Bulk Upload"
                        >
                          <FaUpload style={{ color: ' #6a0dad', fontSize: '1.2rem' }} />
                        </button>
                        <button
                          onClick={() => handleSendEvaluation(exam._id)}
                          style={{
                            // padding: '0.5rem 1rem',
                            borderRadius: '8px',
                            color: '#ffffff',
                            background: 'none',
                            border: ' #007bff 1px solid',
                            fontSize: '0.6rem',
                            fontWeight: 'bold',
                            cursor: 'pointer',
                          }}
                          title="Send Evaluation"
                        >
                          <FaPaperPlane style={{ color: ' #007bff', fontSize: '1.2rem' }} />
                        </button>

                        <button
                          onClick={() => handleMarkAsDone(exam._id)}
                          style={{
                            // padding: '0.5rem 1rem',
                            borderRadius: '8px',
                            color: '#ffffff',
                            background: 'none',
                            border: ' #28a745 1px solid',
                            fontSize: '0.6rem',
                            fontWeight: 'bold',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                          title="Mark as Done"
                        >
                          <FaCheck style={{ color: ' #28a745', fontSize: '1.2rem' }} />
                        </button>

                        <button
                          onClick={() => handleDeleteExam(exam._id)}
                          style={{
                            // padding: '0.5rem 1rem',
                            borderRadius: '8px',
                            color: '#ffffff',
                            background: 'none',
                            border: '#c0392b 1px solid',
                            fontSize: '0.6rem',
                            fontWeight: 'bold',
                            cursor: 'pointer',
                          }}
                          title="Delete Exam"
                        >
                          <FaTrashAlt style={{ color: ' #c0392b', fontSize: '1.2rem' }} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ExamList;