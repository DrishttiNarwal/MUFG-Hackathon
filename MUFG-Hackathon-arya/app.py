from fastapi import FastAPI
from pydantic import BaseModel
from scripts.recommendation.predict import predict
from scripts.llm.llm_client import generate_explanations
from scripts.api.currency_utils import convert_currency

app = FastAPI(title="Insurance Recommendation API")

class RecommendationRequest(BaseModel):
    country: str
    policy: str
    data: dict

COUNTRY_CURRENCIES = {
    "IN": "INR",
    "AU": "AUD"
}

@app.post("/recommend")
def recommend(inp: RecommendationRequest):
    # Get currency for the country
    currency = COUNTRY_CURRENCIES.get(inp.country)
    
    # Get base prediction in INR
    result = predict(inp.country, inp.policy, inp.data)
    
    # Convert monetary values if needed
    if currency == "AUD" and isinstance(result.get('premium'), (int, float)):
        result['premium'] = convert_currency(
            result['premium'], 
            from_currency="INR", 
            to_currency="AUD"
        )

    explanations = generate_explanations(
        user_input=inp.data,
        prediction=result,
        knowledge="Graph RAG knowledge if available",
    )
    
    return {
        "country": inp.country,
        "policy": inp.policy,
        "currency": currency,
        "recommendation": result,
        "explanations": explanations,
    }
