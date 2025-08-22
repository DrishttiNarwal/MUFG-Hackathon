# ============================
# Normalize Standardized Dataset (Block Split per Tier)
# ============================

from __future__ import annotations
from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "processed"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# Schema 
NUMERIC = [
    "age", "annual_premium", "sum_assured",
    "num_diseases", "price_of_vehicle", "age_of_vehicle", 
    "trip_duration_days", "property_value", "property_age", "property_size_sq_feet",
    "trip_premium"
]

CATEGORICAL = [
    "country", "policy_type", "smoker_drinker", "diseases",
    "type_of_vehicle", "destination_country", "existing_medical_condition",
    "health_coverage", "baggage_coverage",
    "trip_cancellation_coverage", "accident_coverage", "property_type"
]

TARGET = "policy_tier"

# ----------------------------
# Preprocessor
# ----------------------------
def build_preprocessor():
    num_pipe = Pipeline(steps=[
        ("impute", SimpleImputer(strategy="median")),  # keep NaN safe
        ("scale", RobustScaler())
    ])
    cat_pipe = Pipeline(steps=[
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])
    return ColumnTransformer(
        transformers=[
            ("num", num_pipe, NUMERIC),
            ("cat", cat_pipe, CATEGORICAL),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )

# ----------------------------
# Block Splitter
# ----------------------------
def block_split(df, block_size=500, train=0.7, val=0.15, test=0.15):
    train_rows, val_rows, test_rows = [], [], []
    
    for start in range(0, len(df), block_size):
        block = df.iloc[start:start+block_size]
        n_train = int(block_size * train)
        n_val = int(block_size * val)
        
        train_rows.append(block.iloc[:n_train])
        val_rows.append(block.iloc[n_train:n_train+n_val])
        test_rows.append(block.iloc[n_train+n_val:])
    
    return pd.concat(train_rows), pd.concat(val_rows), pd.concat(test_rows)

# ----------------------------
# Prepare datasets
# ----------------------------
def prepare_datasets(country: str):
    standardized_parquet = PROCESSED_DIR / f"standardized_{country.lower()}.parquet"
    df = pd.read_parquet(standardized_parquet)

    # Drop rows without target
    clf_df = df.dropna(subset=[TARGET]).copy()
    y = clf_df[TARGET].astype(str)
    X = clf_df[NUMERIC + CATEGORICAL]

    # Build + save preprocessor
    pre = build_preprocessor()
    joblib.dump(pre, ARTIFACTS_DIR / f"preprocessor_{country.lower()}.joblib")

    # Block split (500 per tier assumed)
    X_train, X_val, X_test = block_split(X)
    y_train, y_val, y_test = block_split(y.to_frame())

    # Save splits
    (PROCESSED_DIR / country.lower()).mkdir(exist_ok=True)
    X_train.to_parquet(PROCESSED_DIR / country.lower() / "X_train.parquet", index=False)
    X_val.to_parquet(PROCESSED_DIR / country.lower() / "X_val.parquet", index=False)
    X_test.to_parquet(PROCESSED_DIR / country.lower() / "X_test.parquet", index=False)
    y_train.to_parquet(PROCESSED_DIR / country.lower() / "y_train.parquet", index=False)
    y_val.to_parquet(PROCESSED_DIR / country.lower() / "y_val.parquet", index=False)
    y_test.to_parquet(PROCESSED_DIR / country.lower() / "y_test.parquet", index=False)

    print(f"✅ Saved block-split datasets + preprocessor for {country}")

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    # Run for both countries
    for country in ["India", "Australia"]:
        prepare_datasets(country)
