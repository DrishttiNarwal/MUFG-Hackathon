# ============================
# Normalize Standardized Dataset
# ============================

from __future__ import annotations
from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "processed"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# Feature schema based on your new dataset
NUMERIC = [
    "Age", "AnnualPremium", "SumInsured",
    "PriceOfVehicle", "AgeOfVehicle",
    "TripDurationDays", "PropertyValue", "PropertyAge", "PropertySizeSqFeet"
]

CATEGORICAL = [
    "Country", "ProductType", "SmokerDrinker", "HealthIssues",
    "TypeOfVehicle", "DestinationCountry", "TravelPurpose",
    "ExistingMedicalCondition", "HealthCoverage", "BaggageCoverage",
    "TripCancellationCoverage", "AccidentCoverage", "PropertyType"
]

TARGET = "Tier"

def build_preprocessor():
    num_pipe = Pipeline(steps=[
        ("impute", SimpleImputer(strategy="median")),   # handle null numerics
        ("scale", RobustScaler())
    ])
    cat_pipe = Pipeline(steps=[
        ("impute", SimpleImputer(strategy="most_frequent")),  # handle null categoricals
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])
    pre = ColumnTransformer(
        transformers=[
            ("num", num_pipe, NUMERIC),
            ("cat", cat_pipe, CATEGORICAL),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )
    return pre

def prepare_datasets(standardized_parquet: Path | None = None):
    if standardized_parquet is None:
        standardized_parquet = PROCESSED_DIR / "standardized_india.parquet"
    df = pd.read_parquet(standardized_parquet)

    # Classification target: Tier
    clf_df = df.dropna(subset=[TARGET]).copy()
    y = clf_df[TARGET].astype(str)
    X = clf_df[NUMERIC + CATEGORICAL]

    # Build and save preprocessor
    pre = build_preprocessor()
    joblib.dump(pre, ARTIFACTS_DIR / "preprocessor.joblib")

    # Train/val/test split
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
    )

    # Save splits
    X_train.to_parquet(PROCESSED_DIR / "X_train.parquet", index=False)
    X_val.to_parquet(PROCESSED_DIR / "X_val.parquet", index=False)
    X_test.to_parquet(PROCESSED_DIR / "X_test.parquet", index=False)
    y_train.to_frame("target").to_parquet(PROCESSED_DIR / "y_train.parquet", index=False)
    y_val.to_frame("target").to_parquet(PROCESSED_DIR / "y_val.parquet", index=False)
    y_test.to_frame("target").to_parquet(PROCESSED_DIR / "y_test.parquet", index=False)

    print(f"✅ Saved train/val/test splits → {PROCESSED_DIR}")
    print(f"✅ Preprocessor saved → {ARTIFACTS_DIR/'preprocessor.joblib'}")

if __name__ == "__main__":
    prepare_datasets()
