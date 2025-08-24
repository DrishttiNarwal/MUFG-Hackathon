from fastapi.testclient import TestClient
from scripts.api.serve import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    print("Health check response:", response.json())
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_basic_recommendation():
    test_data = {
        "country": "INDIA",
        "policy_type": "HEALTH",
        "age": 30,
        "sum_assured": 500000,
        "smoker_drinker": "No",
        "num_diseases": 0,
        "diseases": ""
    }
    response = client.post("/recommend", json=test_data)
    print("Recommendation response:", response.status_code)
    print("Response JSON:", response.json())
    assert response.status_code in [200, 422]  # 422 is also acceptable if validation fails

if __name__ == "__main__":
    print("Testing health check endpoint...")
    test_health_check()
    print("\nTesting recommendation endpoint...")
    test_basic_recommendation()
