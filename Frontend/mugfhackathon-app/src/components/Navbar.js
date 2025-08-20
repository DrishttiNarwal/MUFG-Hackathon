import React from "react";
import { Link } from "react-router-dom";
import "./Navbar.css";

export default function Navbar() {
  return (
    <nav className="navbar">
      <h1 className="logo">GuardBot: AI Driven Insurance assistance for Superannuation</h1>
      <div className="nav-links">
        <Link to="/">Home</Link>
        <Link to="/chat">Chat</Link>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/ourteam">Our Team</Link> {/* ✅ Added Our Team link */}
      </div>
    </nav>
  );
}
