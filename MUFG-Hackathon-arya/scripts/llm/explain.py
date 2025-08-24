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
    policy_type: str
    age: int | None = None
    sum_assured: float | None = None
    smoker_drinker: str | None = None
    num_diseases: int | None = None
    diseases: str | None = None
    price_of_vehicle: float | None = None
    age_of_vehicle: int | None = None
    type_of_vehicle: str | None = None
    property_value: float | None = None
    property_age: int | None = None
    property_type: str | None = None
    property_size_sq_feet: float | None = None
    destination_country: str | None = None
    trip_duration_days: int | None = None
    existing_medical_condition: str | None = None
    health_coverage: str | None = None
    baggage_coverage: str | None = None
    trip_cancellation_coverage: str | None = None
    accident_coverage: str | None = None


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
