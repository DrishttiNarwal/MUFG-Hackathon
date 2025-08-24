import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")
database = os.getenv("NEO4J_DATABASE")

print("🔎 DEBUG VALUES:")
print("URI:", uri)
print("USER:", user)
print("DB:", database)

def test_connection(uri, user, password, database):
    try:
        print(f"🔗 Trying URI: {uri}")
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session(database=database) as session:
            result = session.run("RETURN 'Neo4j connection successful!' AS msg")
            print("✅", result.single()["msg"])
        driver.close()
        return True
    except Exception as e:
        print("❌ Error:", str(e))
        return False

# Try original URI
if not test_connection(uri, user, password, database):
    # Fallback: use bolt+s
    alt_uri = uri.replace("neo4j+s", "bolt+s")
    print(f"⚠ Switching to: {alt_uri}")
    test_connection(alt_uri, user, password, database)
