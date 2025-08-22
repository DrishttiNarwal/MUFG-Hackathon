# scripts/recommendation/common.py
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import OneHotEncoder
from pathlib import Path

# -----------------
# Globals
# -----------------
ARTIFACTS = Path("artifacts")
ARTIFACTS.mkdir(exist_ok=True)

TIERS = ["Basic", "Standard", "Gold", "Premium"]

# Targets
TARGET_TIER = "policy_tier"
TARGET_PREMIUM = "premium_unified"

# Universal feature set across all policies
FEATURES = [
    "age",
    "sumassured",
    "smokerdrinker",
    "diseases",
    "country",
    "policytype",
]

# -----------------
# Data Handling
# -----------------
def load_data(country: str) -> pd.DataFrame:
    """Load dataset parquet and normalize column names."""
    if country.lower() == "india":
        df = pd.read_parquet("processed/standardized_india.parquet")
    else:
        df = pd.read_parquet("processed/standardized_australia.parquet")

    # normalize names: lowercase + underscores
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # unify premium into one column
    if "premium_unified" not in df.columns:
        df["premium_unified"] = np.nan

    if "annual_premium" in df.columns:
        df["premium_unified"] = df["premium_unified"].fillna(df["annual_premium"])
    if "trippremium" in df.columns:
        df["premium_unified"] = df["premium_unified"].fillna(df["trippremium"])

    return df

# -----------------
# Artifacts
# -----------------
def save_artifacts(path: Path, obj, name: str):
    path.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, path / f"{name}.pkl")

def load_artifacts(path: Path, name: str):
    return joblib.load(path / f"{name}.pkl")

# -----------------
# Preprocessing
# -----------------
def preprocess(X: pd.DataFrame, encoder: OneHotEncoder = None):
    """Return numeric + one-hot encoded categorical features.

    NaNs are preserved for numeric columns (HGB supports them).
    """
    print(f"Input DataFrame:\n{X}")
    X = X.copy()

    # add missing expected features as NaN
    for col in FEATURES:
        if col not in X.columns:
            print(f"Adding missing column {col}")
            X[col] = np.nan

    X = X[FEATURES]
    print(f"Preprocessed DataFrame:\n{X}")

    cat_cols = X.select_dtypes(include=["object"]).columns
    num_cols = X.select_dtypes(exclude=["object"]).columns

    # OneHotEncoder (only categorical)
    if encoder is None:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        if len(cat_cols):
            encoder.fit(X[cat_cols])
        else:
            encoder.fit(pd.DataFrame({"_dummy": [0]}))  # fallback

    X_num = X[num_cols].to_numpy(dtype=float) if len(num_cols) else np.zeros((len(X), 0))
    X_cat = encoder.transform(X[cat_cols]) if len(cat_cols) else np.zeros((len(X), 0))

    return np.concatenate([X_num, X_cat], axis=1), encoder
