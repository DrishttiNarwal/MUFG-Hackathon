# scripts/api/serve.py
from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from llm.llm_orchestrator import recommend_with_explanation

app = FastAPI(title="Insurance Recommendation API")

class RecommendRequest(BaseModel):
    Country: str
    Language: str = Field("English", description="Response language")
    ProductType: str
    # Common fields (others optional; send whatever your form collects)
    Name: Optional[str] = None
    Age: Optional[int] = None
    Tier: Optional[str] = None

    # Health/Life
    AnnualPremium: Optional[float] = None
    SumInsured: Optional[float] = None
    SmokerDrinker: Optional[str] = None
    HealthIssues: Optional[str] = None

    # Vehicle
    PriceOfVehicle: Optional[float] = None
    AgeOfVehicle: Optional[float] = None
    TypeOfVehicle: Optional[str] = None

    # Travel
    DestinationCountry: Optional[str] = None
    TripDurationDays: Optional[int] = None
    ExistingMedicalCondition: Optional[str] = None
    HealthCoverage: Optional[str] = None
    BaggageCoverage: Optional[str] = None
    TripCancellationCoverage: Optional[str] = None
    AccidentCoverage: Optional[str] = None

    # House
    PropertyValue: Optional[float] = None
    PropertyAge: Optional[int] = None
    PropertyType: Optional[str] = None
    PropertySizeSqFeet: Optional[float] = None


class RecommendResponse(BaseModel):
    suggested_tier: str
    source: str
    probabilities: Optional[Dict[str, float]]
    llm_explanation_md: str
    evidence_sources: List[str]
    graph_facts: List[Any]

@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    result = recommend_with_explanation(req.model_dump())
    return RecommendResponse(
        suggested_tier=result.suggested_tier,
        source=result.model_source,
        probabilities=result.probabilities,
        llm_explanation_md=result.explanation,
        evidence_sources=result.evidence_sources,
        graph_facts=result.graph_facts,
    )

# Run: uvicorn scripts.api.serve:app --reload --port 8000
