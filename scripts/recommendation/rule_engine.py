# recommendation/rule_engine.py
# Hybrid Rule Engine for Insurance Recommendation
# Covers: India + Australia × (Health, Life, Vehicle, Travel, House)
# Each parameter affects final tier. Rules are deterministic, explainable.

from typing import Dict, Optional

# --------------------------
# Utility
# --------------------------

def calculate_idv(price: float, age_years: float) -> float:
    """
    Calculate Insured Declared Value (IDV) using IRDAI slab rules.
    (Same logic generally used by Australian insurers as well.)
    """
    if age_years < 0.5:       # < 6 months
        depreciation = 0.05
    elif age_years < 1:       # 6 months – 1 year
        depreciation = 0.15
    elif age_years < 2:
        depreciation = 0.20
    elif age_years < 3:
        depreciation = 0.30
    elif age_years < 4:
        depreciation = 0.40
    elif age_years < 5:
        depreciation = 0.50
    else:
        depreciation = 0.60  # >5 years (market negotiated ~60%)

    idv = price * (1 - depreciation)
    return max(idv, 0)


# --------------------------
# INDIA RULES
# --------------------------

def india_health_rules(row: Dict) -> Optional[str]:
    """
    Health Insurance (India):
    - Smoker/disease/age increases risk
    - High sum insured or premium → Premium tier
    """
    age = int(row.get("Age", 0) or 0)
    sum_insured = float(row.get("SumInsured", 0) or 0)
    premium = float(row.get("AnnualPremium", 0) or 0)
    smoker = str(row.get("SmokerDrinker", "No")).lower() == "yes"
    disease = str(row.get("HealthIssues", "none")).lower()

    risk_score = 0
    if smoker: risk_score += 1
    if disease != "none": risk_score += 1
    if age >= 45: risk_score += 1
    if age >= 60: risk_score += 2

    if sum_insured > 1500000 or premium > 50000:
        return "Premium"

    if risk_score == 0: return "Basic"
    if risk_score == 1: return "Standard"
    if risk_score == 2: return "Gold"
    return "Premium"


def india_life_rules(row: Dict) -> Optional[str]:
    """
    Life Insurance (India):
    - Smoker/disease heavily penalized
    - Very high premiums → Premium tier
    """
    age = int(row.get("Age", 0) or 0)
    premium = float(row.get("AnnualPremium", 0) or 0)
    smoker = str(row.get("SmokerDrinker", "No")).lower() == "yes"
    disease = str(row.get("HealthIssues", "none")).lower()

    risk_score = 0
    if smoker: risk_score += 2
    if disease != "none": risk_score += 1
    if age >= 50: risk_score += 1
    if age >= 65: risk_score += 2

    if premium > 100000:
        return "Premium"

    if risk_score == 0: return "Basic"
    if risk_score <= 2: return "Standard"
    if risk_score == 3: return "Gold"
    return "Premium"


def india_vehicle_rules(row: Dict) -> Optional[str]:
    """
    Vehicle Insurance (India):
    - Uses IDV + type of vehicle
    - Luxury/trucks riskier, bikes moderate
    """
    price = float(row.get("PriceOfVehicle", 0) or 0)
    age = int(row.get("AgeOfVehicle", 0) or 0)
    vtype = str(row.get("TypeOfVehicle", "")).lower()
    idv = calculate_idv(price, age)

    type_risk = 0
    if vtype in ["luxury", "truck"]: type_risk += 1
    if vtype == "bike": type_risk += 0.5

    if idv < 200000 and type_risk == 0: return "Basic"
    if 200000 <= idv < 600000 or type_risk > 0: return "Standard"
    if 600000 <= idv < 1500000: return "Gold"
    if idv >= 1500000: return "Premium"
    return None


def india_travel_rules(row: Dict) -> Optional[str]:
    """
    Travel Insurance (India):
    - Longer trips, existing medical conditions increase risk
    - More coverage options → higher tiers
    """
    duration = int(row.get("TripDurationDays", 0) or 0)
    medical_cond = str(row.get("ExistingMedicalCondition", "No")).lower() == "yes"
    baggage = str(row.get("BaggageCoverage", "No")).lower() == "yes"
    trip_cancel = str(row.get("TripCancellationCoverage", "No")).lower() == "yes"
    accident = str(row.get("AccidentCoverage", "No")).lower() == "yes"
    health = str(row.get("HealthCoverage", "No")).lower() == "yes"

    risk_score = 0
    if duration > 15: risk_score += 1
    if medical_cond: risk_score += 1

    coverage_count = sum([baggage, trip_cancel, accident, health])

    if coverage_count == 1: return "Basic"
    if coverage_count == 2: return "Standard" if risk_score == 0 else "Gold"
    if coverage_count == 3: return "Gold" if risk_score <= 1 else "Premium"
    if coverage_count == 4: return "Premium"
    return None


def india_house_rules(row: Dict) -> Optional[str]:
    """
    House Insurance (India):
    - Property value, size, type, and age decide risk
    """
    value = float(row.get("PropertyValue", 0) or 0)
    age = int(row.get("PropertyAge", 0) or 0)
    size = float(row.get("PropertySizeSqFeet", 0) or 0)
    ptype = str(row.get("PropertyType", "")).lower()

    risk_score = 0
    if age > 30: risk_score += 1
    if ptype in ["villa", "bungalow"]: risk_score += 1

    if value < 2000000 and size < 800: return "Basic"
    if 2000000 <= value < 10000000 or size < 1500: return "Standard"
    if 10000000 <= value < 30000000 or size < 3000: return "Gold"
    return "Premium"


