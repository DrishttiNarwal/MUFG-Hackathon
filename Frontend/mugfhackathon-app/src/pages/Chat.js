import React from "react";
import Chatbot from "../components/Chatbot";
import "./Chat.css";

export default function Chat() {
  return (
    <div className="chat-page">
      {/* Chat Header */}
      <header className="chat-header">
        <h1>GuardBot</h1>
      </header>

      {/* Chat Interface */}
      <div className="chat-container-wrapper">
        <Chatbot />
      </div>
    </div>
  );
}
