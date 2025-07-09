import React from "react";

const ResultsTable = ({ results, resultExams, selectedResultExam, setSelectedResultExam }) => {
  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      color: "#2d3559",
      width: "100%",
    }}>
      {/* Filter Dropdown */}
      {resultExams.length > 0 && (
        <div style={{
          display: "flex",
          gap: "1rem",
          marginBottom: "1rem",
          width: "100%",
          justifyContent: "center",
        }}>
          <select
            value={selectedResultExam || ""}
            onChange={(e) => setSelectedResultExam(e.target.value)}
            style={{
              width: "auto",
              maxWidth: "100%",
              minWidth: 180,
              padding: "0.6rem 1.2rem",
              borderRadius: "8px",
              border: "1.5px solid #4b3c70",
              fontSize: "1rem",
              background: "#fff",
              color: "#000",
              fontWeight: 500,
              transition: "background 0.2s",
              outline: "none",
              cursor: "pointer",
            }}
          >
            <option value="">All Exams</option>
            {resultExams.map((exam, idx) => (
              <option key={idx} value={exam.examId}>
                {exam.courseName} ({exam.batchName}) - {exam.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Results Table */}
      <table style={{
        width: "100%",
        borderCollapse: "collapse",
        background: "#fff",
        borderRadius: 8,
        boxShadow: "0 2px 8px #4b3c70",
      }}>
        <thead style={{
          backgroundColor: "#4b3c70",
          color: "#ffffff",
          position: "sticky",
          top: 0,
          zIndex: 1,
        }}>
          <tr>
            <th style={{ padding: "12px", textAlign: "center" }}>Course Name</th>
            <th style={{ padding: "12px", textAlign: "center" }}>Batch Id</th>
            <th style={{ padding: "12px", textAlign: "center" }}>Exam Name</th>
            <th style={{ padding: "12px", textAlign: "center" }}>Exam Date</th>
            <th style={{ padding: "12px", textAlign: "center" }}>Total Marks</th>
            <th style={{ padding: "12px", textAlign: "center" }}>Your Marks</th>
            <th style={{ padding: "12px", textAlign: "center" }}>Status</th>
          </tr>
        </thead>
        <tbody>
          {results.length === 0 ? (
            <tr>
              <td colSpan="7" style={{
                padding: "12px",
                textAlign: "center",
                fontWeight: 500,
                color: "gray",
              }}>
                No results found.
              </td>
            </tr>
          ) : (
            results
              .filter(
                (result) =>
                  !selectedResultExam || result.examId === selectedResultExam
              )
              .map((result, idx) => (
                <tr key={idx}>
                  <td style={{ padding: "12px", textAlign: "center", fontWeight: 500 }}>
                    {result.courseName}
                  </td>
                  <td style={{ padding: "12px", textAlign: "center", fontWeight: 500 }}>
                    {result.batchName}
                  </td>
                  <td style={{ padding: "12px", textAlign: "center", fontWeight: 500 }}>
                    {result.examName}
                  </td>
                  <td style={{ padding: "12px", textAlign: "center", fontWeight: 500 }}>
                    {new Date(result.examDate).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })}
                  </td>
                  <td style={{ padding: "12px", textAlign: "center", fontWeight: 500 }}>
                    {result.totalMarks}
                  </td>
                  <td style={{ padding: "12px", textAlign: "center", fontWeight: 500 }}>
                    {result.obtainedMarks}
                  </td>
                  <td style={{ padding: "12px", textAlign: "center", fontWeight: 500 }}>
                    {result.status}
                  </td>
                </tr>
              ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default ResultsTable;