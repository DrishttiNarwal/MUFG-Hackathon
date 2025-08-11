import React from "react";

export default function RecommendationCard({ name, desc, price }) {
  return (
    <div className="card">
      <h3>{name}</h3>
      <p>{desc}</p>
      <p className="price">{price}</p>
      <button>Learn More</button>
    </div>
  );
}
