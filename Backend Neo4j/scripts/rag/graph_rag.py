# scripts/rag/graph_rag.py
from __future__ import annotations
import os, re, hashlib, argparse, time
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Use modern langchain-* packages; fall back if not installed
try:
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
except Exception:
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_chroma import Chroma


# -------------------------------
# Config
# -------------------------------
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.rag"))

NEO4J_URI       = os.getenv("NEO4J_URI")
NEO4J_USERNAME  = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD  = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE  = os.getenv("NEO4J_DATABASE", "neo4j")

CHROMA_DIR      = os.getenv("CHROMA_DIR", "../../vectorstore")
EMB_MODEL       = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# -------------------------------
# Init Chroma + Neo4j
# -------------------------------
embeddings = HuggingFaceEmbeddings(model_name=EMB_MODEL)
vectordb   = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


# -------------------------------
# Utils
# -------------------------------
_STOP = {"the","a","an","and","or","to","of","for","with","on","in","by"}

# Expanded domain-specific vocabulary for all products
_DOMAIN = [
    # Health / Life
    "pre-existing condition","waiting period","claim settlement","exclusion",
    "premium","co-payment","sum insured","deductible","grace period",
    "smoker","diabetes","cancer","maternity","cholesterol","hypertension",
    # Vehicle
    "idv","insured declared value","depreciation","accident","third party",
    "own damage","engine protection","zero depreciation","car","bike","truck",
    # Travel
    "baggage","trip cancellation","delay","hospitalization abroad",
    "medical evacuation","loss of passport","travel assistance",
    # House / Property
    "fire","flood","earthquake","theft","burglary","natural calamity",
    "property value","property age","apartment","bungalow","villa"
]

def extract_entities(text: str, top_k: int = 10) -> List[str]:
    """
    Extract domain-specific entities from text.
    Combines dictionary matches + regex capitalized phrases + keywords.
    """
    out = set()
    tl = text.lower()

    # Match from domain vocab
    for p in _DOMAIN:
        if p in tl:
            out.add(p)

    # Capitalized multi-word phrases (possible named entities)
    for m in re.finditer(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,3})\b", text):
        cand = m.group(0).strip()
        if cand.lower() not in _STOP and len(cand) > 2:
            out.add(cand)

    # Special-case keywords
    for t in re.findall(r"[A-Za-z][A-Za-z\-]{3,}", text):
        if t.lower() in {"diabetes","cancer","maternity","accident","hospital",
                         "baggage","fire","flood","idv","depreciation"}:
            out.add(t.capitalize())

    return list(out)[:top_k]


def md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


# -------------------------------
# Ingest: Chroma -> Neo4j
# -------------------------------
def ensure_schema() -> None:
    """Create idempotent constraints/indexes."""
    with driver.session(database=NEO4J_DATABASE) as s:
        s.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Chunk)  REQUIRE c.id   IS UNIQUE")
        s.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")
        s.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Source) REQUIRE s.path IS UNIQUE")

def _iter_chroma_batches(batch: int = 400):
    col = vectordb._collection
    total = col.count()
    for offset in range(0, total, batch):
        yield col.get(include=["documents","metadatas"], limit=batch, offset=offset)

def ingest_to_graph(limit: int | None = None, batch_size: int = 50) -> None:
    """Fast ingestion using batch UNWIND queries."""
    ensure_schema()
    processed = 0
    start_time = time.time()
    print(f"🚀 Starting ingestion (limit={limit or 'ALL'}) ...")

    with driver.session(database=NEO4J_DATABASE) as s:
        batch = []
        for page in _iter_chroma_batches():
            docs  = page.get("documents") or []
            metas = page.get("metadatas") or []
            for doc, meta in zip(docs, metas):
                if not doc:
                    continue
                source_path = (meta or {}).get("source", "unknown")
                chunk_id    = md5(source_path + "::" + doc[:512])
                preview     = doc[:1200]
                ents        = extract_entities(preview, top_k=12)

                batch.append({
                    "path": source_path,
                    "id": chunk_id,
                    "preview": preview,
                    "entities": ents
                })

                if len(batch) >= batch_size:
                    _flush_batch(s, batch)
                    processed += len(batch)
                    batch.clear()
                    elapsed = time.time() - start_time
                    print(f"⏱️  {processed} chunks in {elapsed:.1f} sec "
                          f"({processed/elapsed:.2f} chunks/sec)")
                    if limit and processed >= limit:
                        print(f"🎉 Done! Ingested {processed} chunks in {elapsed:.1f} seconds")
                        return

        if batch:
            _flush_batch(s, batch)
            processed += len(batch)

    total_time = time.time() - start_time
    print(f"🎉 Done! Ingested {processed} chunks in {total_time:.1f} seconds")

