# scripts/llm/llm_client.py
from __future__ import annotations

import json
import os
import re
from typing import Dict

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    # Don't crash the API; return a stub later
    genai = None
else:
    genai.configure(api_key=GEMINI_API_KEY)

# Use a widely available fast model
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def _safe_json_parse(text: str) -> Dict:
    """
    Robustly parse JSON from LLM output, handling:
      - ```json ... ``` fences
      - trailing commas
      - leading commentary
    """
    if text is None:
        raise ValueError("Empty LLM output")

    # Strip code fences like ```json ... ```
    cleaned = text.strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"^```\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    # Try direct json first
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Extract a JSON object substring
    m = re.search(r"\{.*\}", cleaned, flags=re.S)
    if not m:
        raise ValueError("No JSON object found in LLM output")

    candidate = m.group(0)
    # Remove trailing commas before } or ]
    candidate = re.sub(r",\s*([\}\]])", r"\1", candidate)

    return json.loads(candidate)


def _fallback_explanations(user_input: Dict, prediction: Dict, knowledge: str = "") -> Dict:
    """
    Used when Gemini is unavailable or returns malformed JSON.
    Produces clear, safe defaults based on premiums and recommended tier.
    """
    tiers = prediction.get("all_tiers", {})
    rec = prediction.get("recommended_tier", "")

    def brief(tier: str) -> str:
        premium = tiers.get(tier)
        base = (
            "Basic offers essential coverage at an affordable price."
            if tier == "Basic" else
            "Standard enhances the essentials with a few valuable extras."
            if tier == "Standard" else
            "Gold adds higher limits and more comprehensive protections."
            if tier == "Gold" else
            "Premium provides the most complete protection and highest limits."
        )
        return f"{base} Estimated premium: {premium}."

    why = (
        f"We recommend **{rec}** because it best matches your profile "
        f"(age, dependents, sum assured and other inputs) while balancing cost vs. coverage."
    )
    if knowledge:
        why += " We also considered relevant guidelines and industry details from our knowledge base."

    return {
        "Basic": brief("Basic"),
        "Standard": brief("Standard"),
        "Gold": brief("Gold"),
        "Premium": brief("Premium"),
        "why_recommended": why,
    }


def generate_explanations(user_input: Dict, prediction: Dict, knowledge: str = "") -> Dict:
    """
    Returns explanations for all tiers, and a specific 'why_recommended' field
    justifying the recommended tier.
    Structure:
    {
      "Basic": "...",
      "Standard": "...",
      "Gold": "...",
      "Premium": "...",
      "why_recommended": "..."
    }
    """
    if genai is None:
        # No API key – graceful fallback
        return _fallback_explanations(user_input, prediction, knowledge)

    tiers = prediction.get("all_tiers", {})
    rec = prediction.get("recommended_tier", "")

    system_prompt = (
        "You are a concise, trustworthy insurance advisor. "
        "Generate short, plain-English explanations."
    )

    user_prompt = f"""
User profile (JSON):
{json.dumps(user_input, ensure_ascii=False)}

Predicted premiums (JSON):
{json.dumps(tiers, ensure_ascii=False)}

Recommended tier: {rec}

Extra knowledge (may be empty and not guaranteed): 
{knowledge}

Instructions:
1) For each tier (Basic, Standard, Gold, Premium), write 2–4 sentences:
   - What the tier generally includes and who it suits.
   - Mention its estimated premium from the JSON above.
2) Add a field "why_recommended" explaining why the recommended tier fits this user better than the others.
3) Return STRICT JSON with keys: "Basic", "Standard", "Gold", "Premium", "why_recommended".
"""

    try:
        model = genai.GenerativeModel(
            GEMINI_MODEL,
            generation_config={"response_mime_type": "application/json"},
            system_instruction=system_prompt,
        )
        resp = model.generate_content(user_prompt)
        parsed = _safe_json_parse(getattr(resp, "text", "") or "")
        # Basic validation
        for k in ["Basic", "Standard", "Gold", "Premium", "why_recommended"]:
            if k not in parsed:
                raise ValueError("Missing key in LLM JSON: " + k)
        return parsed
    except Exception:
        # Robust fallback
        return _fallback_explanations(user_input, prediction, knowledge)

# Backward compatibility alias
# Backward compatibility alias
def explain_recommendation(user_input: Dict, prediction: Dict, ranked_policies=None, rag_knowledge: str = "") -> Dict:
    return generate_explanations(user_input, prediction, rag_knowledge)
