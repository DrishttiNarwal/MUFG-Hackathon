# scripts/preprocessing/create_embeddings.py
# ============================
# Create Embeddings from PDFs (India + Australia)
# ============================

from __future__ import annotations
import shutil
from pathlib import Path

# Local import for text cleaning
from clean_text import clean_policy_text

from langchain_community.document_loaders import PyMuPDFLoader as PDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document


# --------------------
# Paths & Embeddings
# --------------------
PDF_DIR = Path("data/pdf")
VECTORSTORE_DIR = Path("vectorstore")  # root folder that will contain chroma_india / chroma_australia
VECTORSTORE_DIR.mkdir(exist_ok=True)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def process_pdfs(country: str) -> None:
    """Process PDFs for a given country and save embeddings with full debug logs."""
    country_path = PDF_DIR / country
    docs: list[Document] = []

    print("\n" + "=" * 60)
    print(f"🌍 Processing country: {country}")
    print(f"🔍 Looking in: {country_path.resolve()}")
    print("=" * 60)

    if not country_path.exists():
        print(f"❌ No folder found for {country}: {country_path}")
        return

    # 1) Load + clean per page
    for pdf_file in sorted(country_path.glob("*.pdf")):
        print(f"\n📄 Loading {pdf_file.name}")
        try:
            loader = PDFLoader(str(pdf_file))
            raw_docs = loader.load()
            print(f"   ➡️ Extracted {len(raw_docs)} raw pages")

            for i, d in enumerate(raw_docs, 1):
                cleaned = clean_policy_text(d.page_content)
                if cleaned.strip():
                    docs.append(
                        Document(
                            page_content=cleaned,
                            metadata={
                                **(d.metadata or {}),
                                "source": str(pdf_file),
                                "filename": pdf_file.name,
                                "country": country,
                                "page": i,
                            },
                        )
                    )
                else:
                    print(f"   ⚠️ Page {i} of {pdf_file.name} was empty after cleaning")

        except Exception as e:
            print(f"   ❌ Failed to load {pdf_file.name}: {e}")

    print(f"\n📑 Total usable pages collected: {len(docs)}")

    if not docs:
        print(f"❌ No text extracted from PDFs in {country_path}. STOPPING.")
        return

    # Show preview of first doc
    print("\n--- Sample cleaned document ---")
    print(docs[0].page_content[:500])
    print("...")

    # 2) Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    print(f"\n🧩 Total chunks created: {len(chunks)}")
    if chunks:
        print("--- Sample chunk ---")
        print(chunks[0].page_content[:300])
        print("...")

    # 3) Persist to Chroma
    db_path = VECTORSTORE_DIR / f"chroma_{country.lower()}"
    if db_path.exists():
        print(f"\n🗑️ Removing old embeddings at {db_path}")
        shutil.rmtree(db_path)

    try:
        db = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(db_path),
            collection_name=f"policies_{country.lower()}",
        )
        # Force materialize and check counts
        stats = db.get()
        print(f"\n💾 Persisted to {db_path}")
        print(f"📦 Collection now contains {len(stats['ids'])} documents")

    except Exception as e:
        print(f"❌ Error while persisting to Chroma: {e}")


def main() -> None:
    process_pdfs("india")
    process_pdfs("australia")


if __name__ == "__main__":
    main()
