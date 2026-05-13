"""
Step 4c: Alternative Assets Agent
Evaluates allocation to alternative investments (PE, REITs, commodities, crypto).
"""
import time

def alt_assets_agent(state):
    start = time.time()
    profile = state.get("profile_summary", {})
    portfolio = state.get("portfolio_data", [])
    risk = state.get("risk_assessment", {})
    risk_score = risk.get("composite_score", 5.0)
    total_value = sum(h.get("current_value", 0) for h in portfolio)

    current_alts = sum(h.get("current_value", 0) for h in portfolio if h.get("asset_type") in ("REITs", "Commodities", "Crypto", "Alternatives"))
    current_alt_pct = round(current_alts / total_value * 100, 1) if total_value else 0

    # Target alt allocation based on risk
    if risk_score >= 7:
        target_alt_pct = 15
        suggestions = [
            {"name": "Private Credit Fund", "type": "Private Credit", "target_pct": 5, "expected_return": "8-10%", "risk": "Medium", "min_investment": 25000, "liquidity": "Quarterly"},
            {"name": "Diversified REIT Portfolio", "type": "REITs", "target_pct": 5, "expected_return": "6-8%", "risk": "Medium", "min_investment": 10000, "liquidity": "Daily"},
            {"name": "Commodity Basket (Gold/Silver)", "type": "Commodities", "target_pct": 3, "expected_return": "4-7%", "risk": "Medium-High", "min_investment": 5000, "liquidity": "Daily"},
            {"name": "Digital Assets (BTC/ETH via ETF)", "type": "Crypto", "target_pct": 2, "expected_return": "Variable", "risk": "High", "min_investment": 5000, "liquidity": "Daily"},
        ]
    elif risk_score >= 4:
        target_alt_pct = 10
        suggestions = [
            {"name": "Core REIT Index Fund", "type": "REITs", "target_pct": 5, "expected_return": "5-7%", "risk": "Medium", "min_investment": 10000, "liquidity": "Daily"},
            {"name": "Gold ETF Allocation", "type": "Commodities", "target_pct": 3, "expected_return": "3-6%", "risk": "Low-Medium", "min_investment": 5000, "liquidity": "Daily"},
            {"name": "Infrastructure Fund", "type": "Infrastructure", "target_pct": 2, "expected_return": "5-7%", "risk": "Medium", "min_investment": 15000, "liquidity": "Monthly"},
        ]
    else:
        target_alt_pct = 5
        suggestions = [
            {"name": "Treasury-Linked REIT Fund", "type": "REITs", "target_pct": 3, "expected_return": "4-5%", "risk": "Low", "min_investment": 10000, "liquidity": "Daily"},
            {"name": "Inflation-Protected Commodities", "type": "Commodities", "target_pct": 2, "expected_return": "3-4%", "risk": "Low-Medium", "min_investment": 5000, "liquidity": "Daily"},
        ]

    gap = target_alt_pct - current_alt_pct
    recommendations = []
    if gap > 1:
        investment_amount = round(gap / 100 * total_value, 2)
        recommendations.append({"type": "alternative_assets", "title": "Alternative Asset Allocation",
            "description": f"Current alternatives at {current_alt_pct}% vs {target_alt_pct}% target. Recommend adding ${investment_amount:,.0f} in alternative assets for better diversification and inflation protection.",
            "details": {"current_alt_pct": current_alt_pct, "target_alt_pct": target_alt_pct, "gap_pct": round(gap, 1), "investment_needed": investment_amount, "suggestions": suggestions},
            "projected_impact": f"+{gap:.1f}% portfolio diversification", "confidence": 0.82, "priority": "medium"})

    reasoning = (f"Alt-assets analysis: Current {current_alt_pct}% vs target {target_alt_pct}% (risk score {risk_score}). "
                 f"Gap: {gap:.1f}%. {len(suggestions)} alternative investment suggestions generated.")
    duration = int((time.time() - start) * 1000)

    return {"alt_asset_recommendations": recommendations, "messages": [("agent", f"[Alt Assets] {reasoning}")],
            "agent_outputs": {"alt_assets_agent": {"recommendations": recommendations, "reasoning": reasoning, "duration_ms": duration}}}
