import pandas as pd
from pathlib import Path
import shutil

def prepare_datasets():
    base_dir = Path(__file__).resolve().parents[2]
    data_dir = base_dir / "Data" / "Latest Generated csv Dataset"
    processed_dir = base_dir / "processed"
    
    # Create processed directory
    processed_dir.mkdir(exist_ok=True)
    
    # Process Indian dataset
    print("\nProcessing Indian dataset...")
    india_df = pd.read_csv(data_dir / "INDIAN-DATASET.csv")
    india_df['country'] = 'INDIA'
    india_df.columns = india_df.columns.str.lower().str.strip()
    india_df = india_df.rename(columns={
        'policy type': 'policytype',
        'policy tier': 'policytier',
        'sum assured': 'sumassured',
        'annual premium': 'annualpremium',
        'property size sq feet': 'propertysize',
    })
    india_df.to_csv(processed_dir / "standardized_india.csv", index=False)
    print("Indian dataset processed and saved")

    # Process Australian dataset
    print("\nProcessing Australian dataset...")
    australia_df = pd.read_csv(data_dir / "AUSTRALIAN - DATASET.csv")
    australia_df['country'] = 'AUSTRALIA'
    australia_df.columns = australia_df.columns.str.lower().str.strip()
    australia_df = australia_df.rename(columns={
        'policy type': 'policytype',
        'policy tier': 'policytier',
        'sum assured': 'sumassured',
        'annual premium': 'annualpremium',
        'property size sq feet': 'propertysize',
    })
    australia_df.to_csv(processed_dir / "standardized_australia.csv", index=False)
    print("Australian dataset processed and saved")

    # Clear existing artifacts
    artifacts_dir = base_dir / "artifacts"
    if artifacts_dir.exists():
        shutil.rmtree(artifacts_dir)
    artifacts_dir.mkdir(exist_ok=True)
    print("\nArtifacts directory cleared and recreated")

if __name__ == "__main__":
    print("Starting data preparation...")
    prepare_datasets()
    print("\nData preparation complete!")
