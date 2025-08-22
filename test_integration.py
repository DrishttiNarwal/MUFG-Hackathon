import pandas as pd
from scripts.preprocessing.standardize_data import clean_dataset
from scripts.preprocessing.normalize_data import prepare_datasets
from scripts.recommendation.predict import predict

def test_data_pipeline():
    # Test standardization
    df = clean_dataset(
        "data/csv/INDIA.csv",
        "processed/standardized_india.csv", 
        "india"
    )
    
    # Verify column standardization
    expected_cols = [
        "name", "age", "country", "policy_type", "policy_tier", "sum_assured", "smoker_drinker",
        "num_diseases", "diseases", "annual_premium",
        "price_of_vehicle", "age_of_vehicle", "type_of_vehicle",
        "property_value", "property_age", "property_type", "property_size_sq_feet",
        "destination_country", "trip_duration_days", "existing_medical_condition",
        "health_coverage", "baggage_coverage", "trip_cancellation_coverage", "accident_coverage", "trip_premium"
    ]
    
    # Check standardized columns
    print("Actual columns:", df.columns.tolist())
    print("All expected columns present:", all(col in df.columns for col in expected_cols))
    
    # Test prediction
    test_data = {
        "age": 30,
        "sum_assured": 2000000,
        "smoker_drinker": "No",
        "num_diseases": 1,
        "diseases": "Hypertension"
    }
    
    result = predict("india", "health", test_data)
    print("\nPrediction result:", result)

if __name__ == "__main__":
    test_data_pipeline()
