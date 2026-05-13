"""
Step 4b: Portfolio Rebalancing Agent
Analyzes portfolio drift and generates rebalancing recommendations.
"""
import time

TARGET_ALLOCATIONS = {
    "conservative": {"US Equity": 25, "Intl Equity": 10, "Fixed Income": 40, "REITs": 5, "Commodities": 5, "Cash": 15},
    "moderate": {"US Equity": 40, "Intl Equity": 15, "Fixed Income": 25, "REITs": 5, "Commodities": 5, "Cash": 10},
    "aggressive": {"US Equity": 50, "Intl Equity": 20, "Fixed Income": 10, "REITs": 5, "Commodities": 3, "Cash": 2},
}

def portfolio_agent(state):
    start = time.time()
    profile = state.get("profile_summary", {})
    portfolio = state.get("portfolio_data", [])
    risk_tolerance = profile.get("risk_tolerance", "moderate")
    target = TARGET_ALLOCATIONS.get(risk_tolerance, TARGET_ALLOCATIONS["moderate"])
    total_value = sum(h.get("current_value", 0) for h in portfolio)

    current_alloc = {}
    for h in portfolio:
        at = h.get("asset_type", "Other")
        if at in ("Single Stock", "Crypto"):
            at = "US Equity" if at == "Single Stock" else "Alternatives"
        current_alloc[at] = current_alloc.get(at, 0) + h.get("current_value", 0)

    current_pct = {k: round(v / total_value * 100, 1) if total_value else 0 for k, v in current_alloc.items()}

    drift_analysis, trades, total_drift = [], [], 0
    for asset_type, target_pct in target.items():
        current = current_pct.get(asset_type, 0)
        drift = round(current - target_pct, 1)
        total_drift += abs(drift)
        drift_analysis.append({"asset_type": asset_type, "target_pct": target_pct, "current_pct": current, "drift_pct": drift,
                               "status": "overweight" if drift > 2 else ("underweight" if drift < -2 else "on_target")})
        if abs(drift) > 2:
            trades.append({"asset_type": asset_type, "action": "SELL" if drift > 0 else "BUY",
                           "amount": round(abs(drift / 100 * total_value), 2), "from_pct": current, "to_pct": target_pct,
                           "rationale": f"{'Reduce' if drift > 0 else 'Increase'} {asset_type} by {abs(drift):.1f}%"})

    health_score = max(0, round(100 - total_drift * 2, 1))
    recommendations = []
    if trades:
        recommendations.append({"type": "portfolio_rebalancing", "title": "Portfolio Rebalancing Required",
            "description": f"Portfolio drifted {total_drift:.1f}% from target. Health: {health_score}/100. {len(trades)} trades needed.",
            "details": {"health_score": health_score, "drift_analysis": drift_analysis, "trades": trades,
                        "current_allocation": current_pct, "target_allocation": target},
            "projected_impact": f"Portfolio health {health_score} → 100", "confidence": 0.88,
            "priority": "high" if health_score < 70 else "medium"})

    reasoning = (f"Portfolio analysis for {risk_tolerance} profile. AUM: ${total_value:,.0f}. "
                 f"Drift: {total_drift:.1f}%. Health: {health_score}/100. {len(trades)} rebalancing trades generated.")
    duration = int((time.time() - start) * 1000)

    return {"portfolio_recommendations": recommendations, "messages": [("agent", f"[Portfolio Agent] {reasoning}")],
            "agent_outputs": {"portfolio_agent": {"recommendations": recommendations, "health_score": health_score, "reasoning": reasoning, "duration_ms": duration}}}
