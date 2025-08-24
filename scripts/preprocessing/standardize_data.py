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
        "sumsssured": "sumassured",   # fix typo
        "Sumsssured": "sumassured",
        "smokerdrinker": "smokerdrinker",
        "numdiseases": "numdiseases", 
        "annualpremium": "annualpremium",
        "priceofvehicle": "priceofvehicle",
        "ageofvehicle": "ageofvehicle",
        "typeofvehicle": "typeofvehicle",
        "propertyvalue": "propertyvalue",
        "propertyage": "propertyage",
        "propertytype": "propertytype",
        "propertysize": "propertysize",
        "destinationcountry": "destinationcountry",
        "tripdurationdays": "tripdurationdays",
        "existingmedicalcondition": "existingmedicalcondition",
        "healthcoverage": "healthcoverage", 
        "baggagecoverage": "baggagecoverage",
        "tripcancellationcoverage": "tripcancellationcoverage",
        "accidentcoverage": "accidentcoverage",
        "trippremium": "trippremium",
        "policytype": "policytype",
        "policytier": "policytier"
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
