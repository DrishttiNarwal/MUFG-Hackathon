# recommendation/predict.py
import pandas as pd
import numpy as np
from typing import Dict
from recommendation.rule_engine import apply_rules
from recommendation.utils import load_model, load_features, load_preprocessor

def hybrid_predict(user_input: Dict):
    """
    Hybrid pipeline:
      1) Apply deterministic rules
      2) If rules fail → ML classifier
    """

    # ----------------
    # 1. Rule engine
    # ----------------
    rule_based = apply_rules(user_input)
    if rule_based:
        return {
            "final_tier": rule_based,
            "source": "rule_engine",
            "probabilities": None
        }

    # ----------------
    # 2. ML prediction
    # ----------------
    model = load_model()
    features = load_features()
    preprocessor = load_preprocessor()

    # Convert dict → DataFrame
    df = pd.DataFrame([user_input])

    # Align columns
    df = df.reindex(columns=features, fill_value=np.nan)

    # Apply preprocessor (scaling/encoding)
    X = preprocessor.transform(df)

    # Predict
    probs = model.predict_proba(X)[0]
    classes = model.classes_
    top_idx = probs.argmax()

    return {
        "final_tier": classes[top_idx],
        "source": "ml_classifier",
        "probabilities": dict(zip(classes, probs.round(3)))
    }

if __name__ == "__main__":
    # Example user input
    sample = {
        "Country": "India",
        "ProductType": "Travel",
        "Age": 40,
        "AnnualPremium": 20000,
        "TripDurationDays": 10,
        "ExistingMedicalCondition": "Yes",
        "BaggageCoverage": "Yes",
        "AccidentCoverage": "Yes",
        "TripCancellationCoverage": "No",
        "HealthCoverage": "Yes",
        "SmokerDrinker": "No",
        "HealthIssues": "none",
        "PriceOfVehicle": 0,
        "AgeOfVehicle": 0,
        "TypeOfVehicle": "",
        "PropertyValue": 0,
        "PropertyAge": 0,
        "PropertySizeSqFeet": 0,
        "PropertyType": ""
    }
    result = hybrid_predict(sample)
    print("🔮 Prediction Result:")
    print(result)
