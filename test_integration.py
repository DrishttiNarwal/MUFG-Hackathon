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
        "name", "age", "country", "policytype", "policy_tier", "sumassured", "smokerdrinker",
        "num_diseases", "diseases", "annual_premium",
        "priceofvehicle", "ageofvehicle", "typeofvehicle",
        "propertyvalue", "propertyage", "propertytype", "propertysizesqfeet",
        "destinationcountry", "tripdurationdays", "existing_medical_condition",
        "healthcoverage", "baggagecoverage", "tripcancellationcoverage", "accidentcoverage", "trippremium"
    ]
    
    # Check standardized columns
    print("Actual columns:", df.columns.tolist())
    print("All expected columns present:", all(col in df.columns for col in expected_cols))
    
    # Test prediction
    test_data = {
        "age": 30,
        "sumassured": 2000000,
        "smokerdrinker": "No",
        "num_diseases": 1,
        "diseases": "Hypertension"
    }
    
    result = predict("india", "health", test_data)
    print("\nPrediction result:", result)

if __name__ == "__main__":
    test_data_pipeline()
