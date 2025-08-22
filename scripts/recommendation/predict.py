from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from .common import ARTIFACTS, load_artifacts, preprocess

TIERS = ["Basic", "Standard", "Gold", "Premium"]

TIER_MULTIPLIER = {
    "Basic": 0.90,
    "Standard": 1.00,
    "Gold": 1.20,
    "Premium": 1.45,
}

# Master CSV schema (standardized)
CSV_FEATURES = [
    "name", "age", "country", "policy_type", "policy_tier", "sum_assured", "smoker_drinker",
    "num_diseases", "diseases", "annual_premium",
    "price_of_vehicle", "age_of_vehicle", "type_of_vehicle",
    "property_value", "property_age", "property_type", "property_size_sq_feet",
    "destination_country", "trip_duration_days", "existing_medical_condition",
    "health_coverage", "baggage_coverage", "trip_cancellation_coverage", "accident_coverage", "trip_premium"
]

AUD_TO_INR = 55.0
INR_TO_AUD = 1 / AUD_TO_INR

# Vehicle IDV depreciation rates (based on vehicle age)
VEHICLE_DEPRECIATION = {
    0: 0.0,    # New vehicle
    1: 0.15,   # 15% for 1st year
    2: 0.25,   # 25% for 2nd year
    3: 0.35,   # 35% for 3rd year
    4: 0.45,   # 45% for 4th year
    5: 0.50    # 50% for 5th year and beyond
}

# Base premium rates by vehicle type (percentage of IDV)
VEHICLE_BASE_PREMIUM = {
    "2wheeler": 0.02,     # 2% of IDV
    "car": 0.03,         # 3% of IDV
    "suv": 0.035,        # 3.5% of IDV
    "commercial": 0.04   # 4% of IDV
}

# Property insurance base rates and multipliers
PROPERTY_BASE_RATE = 0.001  # 0.1% of property value
PROPERTY_AGE_MULTIPLIER = {
    0: 1.0,    # New property
    5: 1.1,    # 5 years
    10: 1.2,   # 10 years
    15: 1.3,   # 15 years
    20: 1.4,   # 20 years and above
}

PROPERTY_TYPE_MULTIPLIER = {
    "apartment": 1.0,
    "house": 1.2,
    "villa": 1.4,
    "commercial": 1.5
}

def calculate_property_premium(value: float, age: int, property_type: str, size: float) -> float:
    """Calculate annual premium for property insurance."""
    try:
        # Get base premium
        base_premium = value * PROPERTY_BASE_RATE
        
        # Apply age multiplier
        age_multiplier = 1.0
        for threshold_age, mult in sorted(PROPERTY_AGE_MULTIPLIER.items()):
            if age >= threshold_age:
                age_multiplier = mult
        
        # Apply property type multiplier
        type_multiplier = PROPERTY_TYPE_MULTIPLIER.get(property_type.lower(), 1.2)
        
        # Apply size adjustment (additional 5% per 1000 sq ft over 1000)
        size_multiplier = 1.0 + max(0, (size - 1000) / 1000) * 0.05
        
        final_premium = base_premium * age_multiplier * type_multiplier * size_multiplier
        return round(final_premium, 2)
    except Exception as e:
        print(f"Error calculating property premium: {str(e)}")
        return 0.0

# -------------------------
# Helpers
# -------------------------

def ensure_required_features(data: dict, policy_type: str) -> dict:
    """Ensure all required features are present in the data."""
    required_features = {
        "house": [
            "age", "sumassured", "propertyvalue", "propertyage",
            "propertytype", "propertysize", "country", "policytype"
        ],
        "vehicle": [
            "age", "sumassured", "priceofvehicle", "ageofvehicle",
            "typeofvehicle", "country", "policytype"
        ],
        "health": [
            "age", "sumassured", "smokerdrinker", "diseases",
            "country", "policytype"
        ],
        "travel": [
            "age", "destination_country", "trip_duration_days",
            "existing_medical_condition", "health_coverage",
            "baggage_coverage", "trip_cancellation_coverage",
            "accident_coverage", "country", "policytype"
        ]
    }
    
    policy = policy_type.lower()
    if policy not in required_features:
        return data
        
    result = data.copy()
    for feature in required_features[policy]:
        if feature not in result:
            print(f"Adding missing feature: {feature}")
            result[feature] = None
    return result

