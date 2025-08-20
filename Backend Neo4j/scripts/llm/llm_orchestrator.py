# scripts/llm/llm_orchestrator.py
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Dict, Any, List

# prediction stack
from recommendation.predict import hybrid_predict
from recommendation.rule_engine import apply_rules

# GraphRAG
from rag.graph_rag import hybrid_retrieve, build_prompt as build_graph_prompt

# ---- LLM client (OpenAI-compatible) ----
# You can swap this to your provider; keep one tiny wrapper.
try:
    from openai import OpenAI
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    def llm_complete(prompt: str, lang: str = "en") -> str:
        sys = f"You are a bilingual insurance assistant. Reply in {lang}."
        resp = _client.chat.completions.create(
            model=os.getenv("LLM_MODEL","gpt-4o-mini"),
            messages=[{"role":"system","content":sys},{"role":"user","content":prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
except Exception:
    # Very simple fallback for dev environments without an API key.
    def llm_complete(prompt: str, lang: str = "en") -> str:
        return f"[DEV-LLM] ({lang})\n" + prompt[:1200]


@dataclass
class LLMResult:
    suggested_tier: str
    model_source: str            # "rule_engine" | "ml_classifier"
    probabilities: Dict[str, float] | None
    explanation: str             # LLM paragraph
    evidence_sources: List[str]  # PDF paths (vector hits)
    graph_facts: List[Any]       # [(a,rel,b)]
    contexts: List[str]          # evidence chunks


def build_user_summary(user: Dict[str, Any]) -> str:
    """Human-readable one‑pager for the LLM; only the filled fields."""
    keep_keys = [
        "Name","Age","Country","Language","ProductType","Tier",
        "AnnualPremium","SumInsured","SmokerDrinker","HealthIssues",
        "PriceOfVehicle","AgeOfVehicle","TypeOfVehicle",
        "DestinationCountry","TripDurationDays","ExistingMedicalCondition",
        "HealthCoverage","BaggageCoverage","TripCancellationCoverage","AccidentCoverage",
        "PropertyValue","PropertyAge","PropertyType","PropertySizeSqFeet",
    ]
    lines = []
    for k in keep_keys:
        if k in user and user[k] not in (None,"","NA"):
            lines.append(f"{k}: {user[k]}")
    return "\n".join(lines)


def build_unified_prompt(
    user: Dict[str,Any],
    hybrid_pack: Dict[str,Any],
    rag_pack: Dict[str,Any],
    lang: str = "en"
) -> str:
    """Merge user summary + hybrid prediction + graph RAG prompt."""
    user_sum = build_user_summary(user)

    # GraphRAG prompt section (already formatted)
    rag_prompt = build_graph_prompt(rag_pack, prediction=hybrid_pack["final_tier"])

    # A thin header to guide the LLM to produce a crisp, structured answer
    header = f"""
Task: Recommend the most suitable insurance policy tier for the user and justify it.
Language: {lang}

Return:
1) A one-line recommendation with the tier.
2) 3–5 bullet reasons grounded in the evidence.
3) A short counterfactual: when the user might consider the next higher/lower tier.
4) A plain table of key parameters you used.
"""

    return (
        header
        + "\n\n=== USER PROFILE (structured) ===\n"
        + user_sum
        + "\n\n=== HYBRID PREDICTION (rules + model) ===\n"
        + f"Source: {hybrid_pack['source']}\n"
        + f"Suggested Tier: {hybrid_pack['final_tier']}\n"
        + (f"Model Probabilities: {hybrid_pack['probabilities']}\n" if hybrid_pack['probabilities'] else "")
        + "\n=== RETRIEVAL EVIDENCE (Graph + Vector) ===\n"
        + rag_prompt
    )


def recommend_with_explanation(user: Dict[str,Any]) -> LLMResult:
    """
    End‑to‑end:
      1) rules+ML hybrid prediction
      2) GraphRAG evidence
      3) LLM explanation (multilingual if user['Language'] provided)
    """
    # 1) hybrid prediction (rule → ML fallback)
    hybrid_pack = hybrid_predict(user)

    # 2) build a concise search query from product + any issue keywords
    q = f"{user.get('ProductType','')} insurance for {user.get('Country','')}: "
    if user.get("HealthIssues"): q += f"exclusions for {user['HealthIssues']}, "
    if user.get("SmokerDrinker") == "Yes": q += "smoker, "
    if user.get("TripDurationDays"): q += f"travel {user['TripDurationDays']} days, "
    q = q.strip(", ")

    # 3) GraphRAG hybrid retrieve
    rag_pack = hybrid_retrieve(q, k_vec=6, k_graph_ctx=6)

    # 4) unified prompt and LLM completion
    lang = user.get("Language","English")
    prompt = build_unified_prompt(user, hybrid_pack, rag_pack, lang=lang)
    answer = llm_complete(prompt, lang=lang)

    return LLMResult(
        suggested_tier=hybrid_pack["final_tier"],
        model_source=hybrid_pack["source"],
        probabilities=hybrid_pack["probabilities"],
        explanation=answer,
        evidence_sources=rag_pack.get("vector_sources",[]),
        graph_facts=rag_pack.get("facts",[]),
        contexts=rag_pack.get("contexts",[]),
    )