def _flush_batch(session, batch: List[Dict[str, Any]]):
    """Insert one batch into Neo4j via UNWIND."""
    session.run(
        """
        UNWIND $batch AS row
        MERGE (src:Source {path: row.path})
        MERGE (c:Chunk {id: row.id})
          ON CREATE SET c.preview = row.preview
        MERGE (src)-[:HAS_CHUNK]->(c)
        WITH row, c
        UNWIND row.entities AS ent
          MERGE (e:Entity {name: ent})
          MERGE (c)-[:MENTIONS]->(e)
        """,
        batch=batch
    )
    # For co-occurrence edges
    session.run(
        """
        UNWIND $batch AS row
        UNWIND row.entities AS a
        UNWIND row.entities AS b
        WITH a,b WHERE a<b
        MERGE (ea:Entity {name:a})
        MERGE (eb:Entity {name:b})
        MERGE (ea)-[:CO_OCCURS]->(eb)
        """,
        batch=batch
    )


# -------------------------------
# Retrieval
# -------------------------------
def query_graph_entities(entities: List[str], limit_ctx: int = 5) -> Tuple[List[Tuple[str,str,str]], List[str]]:
    if not entities:
        return [], []
    facts, ctxs = [], []
    with driver.session(database=NEO4J_DATABASE) as s:
        for e in entities:
            recs = s.run(
                """MATCH (x:Entity {name:$name})-[r]-(y)
                   RETURN x.name AS src, type(r) AS rel, coalesce(y.name, head(labels(y))) AS tgt
                   LIMIT $lim""", name=e, lim=limit_ctx
            )
            facts.extend([(r["src"], r["rel"], r["tgt"]) for r in recs])
            recs2 = s.run(
                """MATCH (e:Entity {name:$name})<-[:MENTIONS]-(c:Chunk)
                   RETURN c.preview AS pv LIMIT $lim""", name=e, lim=limit_ctx
            )
            ctxs.extend([r["pv"] for r in recs2 if r["pv"]])

    def dedupe(seq):
        seen=set(); out=[]
        for x in seq:
            key = x if isinstance(x, str) else tuple(x)
            if key not in seen:
                out.append(x); seen.add(key)
        return out

    return dedupe(facts), dedupe(ctxs)

def hybrid_retrieve(user_query: str, k_vec: int = 6, k_graph_ctx: int = 6) -> Dict[str, Any]:
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": k_vec})
    vdocs = retriever.get_relevant_documents(user_query)
    vec_ctx  = [d.page_content for d in vdocs]
    sources  = [d.metadata.get("source", "unknown") for d in vdocs]

    q_entities = extract_entities(user_query, top_k=10)
    facts, graph_ctx = query_graph_entities(q_entities, limit_ctx=k_graph_ctx)

    texts, seen = [], set()
    for t in (vec_ctx + graph_ctx):
        h = md5(t[:512])
        if h not in seen:
            texts.append(t.strip()); seen.add(h)
        if len(texts) >= (k_vec + k_graph_ctx): break

    return {
        "query": user_query,
        "entities": q_entities,
        "facts": facts,
        "contexts": texts,
        "vector_sources": sources
    }


# -------------------------------
# Prompt Builder
# -------------------------------
def build_prompt(pack: Dict[str, Any], prediction: str | None = None) -> str:
    facts_txt = "\n".join([f" - {a} —{r}→ {b}" for a,r,b in pack["facts"]]) or " - (no graph facts)"
    ctx_txt   = "\n\n".join([f"[CTX {i+1}] {c}" for i,c in enumerate(pack["contexts"])]) or "(no contexts)"
    src_txt   = "\n".join([f" - {s}" for s in pack["vector_sources"]]) or " - (n/a)"

    return f"""You are an insurance assistant. Use only the evidence below.

User question:
{pack['query']}

Model prediction (if any):
{prediction or 'N/A'}

Graph facts:
{facts_txt}

Evidence contexts (from policy PDFs):
{ctx_txt}

Top vector sources:
{src_txt}

Answer clearly. If something is not supported by evidence, say you don't know.
"""


# -------------------------------
# CLI
# -------------------------------
def main():
    parser = argparse.ArgumentParser(description="Minimal GraphRAG (Optimized)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ping", help="verify Neo4j connectivity")
    p_ing = sub.add_parser("ingest", help="ingest Chroma chunks into Neo4j")
    p_ing.add_argument("--limit", type=int, default=None)
    p_ing.add_argument("--batch", type=int, default=50, help="batch size for ingestion")
    p_q = sub.add_parser("query", help="hybrid retrieval (vector + graph)")
    p_q.add_argument("--q", type=str, required=True)
    p_q.add_argument("--kvec", type=int, default=6)
    p_q.add_argument("--kgraph", type=int, default=6)

    args = parser.parse_args()

    if args.cmd == "ping":
        driver.verify_connectivity()
        print("✅ Neo4j connectivity OK")
    elif args.cmd == "ingest":
        ingest_to_graph(limit=args.limit, batch_size=args.batch)
    elif args.cmd == "query":
        pack = hybrid_retrieve(args.q, k_vec=args.kvec, k_graph_ctx=args.kgraph)
        prompt = build_prompt(pack)
        print("\n=== ENTITIES ===")
        print(pack["entities"])
        print("\n=== PROMPT (feed to LLM) ===\n")
        print(prompt)


if __name__ == "__main__":
    main()
