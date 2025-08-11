import React, { useState } from "react";
import RecommendationCard from "./RecommendationCard";

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hello! Tell me about your lifestyle and goals." }
  ]);
  const [input, setInput] = useState("");
  const [recommendations, setRecommendations] = useState([]);

  const handleSend = () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { sender: "user", text: input }];
    setMessages(newMessages);
    setInput("");

    setTimeout(() => {
      const botReply =
        "Based on your input, here are some insurance plans you may like:";
      setMessages([...newMessages, { sender: "bot", text: botReply }]);
      setRecommendations([
  {
    name: "Life Gold Protection Plan",
    desc: "Upgrades your basic life insurance to a Gold-tier plan, ensuring higher payout and better coverage for your family in case of unforeseen events.",
    price: "AUD 250/month"
  },
  {
    name: "Family Health Premium Plan",
    desc: "Comprehensive health insurance for you, your spouse, and children — covering hospital stays, surgeries, and preventive care.",
    price: "AUD 180/month"
  },
   {
    name: "Travel Annual Cover Plan",
    desc: "Annual family travel insurance covering medical emergencies, cancellations, and also lost luggage for domestic and overseas trips for family.",
    price: "AUD 50/month"
  }
]
);
    }, 1000);
  };

  return (
    <div className="chat-container">
      <div className="chat-box">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`message ${msg.sender === "user" ? "user" : "bot"}`}
          >
            {msg.text}
          </div>
        ))}
      </div>
      <div className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button onClick={handleSend}>Send</button>
      </div>

      {recommendations.length > 0 && (
        <div className="recommendations">
          {recommendations.map((rec, idx) => (
            <RecommendationCard key={idx} {...rec} />
          ))}
        </div>
      )}
    </div>
  );
}
