import requests
import json
from typing import Dict, Any
from pprint import pprint

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("\n=== Health Check ===")
    pprint(response.json())
    return response.json()

def test_recommend(data: Dict[str, Any]):
    """Test the single recommendation endpoint"""
    response = requests.post(f"{BASE_URL}/recommend", json=data)
    print(f"\n=== Single Recommendation Test for {data['policy_type']} ===")
    print("Request:")
    pprint(data)
    print("\nResponse:")
    pprint(response.json())
    return response.json()

def test_recommend_multiple(data: Dict[str, Any]):
    """Test the multiple recommendations endpoint"""
    response = requests.post(f"{BASE_URL}/recommend_multiple", json=data)
    print("\n=== Multiple Recommendations Test ===")
    print("Request:")
    pprint(data)
    print("\nResponse:")
    pprint(response.json())
    return response.json()

def main():
    # Test 1: Health Check
    test_health()

    # Test 2: Health Insurance Recommendation
    health_data = {
        "country": "INDIA",
        "policy_type": "HEALTH",
        "name": "Test User",
        "age": 35,
        "policy_tier": "PREMIUM",
        "sum_assured": 500000,
        "smoker_drinker": "No",
        "num_diseases": 0,
        "diseases": "",
        "annual_premium": 12000
    }
    test_recommend(health_data)

    # Test 3: Vehicle Insurance Recommendation
    vehicle_data = {
        "country": "INDIA",
        "policy_type": "VEHICLE",
        "name": "Test User",
        "age": 35,
        "price_of_vehicle": 1500000,
        "age_of_vehicle": 0,
        "type_of_vehicle": "suv"
    }
    test_recommend(vehicle_data)

    # Test 4: Multiple Recommendations
    multiple_data = {
        "policies": [
            {
                "country": "INDIA",
                "policy_type": "HEALTH",
                "age": 35,
                "sum_assured": 500000,
                "smoker_drinker": "No",
                "num_diseases": 0
            },
            {
                "country": "INDIA",
                "policy_type": "VEHICLE",
                "age": 35,
                "price_of_vehicle": 1500000,
                "age_of_vehicle": 0,
                "type_of_vehicle": "suv"
            }
        ]
    }
    test_recommend_multiple(multiple_data)

    # Test 5: Australian Health Insurance
    aus_health_data = {
        "country": "AUSTRALIA",
        "policy_type": "HEALTH",
        "name": "Test User",
        "age": 40,
        "policy_tier": "GOLD",
        "sum_assured": 1000000,
        "smoker_drinker": "No",
        "num_diseases": 0,
        "annual_premium": 20000
    }
    test_recommend(aus_health_data)

    # Test 6: Australian Vehicle Insurance
    aus_vehicle_data = {
        "country": "AUSTRALIA",
        "policy_type": "VEHICLE",
        "name": "Test User",
        "age": 40,
        "price_of_vehicle": 3000000,
        "age_of_vehicle": 1,
        "type_of_vehicle": "car"
    }
    test_recommend(aus_vehicle_data)

if __name__ == "__main__":
    main()
