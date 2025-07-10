import React from "react";
import { FaTimes } from "react-icons/fa";

const PeerResultOverlay = ({ 
  isPeerResultOverlayOpen, 
  closePeerResultOverlay, 
  selectedExamForPeerResult, 
  peerResultsForExam 
}) => {
  if (!isPeerResultOverlayOpen) return null;

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
              borderCollapse: "collapse",
              background: "#fff",
              fontSize: "0.9rem",
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
                    Evaluator
                  </th>
                  <th style={{ ...thCellStyle }}>
                    Student
                  </th>
                  <th style={{ ...thCellStyle }}>
                    Score
                  </th>
                  <th style={{ ...thCellStyle }}>
                    Feedback
                  </th>
                  <th style={{ ...thCellStyle }}>
                    Status
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
                        {result.evaluator.name || 'Unknown'}
                      </td>
                      <td style={{ ...tdCellStyle }}>
                        {result.student.name || 'Unknown'}
                      </td>
                      <td style={{ ...tdCellStyle }}>
                        {Array.isArray(result.score) 
                          ? result.score.reduce((sum, current) => sum + current, 0)
                          : result.score || 0}
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
                Exam: {selectedExamForPeerResult?.name}
              </label>
            </div>

            <div style={{ flex: 1, textAlign: "right" }}>
              <label style={{ fontWeight: "bold", color: "#4b3c70" }}>
                Total Marks: {selectedExamForPeerResult?.totalMarks}
              </label>
            </div>
          </div>
        </div>
      </div>
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