import React, { useState } from "react";
import { FaTimes } from "react-icons/fa";

const PeerResultOverlay = ({ 
  isPeerResultOverlayOpen, 
  closePeerResultOverlay, 
  selectedExamForPeerResult, 
  peerResultsForExam 
}) => {
  const [ticketModal, setTicketModal] = useState(false);
  const [selectedEvaluation, setSelectedEvaluation] = useState(null);
  const [ticketData, setTicketData] = useState({
    reason: '',
    description: '',
    priority: 'medium'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isPeerResultOverlayOpen) return null;

  const calculateAverageScore = () => {
    const completedEvaluations = peerResultsForExam.filter(
      result => result.eval_status === 'completed'
    );
    
    if (completedEvaluations.length === 0) return 0;
    
    const totalScore = completedEvaluations.reduce((sum, result) => {
      const score = Array.isArray(result.score) 
        ? result.score.reduce((scoreSum, current) => scoreSum + current, 0)
        : result.score || 0;
      return sum + score;
    }, 0);
    
    return (totalScore / completedEvaluations.length).toFixed(2);
  };

  const handleRaiseTicket = (evaluation) => {
    setSelectedEvaluation(evaluation);
    setTicketModal(true);
    setTicketData({ reason: '', description: '', priority: 'medium' });
  };

  const submitTicket = async () => {
    if (!ticketData.reason.trim() || !ticketData.description.trim()) {
      alert('Please fill in all required fields');
      return;
    }

    setIsSubmitting(true);

    try {
      const ticketPayload = {
        evaluationId: selectedEvaluation.id,
        evaluatorName: selectedEvaluation.student.name,
        examId: selectedExamForPeerResult.id,
        examName: selectedExamForPeerResult.name,
        reason: ticketData.reason,
        description: ticketData.description,
        priority: ticketData.priority,
        status: 'open',
        createdAt: new Date().toISOString(),
        evaluationScore: Array.isArray(selectedEvaluation.score) 
          ? selectedEvaluation.score.reduce((sum, current) => sum + current, 0)
          : selectedEvaluation.score || 0,
        feedback: Array.isArray(selectedEvaluation.feedback)
          ? selectedEvaluation.feedback.join(", ")
          : selectedEvaluation.feedback || ""
      };

      // API call to submit ticket
      const response = await fetch('/api/tickets/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(ticketPayload)
      });

      if (response.ok) {
        alert('Ticket raised successfully! You will be notified once it is reviewed.');
        setTicketModal(false);
        setSelectedEvaluation(null);
        setTicketData({ reason: '', description: '', priority: 'medium' });
      } else {
        const errorData = await response.json();
        alert(`Error raising ticket: ${errorData.message || 'Please try again later'}`);
      }
    } catch (error) {
      console.error('Error submitting ticket:', error);
      alert('Network error. Please check your connection and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const closeTicketModal = () => {
    setTicketModal(false);
    setSelectedEvaluation(null);
    setTicketData({ reason: '', description: '', priority: 'medium' });
  };

  return (
    <div
      onClick={closePeerResultOverlay}
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        background: "rgba(0, 0, 0, 0.5)",
        color: "#4b3c70",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 1001,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: "#fff",
          padding: "2rem",
          borderRadius: "8px",
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.2)",
          width: "90%",
          maxWidth: "1200px",
          height: "90%",
          display: "flex",
          flexDirection: "column",
          gap: "2rem",
          position: "relative",
        }}
      >
        {/* Close Button */}
        <button
          onClick={closePeerResultOverlay}
          style={{
            position: "absolute",
            top: "0.5rem",
            right: "0.5rem",
            padding: "0.5rem 1rem",
            borderRadius: "8px",
            border: "none",
            background: "#fc1717",
            color: "#fff",
            fontWeight: 200,
            cursor: "pointer",
            transition: "background 0.2s",
          }}
        >
          <FaTimes style={{ fontSize: "1rem" }} />
        </button>

        {/* Header Section */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            marginTop: "2rem",
            marginBottom: "1rem",
          }}
        >
          <h2 style={{ textAlign: "center", flex: 1, margin: 0 }}>
            Results - {selectedExamForPeerResult?.name}
          </h2>
        </div>

        {/* Content Section */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            height: "90%",
            width: "100%",
            position: "relative",
          }}
        >
          {/* Table Container with Scroll */}
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              paddingRight: "0.5rem",
              border: "1px solid #e0e0e0",
              borderRadius: "8px",
            }}
          >
            <table style={{
              width: "100%",
              minWidth: "800px",
              borderCollapse: "collapse",
              background: "#fff",
              fontSize: "0.9rem",
              tableLayout: "auto",
            }}>
              <thead style={{
                backgroundColor: "#4b3c70",
                color: "#ffffff",
                position: "sticky",
                top: 0,
                zIndex: 2,
              }}>
                <tr>
                  <th style={{ ...thCellStyle }}>
                    Student
                  </th>
                  <th style={{ ...thCellStyle }}>
                    Question-wise Score
                  </th>
                  <th style={{ ...thCellStyle }}>
                    Feedback
                  </th>
                  <th style={{ ...thCellStyle }}>
                    Status
                  </th>
                  <th style={{ ...thCellStyle }}>
                    Total Score
                  </th>
                  <th style={{ ...thCellStyle }}>
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {peerResultsForExam.length === 0 ? (
                  <tr>
                    <td colSpan="4" style={{
                      padding: "20px 12px",
                      textAlign: "center",
                      fontWeight: 500,
                      color: "gray",
                      fontSize: "1rem",
                    }}>
                      No peer results found for this exam.
                    </td>
                  </tr>
                ) : (
                  peerResultsForExam.map((result, idx) => (
                    <tr 
                      key={idx}
                      style={{
                        borderBottom: "1px solid #e0e0e0",
                        "&:hover": {
                          backgroundColor: "#f8f9fa"
                        }
                      }}
                    >
                      <td style={{ ...tdCellStyle }}>
                        {result.student.name || 'Unknown'}
                      </td>
                      <td style={{ ...tdCellStyle }}>
                        {Array.isArray(result.score) 
                          ? result.score.join(", ")
                          : result.score || "No scores"}
                      </td>
                      <td style={{ ...tdCellStyle, maxWidth: "300px", wordWrap: "break-word" }}>
                        {Array.isArray(result.feedback)
                          ? result.feedback.join(", ")
                          : result.feedback || "No feedback"}
                      </td>
                      <td style={{ ...tdCellStyle }}>
                        <span style={{
                          padding: "0.3rem 0.8rem",
                          borderRadius: "15px",
                          fontSize: "0.8rem",
                          fontWeight: 600,
                          backgroundColor: (result.eval_status === 'completed') ? '#d4edda' : '#f8d7da',
                          color: (result.eval_status === 'completed') ? ' #155724' : ' #721c24',
                        }}>
                          {(result.eval_status || 'pending').charAt(0).toUpperCase() + (result.eval_status || 'pending').slice(1)}
                        </span>
                      </td>
                      <td style={{ ...tdCellStyle }}>
                        {Array.isArray(result.score) 
                          ? result.score.reduce((sum, current) => sum + current, 0)
                          : result.score || 0}
                      </td>
                      <td style={{ ...tdCellStyle }}>
                        <button
                          style={{
                            padding: "0.5rem 1rem",
                            backgroundColor: "#ff6b6b",
                            color: "white",
                            border: "none",
                            borderRadius: "5px",
                            cursor: "pointer",
                            fontSize: "0.8rem",
                            fontWeight: "600",
                            transition: "background-color 0.2s",
                          }}
                          onMouseOver={(e) => e.target.style.backgroundColor = "#ff5252"}
                          onMouseOut={(e) => e.target.style.backgroundColor = "#ff6b6b"}
                          onClick={() => {
                            handleRaiseTicket(result);
                          }}
                        >
                          Raise Ticket
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Footer Section */}
          <div
            style={{
              padding: "1rem",
              marginBottom: "1rem",
              borderTop: "1px solid #ddd",
              background: "#fff",
              position: "relative",
              bottom: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              zIndex: 1,
            }}
          >
            <div style={{ flex: 1, textAlign: "left" }}>
              <label style={{ fontWeight: "bold", color: "#4b3c70" }}>
                Total Evaluations: {peerResultsForExam.length}
              </label>
            </div>

            <div style={{ flex: 1, textAlign: "center" }}>
              <label style={{ fontWeight: "bold", color: "#4b3c70" }}>
                Maximum Marks: {selectedExamForPeerResult?.totalMarks}
              </label>
            </div>

            <div style={{ flex: 1, textAlign: "right" }}>
              <label style={{ fontWeight: "bold", color: "#4b3c70" }}>
                Total Avg. Scored Marks: {calculateAverageScore()}
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Ticket Modal */}
      {ticketModal && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100vw",
            height: "100vh",
            background: "rgba(0, 0, 0, 0.7)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 1002,
          }}
          onClick={closeTicketModal}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "#fff",
              padding: "2rem",
              borderRadius: "12px",
              boxShadow: "0 8px 24px rgba(0, 0, 0, 0.3)",
              width: "90%",
              maxWidth: "600px",
              maxHeight: "80vh",
              overflowY: "auto",
              position: "relative",
            }}
          >
            <button
              onClick={closeTicketModal}
              style={{
                position: "absolute",
                top: "1rem",
                right: "1rem",
                background: "none",
                border: "none",
                fontSize: "1.5rem",
                cursor: "pointer",
                color: "#666",
              }}
            >
              <FaTimes />
            </button>

            <h3 style={{ marginBottom: "1.5rem", color: "#4b3c70" }}>
              Raise Ticket for Evaluation
            </h3>

            {selectedEvaluation && (
              <div style={{ 
                marginBottom: "1.5rem", 
                padding: "1rem", 
                backgroundColor: "#f8f9fa", 
                borderRadius: "8px",
                border: "1px solid #e9ecef"
              }}>
                <h4 style={{ margin: "0 0 0.5rem 0", color: "#4b3c70" }}>Evaluation Details:</h4>
                <p style={{ margin: "0.25rem 0", fontSize: "0.9rem" }}>
                  <strong>Evaluator:</strong> {selectedEvaluation.student.name}
                </p>
                <p style={{ margin: "0.25rem 0", fontSize: "0.9rem" }}>
                  <strong>Score:</strong> {Array.isArray(selectedEvaluation.score) 
                    ? selectedEvaluation.score.reduce((sum, current) => sum + current, 0)
                    : selectedEvaluation.score || 0}
                </p>
                <p style={{ margin: "0.25rem 0", fontSize: "0.9rem" }}>
                  <strong>Status:</strong> {selectedEvaluation.eval_status || 'pending'}
                </p>
              </div>
            )}

            <div style={{ marginBottom: "1rem" }}>
              <label style={{ 
                display: "block", 
                marginBottom: "0.5rem", 
                fontWeight: "600", 
                color: "#4b3c70" 
              }}>
                Reason for Ticket *
              </label>
              <select
                value={ticketData.reason}
                onChange={(e) => setTicketData({...ticketData, reason: e.target.value})}
                style={{
                  width: "100%",
                  padding: "0.75rem",
                  border: "2px solid #e1e5e9",
                  borderRadius: "8px",
                  fontSize: "1rem",
                  color: "#4b3c70",
                }}
              >
                <option value="">Select a reason</option>
                <option value="unfair_scoring">Unfair Scoring</option>
                <option value="bias_evaluation">Biased Evaluation</option>
                <option value="incomplete_feedback">Incomplete Feedback</option>
                <option value="technical_issue">Technical Issue</option>
                <option value="evaluation_error">Evaluation Error</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div style={{ marginBottom: "1rem" }}>
              <label style={{ 
                display: "block", 
                marginBottom: "0.5rem", 
                fontWeight: "600", 
                color: "#4b3c70" 
              }}>
                Priority Level
              </label>
              <select
                value={ticketData.priority}
                onChange={(e) => setTicketData({...ticketData, priority: e.target.value})}
                style={{
                  width: "100%",
                  padding: "0.75rem",
                  border: "2px solid #e1e5e9",
                  borderRadius: "8px",
                  fontSize: "1rem",
                  color: "#4b3c70",
                }}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>

            <div style={{ marginBottom: "1.5rem" }}>
              <label style={{ 
                display: "block", 
                marginBottom: "0.5rem", 
                fontWeight: "600", 
                color: "#4b3c70" 
              }}>
                Detailed Description *
              </label>
              <textarea
                value={ticketData.description}
                onChange={(e) => setTicketData({...ticketData, description: e.target.value})}
                placeholder="Please provide a detailed explanation of your concern..."
                style={{
                  width: "100%",
                  minHeight: "120px",
                  padding: "0.75rem",
                  border: "2px solid #e1e5e9",
                  borderRadius: "8px",
                  fontSize: "1rem",
                  color: "#4b3c70",
                  resize: "vertical",
                }}
              />
            </div>

            <div style={{ 
              display: "flex", 
              gap: "1rem", 
              justifyContent: "flex-end" 
            }}>
              <button
                onClick={closeTicketModal}
                disabled={isSubmitting}
                style={{
                  padding: "0.75rem 1.5rem",
                  border: "2px solid #6c757d",
                  borderRadius: "8px",
                  background: "white",
                  color: "#6c757d",
                  fontSize: "1rem",
                  fontWeight: "600",
                  cursor: isSubmitting ? "not-allowed" : "pointer",
                  opacity: isSubmitting ? 0.6 : 1,
                }}
              >
                Cancel
              </button>
              <button
                onClick={submitTicket}
                disabled={isSubmitting || !ticketData.reason.trim() || !ticketData.description.trim()}
                style={{
                  padding: "0.75rem 1.5rem",
                  border: "none",
                  borderRadius: "8px",
                  background: isSubmitting || !ticketData.reason.trim() || !ticketData.description.trim() 
                    ? "#cccccc" : "#4b3c70",
                  color: "white",
                  fontSize: "1rem",
                  fontWeight: "600",
                  cursor: isSubmitting || !ticketData.reason.trim() || !ticketData.description.trim() 
                    ? "not-allowed" : "pointer",
                }}
              >
                {isSubmitting ? "Submitting..." : "Submit Ticket"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PeerResultOverlay;

const thCellStyle = {
    padding: "12px 8px", 
    textAlign: "center",
    fontWeight: "bold",
    fontSize: "1rem"
};

const tdCellStyle = {
    padding: "12px 8px", 
    textAlign: "center", 
    fontWeight: 500,
    color: "#4b3c70"
};