def calculate_vehicle_idv(price: float, age: int, vehicle_type: str) -> tuple[float, float]:
    """Calculate IDV and annual premium for a vehicle."""
    # Get depreciation rate based on age
    depreciation_rate = VEHICLE_DEPRECIATION.get(min(age, 5))
    
    # Calculate IDV
    idv = price * (1 - depreciation_rate)
    
    # Get base premium rate based on vehicle type
    base_rate = VEHICLE_BASE_PREMIUM.get(vehicle_type.lower(), 0.03)  # Default to car rate
    
    # Calculate annual premium
    annual_premium = idv * base_rate
    
    return idv, annual_premium
def _canon(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())

def _load_feature_list(path: Path, name: str) -> Optional[List[str]]:
    p = path / name
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def _align_columns(X: pd.DataFrame, expected_cols: List[str]) -> pd.DataFrame:
    print(f"Input columns: {X.columns.tolist()}")
    print(f"Expected columns: {expected_cols}")
    
    can_to_expected = {_canon(c): c for c in expected_cols}
    renames = {}
    for col in X.columns:
        c = _canon(col)
        if c in can_to_expected:
            renames[col] = can_to_expected[c]
    
    print(f"Column renames: {renames}")
    X2 = X.rename(columns=renames).copy()
    for col in expected_cols:
        if col not in X2.columns:
            X2[col] = pd.NA
            print(f"Added missing column: {col}")
    
    final_cols = X2[expected_cols].columns.tolist()
    print(f"Final columns: {final_cols}")
    return X2[expected_cols]

def _expected_features_from_encoder(enc, fallback: List[str]) -> List[str]:
    if hasattr(enc, "feature_names_in_"):
        return list(enc.feature_names_in_)
    return fallback

def _ensure_csv_schema(data_norm: dict) -> pd.DataFrame:
    """Force input row to match the CSV schema exactly."""
    row = {}
    for col in CSV_FEATURES:
        row[col] = data_norm.get(col, pd.NA)
    return pd.DataFrame([row], dtype="object")

# -------------------------
# Currency conversion
# -------------------------
def _try_float(x):
    try:
        return float(x)
    except Exception:
        return None

def convert_output_for_country(country: str, premiums_in_inr: Dict[str, float]) -> Dict[str, float]:
    if country and country.upper() == "AUSTRALIA":
        return {t: round(v * INR_TO_AUD, 2) for t, v in premiums_in_inr.items()}
    return premiums_in_inr

