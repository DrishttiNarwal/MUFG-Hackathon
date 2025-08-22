"""
GraphRAG pipeline:
- Chroma (vectorstore) with collections per country
- Neo4j (graph database)
- HuggingFace embeddings

Retrieves: context (PDF/Vectorstore) + graph facts (Neo4j) for LLM
"""

import os
import argparse
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# ============================
# Load environment variables
# ============================
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

CHROMA_ROOT = os.getenv("CHROMA_ROOT", "vectorstore")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# ============================
# Embeddings + Neo4j Driver
# ============================
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# ============================
# Helpers
# ============================

def _load_chroma(country: str):
    """Load country-specific Chroma collection created by create_embeddings.py"""
    db_path = f"{CHROMA_ROOT}/chroma_{country.lower()}"
    collection_name = f"policies_{country.lower()}"
    print(f"📂 Loading {country} Chroma: {db_path} (collection={collection_name})")
    return Chroma(
        persist_directory=db_path,
        embedding_function=embeddings,
        collection_name=collection_name,
    )

def ping():
    """Check Neo4j connectivity"""
    try:
        driver.verify_connectivity()
        print("✅ Neo4j connectivity OK")
    except Exception as e:
        print(f"❌ Neo4j connection error: {e}")

def fetch_related_nodes(user_q: str, country: str, limit: int = 8):
    """
    Query Neo4j for relevant policy facts.
    - Extracts tier/type/disease hints from the query for precise filtering.
    - Falls back to broad OR text match across connected nodes.
    """
    # Lightweight hints
    q_low = user_q.lower()
    tiers = ["basic", "standard", "gold", "premium"]
    types = ["health", "life", "vehicle", "car", "home", "house", "travel"]

    tier_hint = next((t for t in tiers if t in q_low), None)
    type_hint = next((t for t in types if t in q_low), None)

    # crude disease extraction: anything that looks like a single medical word
    # (you can swap this with a proper list)
    disease_hint = None
    for key in ["diabetes", "hypertension", "asthma", "thyroid", "heart"]:
        if key in q_low:
            disease_hint = key
            break

    cypher = """
    MATCH (p:Policy {country:$country})
    OPTIONAL MATCH (p)-[:HOLDS]-(u:User)
    OPTIONAL MATCH (p)-[:COVERS]->(d:Disease)
    OPTIONAL MATCH (p)-[:COVERS]->(v:Vehicle)
    OPTIONAL MATCH (p)-[:COVERS]->(h:House)
    OPTIONAL MATCH (p)-[:HAS_TRIP]->(t:Trip)
    OPTIONAL MATCH (t)-[:DESTINATION]->(dest:Country)
    OPTIONAL MATCH (p)-[:APPLICABLE_IN]->(c:Country)
    WHERE
      (
        toLower(p.policy_type) CONTAINS toLower($q) OR
        toLower(p.policy_tier)  CONTAINS toLower($q) OR
        toLower(coalesce(p.sum_assured, ""))     CONTAINS toLower($q) OR
        toLower(coalesce(p.annual_premium, ""))  CONTAINS toLower($q) OR
        toLower(coalesce(u.name, ""))            CONTAINS toLower($q) OR
        toLower(coalesce(u.smoker_drinker, ""))  CONTAINS toLower($q) OR
        toLower(coalesce(d.name, ""))            CONTAINS toLower($q) OR
        toLower(coalesce(v.type, ""))            CONTAINS toLower($q) OR
        toLower(coalesce(h.type, ""))            CONTAINS toLower($q) OR
        toLower(coalesce(c.name, ""))            CONTAINS toLower($q) OR
        toLower(coalesce(dest.name, ""))         CONTAINS toLower($q) OR
        toLower(coalesce(t.existing_condition, "")) CONTAINS toLower($q)
      )
      AND ($tier IS NULL OR toLower(p.policy_tier) = toLower($tier))
      AND (
        $ptype IS NULL OR
        toLower(p.policy_type) = toLower($ptype) OR
        ($ptype = 'car' AND toLower(p.policy_type) = 'vehicle') OR
        ($ptype = 'house' AND toLower(p.policy_type) = 'home')
      )
      AND (
        $disease IS NULL OR EXISTS {
          MATCH (p)-[:COVERS]->(dx:Disease)
          WHERE toLower(dx.name) CONTAINS toLower($disease)
        }
      )
    RETURN DISTINCT
      p.id AS policy_id,
      p.policy_type AS type,
      p.policy_tier AS tier,
      p.annual_premium AS premium,
      u.age AS age,
      u.smoker_drinker AS smoker,
      collect(DISTINCT d.name) AS diseases,
      v.type AS vehicle,
      h.type AS house,
      c.name AS country,
      dest.name AS trip_dest
    ORDER BY CASE WHEN $tier IS NOT NULL AND toLower(p.policy_tier)=toLower($tier) THEN 0 ELSE 1 END,
             CASE WHEN $ptype IS NOT NULL AND toLower(p.policy_type) IN [toLower($ptype),
                     CASE WHEN $ptype='car' THEN 'vehicle' WHEN $ptype='house' THEN 'home' ELSE $ptype END] THEN 0 ELSE 1 END,
             policy_id
    LIMIT $limit
    """
    try:
        records, _, _ = driver.execute_query(
            cypher,
            q=user_q,
            country=country,
            tier=tier_hint,
            ptype=type_hint,
            disease=disease_hint,
            limit=limit,
            database_=NEO4J_DATABASE,
        )
        return [dict(r) for r in records]
    except Exception as e:
        print(f"❌ Neo4j query failed: {e}")
        return []


