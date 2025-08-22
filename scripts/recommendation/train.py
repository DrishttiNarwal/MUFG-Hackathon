# scripts/recommendation/train.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.metrics import classification_report, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

# -------------------------------------------------------------------
# Paths / constants
# -------------------------------------------------------------------
ARTIFACTS = Path(__file__).resolve().parents[2] / "artifacts"
ARTIFACTS.mkdir(parents=True, exist_ok=True)

TIERS = ["Basic", "Standard", "Gold", "Premium"]

# Feature sets per policy (lowercase; must match CSV headers you have)
POLICY_FEATURES: Dict[str, List[str]] = {
    "health": ["age", "sumassured", "smokerdrinker", "diseases", "country", "policytype"],
    "life":   ["age", "sumassured", "smokerdrinker", "diseases", "country", "policytype"],
    "vehicle": ["age", "priceofvehicle", "ageofvehicle", "typeofvehicle", "country", "policytype"],
    "house":  ["age", "sumassured", "propertyvalue", "propertyage", "propertytype", "propertysize", "country", "policytype"],
    "travel": ["age", "sumassured", "destinationcountry", "tripdurationdays",
               "existingmedicalcondition", "healthcoverage", "baggagecoverage",
               "tripcancellationcoverage", "accidentcoverage", "country", "policytype"],
}

# Premium target per policy (lowercase; must match CSV)
PREMIUM_COLUMN = {
    "health": "annualpremium",
    "life": "annualpremium",
    "vehicle": "annualpremium",
    "house": "annualpremium",
    "travel": "trippremium",
}


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def _split_num_cat(X: pd.DataFrame) -> Tuple[List[str], List[str]]:
    cat_cols = [c for c in X.columns if X[c].dtype == "object" or str(X[c].dtype).startswith("string")]
    num_cols = [c for c in X.columns if c not in cat_cols]
    return num_cols, cat_cols


def _fit_encoder(X: pd.DataFrame) -> OneHotEncoder:
    """Fit OneHotEncoder on categorical columns (object dtype)."""
    _, cat_cols = _split_num_cat(X)
    enc = OneHotEncoder(handle_unknown="ignore", sparse=False)
    if len(cat_cols):
        enc.fit(X[cat_cols])
    else:
        # Fit a dummy so we always have a valid encoder object
        enc.fit(pd.DataFrame({"__dummy__": []}))
    return enc


def _encode(X: pd.DataFrame, enc: OneHotEncoder) -> np.ndarray:
    """Return numeric + encoded categorical matrix; fill NA properly first."""
    num_cols, cat_cols = _split_num_cat(X)

    # numeric: coerce to numeric, fillna -1
    Xn = np.zeros((len(X), 0))
    if len(num_cols):
        X_num = X[num_cols].apply(pd.to_numeric, errors="coerce").fillna(-1.0)
        Xn = X_num.to_numpy(dtype=float)

    # categorical: fillna "__missing__" and cast to str
    Xc = np.zeros((len(X), 0))
    if len(cat_cols):
        X_cat = X[cat_cols].astype("object").fillna("__missing__").astype(str)
        Xc = enc.transform(X_cat)

    return np.hstack([Xn, Xc])


def _save_feature_lists(outdir: Path, features: List[str]) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "features_cls.json", "w", encoding="utf-8") as f:
        json.dump(features, f, ensure_ascii=False, indent=2)
    with open(outdir / "features_reg.json", "w", encoding="utf-8") as f:
        json.dump(features, f, ensure_ascii=False, indent=2)
    # backward compat
    with open(outdir / "features.json", "w", encoding="utf-8") as f:
        json.dump(features, f, ensure_ascii=False, indent=2)


