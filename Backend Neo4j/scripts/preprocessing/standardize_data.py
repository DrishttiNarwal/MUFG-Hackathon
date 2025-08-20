# ============================
# Standardize Insurance Dataset (India Example)
# ============================

import pandas as pd
from pathlib import Path

def preprocess_dataset(path, country_tag):
    # Load dataset (already cleaned with correct schema)
    df = pd.read_csv(path)

    # Ensure Country column exists
    if "Country" not in df.columns:
        df["Country"] = country_tag

    return df

def main():
    Path("processed").mkdir(exist_ok=True)

    # India dataset (already cleaned schema)
    india = preprocess_dataset("data/csv/India_data.csv", "India")

    # Save standardized dataset
    india.to_parquet("processed/standardized_india.parquet", index=False)

    print("✅ Saved standardized dataset for India at processed/standardized_india.parquet")

if __name__ == "__main__":
    main()
