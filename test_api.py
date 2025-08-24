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
    print(f"\n=== Single Recommendation Test for {data['policytype']} ===")
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
        "policytype": "HEALTH",
        "name": "Test User",
        "age": 35,
        "policy_tier": "PREMIUM",
        "sumassured": 500000,
        "smokerdrinker": "No",
        "num_diseases": 0,
        "diseases": "",
        "annual_premium": 12000
    }
    test_recommend(health_data)

    # Test 3: Vehicle Insurance Recommendation
    vehicle_data = {
        "country": "INDIA",
        "policytype": "VEHICLE",
        "name": "Test User",
        "age": 35,
        "priceofvehicle": 1500000,
        "ageofvehicle": 0,
        "typeofvehicle": "suv"
    }
    test_recommend(vehicle_data)

    # Test 4: Multiple Recommendations
    multiple_data = {
        "policies": [
            {
                "country": "INDIA",
                "policytype": "HEALTH",
                "age": 35,
                "sumassured": 500000,
                "smokerdrinker": "No",
                "num_diseases": 0
            },
            {
                "country": "INDIA",
                "policytype": "VEHICLE",
                "age": 35,
                "priceofvehicle": 1500000,
                "ageofvehicle": 0,
                "typeofvehicle": "suv"
            }
        ]
    }
    test_recommend_multiple(multiple_data)

    # Test 5: Australian Health Insurance
    aus_health_data = {
        "country": "AUSTRALIA",
        "policytype": "HEALTH",
        "name": "Test User",
        "age": 40,
        "policy_tier": "GOLD",
        "sumassured": 1000000,
        "smokerdrinker": "No",
        "num_diseases": 0,
        "annual_premium": 20000
    }
    test_recommend(aus_health_data)

    # Test 6: Australian Vehicle Insurance
    aus_vehicle_data = {
        "country": "AUSTRALIA",
        "policytype": "VEHICLE",
        "name": "Test User",
        "age": 40,
        "priceofvehicle": 3000000,
        "ageofvehicle": 1,
        "typeofvehicle": "car"
    }
    test_recommend(aus_vehicle_data)

if __name__ == "__main__":
    main()
