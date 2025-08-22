# ============================
# Clean & Standardize Insurance Datasets
# ============================

import pandas as pd
from pathlib import Path

def clean_dataset(input_path: str, output_path: str, country_tag: str):
    # Load dataset
    df = pd.read_csv(input_path)

    # --- Fix known typos and standardize column names ---
    col_rename = {
        "sumsssured": "sum_assured",   # fix typo
        "Sumsssured": "sum_assured",
        "smokerdrinker": "smoker_drinker",
        "numdiseases": "num_diseases",
        "annualpremium": "annual_premium",
        "priceofvehicle": "price_of_vehicle",
        "ageofvehicle": "age_of_vehicle",
        "typeofvehicle": "type_of_vehicle",
        "propertyvalue": "property_value", 
        "propertyage": "property_age",
        "propertytype": "property_type",
        "propertysize": "property_size_sq_feet",
        "destinationcountry": "destination_country",
        "tripdurationdays": "trip_duration_days",
        "existingmedicalcondition": "existing_medical_condition",
        "healthcoverage": "health_coverage",
        "baggagecoverage": "baggage_coverage",
        "tripcancellationcoverage": "trip_cancellation_coverage",
        "accidentcoverage": "accident_coverage",
        "trippremium": "trip_premium",
        "policytype": "policy_type",
        "policytier": "policy_tier"
    }

    # Ensure all column names are lowercase first
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Then apply the standardized naming
    df.rename(columns=col_rename, inplace=True)

    # --- Ensure country column exists ---
    if "country" not in df.columns:
        df["country"] = country_tag.lower()

    # --- Convert all string values to lowercase ---
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip().str.lower()

    # --- Save cleaned CSV ---
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"✅ Cleaned dataset saved: {output_path}")
    return df


def main():
    # India dataset
    clean_dataset(
        "data\csv\INDIA.csv",
        "processed/standardized_india.csv",
        "india"
    )

    # Australia dataset
    clean_dataset(
        "data\csv\AUSTRALIA.csv",   # ✅ input file
        "processed/standardized_australia.csv",  # ✅ output file
        "australia"
    )



if __name__ == "__main__":
    main()