# -------------------------------------------------------------------
# Training
# -------------------------------------------------------------------
def train_one(country: str, df: pd.DataFrame, policy: str) -> None:
    print("\n" + "=" * 68)
    print(f"🚀 Training {country.upper()} — {policy.upper()}")
    print("=" * 68)

    feats   = POLICY_FEATURES[policy]
    tgt_cls = "policytier"
    tgt_reg = PREMIUM_COLUMN[policy]

    # Filter to rows for this (country, policy)
    sub = df[(df["country"].str.lower() == country.lower()) &
             (df["policytype"].str.lower() == policy.lower())].copy()

    if sub.empty:
        print(f"⚠️  Skipping {country}-{policy}: no rows after filter.")
        return

    # Remove rows missing targets
    sub = sub.dropna(subset=[tgt_cls, tgt_reg])
    if sub.empty:
        print(f"⚠️  Skipping {country}-{policy}: no rows with targets.")
        return

    # Build X/y
    X = sub.reindex(columns=feats).copy()
    y_cls = sub[tgt_cls].astype(str)
    y_reg = pd.to_numeric(sub[tgt_reg], errors="coerce")
    keep = y_reg.notna()
    X, y_cls, y_reg = X.loc[keep], y_cls.loc[keep], y_reg.loc[keep]

    # Fill missing values now (so encoder doesn’t see NaN in object arrays)
    num_cols, cat_cols = _split_num_cat(X)
    if len(num_cols):
        for c in num_cols:
            X[c] = pd.to_numeric(X[c], errors="coerce").fillna(-1.0)
    if len(cat_cols):
        for c in cat_cols:
            X[c] = X[c].astype("object").fillna("__missing__").astype(str)

    # Save feature order to artifacts
    outdir = ARTIFACTS / f"{country.lower()}_{policy.lower()}"
    _save_feature_lists(outdir, list(X.columns))

    # Split
    try:
        Xtr, Xte, yct, yce, yrt, yre = train_test_split(
            X, y_cls, y_reg, test_size=0.2, random_state=42, stratify=y_cls
        )
    except Exception:
        # if stratify fails (too few samples per class), use non‑stratified split
        Xtr, Xte, yct, yce, yrt, yre = train_test_split(
            X, y_cls, y_reg, test_size=0.2, random_state=42
        )

    # ---- Classifier ----
    enc_cls = _fit_encoder(Xtr)
    Mtr_cls = _encode(Xtr, enc_cls)
    Mte_cls = _encode(Xte, enc_cls)

    clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05)
    clf.fit(Mtr_cls, yct)

    try:
        yhat = clf.predict(Mte_cls)
        print(f"[{country}-{policy}] Classifier report:")
        print(classification_report(yce, yhat, labels=TIERS, zero_division=0))
    except Exception as e:
        print(f"[{country}-{policy}] Classifier eval skipped: {e}")

    # ---- Regressor ----
    enc_reg = _fit_encoder(Xtr)  # separate encoder
    Mtr_reg = _encode(Xtr, enc_reg)
    Mte_reg = _encode(Xte, enc_reg)

    reg = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05)
    reg.fit(Mtr_reg, yrt)

    try:
        r2 = r2_score(yre, reg.predict(Mte_reg))
        print(f"[{country}-{policy}] Regressor R²: {r2:.3f}")
    except Exception as e:
        print(f"[{country}-{policy}] Regressor eval skipped: {e}")

    # Save artifacts
    joblib.dump(clf, outdir / "clf.pkl")
    joblib.dump(reg, outdir / "reg.pkl")
    joblib.dump(enc_cls, outdir / "encoder_cls.pkl")
    joblib.dump(enc_reg, outdir / "encoder_reg.pkl")
    print(f"✅ Saved to {outdir}")


def train_all(csv_path: str, country: str) -> None:
    csv = Path(csv_path)
    if not csv.exists():
        raise FileNotFoundError(f"Data not found: {csv}")

    df = pd.read_csv(csv)
    # normalize headers -> lowercase, strip spaces/underscores to your schema
    df.columns = df.columns.str.lower().str.strip()
    # also unify some headers that might vary across sources
    df = df.rename(columns={
        "policy type": "policytype",
        "policy tier": "policytier",
        "sum assured": "sumassured",
        "annual premium": "annualpremium",
        "property size sq feet": "propertysize",
    })

    required = {"country", "policytype", "policytier"}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {csv}: {missing}")

    print("\n" + "#" * 72)
    print(f"### Training for {country.upper()} from {csv} ###")
    print("#" * 72)

    for policy in POLICY_FEATURES.keys():
        try:
            train_one(country, df, policy)
        except Exception as e:
            print(f"❌ Failed {country}-{policy}: {e}")



# Main
# -------------------------------------------------------------------
if __name__ == "__main__":
    base = Path(__file__).resolve().parents[1].parent / "processed"
    # OR simply: Path(__file__).resolve().parents[2] / "processed"

    train_all(str(base / "standardized_india.csv"), "india")
    train_all(str(base / "standardized_australia.csv"), "australia")
