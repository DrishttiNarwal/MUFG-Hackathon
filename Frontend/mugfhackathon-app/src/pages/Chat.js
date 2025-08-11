import React from "react";
import { useNavigate } from "react-router-dom";
import Chatbot from "../components/Chatbot";
import "./Chat.css";

export default function Chat() {
  const navigate = useNavigate();

  const handleSummarize = () => {
    // Later: Pass chat history via state or global store
    navigate("/export");
  };

  return (
    <div className="chat-page">
      {/* Chat Header */}
      <header className="chat-header">
        <h1>GuardBot</h1>
        <p className="chat-tagline">
          Your AI-powered insurance advisor — guiding you to smarter coverage.
        </p>
      </header>

      {/* Chat Interface */}
      <div className="chat-container-wrapper">
        <Chatbot />
      </div>

      {/* Summarize Button */}
      <div className="chat-footer">
        <button className="summarize-btn" onClick={handleSummarize}>
          Summarize Chat
        </button>
      </div>
    </div>
  );
}
