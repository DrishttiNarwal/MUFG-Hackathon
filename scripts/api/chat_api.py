import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from scripts.recommendation.predict import predict_all
from scripts.rag.graph_rag import hybrid_retrieve
from scripts.llm.llm_client import generate_policy_explanation
from scripts.api.schemas import ChatRequest, ChatResponse, PolicyOption
from .pdf_utils import build_summary_pdf  # keep PDF code separate

# --------------------------
# Static files (frontend)
# --------------------------
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "web")

app = FastAPI(title="Insurance Chatbot", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
def root():
    with open(os.path.join(STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


# --------------------------
# Chat Endpoint
# --------------------------
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        # ✅ Access directly
        country = req.country.lower() if req.country else "australia"

        # 1. Predict policy options (per-country model)
        preds = predict_all(req.model_dump(), country=country)
        options = preds["options"]
        rec = preds["recommended"]

        # 2. Hybrid retrieval (GraphRAG)
        pack = hybrid_retrieve(req.query, k_vec=6, k_graph_ctx=6)

        # 3. Generate explanation
        answer = generate_policy_explanation(
            user_message=req.query,
            user_form=req.model_dump(),
            predictions=options,
            recommended=rec,
            graph_pack=pack,
            lang=getattr(req, "user_language", "en"),  # fallback to English
        )

        return ChatResponse(
            answer=answer,
            evidence=pack.get("contexts", []),
            predictions=[PolicyOption(**o) for o in options],
            recommended=rec,
            language=getattr(req, "user_language", "en"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------
# Summarize & PDF Download
# --------------------------
@app.post("/summarize")
def summarize(req: ChatRequest):
    try:
        country = req.country.lower() if req.country else "australia"

        preds = predict_all(req.model_dump(), country=country)
        options = preds["options"]
        rec = preds["recommended"]

        pack = hybrid_retrieve(req.query, k_vec=6, k_graph_ctx=6)

        explanation = generate_policy_explanation(
            user_message=req.query,
            user_form=req.model_dump(),
            predictions=options,
            recommended=rec,
            graph_pack=pack,
            lang=getattr(req, "user_language", "en"),
        )

        pdf_path = build_summary_pdf(options, rec, explanation)
        return FileResponse(pdf_path, filename="recommendation_summary.pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