def query_for_context(user_query: str, country: str = "india", k: int = 5, use_graph: bool = True):
    """
    Retrieve from Chroma + Neo4j, return dict for LLM:
    { "contexts": <pdf text>, "graph": <facts> }
    """
    # --- Load Chroma ---
    db = _load_chroma(country)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": k})
    docs = retriever.invoke(user_query)
    contexts = "\n\n".join([d.page_content for d in docs]) if docs else ""

    # --- Query Neo4j ---
    graph_text = ""
    if use_graph:
        facts = fetch_related_nodes(user_query, country)
        if facts:
            graph_lines = []
            for f in facts:
                line = f"Policy {f.get('policy_id')} | {f.get('tier')} {f.get('type')} | Premium: {f.get('premium')}"
                if f.get("country"):
                    line += f" | Country: {f['country']}"
                if f.get("diseases"):
                    line += f" | Diseases: {', '.join([d for d in f['diseases'] if d])}"
                if f.get("vehicle"):
                    line += f" | Vehicle: {f['vehicle']}"
                if f.get("house"):
                    line += f" | House: {f['house']}"
                if f.get("trip_dest"):
                    line += f" | TripDest: {f['trip_dest']}"
                graph_lines.append(line)
            graph_text = "\n".join(graph_lines)
        else:
            graph_text = "⚠️ No Neo4j facts retrieved."

    # --- Fallback ---
    if not contexts and not graph_text:
        graph_text = "⚠️ No context available (both Chroma & Neo4j empty)."

    return {"contexts": contexts, "graph": graph_text}

# ============================
# CLI (for debugging)
# ============================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GraphRAG CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("ping")

    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("--q", type=str, required=True)
    query_parser.add_argument("--country", type=str, default="india", help="india | australia")
    query_parser.add_argument("--k", type=int, default=5)
    query_parser.add_argument("--no-graph", action="store_true", help="Disable Neo4j enrichment")

    args = parser.parse_args()

    if args.command == "ping":
        ping()
    elif args.command == "query":
        result = query_for_context(
            user_query=args.q,
            country=args.country,
            k=args.k,
            use_graph=not args.no_graph
        )
        print("\n=== Top Contexts (Vectorstore/PDF) ===")
        print((result["contexts"][:1000] + "...") if result["contexts"] else "⚠️ No Chroma context.")
        print("\n=== Graph Facts (Neo4j) ===")
        print(result["graph"])
    else:
        parser.print_help()
