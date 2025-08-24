from __future__ import annotations

from typing import List, Dict, Any, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, root_validator

from scripts.recommendation.predict import predict
from scripts.llm.llm_client import explain_recommendation

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

app = FastAPI(
    title="Insurance Bot API",
    version="0.3.2",
    description="API for insurance policy recommendation and explanation",
)

# CORS configuration
origins = [
    "http://localhost:3000",           # React dev server
    "http://localhost:5173",           # Vite dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://localhost:8000",           # FastAPI server
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    print(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    print(f"General error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"},
    )

# -----------------------------
# Models
# -----------------------------
class RecommendRequest(BaseModel):
    country: str = Field(
        ..., 
        description="Country for insurance. Can be country code (IN, AU) or full name (INDIA, AUSTRALIA)"
    )
    policytype: str = Field(
        ..., 
        description="Type of insurance policy (HEALTH, LIFE, TRAVEL, HOUSE, VEHICLE)"
    )
    
    # Common fields
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0)
    
    @root_validator(pre=True)
    def validate_country(cls, values):
        if "country" in values:
            country = values["country"].upper()
            country_mapping = {
                "IN": "INDIA",
                "AU": "AUSTRALIA",
                "INDIA": "INDIA",
                "AUSTRALIA": "AUSTRALIA"
            }
            if country not in country_mapping:
                raise ValueError(f"Invalid country: {country}. Must be one of: IN, AU, INDIA, AUSTRALIA")
            values["country"] = country_mapping[country]
        return values
    policy_tier: Optional[str] = None
    
    # Health/Life Insurance fields
    sumassured: Optional[float] = Field(None, ge=0)
    smokerdrinker: Optional[str] = Field(None, pattern="^(Yes|No)$", case_sensitive=False)
    num_diseases: Optional[int] = Field(None, ge=0)
    diseases: Optional[str] = None
    annual_premium: Optional[float] = Field(None, ge=0)
    
    # Vehicle Insurance fields
    priceofvehicle: Optional[float] = Field(None, ge=0)
    ageofvehicle: Optional[int] = Field(None, ge=0)
    typeofvehicle: Optional[str] = None
    
    # Property Insurance fields
    propertyvalue: Optional[float] = Field(None, ge=0)
    propertyage: Optional[int] = Field(None, ge=0)
    propertytype: Optional[str] = Field(None, description="Type of property (apartment, house, villa,)")
    propertysizesqfeet: Optional[float] = Field(None, ge=0, description="Property size in square feet")
    
    # Travel Insurance fields
    destinationcountry: Optional[str] = None
    tripdurationdays: Optional[int] = Field(None, ge=0)
    existingmedicalcondition: Optional[str] = None
    healthcoverage: Optional[str] = None
    baggagecoverage: Optional[str] = None
    tripcancellationcoverage: Optional[str] = None
    accidentcoverage: Optional[str] = None
    trippremium: Optional[float] = Field(None, ge=0)

    @root_validator(pre=True)
    def standardize_fields(cls, values):
        # Handle empty strings
        for k, v in values.items():
            if v == "":
                values[k] = None
                
        # Convert to proper types
        type_conversions = {
            "age": int,
            "sumassured": float,
            "num_diseases": int,
            "annual_premium": float,
            "priceofvehicle": float,
            "ageofvehicle": int,
            "propertyvalue": float,
            "propertyage": int,
            "propertysizesqfeet": float,
            "tripdurationdays": int,
            "trippremium": float
        }
        
        for field, conv in type_conversions.items():
            if values.get(field) is not None:
                try:
                    values[field] = conv(values[field])
                except (ValueError, TypeError):
                    values[field] = None
                    
        # Standardize country and policytype
        if values.get("country"):
            values["country"] = str(values["country"]).upper()
        if values.get("policytype"):
            values["policytype"] = str(values["policytype"]).upper()
            
        return values

class RecommendResponse(BaseModel):
    prediction: Dict[str, Any]
    explanation: Dict[str, Any]

class PolicyItem(BaseModel):
    country: str = Field(..., description="Country for insurance (INDIA or AUSTRALIA)")
    policytype: str = Field(..., description="Type of insurance policy (HEALTH, VEHICLE)")
    age: Optional[int] = Field(None, ge=0)
    
    # Health Insurance fields
    sumassured: Optional[float] = Field(None, ge=0)
    smokerdrinker: Optional[str] = Field(None, pattern="^(Yes|No)?$", case_sensitive=False)
    num_diseases: Optional[int] = Field(None, ge=0)
    diseases: Optional[str] = None
    
    # Vehicle Insurance fields
    priceofvehicle: Optional[float] = Field(None, ge=0)
    ageofvehicle: Optional[int] = Field(None, ge=0)
    typeofvehicle: Optional[str] = Field(
        None,
        description="Type of vehicle (2wheeler, car, suv, commercial)"
    )

    class Config:
        schema_extra = {
            "example": {
                "country": "INDIA",
                "policytype": "VEHICLE",
                "age": 45,
                "priceofvehicle": 5000000,
                "ageofvehicle": 0,
                "typeofvehicle": "suv"
            }
        }

    @root_validator(pre=True)
    def standardize_fields(cls, values):
        try:
            # Handle empty strings and convert types
            type_conversions = {
                "age": int,
                "sumassured": float,
                "num_diseases": int,
                "priceofvehicle": float,
                "ageofvehicle": int,
            }
            
            for k, v in values.items():
                # Convert empty strings to None
                if v == "":
                    values[k] = None
                    continue
                    
                # Convert types if needed
                if k in type_conversions and v is not None:
                    try:
                        values[k] = type_conversions[k](v)
                    except (ValueError, TypeError):
                        values[k] = None
            
            # Standardize and validate country
            country = str(values.get("country", "")).upper()
            if country not in ["INDIA", "AUSTRALIA"]:
                raise ValueError(f"Invalid country: {country}")
            values["country"] = country
            
            # Standardize and validate policytype
            policy = str(values.get("policytype", "")).upper()
            if policy not in ["HEALTH", "VEHICLE"]:
                raise ValueError(f"Invalid policy type: {policy}")
            values["policytype"] = policy
            
            # Validate required fields based on policy type
            if policy == "VEHICLE":
                if not values.get("priceofvehicle"):
                    raise ValueError("priceofvehicle is required for vehicle insurance")
                if values.get("ageofvehicle") is None:
                    raise ValueError("ageofvehicle is required for vehicle insurance")
                if not values.get("typeofvehicle"):
                    raise ValueError("typeofvehicle is required for vehicle insurance")
                    
            elif policy == "HEALTH":
                if not values.get("age"):
                    raise ValueError("age is required for health insurance")
                
            return values
            
        except Exception as e:
            raise ValueError(f"Validation error: {str(e)}")
            
        return values

