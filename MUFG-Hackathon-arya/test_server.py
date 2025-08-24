from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class InsuranceRequest(BaseModel):
    country: str
    policy_type: str
    age: Optional[int] = None
    price_of_vehicle: Optional[float] = None
    age_of_vehicle: Optional[int] = None
    type_of_vehicle: Optional[str] = None
    property_value: Optional[float] = None
    property_age: Optional[int] = None
    property_type: Optional[str] = None
    property_size: Optional[float] = None
    
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/recommend")
async def recommend(request: InsuranceRequest):
    try:
        print(f"Received request: {request}")
        
        # Basic premium calculation
        base_premium = 1000  # Default base premium
        
        if request.policy_type.upper() == "VEHICLE":
            if not request.price_of_vehicle:
                raise HTTPException(status_code=400, detail="Vehicle price is required")
            base_premium = request.price_of_vehicle * 0.03  # 3% of vehicle price
            if request.age_of_vehicle:
                base_premium *= (1 - min(request.age_of_vehicle * 0.1, 0.5))  # Depreciation
                
        elif request.policy_type.upper() == "HOUSE":
            if not request.property_value:
                raise HTTPException(status_code=400, detail="Property value is required")
            base_premium = request.property_value * 0.001  # 0.1% of property value
            if request.property_age:
                base_premium *= (1 + request.property_age * 0.05)  # Age factor
                
        # Calculate tier premiums
        premiums = {
            "Basic": round(base_premium * 0.8, 2),
            "Standard": round(base_premium, 2),
            "Gold": round(base_premium * 1.2, 2),
            "Premium": round(base_premium * 1.5, 2)
        }
        
        # Convert to AUD if needed
        if request.country.upper() in ["AU", "AUSTRALIA"]:
            premiums = {k: round(v / 55.0, 2) for k, v in premiums.items()}
            
        response = {
            "prediction": {
                "recommended_tier": "Standard",
                "all_tiers": premiums,
                "confidence": {
                    "Basic": 0.25,
                    "Standard": 0.35,
                    "Gold": 0.25,
                    "Premium": 0.15
                }
            },
            "explanation": {
                "summary": "Based on your provided information, we have generated the following recommendation.",
                "benefits": [
                    "Comprehensive coverage suited to your needs",
                    "Competitive premium rates",
                    "Flexible payment options"
                ],
                "recommendations": [
                    "We recommend the Standard plan",
                    "Consider annual payment for additional discounts",
                    "Review coverage details in policy document"
                ]
            }
        }
        
        print(f"Sending response: {response}")
        return response
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