# -------------------------
# Main Prediction
# -------------------------
def predict(country: str, policy: str, data: dict) -> Dict:
    """
    Predict recommended tier + all-tier premiums.
    """
    print(f"Input data: {data}")
    print(f"Country: {country}, Policy: {policy}")

    # Normalize country
    country_mapping = {
        "IN": "INDIA",
        "AU": "AUSTRALIA",
        "INDIA": "INDIA",
        "AUSTRALIA": "AUSTRALIA"
    }
    normalized_country = country_mapping.get(country.upper())
    if not normalized_country:
        raise ValueError(f"Invalid country: {country}. Must be one of: IN, AU, INDIA, AUSTRALIA")
    
    print("\nNormalizing input data:")
    print(f"Raw input - Country: {normalized_country}, Policy: {policy}")
    print(f"Raw data: {data}")
    
    # Normalize field names to match model expectations
    data_norm = {
        "country": normalized_country.lower(),
        "policytype": policy.lower(),
        "age": float(data.get("age", 0))
    }
    
    # Print input feature names for debugging
    print(f"Initial features: {list(data_norm.keys())}")
    
    try:
        # Add policy-specific fields
        if policy.lower() == "health":
            data_norm.update({
                "sumassured": float(data.get("sum_assured", 0)),
                "smokerdrinker": str(data.get("smoker_drinker", "No")).lower(),
                "diseases": str(data.get("diseases", "")) if "diseases" in data else str(data.get("num_diseases", "0"))
            })
        elif policy.lower() == "vehicle":
            vehicle_price = float(data.get("price_of_vehicle", 0))
            vehicle_age = int(data.get("age_of_vehicle", 0))
            vehicle_type = str(data.get("type_of_vehicle", "car")).lower()
            
            print(f"Vehicle data - Price: {vehicle_price}, Age: {vehicle_age}, Type: {vehicle_type}")
            
            # Calculate IDV and annual premium
            idv, annual_premium = calculate_vehicle_idv(vehicle_price, vehicle_age, vehicle_type)
            print(f"Calculated IDV: {idv}, Annual Premium: {annual_premium}")
            
            data_norm.update({
                "priceofvehicle": vehicle_price,
                "ageofvehicle": vehicle_age,
                "typeofvehicle": vehicle_type,
                "sumassured": idv,  # Use IDV as sum assured
                "annual_premium": annual_premium
            })
        elif policy.lower() == "house":
            try:
                print("Processing house insurance data...")
                print(f"Raw input data: {data}")
                
                # Extract and validate required fields
                property_value = float(data.get("property_value", 0))
                if property_value <= 0:
                    raise ValueError("Property value must be greater than 0")
                    
                property_age = int(float(data.get("property_age", 0)))  # Convert through float for string inputs
                property_type = str(data.get("property_type", "house")).lower()
                if property_type not in PROPERTY_TYPE_MULTIPLIER:
                    property_type = "house"  # Default to house if invalid type
                    
                property_size = float(data.get("property_size_sq_feet", 1000))
                if property_size <= 0:
                    property_size = 1000  # Default size if invalid
                
                print(f"Validated inputs - Value: {property_value}, Age: {property_age}, Type: {property_type}, Size: {property_size}")
                
                # Calculate premium
                annual_premium = calculate_property_premium(
                    value=property_value,
                    age=property_age,
                    property_type=property_type,
                    size=property_size
                )
                print(f"Calculated annual premium: {annual_premium}")
                
                # Update data with normalized values using exact field names from features.json
                data_norm.update({
                    "propertyvalue": property_value,
                    "propertyage": property_age,
                    "propertytype": property_type,
                    "propertysize": property_size,  # Changed from propertysizesqfeet to propertysize
                    "sumassured": property_value,  # Same as property value for house insurance
                    "annual_premium": annual_premium  # Using standard field name
                })
                print(f"Updated normalized data: {data_norm}")
                
                # Ensure all required features are present
                data_norm = ensure_required_features(data_norm, "house")
                print(f"Final features after ensuring required ones: {list(data_norm.keys())}")
                
            except (ValueError, TypeError) as e:
                print(f"Error processing house insurance data: {str(e)}")
                print(f"Data that caused error: {data}")
                raise ValueError(f"Invalid house insurance data: {str(e)}")
        elif policy.lower() == "travel":
            try:
                data_norm.update({
                    "destination_country": str(data.get("destination_country", "")),
                    "trip_duration_days": int(data.get("trip_duration_days", 0)),
                    "existing_medical_condition": str(data.get("existing_medical_condition", "No")).lower(),
                    "health_coverage": str(data.get("health_coverage", "Basic")).lower(),
                    "baggage_coverage": str(data.get("baggage_coverage", "Basic")).lower(),
                    "trip_cancellation_coverage": str(data.get("trip_cancellation_coverage", "No")).lower(),
                    "accident_coverage": str(data.get("accident_coverage", "Basic")).lower()
                })
                # Calculate base trip premium based on duration and coverages
                duration = int(data.get("trip_duration_days", 0))
                base_premium = duration * 100  # Base rate per day
                
                # Adjust premium based on coverages
                coverage_multipliers = {
                    "health_coverage": {"basic": 1.0, "standard": 1.2, "gold": 1.5, "premium": 2.0},
                    "baggage_coverage": {"basic": 1.0, "standard": 1.1, "gold": 1.3, "premium": 1.5},
                    "accident_coverage": {"basic": 1.0, "standard": 1.2, "gold": 1.4, "premium": 1.6}
                }
                
                for coverage, multipliers in coverage_multipliers.items():
                    level = str(data.get(coverage, "basic")).lower()
                    base_premium *= multipliers.get(level, 1.0)
                
                # Additional premium for medical condition and trip cancellation
                if str(data.get("existing_medical_condition", "No")).lower() == "yes":
                    base_premium *= 1.3
                if str(data.get("trip_cancellation_coverage", "No")).lower() == "yes":
                    base_premium *= 1.2
                    
                data_norm["trip_premium"] = base_premium
            except (ValueError, TypeError) as e:
                print(f"Error processing travel insurance data: {str(e)}")
                raise ValueError(f"Invalid travel insurance data: {str(e)}")
    except (ValueError, TypeError) as e:
        print(f"Error converting data: {str(e)}")
        raise ValueError(f"Invalid data format: {str(e)}")
        
    print(f"Normalized data: {data_norm}")
    data_norm = pd.DataFrame([data_norm])
    print(f"Normalized data:\n{data_norm}")

    # Load artifacts
    path = ARTIFACTS / f"{country.lower()}_{policy.lower()}"
    clf = load_artifacts(path, "clf")
    reg = load_artifacts(path, "reg")
    enc_cls = load_artifacts(path, "encoder_cls")
    enc_reg = load_artifacts(path, "encoder_reg")

    # Load artifacts
    path = ARTIFACTS / f"{country.lower()}_{policy.lower()}"
    clf = load_artifacts(path, "clf")
    reg = load_artifacts(path, "reg")
    enc_cls = load_artifacts(path, "encoder_cls")
    enc_reg = load_artifacts(path, "encoder_reg")

    # Feature lists
    features_cls = _load_feature_list(path, "features_cls.json") or []
    features_reg = _load_feature_list(path, "features_reg.json") or features_cls

    exp_cls = _expected_features_from_encoder(enc_cls, features_cls)
    exp_reg = _expected_features_from_encoder(enc_reg, features_reg if features_reg else features_cls)

    # Use the normalized DataFrame directly
    X_enc_cls, _ = preprocess(data_norm, enc_cls)
    recommended_tier = clf.predict(X_enc_cls)[0]

    confidence: Dict[str, float] = {}
    if hasattr(clf, "predict_proba"):
        probs = clf.predict_proba(X_enc_cls)[0]
        classes = list(clf.classes_)
        confidence = {c: round(float(p), 4) for c, p in zip(classes, probs)}

    # ---- Regressor
    X_enc_reg, _ = preprocess(data_norm, enc_reg)
    all_tiers: Dict[str, float] = {}
    reg_has_policy_tier = any(_canon(c) == "policytier" for c in exp_reg)

    if reg_has_policy_tier:
        tier_col = next(c for c in exp_reg if _canon(c) == "policytier")
        for t in TIERS:
            data_with_tier = data_norm.copy()
            data_with_tier[tier_col] = t
            X_enc_reg_t, _ = preprocess(data_with_tier, enc_reg)
            premium = float(reg.predict(X_enc_reg_t)[0])
            all_tiers[t] = round(premium, 2)
    else:
        base = float(reg.predict(X_enc_reg)[0])
        for t in TIERS:
            all_tiers[t] = round(base * TIER_MULTIPLIER[t], 2)

    all_tiers = convert_output_for_country(country, all_tiers)

    return {
        "recommended_tier": recommended_tier,
        "all_tiers": all_tiers,
        "confidence": confidence,
    }

