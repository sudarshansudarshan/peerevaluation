import React from "react";
import { FaTimes } from "react-icons/fa";

const EvaluationOverlay = ({
  isOverlayOpen,
  selectedEvaluation,
  closeEvalOverlay,
  handleEvaluationSubmit,
}) => {
  if (!isOverlayOpen) return null;

  return (
    <div
      onClick={closeEvalOverlay}
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        background: "rgba(0, 0, 0, 0.5)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 1000,
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
          maxWidth: "1700px",
          height: "90%",
          display: "flex",
          flexDirection: "column",
          gap: "2rem",
          position: "relative",
        }}
      >
        {/* Close Button */}
        <button
          onClick={closeEvalOverlay}
          style={{
            position: "absolute",
            top: "0.5rem",
            right: "0.5rem",
            padding: "0.5rem 1rem",
            borderRadius: "8px",
            border: "none",
            background: " #fc1717",
            color: "#fff",
            fontWeight: 200,
            cursor: "pointer",
            transition: "background 0.2s",
          }}
        >
          <FaTimes style={{ fontSize: "1rem" }} />
        </button>

        <div
          style={{ display: "flex", flex: 1, gap: "2rem", overflowY: "hidden" }}
        >
          {/* PDF Viewer */}
          <div
            style={{ flex: 1, border: "1px solid #ccc", borderRadius: "8px" }}
          >
            <iframe
              src={`http://localhost:5000/${selectedEvaluation?.documentPath}`}
              title="Document Viewer"
              style={{
                width: "100%",
                height: "100%",
                border: "none",
                borderRadius: "8px",
              }}
            />
          </div>

          {/* Form for Marks and Feedback */}
          <div style={{ flex: 1 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <h2
                style={{ marginBottom: "1rem", textAlign: "center", flex: 1 }}
              >
                Evaluation Form
              </h2>
              <div style={{ display: "flex", gap: "1rem" }}>
                <a
                  href={`http://localhost:5000/${selectedEvaluation?.documentPath}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    display: "block",
                    textAlign: "center",
                    padding: "0.5rem 1rem",
                    borderRadius: "8px",
                    background: "#4b3c70",
                    color: "#fff",
                    fontWeight: 500,
                    textDecoration: "none",
                    transition: "background 0.2s",
                  }}
                >
                  Evaluation File
                </a>
                <a
                  href={`http://localhost:5000/${selectedEvaluation?.exam_solutions}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    display: "block",
                    textAlign: "center",
                    padding: "0.5rem 1rem",
                    borderRadius: "8px",
                    background: "#4b3c70",
                    color: "#fff",
                    fontWeight: 500,
                    textDecoration: "none",
                    transition: "background 0.2s",
                  }}
                >
                  Solutions
                </a>
              </div>
            </div>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                height: "90%",
                width: "100%",
                position: "relative",
              }}
            >
              <div
                style={{ flex: 1, overflowY: "auto", paddingRight: "0.5rem" }}
              >
                <form
                  id="evaluation-form"
                  onSubmit={(e) => {
                    handleEvaluationSubmit(e, selectedEvaluation);
                  }}
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "1rem",
                  }}
                >
                  {Array.from({
                    length: selectedEvaluation?.exam_number_of_Questions || 0,
                  }).map((_, index) => (
                    <div
                      key={index}
                      style={{
                        marginTop: "0.25rem",
                        display: "flex",
                        alignItems: "center",
                        gap: "1rem",
                        marginBottom: "0.25rem",
                      }}
                    >
                      <label
                        style={{
                          fontWeight: "bold",
                          flex: "0 0 50px",
                          textAlign: "center",
                        }}
                      >
                        {`Q${index + 1}`}
                      </label>
                      <input
                        type="number"
                        placeholder="Marks"
                        min="0"
                        max={selectedEvaluation?.examTotalMarks || 0}
                        style={{
                          flex: 1,
                          padding: "0.4rem",
                          borderRadius: "6px",
                          border: "1px solid #4b3c70",
                          fontSize: "0.8rem",
                          boxShadow: "inset 0 1px 3px rgba(0, 0, 0, 0.1)",
                          background: "#f9f9f9",
                          color: "#4b3c70",
                        }}
                        required
                      />
                      <input
                        type="text"
                        placeholder="Feedback"
                        style={{
                          flex: 2,
                          padding: "0.4rem",
                          borderRadius: "6px",
                          border: "1px solid #4b3c70",
                          fontSize: "0.8rem",
                          boxShadow: "inset 0 1px 3px rgba(0, 0, 0, 0.1)",
                          background: "#f9f9f9",
                          color: "#4b3c70",
                        }}
                      />
                    </div>
                  ))}
                </form>
              </div>
              <div
                style={{
                  padding: "1rem",
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
                  <label style={{ fontWeight: "bold" }}>
                    {`Total marks = ${selectedEvaluation?.examTotalMarks || 0}`}
                  </label>
                </div>

                <div style={{ flex: 1, textAlign: "center" }}>
                  <button
                    type="submit"
                    form="evaluation-form"
                    style={{
                      padding: "0.5rem 0.8rem",
                      borderRadius: "8px",
                      border: "none",
                      background: "#4b3c70",
                      color: "#fff",
                      fontWeight: 500,
                      cursor: "pointer",
                      transition: "background 0.2s",
                      whiteSpace: "nowrap",
                    }}
                  >
                    Submit
                  </button>
                </div>

                <div style={{ flex: 1 }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EvaluationOverlay;
