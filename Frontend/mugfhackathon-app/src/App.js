import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Footer from "./components/Footer";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Chat from "./pages/Chat";
import Export from "./pages/Export"; // ✅ Added import
import "./App.css";

function App() {
  return (
    <div className="app-wrapper">
      <Router>
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/export" element={<Export />} /> {/* ✅ Added route */}
          </Routes>
        </main>
        <Footer />
      </Router>
    </div>
  );
}

export default App;
