import React, { useState } from "react";
import RecommendationCard from "./RecommendationCard";
import "./Chatbot.css";

export default function Chatbot() {
  const steps = [
    { key: "age", question: "Select your age range:", type: "dropdown", options: ["18-30", "31-50", "51+"], required: true },
    { key: "state", question: "Which Australian state or territory do you live in?", type: "dropdown", options: ["ACT", "NSW", "NT", "QLD", "SA", "TAS", "VIC", "WA"], required: true },
    { key: "insuranceType", question: "What type of insurance are you interested in?", type: "dropdown", options: ["Health", "Life", "Home", "Travel"], required: true },
    { key: "annualPremium", question: "How much do you expect to pay annually for your insurance (AUD)?", type: "dropdown", options: ["$0 – $1000", "$1001 – $2500", "$2501 – $5000", "$5000+"], required: true },
    { key: "preference", question: "Do you prefer lower premiums or more comprehensive coverage?", type: "dropdown", options: ["Lower Premiums", "Balanced", "Comprehensive Coverage"], required: false },
    { 
      key: "addons", 
      question: "Do you want to add Dental cover?", 
      type: "dropdown", 
      options: ["Yes", "No"], 
      condition: (data) => data.insuranceType === "Health", 
      required: true 
    }
  ];

  const [formData, setFormData] = useState({});
  const [recommendations, setRecommendations] = useState([]);
  const [errors, setErrors] = useState({});

  const handleChange = (key, value) => {
    setFormData(prev => ({ ...prev, [key]: value }));
    setErrors(prev => ({ ...prev, [key]: "" }));
  };

  const validateForm = () => {
    let newErrors = {};
    steps.forEach(step => {
      if (step.required) {
        if (step.condition && !step.condition(formData)) return; 
        if (!formData[step.key]) {
          newErrors[step.key] = "This field is required";
        }
      }
    });
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validateForm()) return;
    generateRecommendations(formData);
  };

  const generateRecommendations = (data) => {
    let recs = [];

    if (data.insuranceType === "Health") {
      recs.push({
        name: "Standard Health Plan",
        desc: "Covers hospital stays, surgeries, and preventive care.",
        price: "AUD 180/month"
      });
      if (data.addons === "Yes") {
        recs.push({
          name: "Dental Add-on",
          desc: "Covers dental checkups, cleanings, and emergency dental work.",
          price: "+ AUD 20/month"
        });
      }
    } else if (data.insuranceType === "Life") {
      recs.push({
        name: "Gold Life Plan",
        desc: "High payout and comprehensive coverage.",
        price: "AUD 250/month"
      });
    } else if (data.insuranceType === "Home") {
      recs.push({
        name: "Home Protection Standard",
        desc: "Covers property damage, theft, and liability.",
        price: "AUD 200/month"
      });
    } else if (data.insuranceType === "Travel") {
      recs.push({
        name: "Annual Travel Cover",
        desc: "Medical emergencies, trip cancellations, lost luggage.",
        price: "AUD 50/month"
      });
    }

    setRecommendations(recs);
  };

  return (
    <div className="chatbot-container">
      {recommendations.length === 0 ? (
        <>
          <h2 className="chatbot-title">Insurance Recommendation Form</h2>
          {steps.map((step, idx) => {
            if (step.condition && !step.condition(formData)) return null;
            return (
              <div key={idx} className="chatbot-field">
                <label className="chatbot-label">{step.question}</label>
                {step.type === "dropdown" && (
                  <select
                    value={formData[step.key] || ""}
                    onChange={(e) => handleChange(step.key, e.target.value)}
                    className="chatbot-input"
                  >
                    <option value="">Select...</option>
                    {step.options.map((opt, i) => (
                      <option key={i} value={opt}>{opt}</option>
                    ))}
                  </select>
                )}
                {errors[step.key] && <p className="chatbot-error">{errors[step.key]}</p>}
              </div>
            );
          })}
          <button onClick={handleSubmit} className="chatbot-button">
            Get Recommendations
          </button>
        </>
      ) : (
        <div>
          <h3 className="chatbot-subtitle">Recommended Plans for You:</h3>
          {recommendations.map((rec, idx) => (
            <RecommendationCard key={idx} {...rec} />
          ))}
        </div>
      )}
    </div>
  );
}
