import React from "react";
import "./OurTeam.css";


const teamMembers = [
  {
    name: "Drishti Narwal",
    role: "AI/ML Engineer & Frontend Architect",
    image: "/images/drishtti.jpg", // place in public/images/
    bio: "Designed the complete UI/UX frontend, implemented explainable AI modules, and developed predictive regression models for insurance analytics.",
  },
  {
    name: "Atharv Kulkarni",
    role: "Data Scientist & Graph Analyst",
    image: "/images/atharv.jpg",
    bio: "Specialized in graph analysis for insights discovery, applied unsupervised learning models, and contributed to advanced clustering techniques.",
  },
  {
    name: "Arya Barai",
    role: "Data Engineer & Knowledge Curator",
    image: "/images/arya.jpg",
    bio: "Led dataset generation and preprocessing, ensuring data quality, while managing presentations and project documentation.",
  },
  {
    name: "Ishaan Deshpande",
    role: "Backend Engineer & Knowledge Graph Specialist",
    image: "/images/ishaan.jpg",
    bio: "Implemented Neo4j graph database, optimized the backend pipeline, and ensured seamless data integration across the system.",
  },
];

export default function OurTeam() {
  return (
    <div className="our-team">
      <h2 className="team-title">Meet Our Team 👩‍💻👨‍💻</h2>
      <div className="team-grid">
        {teamMembers.map((member, index) => (
          <div className="team-card" key={index}>
            <img src={member.image} alt={member.name} className="team-img" />
            <h3 className="team-name">{member.name}</h3>
            <p className="team-role">{member.role}</p>
            <p className="team-bio">{member.bio}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
