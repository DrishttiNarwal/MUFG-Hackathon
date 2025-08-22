# scripts/api/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    user_id: str
    query: str
    country: Optional[str] = "india"   # default to india dataset

class PolicyOption(BaseModel):
    policy_name: str
    confidence: float
    explanation: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    recommendations: Optional[List[PolicyOption]] = None
