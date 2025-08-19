import React, { useState } from "react";
import "./Chatbot.css";

const questions = [
  { key: "name", text: "Hi! What’s your name?" },
  { key: "age", text: "Great, how old are you?" },
  { key: "country", text: "Which country are you from?" },
  { key: "productType", text: "Which insurance do you need? (health / life / vehicle / travel / house)" },
  { key: "annualPremium", text: "What’s your annual premium budget?" },
  { key: "smokerDrinker", text: "Do you smoke or drink? (yes/no)" },
  { key: "healthIssues", text: "Any existing health issues? (yes/no)" }
];

export default function Chatbot({ onComplete }) {
  const [chat, setChat] = useState([{ from: "bot", text: questions[0].text }]);
  const [step, setStep] = useState(0);
  const [input, setInput] = useState("");
  const [answers, setAnswers] = useState({});

  const handleSend = () => {
    if (!input.trim()) return;

    const userMsg = { from: "user", text: input };
    const newAnswers = { ...answers, [questions[step].key]: input };

    setChat([...chat, userMsg]);

    if (step + 1 < questions.length) {
      const botMsg = { from: "bot", text: questions[step + 1].text };
      setChat((prev) => [...prev, botMsg]);
      setStep(step + 1);
    } else {
      const botMsg = { from: "bot", text: "Thanks! I’ve collected all your details 🎉" };
      setChat((prev) => [...prev, botMsg]);

      // Pass answers back to parent (Chat.js)
      if (onComplete) onComplete(newAnswers);
    }

    setAnswers(newAnswers);
    setInput("");
  };

  return (
    <div className="chatbot-container">
      <div className="chat-window">
        {chat.map((msg, idx) => (
          <div
            key={idx}
            className={`chat-bubble ${msg.from === "bot" ? "bot" : "user"}`}
          >
            {msg.text}
          </div>
        ))}
      </div>

      <div className="chat-input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type your answer..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}
