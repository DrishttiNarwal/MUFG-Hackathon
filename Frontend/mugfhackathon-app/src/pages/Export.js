import React from "react";
import { useNavigate } from "react-router-dom";
import jsPDF from "jspdf";
import "jspdf-autotable";
import "./Export.css";

export default function Export() {
  const navigate = useNavigate();

  // Dummy summary (replace later with actual state/context data)
  const summaryText = `
    GuardBot Conversation Summary:
    - User discussed insurance needs for retirement planning.
    - Recommended Life Insurance with Income Protection.
    - Suggested premium adjustment based on lifestyle.
    - Provided risk analysis and future premium projection.
  `;

  const downloadPDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(14);
    doc.text("GuardBot Chat Summary", 14, 20);
    doc.setFontSize(12);
    doc.text(summaryText, 14, 30, { maxWidth: 180 });
    doc.save("GuardBot_Chat_Summary.pdf");
  };

  return (
    <div className="export-page">
      <h1>GuardBot Chat Summary</h1>
      <pre className="summary-box">{summaryText}</pre>

      <div className="export-actions">
        <button onClick={downloadPDF}>Download PDF</button>
        <button onClick={() => navigate(-1)}>Back to Chat</button>
      </div>
    </div>
  );
}
