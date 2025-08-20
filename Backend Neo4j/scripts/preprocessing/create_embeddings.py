# create_embeddings.py
from __future__ import annotations
from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from .clean_text import clean_policy_text
from .multilingual_handler import normalize_multilingual
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = PROJECT_ROOT / "data" / "pdf"
VSTORE_DIR = PROJECT_ROOT / "vectorstore"
VSTORE_DIR.mkdir(parents=True, exist_ok=True)

EMB_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pieces = []
    for p in reader.pages:
        pieces.append(p.extract_text() or "")
    return "\n".join(pieces)

def iter_policy_docs():
    for path in PDF_DIR.rglob("*.pdf"):
        yield path

def run_embedding():
    docs = []
    for pdf in iter_policy_docs():
        raw = extract_pdf_text(pdf)
        # multilingual normalization (keep original; use ascii for retrieval robustness)
        norm = normalize_multilingual(raw)
        cleaned = clean_policy_text(norm["original"])
        if not cleaned:
            continue
        docs.append({"source": str(pdf.relative_to(PROJECT_ROOT)), "content": cleaned})

    if not docs:
        print("No documents found under data/pdf")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts, metas = [], []
    for d in docs:
        for chunk in splitter.split_text(d["content"]):
            texts.append(chunk)
            metas.append({"source": d["source"]})

    embeddings = HuggingFaceEmbeddings(model_name=EMB_MODEL)
    _ = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metas,
        persist_directory=str(VSTORE_DIR),
    )
    print(f"✅ Embedded {len(texts)} chunks from {len(docs)} policy PDFs → {VSTORE_DIR}")

if __name__ == "__main__":
    run_embedding()
