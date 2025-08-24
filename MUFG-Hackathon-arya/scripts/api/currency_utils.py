from decimal import Decimal

# Current exchange rates (you might want to use an API for real-time rates)
EXCHANGE_RATES = {
    "INR": Decimal('1.0'),  # Base currency
    "AUD": Decimal('0.018')  # 1 INR = 0.018 AUD (example rate)
}

def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """
    Convert amount between currencies using INR as base currency
    """
    if from_currency == to_currency:
        return amount
    
    # Convert to INR first if amount is in AUD
    amount_in_inr = (
        Decimal(str(amount)) / EXCHANGE_RATES["AUD"] 
        if from_currency == "AUD" 
        else Decimal(str(amount))
    )
    
    # Convert to target currency
    result = (
        amount_in_inr * EXCHANGE_RATES[to_currency] 
        if to_currency == "AUD" 
        else amount_in_inr
    )
    
    return float(round(result, 2))
