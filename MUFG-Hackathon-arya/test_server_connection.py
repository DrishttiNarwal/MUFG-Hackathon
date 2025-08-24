import requests
import time
import sys

def test_server_connection():
    base_url = "http://localhost:8000"
    max_retries = 3
    retry_delay = 2  # seconds

    print(f"Testing connection to {base_url}...")
    
    for i in range(max_retries):
        try:
            # Test health endpoint
            health_response = requests.get(f"{base_url}/health", timeout=5)
            print("\nHealth check response:")
            print(f"Status code: {health_response.status_code}")
            print(f"Response: {health_response.json()}")

            # Test recommend endpoint
            test_data = {
                "country": "INDIA",
                "policy_type": "HEALTH",
                "age": 30,
                "sum_assured": 500000,
                "smoker_drinker": "No",
                "num_diseases": 0,
                "diseases": ""
            }
            
            recommend_response = requests.post(
                f"{base_url}/recommend",
                json=test_data,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            print("\nRecommendation endpoint response:")
            print(f"Status code: {recommend_response.status_code}")
            if recommend_response.status_code == 200:
                print("Response:", recommend_response.json())
            else:
                print("Error response:", recommend_response.text)

            return True

        except requests.exceptions.ConnectionError as e:
            print(f"\nAttempt {i+1}/{max_retries}: Connection failed")
            print(f"Error: {str(e)}")
            if i < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("\nFailed to connect to server after all retries")
                return False

        except Exception as e:
            print(f"\nUnexpected error: {str(e)}")
            return False

if __name__ == "__main__":
    success = test_server_connection()
    sys.exit(0 if success else 1)
