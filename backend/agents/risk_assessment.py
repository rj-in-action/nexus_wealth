"""
Step 3: AI Risk Assessment Agent
Produces a composite risk score based on profile, portfolio, and market conditions.
"""
import time
import random


def risk_assessment_agent(state):
    """
    Performs comprehensive risk assessment using client profile,
    portfolio characteristics, and simulated market conditions.
    """
    start = time.time()
    profile = state.get("profile_summary", {})
    portfolio = state.get("portfolio_data", [])

    # Base risk score from stated tolerance
    tolerance_map = {"conservative": 3.0, "moderate": 5.5, "aggressive": 8.0}
    base_score = tolerance_map.get(profile.get("risk_tolerance", "moderate"), 5.5)

    # Age adjustment (younger = can take more risk)
    age = profile.get("age", 40)
    age_factor = max(0, min(2, (65 - age) / 15))  # 0-2 scale

    # Concentration risk
    concentration_penalty = len(profile.get("concentration_warnings", [])) * 0.5

    # Portfolio diversification score
    allocation = profile.get("asset_allocation", {})
    num_asset_types = len(allocation)
    diversification_bonus = min(1.0, num_asset_types / 5)

    # Simulated market conditions
    market_volatility = 0.65  # Moderate volatility environment
    market_adjustment = -market_volatility * 0.5

    # Compute composite score (1-10 scale)
    composite = base_score + age_factor * 0.3 - concentration_penalty + diversification_bonus + market_adjustment
    composite = max(1.0, min(10.0, round(composite, 1)))

    # Risk category
    if composite <= 3.5:
        category = "Low Risk"
        color = "green"
    elif composite <= 6.5:
        category = "Moderate Risk"
        color = "yellow"
    else:
        category = "High Risk"
        color = "red"

    # Risk factors breakdown
    risk_factors = [
        {"factor": "Stated Risk Tolerance", "value": profile.get("risk_tolerance", "moderate").title(), "impact": f"{base_score}/10 base"},
        {"factor": "Age-Based Capacity", "value": f"{age} years old", "impact": f"+{age_factor * 0.3:.1f}"},
        {"factor": "Concentration Risk", "value": f"{len(profile.get('concentration_warnings', []))} warnings", "impact": f"-{concentration_penalty:.1f}"},
        {"factor": "Diversification", "value": f"{num_asset_types} asset types", "impact": f"+{diversification_bonus:.1f}"},
        {"factor": "Market Environment", "value": "Moderate Volatility", "impact": f"{market_adjustment:.1f}"},
    ]

    # Suitability constraints based on risk
    suitability_limits = {
        "max_equity_pct": min(90, 40 + composite * 6),
        "max_single_stock_pct": 15 if composite < 7 else 25,
        "max_alternatives_pct": min(30, composite * 3),
        "min_fixed_income_pct": max(10, 60 - composite * 6),
        "max_crypto_pct": 0 if composite < 5 else min(10, (composite - 5) * 2),
    }

    reasoning = (
        f"Composite risk score: {composite}/10 ({category}). "
        f"Base from stated tolerance ({profile.get('risk_tolerance')}): {base_score}. "
        f"Age capacity adjustment: +{age_factor * 0.3:.1f}. "
        f"Concentration penalty: -{concentration_penalty:.1f}. "
        f"Diversification bonus: +{diversification_bonus:.1f}. "
        f"Market volatility adjustment: {market_adjustment:.1f}. "
        f"Suitability: Max equity {suitability_limits['max_equity_pct']:.0f}%, "
        f"Min fixed income {suitability_limits['min_fixed_income_pct']:.0f}%."
    )

    duration = int((time.time() - start) * 1000)

    return {
        "risk_score": composite,
        "risk_assessment": {
            "composite_score": composite,
            "category": category,
            "color": color,
            "factors": risk_factors,
            "suitability_limits": suitability_limits,
        },
        "messages": [("agent", f"[Risk Assessment] {reasoning}")],
        "agent_outputs": {"risk_assessment": {"score": composite, "category": category, "factors": risk_factors, "limits": suitability_limits, "reasoning": reasoning, "duration_ms": duration}},
    }
