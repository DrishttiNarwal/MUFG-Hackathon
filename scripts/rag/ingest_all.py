"""
Full ingestion of insurance dataset into Neo4j (Parquet-ready)
With checkpointing + smaller batches (50 rows)
Handles ALL policy types (Health, Life, Vehicle, House, Travel)
"""

import os
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase
from typing import List, Dict

# ============================
# Env + Neo4j setup
# ============================
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

if not (NEO4J_URI and NEO4J_USERNAME and NEO4J_PASSWORD):
    raise RuntimeError("Missing Neo4j env vars. Please set NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD.")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# ============================
# Input data (Parquet paths)
# ============================
DATA_PATHS = {
    "india":     "processed/standardized_india.parquet",
    "australia": "processed/standardized_australia.parquet",
}

# ============================
# Helpers
# ============================
def clean_val(val):
    """Normalize blanks/NaNs to None, trim strings."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    if s.lower() in {"nan", "na", "none", ""}:
        return None
    return s

def _read_table(path: str) -> pd.DataFrame:
    """Read parquet with CSV fallback."""
    if path.lower().endswith(".parquet"):
        return pd.read_parquet(path)
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.read_csv(path)

# ============================
# Batch insert
# ============================
def _batch_ingest(tx, batch: List[Dict]):
    tx.run(
        """
        UNWIND $batch AS row

        // --- Core Policy ---
        MERGE (p:Policy {id: row.id})
        SET p.country = row.country,
            p.policytype = row.policytype,
            p.policy_tier = row.policy_tier,
            p.sumassured = row.sumassured,
            p.annual_premium = row.annual_premium

        // --- Home Country node + link ---
        FOREACH (_ IN CASE WHEN row.home_country IS NOT NULL THEN [1] ELSE [] END |
            MERGE (hc:Country {name: row.home_country})
            MERGE (p)-[:APPLICABLE_IN]->(hc)
        )

        // --- User (policy holder) ---
        FOREACH (_ IN CASE WHEN row.name IS NOT NULL OR row.age IS NOT NULL OR row.smokerdrinker IS NOT NULL THEN [1] ELSE [] END |
            MERGE (u:User {name: coalesce(row.name, row.id)})
            SET u.country = row.home_country,
                u.age = row.age,
                u.smokerdrinker = row.smokerdrinker
            MERGE (u)-[:HOLDS]->(p)
        )

        // --- Health/Life: Diseases ---
        FOREACH (d IN row.diseases |
            MERGE (dis:Disease {name: d})
            MERGE (p)-[:COVERS]->(dis)
        )

        // --- Vehicle ---
        FOREACH (_ IN CASE WHEN row.priceofvehicle IS NOT NULL OR row.typeofvehicle IS NOT NULL OR row.ageofvehicle IS NOT NULL THEN [1] ELSE [] END |
            MERGE (v:Vehicle {type: coalesce(row.typeofvehicle, "Unknown")})
            SET v.price = row.priceofvehicle,
                v.age = row.ageofvehicle
            MERGE (p)-[:COVERS]->(v)
        )

        // --- House / Property ---
        FOREACH (_ IN CASE WHEN row.propertyvalue IS NOT NULL OR row.propertytype IS NOT NULL OR row.propertyage IS NOT NULL OR row.propertysize IS NOT NULL THEN [1] ELSE [] END |
            MERGE (h:House {type: coalesce(row.propertytype, "Unknown")})
            SET h.value = row.propertyvalue,
                h.age = row.propertyage,
                h.size_sqft = row.propertysize
            MERGE (p)-[:COVERS]->(h)
        )

        // --- Travel ---
        FOREACH (_ IN CASE WHEN row.destinationcountry IS NOT NULL OR row.trip_duration IS NOT NULL OR row.trippremium IS NOT NULL THEN [1] ELSE [] END |
            MERGE (t:Trip {duration: coalesce(row.trip_duration, "NA")})
            SET t.existing_condition = row.existing_medical_condition,
                t.healthcoverage = row.healthcoverage,
                t.baggagecoverage = row.baggagecoverage,
                t.trip_cancellation = row.trip_cancellation,
                t.accidentcoverage = row.accidentcoverage,
                t.trippremium = row.trippremium
            MERGE (p)-[:HAS_TRIP]->(t)
            FOREACH (_2 IN CASE WHEN row.destinationcountry IS NOT NULL THEN [1] ELSE [] END |
                MERGE (dest:Country {name: row.destinationcountry})
                MERGE (t)-[:DESTINATION]->(dest)
            )
        )
        """,
        batch=batch
    )

# ============================
# Checkpoint helpers
# ============================
def _checkpoint_file(country_key: str) -> str:
    os.makedirs("checkpoints", exist_ok=True)
    return os.path.join("checkpoints", f"{country_key}.txt")

def _save_checkpoint(country_key: str, row_idx: int):
    """Save last inserted row index."""
    fname = _checkpoint_file(country_key)
    with open(fname, "w") as f:
        f.write(str(row_idx))

# ============================
# Ingest one DataFrame
# ============================
def _ingest_df(country_key: str, df: pd.DataFrame, batch_size: int = 25):
    df.columns = [c.strip() for c in df.columns]

    total_rows = len(df)
    print(f"📊 Rows to ingest for {country_key}: {total_rows}")

    # Always reset checkpoint at the start (force fresh ingestion)
    _save_checkpoint(country_key, 0)
    start_idx = 0
    print(f"⏩ Starting fresh ingestion for {country_key}...")

    inserted = start_idx
    with driver.session(database=NEO4J_DATABASE) as session:
        batch = []
        for idx, row in df.iloc[start_idx:].iterrows():
            diseases = []
            if "Diseases" in df.columns and pd.notna(row.get("Diseases")):
                diseases = [
                    d.strip() for d in str(row.get("Diseases")).split(",")
                    if d and str(d).strip().lower() not in {"nan", "na", "none", ""}
                ]

            rec = {
                "id": f"{country_key}_{idx}",
                "country": country_key,
                "home_country": clean_val(row.get("Country")),

                # User / core
                "name": clean_val(row.get("Name")),
                "age": clean_val(row.get("Age")),
                "policytype": clean_val(row.get("Policy Type")),
                "policy_tier": clean_val(row.get("Policy Tier")),
                "sumassured": clean_val(row.get("Sum Assured")),
                "annual_premium": clean_val(row.get("Annual Premium")),
                "smokerdrinker": clean_val(row.get("SmokerDrinker")),
                "diseases": diseases,

                # Vehicle
                "priceofvehicle": clean_val(row.get("PriceOfVehicle")),
                "ageofvehicle": clean_val(row.get("AgeOfVehicle")),
                "typeofvehicle": clean_val(row.get("TypeOfVehicle")),

                # House / Property
                "propertyvalue": clean_val(row.get("PropertyValue")),
                "propertyage": clean_val(row.get("PropertyAge")),
                "propertytype": clean_val(row.get("PropertyType")),
                "propertysize": clean_val(row.get("PropertySizeSqFeet")),

                # Travel
                "destinationcountry": clean_val(row.get("DestinationCountry")),
                "trip_duration": clean_val(row.get("tripdurationdays")),
                "existing_medical_condition": clean_val(row.get("ExistingMedicalCondition")),
                "healthcoverage": clean_val(row.get("HealthCoverage")),
                "baggagecoverage": clean_val(row.get("BaggageCoverage")),
                "trip_cancellation": clean_val(row.get("TripCancellationCoverage")),
                "accidentcoverage": clean_val(row.get("AccidentCoverage")),
                "trippremium": clean_val(row.get("TripPremium")),
            }

            batch.append(rec)
            if len(batch) >= batch_size:
                session.execute_write(_batch_ingest, batch)
                inserted += len(batch)
                _save_checkpoint(country_key, inserted)
                print(f"   ✅ Inserted {inserted}/{total_rows} rows...")
                batch = []

        if batch:
            session.execute_write(_batch_ingest, batch)
            inserted += len(batch)
            _save_checkpoint(country_key, inserted)
            print(f"   ✅ Inserted {inserted}/{total_rows} rows... (final batch)")

# ============================
# Post-ingest quick verification
# ============================
def _post_verify():
    with driver.session() as session:
        res = session.run("""
        CALL () {
            MATCH (u:User) RETURN 'User' AS label, count(u) AS count
            UNION
            MATCH (p:Policy) RETURN 'Policy' AS label, count(p) AS count
            UNION
            MATCH (c:Country) RETURN 'Country' AS label, count(c) AS count
        }
        RETURN label, count
        """)
        for record in res:
            print(f"✅ {record['label']}: {record['count']}")

        sample = session.run("MATCH (p:Policy) RETURN p.id AS id, p.policytype AS type LIMIT 5")
        print("\n🔍 Sample policies:")
        for r in sample:
            print(f"   {r['id']} ({r['type']})")

# ============================
# Main
# ============================
def main():
    for key, path in DATA_PATHS.items():
        print("\n" + "="*28 + f" INGEST START: {key.upper()} " + "="*28)
        if not os.path.exists(path):
            print(f"⚠️ Missing data for {key}: {path}")
            print("="*70)
            continue

        print(f"📂 Reading: {path}")
        df = _read_table(path)
        _ingest_df(key, df, batch_size=25)
        print("="*28 + f" INGEST COMPLETE: {key.upper()} " + "="*28)

    _post_verify()
    print("\n🎉 All data ingested into Neo4j with checkpointing + small batches.")

if __name__ == "__main__":
    main()
