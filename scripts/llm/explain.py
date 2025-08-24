from fastapi import FastAPI
from pydantic import BaseModel
from scripts.llm.llm_client import explain_recommendation
from scripts.recommendation.predict import recommend

# Create FastAPI app
app = FastAPI(
    title="Insurance Bot API",
    version="0.1.0",
    description="API for insurance policy recommendation and explanation"
)

# ---- Request Schema ----
# ---- Request Schema ----
class RecommendRequest(BaseModel):
    country: str
    policytype: str
    age: int | None = None
    sumassured: float | None = None
    smokerdrinker: str | None = None
    num_diseases: int | None = None
    diseases: str | None = None
    priceofvehicle: float | None = None
    ageofvehicle: int | None = None
    typeofvehicle: str | None = None
    propertyvalue: float | None = None
    propertyage: int | None = None
    propertytype: str | None = None
    propertysizesqfeet: float | None = None
    destinationcountry: str | None = None
    tripdurationdays: int | None = None
    existingmedicalcondition: str | None = None
    healthcoverage: str | None = None
    baggagecoverage: str | None = None
    tripcancellationcoverage: str | None = None
    accidentcoverage: str | None = None


# ---- Routes ----
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/recommend_and_explain")
def recommend_and_explain(req: RecommendRequest):
    user_input = req.dict()

    # Run prediction
    prediction = recommend(user_input)

    # Ask LLM for explanation
    explanation = explain_recommendation(
        user_input=user_input,
        prediction=prediction,
        ranked_policies=prediction["options"],
        rag_knowledge="GraphRAG knowledge goes here"
    )

    return {
        "prediction": prediction,
        "explanation": explanation
    }
