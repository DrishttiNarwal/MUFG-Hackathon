import React from "react";
import { Link } from "react-router-dom";
import "./Home.css";

export default function Home() {
  return (
    <div className="home">
      <div className="hero-content">
        <h1>
          Your Personal <span className="highlight">Insurance Advisor</span>
        </h1>
        <p className="subtitle">
          Empowering superannuation members to make smarter insurance choices —
          tailored to your lifestyle, family, and financial goals.
        </p>
        <Link to="/chat" className="cta-button">
          💬 Start Your Smart Insurance Chat
        </Link>
      </div>
    </div>
  );
}