# --------------------------
# AUSTRALIA RULES
# --------------------------

def australia_health_rules(row: Dict) -> Optional[str]:
    """
    Health Insurance (Australia):
    - Smoker/disease much heavier impact
    - Higher sum insured → Premium tier
    """
    age = int(row.get("Age", 0) or 0)
    sum_insured = float(row.get("SumInsured", 0) or 0)
    smoker = str(row.get("SmokerDrinker", "No")).lower() == "yes"
    disease = str(row.get("HealthIssues", "none")).lower()

    risk_score = 0
    if smoker: risk_score += 2
    if disease != "none": risk_score += 2
    if age >= 50: risk_score += 1
    if age >= 65: risk_score += 2

    if sum_insured > 2000000: return "Premium"

    if risk_score == 0: return "Basic"
    if risk_score <= 2: return "Standard"
    if risk_score <= 4: return "Gold"
    return "Premium"


def australia_life_rules(row: Dict) -> Optional[str]:
    """
    Life Insurance (Australia):
    - Smoker and higher age are strong negatives
    - High premiums → Premium tier
    """
    age = int(row.get("Age", 0) or 0)
    premium = float(row.get("AnnualPremium", 0) or 0)
    smoker = str(row.get("SmokerDrinker", "No")).lower() == "yes"

    risk_score = 0
    if smoker: risk_score += 2
    if age >= 55: risk_score += 2
    if age >= 70: risk_score += 2

    if premium > 150000: return "Premium"

    if risk_score == 0: return "Basic"
    if risk_score <= 2: return "Standard"
    if risk_score <= 4: return "Gold"
    return "Premium"


def australia_vehicle_rules(row: Dict) -> Optional[str]:
    """
    Vehicle Insurance (Australia):
    - Uses IDV + type of vehicle
    - Higher thresholds than India
    """
    price = float(row.get("PriceOfVehicle", 0) or 0)
    age = int(row.get("AgeOfVehicle", 0) or 0)
    vtype = str(row.get("TypeOfVehicle", "")).lower()
    idv = calculate_idv(price, age)

    type_risk = 0
    if vtype in ["luxury", "truck"]: type_risk += 1
    if vtype == "bike": type_risk += 0.5

    if idv < 5000 and type_risk == 0: return "Basic"
    if 5000 <= idv < 15000 or type_risk > 0: return "Standard"
    if 15000 <= idv < 30000: return "Gold"
    if idv >= 30000: return "Premium"
    return None


def australia_travel_rules(row: Dict) -> Optional[str]:
    """
    Travel Insurance (Australia):
    - More weight on medical conditions
    - Longer trip durations are riskier
    """
    duration = int(row.get("TripDurationDays", 0) or 0)
    baggage = str(row.get("BaggageCoverage", "No")).lower() == "yes"
    trip_cancel = str(row.get("TripCancellationCoverage", "No")).lower() == "yes"
    accident = str(row.get("AccidentCoverage", "No")).lower() == "yes"
    health = str(row.get("HealthCoverage", "No")).lower() == "yes"
    medical_cond = str(row.get("ExistingMedicalCondition", "No")).lower() == "yes"

    risk_score = 0
    if duration > 20: risk_score += 1
    if medical_cond: risk_score += 2

    coverage_count = sum([baggage, trip_cancel, accident, health])

    if coverage_count == 1: return "Basic"
    if coverage_count == 2: return "Standard" if risk_score == 0 else "Gold"
    if coverage_count == 3: return "Gold" if risk_score <= 2 else "Premium"
    if coverage_count == 4: return "Premium"
    return None


def australia_house_rules(row: Dict) -> Optional[str]:
    """
    House Insurance (Australia):
    - Higher base property values compared to India
    - Larger homes and villas → higher tiers
    """
    value = float(row.get("PropertyValue", 0) or 0)
    age = int(row.get("PropertyAge", 0) or 0)
    size = float(row.get("PropertySizeSqFeet", 0) or 0)
    ptype = str(row.get("PropertyType", "")).lower()

    risk_score = 0
    if age > 40: risk_score += 1
    if ptype in ["villa", "bungalow"]: risk_score += 1

    if value < 300000 and size < 1000: return "Basic"
    if 300000 <= value < 1000000 or size < 2000: return "Standard"
    if 1000000 <= value < 3000000 or size < 4000: return "Gold"
    return "Premium"


# --------------------------
# Dispatcher
# --------------------------

def apply_rules(row: Dict) -> Optional[str]:
    """Main dispatcher to apply country + product-specific rules."""
    country = str(row.get("Country", "")).lower()
    product = str(row.get("ProductType", "")).lower()

    if country == "india":
        if product == "health": return india_health_rules(row)
        if product == "life": return india_life_rules(row)
        if product == "vehicle": return india_vehicle_rules(row)
        if product == "travel": return india_travel_rules(row)
        if product == "house": return india_house_rules(row)

    if country == "australia":
        if product == "health": return australia_health_rules(row)
        if product == "life": return australia_life_rules(row)
        if product == "vehicle": return australia_vehicle_rules(row)
        if product == "travel": return australia_travel_rules(row)
        if product == "house": return australia_house_rules(row)

    return None
