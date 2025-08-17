import React, { useState } from "react";
import "./Dashboard.css";
import { Bar, Radar, Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, RadialLinearScale } from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, RadialLinearScale);

export default function Dashboard() {
  const [premiumRange, setPremiumRange] = useState(5000);
  const [coverageAmount, setCoverageAmount] = useState(500000);
  const [claimRatio, setClaimRatio] = useState(95);

  const handleRecompute = () => {
    alert("Scores recomputed!");
  };

  const barData = {
    labels: ["Policy A", "Policy B", "Policy C"],
    datasets: [
      {
        label: "Premium vs Coverage",
        data: [500000, 700000, 400000],
        backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
        borderRadius: 6,
      },
    ],
  };

  const radarData = {
    labels: ["Premium", "Coverage", "Claim", "Add-ons", "AI Fit Score"],
    datasets: [
      {
        label: "Policy Comparison",
        data: [12000, 500000, 96, 1, 92],
        backgroundColor: "rgba(54,162,235,0.2)",
        borderColor: "#36A2EB",
        borderWidth: 2,
        pointBackgroundColor: "#36A2EB",
      },
    ],
  };

  const lineData = {
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    datasets: [
      {
        label: "Historical Premium Trends",
        data: [12000, 12500, 13000, 11000, 14000, 11500],
        fill: false,
        borderColor: "#FF6384",
        tension: 0.3,
      },
    ],
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <input type="text" placeholder="Search..." className="search-input" />
        <select className="insurance-select">
          <option>Life Insurance</option>
          <option>Health Insurance</option>
          <option>Motor Insurance</option>
        </select>
      </div>

      <h2>Policy Comparison Dashboard</h2>

      <div className="controls">
        <div className="slider-group">
          <label>Premium Range</label>
          <input type="range" min="5000" max="20000" value={premiumRange} onChange={e => setPremiumRange(e.target.value)} />
        </div>
        <div className="slider-group">
          <label>Coverage Amount</label>
          <input type="range" min="100000" max="1000000" step="50000" value={coverageAmount} onChange={e => setCoverageAmount(e.target.value)} />
        </div>
        <div className="addons">
          <label><input type="checkbox" /> Critical Illness</label>
          <label><input type="checkbox" /> Accidental Cover</label>
        </div>
      </div>

      <table className="policy-table">
        <thead>
          <tr>
            <th>Feature</th>
            <th>Policy A</th>
            <th>Policy B</th>
            <th>Policy C</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Premium (per year)</td>
            <td>₹12,000</td>
            <td>₹14,500</td>
            <td>₹11,200</td>
          </tr>
          <tr>
            <td>Coverage Amount</td>
            <td>₹5,00,000</td>
            <td>₹7,00,000</td>
            <td>₹4,00,000</td>
          </tr>
          <tr>
            <td>Claim Settlement %</td>
            <td>96%</td>
            <td>92%</td>
            <td>98%</td>
          </tr>
          <tr>
            <td>Add-ons</td>
            <td>✔</td>
            <td>✔</td>
            <td>✔</td>
          </tr>
          <tr>
            <td>AI Fit Score</td>
            <td>92%</td>
            <td>88%</td>
            <td>94%</td>
          </tr>
          <tr>
            <td>Recommended For You</td>
            <td>✔</td>
            <td>✖</td>
            <td>✔</td>
          </tr>
        </tbody>
      </table>

      <button className="recompute-btn" onClick={handleRecompute}>Recompute Scores</button>

      <div className="charts">
        <div className="chart">
          <h4>Premium vs Coverage</h4>
          <Bar data={barData} />
        </div>
        <div className="chart">
          <h4>Policy Radar</h4>
          <Radar data={radarData} />
        </div>
        <div className="chart">
          <h4>Historical Premium Trends</h4>
          <Line data={lineData} />
        </div>
      </div>
    </div>
  );
}