def predict_probability(data: dict, country: str, policy: str) -> pd.DataFrame:
    """Get probability prediction for a single row."""
    print(f"\nPredicting probability for {country} {policy}")
    print(f"Input data: {data}")
    
    try:
        # Normalize data
        data_norm = pd.DataFrame([{
            "country": country.lower(),
            "policytype": policy.lower(),
            "age": float(data.get("age", 0)),
            "priceofvehicle": float(data.get("price_of_vehicle", 0)),
            "ageofvehicle": float(data.get("age_of_vehicle", 0)),
            "typeofvehicle": str(data.get("type_of_vehicle", "")).lower()
        }])
        
        print(f"Normalized data:\n{data_norm}")
        
        # Load classifier model and encoder
        path = ARTIFACTS / f"{country.lower()}_{policy.lower()}"
        clf = load_artifacts(path, "clf")
        enc = load_artifacts(path, "encoder_cls")
        
        # Preprocess data
        X_enc, _ = preprocess(data_norm, enc)
        print(f"Preprocessed data shape: {X_enc.shape}")
        
        # Get probabilities
        if hasattr(clf, "predict_proba"):
            result = pd.DataFrame(clf.predict_proba(X_enc), columns=clf.classes_)
            print(f"Probability prediction:\n{result}")
            return result
        return pd.DataFrame(clf.predict(X_enc), columns=["prediction"])
    except Exception as e:
        print(f"Error in predict_probability: {str(e)}")
        raise