class MultiRecommendRequest(BaseModel):
    policies: List[PolicyItem] = Field(..., min_items=1, max_items=5)

class MultiRecommendResponse(BaseModel):
    results: List[RecommendResponse]

# -----------------------------
# Helpers
# -----------------------------
def to_dict_safe(model: BaseModel) -> Dict[str, Any]:
    dump = getattr(model, "model_dump", None)
    return dump() if callable(dump) else model.dict()

# -----------------------------
# Endpoints
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest):
    try:
        print(f"\n=== Starting recommendation request ===")
        print(f"Request data: {req}")
        
        data = to_dict_safe(req)
        # Get and normalize country
        country = data.get("country", "").upper()
        if not country:
            raise ValueError("Country is required")
            
        # Handle country codes
        country_mapping = {
            "IN": "INDIA",
            "AU": "AUSTRALIA",
            "INDIA": "INDIA",
            "AUSTRALIA": "AUSTRALIA"
        }
        
        country = country_mapping.get(country)
        if not country:
            raise ValueError(f"Invalid country. Must be one of: IN, AU, INDIA, AUSTRALIA")
            
        # Get and validate policy type
        policytype = data.get("policytype", "").upper()
        if not policytype:
            raise ValueError("Policy type is required")
        if policytype not in ["HEALTH", "LIFE", "TRAVEL", "HOUSE", "VEHICLE"]:
            raise ValueError(f"Invalid policy type: {policytype}")
        
        data.pop("policy", None)  # Remove extra field if present
        
        print(f"Processing request for {country} - {policytype}")
        print(f"Input data: {data}")
        
        # Policy-specific validation
        if policytype == "HOUSE":
            if not data.get("propertyvalue"):
                raise ValueError("Property value is required for house insurance")
            if "propertyage" not in data:
                raise ValueError("Property age is required for house insurance")
            if not data.get("propertytype"):
                raise ValueError("Property type is required for house insurance")
        
        prediction = predict(country, policytype, data)
        print(f"Prediction result: {prediction}")

        explanation = explain_recommendation(
            user_input=data,
            prediction=prediction,
            ranked_policies=None,
            rag_knowledge="GraphRAG knowledge goes here",
        )
        print(f"Generated explanation: {explanation}")
        
        return {"prediction": prediction, "explanation": explanation}
        
    except ValueError as ve:
        print(f"Validation error: {str(ve)}")
        return JSONResponse(
            status_code=400,
            content={"detail": str(ve)}
        )
    except Exception as e:
        print(f"Error in recommend endpoint: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred. Please try again later."}
        )

@app.post("/recommend_multiple", response_model=MultiRecommendResponse)
async def recommend_multiple(req: MultiRecommendRequest):
    print("Processing multiple recommendations request")
    print(f"Number of policies: {len(req.policies)}")
    results = []
    
    for idx, policy in enumerate(req.policies):
        try:
            print(f"\nProcessing policy {idx + 1}:")
            # Convert policy to dict and make prediction
            policy_dict = to_dict_safe(policy)
            print(f"Policy data: {policy_dict}")
            
            country = policy_dict.pop("country", "").upper()
            policytype = policy_dict.pop("policytype", "").upper()
            print(f"Country: {country}, Policy Type: {policytype}")
            
            if not country or not policytype:
                print(f"Skipping policy {idx + 1}: Missing country or policytype")
                continue
                
            # Remove None values to avoid prediction issues
            policy_dict = {k: v for k, v in policy_dict.items() if v is not None}
            
            try:
                prediction = predict(
                    country=country,
                    policy=policytype,
                    data=policy_dict
                )
                print(f"Prediction result: {prediction}")
                
                explanation = explain_recommendation(
                    user_input=policy_dict,
                    prediction=prediction,
                    ranked_policies=None,
                    rag_knowledge="GraphRAG knowledge goes here"
                )
                
                results.append({
                    "prediction": prediction,
                    "explanation": explanation
                })
                print(f"Successfully processed policy {idx + 1}")
            except ValueError as ve:
                print(f"Validation error in policy {idx + 1}: {str(ve)}")
                continue
            except Exception as e:
                import traceback
                print(f"Error processing policy {idx + 1}: {str(e)}")
                print(traceback.format_exc())
                continue
                
        except Exception as e:
            print(f"Error parsing policy {idx + 1}: {str(e)}")
            continue
    
    if not results:
        return {"results": []}  # Return empty results instead of raising error
        
    return {"results": results}
