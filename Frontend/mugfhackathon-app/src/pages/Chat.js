import React, { useState } from "react";
import "./Chat.css";

export default function Chat() {
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    country: "",
    productType: "",
    tier: "",
    // Insurance-specific fields
    annualPremium: "",
    sumInsured: "",
    smokerDrinker: "",
    healthIssues: "",
    priceOfVehicle: "",
    ageOfVehicle: "",
    typeOfVehicle: "",
    destinationCountry: "",
    tripDuration: "",
    medicalCondition: "",
    healthCoverage: "",
    baggageCoverage: "",
    tripCancellationCoverage: "",
    accidentCoverage: "",
    propertyValue: "",
    propertyAge: "",
    propertyType: "",
    propertySize: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Collected Data: ", formData);
    alert("Form Submitted! Check console for data.");
  };

  return (
    <div className="chat-page">
      <header className="chat-header">
        <h1>GuardBot</h1>
        <p className="chat-tagline">
          Your AI-powered insurance advisor — guiding you to smarter coverage.
        </p>
      </header>

      {/* Input Form */}
      <div className="chat-container-wrapper">
        <form className="form-container" onSubmit={handleSubmit}>
          {/* Basic Info */}
          <h2>Basic Information</h2>
          <input
            type="text"
            name="name"
            placeholder="Name"
            value={formData.name}
            onChange={handleChange}
            required
          />
          <input
            type="number"
            name="age"
            placeholder="Age"
            value={formData.age}
            onChange={handleChange}
            required
          />
          <input
            type="text"
            name="country"
            placeholder="Country"
            value={formData.country}
            onChange={handleChange}
            required
          />
          <select
            name="productType"
            value={formData.productType}
            onChange={handleChange}
            required
          >
            <option value="">Select Product Type</option>
            <option value="health">Health Insurance</option>
            <option value="life">Life Insurance</option>
            <option value="vehicle">Vehicle Insurance</option>
            <option value="travel">Travel Insurance</option>
            <option value="house">House Insurance</option>
          </select>
          <select
            name="tier"
            value={formData.tier}
            onChange={handleChange}
            required
          >
            <option value="">Select Tier</option>
            <option value="basic">Basic</option>
            <option value="standard">Standard</option>
            <option value="gold">Gold</option>
            <option value="premium">Premium</option>
          </select>

          {/* Conditional Forms */}
          {formData.productType === "health" || formData.productType === "life" ? (
            <>
              <h2>{formData.productType === "health" ? "Health Insurance" : "Life Insurance"} Details</h2>
              <input
                type="number"
                name="annualPremium"
                placeholder="Annual Premium"
                value={formData.annualPremium}
                onChange={handleChange}
              />
              <input
                type="number"
                name="sumInsured"
                placeholder="Sum Insured"
                value={formData.sumInsured}
                onChange={handleChange}
              />
              <select
                name="smokerDrinker"
                value={formData.smokerDrinker}
                onChange={handleChange}
              >
                <option value="">Smoker/Drinker?</option>
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
              <input
                type="text"
                name="healthIssues"
                placeholder="Health Issues"
                value={formData.healthIssues}
                onChange={handleChange}
              />
            </>
          ) : null}

          {formData.productType === "vehicle" && (
            <>
              <h2>Vehicle Insurance Details</h2>
              <input
                type="number"
                name="priceOfVehicle"
                placeholder="Price of Vehicle"
                value={formData.priceOfVehicle}
                onChange={handleChange}
              />
              <input
                type="number"
                name="ageOfVehicle"
                placeholder="Age of Vehicle"
                value={formData.ageOfVehicle}
                onChange={handleChange}
              />
              <select
                name="typeOfVehicle"
                value={formData.typeOfVehicle}
                onChange={handleChange}
              >
                <option value="">Type of Vehicle</option>
                <option value="bike">Bike</option>
                <option value="car">Car</option>
                <option value="truck">Truck</option>
                <option value="three-wheeler">Three Wheeler</option>
              </select>
            </>
          )}

          {formData.productType === "travel" && (
            <>
              <h2>Travel Insurance Details</h2>
              <input
                type="text"
                name="destinationCountry"
                placeholder="Destination Country"
                value={formData.destinationCountry}
                onChange={handleChange}
              />
              <input
                type="number"
                name="tripDuration"
                placeholder="Trip Duration (Days)"
                value={formData.tripDuration}
                onChange={handleChange}
              />
              <select
                name="medicalCondition"
                value={formData.medicalCondition}
                onChange={handleChange}
              >
                <option value="">Existing Medical Condition?</option>
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>

              <h3>Coverage Options</h3>
              <select
                name="baggageCoverage"
                value={formData.baggageCoverage}
                onChange={handleChange}
              >
                <option value="">Baggage Coverage?</option>
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
              <select
                name="tripCancellationCoverage"
                value={formData.tripCancellationCoverage}
                onChange={handleChange}
              >
                <option value="">Trip Cancellation Coverage?</option>
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
              <select
                name="accidentCoverage"
                value={formData.accidentCoverage}
                onChange={handleChange}
              >
                <option value="">Accident Coverage?</option>
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </>
          )}

          {formData.productType === "house" && (
            <>
              <h2>House Insurance Details</h2>
              <input
                type="number"
                name="propertyValue"
                placeholder="Property Value"
                value={formData.propertyValue}
                onChange={handleChange}
              />
              <input
                type="number"
                name="propertyAge"
                placeholder="Property Age"
                value={formData.propertyAge}
                onChange={handleChange}
              />
              <select
                name="propertyType"
                value={formData.propertyType}
                onChange={handleChange}
              >
                <option value="">Property Type</option>
                <option value="house">House</option>
                <option value="bunglow">Bunglow</option>
                <option value="apartment">Apartment</option>
              </select>
              <input
                type="number"
                name="propertySize"
                placeholder="Property Size (sq ft)"
                value={formData.propertySize}
                onChange={handleChange}
              />
            </>
          )}

          {/* Submit */}
          <button type="submit" className="summarize-btn">
            Submit Details
          </button>
        </form>
      </div>
    </div>
  );
}
