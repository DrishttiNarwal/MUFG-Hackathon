import requests
import json

# Base URL for the FastAPI server
BASE_URL = "http://localhost:8000"

def print_test(name, response):
    print("\n" + "="*50)
    print(f"Testing: {name}")
    print("Status Code:", response.status_code)
    print("Response:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print("="*50)

# 1. Test Health Check
print("\nTesting Health Check...")
response = requests.get(f"{BASE_URL}/health")
print_test("Health Check", response)

# 2. Test Health Insurance Recommendation
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
response = requests.post(f"{BASE_URL}/recommend", json=health_data)
print_test("Health Insurance Recommendation", response)

# 3. Test Vehicle Insurance Recommendation
vehicle_data = {
    "country": "INDIA",
    "policy_type": "VEHICLE",
    "name": "Test User",
    "age": 35,
    "price_of_vehicle": 1500000,
    "age_of_vehicle": 0,
    "type_of_vehicle": "suv"
}
response = requests.post(f"{BASE_URL}/recommend", json=vehicle_data)
print_test("Vehicle Insurance Recommendation", response)

# 4. Test Multiple Recommendations
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
response = requests.post(f"{BASE_URL}/recommend_multiple", json=multiple_data)
print_test("Multiple Recommendations", response)

# 5. Test Australian Policies
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
response = requests.post(f"{BASE_URL}/recommend", json=aus_health_data)
print_test("Australian Health Insurance", response)
