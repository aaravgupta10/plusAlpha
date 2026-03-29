from typing import Dict, Any

def calculate_risk_score(daily_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates a deterministic 0-100 risk score based on macro thresholds.
    0-33: Safe (Risk-On)
    34-66: Neutral
    67-100: Danger (Risk-Off)
    """
    score = 50  # Start at a neutral baseline

    # Volatility Logic (India VIX historical median is roughly 15)
    vix = daily_data.get("india_vix")
    if vix:
        if vix > 20.0: score += 15
        elif vix < 13.0: score -= 10

    # Institutional Flow Logic (FII Selling drains liquidity)
    fii = daily_data.get("fii_net_flow")
    if fii:
        if fii < -2000: score += 10  # Massive outflow
        elif fii > 2000: score -= 10 # Massive inflow

    # Global Yield Logic (US 10Y acts as global cost of capital)
    yield_10y = daily_data.get("us_10y_yield")
    if yield_10y:
        if yield_10y > 4.5: score += 10
        elif yield_10y < 3.8: score -= 5

    # Interbank Liquidity (High call rate = tight domestic liquidity)
    call_rate = daily_data.get("rbi_call_rate")
    if call_rate:
        if call_rate > 6.75: score += 5 

    # Constrain score between 0 and 100
    final_score = max(0, min(100, score))

    # Determine Status
    status = "Neutral"
    if final_score >= 67: status = "Danger"
    elif final_score <= 33: status = "Safe"

    return {
        "risk_score": final_score,
        "status": status
    }