def predict_amount(data: dict, country: str, policy: str) -> pd.DataFrame:
    """Get amount prediction for a single row."""
    print(f"\nPredicting amount for {country} {policy}")
    print(f"Input data: {data}")
    
    try:
        # Normalize data
        data_norm = pd.DataFrame([{
            "country": country.lower(),
            "policytype": policy.lower(),
            "age": float(data.get("age", 0)),
            "priceofvehicle": float(data.get("price_of_vehicle", 0)),
            "ageofvehicle": float(data.get("age_of_vehicle", 0)), 
            "typeofvehicle": str(data.get("type_of_vehicle", "")).lower()
        }])
        
        print(f"Normalized data:\n{data_norm}")
        
        # Load regression model and encoder
        path = ARTIFACTS / f"{country.lower()}_{policy.lower()}"
        reg = load_artifacts(path, "reg")
        enc = load_artifacts(path, "encoder_reg")
        
        # Preprocess data
        X_enc, _ = preprocess(data_norm, enc)
        print(f"Preprocessed data shape: {X_enc.shape}")
        
        # Get prediction
        result = pd.DataFrame(reg.predict(X_enc))
        print(f"Amount prediction:\n{result}")
        return result
    except Exception as e:
        print(f"Error in predict_amount: {str(e)}")
        raise

def recommend_multiple(data, country, policy):
    """Get multiple recommendations based on data for specific country and policy."""
    print(f"\nProcessing multiple recommendations for {country} {policy}")
    print(f"Number of items to process: {len(data)}")
    
    recommendations = []
    for idx, item in enumerate(data):
        try:
            print(f"\nProcessing item {idx + 1}:")
            print(f"Input data: {item}")
            
            recommendation = {}
            clf_result = predict_probability(item, country, policy)
            print(f"Classification result: {clf_result.iloc[0][1]}")
            
            if clf_result.iloc[0][1] > 0.5:  # If positive class probability > 0.5
                reg_result = predict_amount(item, country, policy)
                print(f"Regression result: {reg_result.iloc[0][0]}")
                
                recommendation = {
                    "insurance": float(clf_result.iloc[0][1]),
                    "amount": float(reg_result.iloc[0][0])
                }
                recommendations.append(recommendation)
                print(f"Added recommendation: {recommendation}")
            else:
                print("Skipped recommendation due to low probability")
                
        except Exception as e:
            print(f"Error processing item {idx + 1}: {str(e)}")
            # Instead of failing the entire request, continue with other items
            continue
            
    print(f"Successfully processed {len(recommendations)} recommendations")
    return recommendations
