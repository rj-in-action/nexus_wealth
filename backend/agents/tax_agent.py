"""
Step 4a: Tax Optimization Agent
Identifies tax-loss harvesting opportunities, Roth conversion analysis,
and tax-efficient positioning strategies.
"""
import time
import json


def tax_agent(state):
    """
    Analyzes portfolio for tax optimization opportunities including
    tax-loss harvesting, Roth conversions, and asset location optimization.
    """
    start = time.time()
    profile = state.get("profile_summary", {})
    portfolio = state.get("portfolio_data", [])
    tax_bracket = profile.get("tax_bracket", "24%")
    income = profile.get("annual_income", 0)

    tax_rate = float(tax_bracket.replace("%", "")) / 100

    recommendations = []

    # 1. Tax-Loss Harvesting scan
    harvest_candidates = []
    for h in portfolio:
        unrealized = h.get("unrealized_gain_loss", 0)
        if unrealized < -500:  # Material loss threshold
            tax_savings = abs(unrealized) * tax_rate
            harvest_candidates.append({
                "asset": h["asset_name"],
                "ticker": h.get("ticker", ""),
                "unrealized_loss": unrealized,
                "potential_tax_savings": round(tax_savings, 2),
                "replacement_etf": _get_replacement(h.get("ticker", "")),
            })

    if harvest_candidates:
        total_harvest_savings = sum(c["potential_tax_savings"] for c in harvest_candidates)
        recommendations.append({
            "type": "tax_loss_harvesting",
            "title": "Tax-Loss Harvesting Opportunities",
            "description": f"Identified {len(harvest_candidates)} positions with unrealized losses. "
                          f"Harvesting these losses could save approximately ${total_harvest_savings:,.0f} in taxes this year.",
            "details": harvest_candidates,
            "projected_impact": f"${total_harvest_savings:,.0f} estimated tax savings",
            "confidence": 0.92,
            "priority": "high",
        })

    # 2. Roth Conversion Analysis
    if income < 350000 and profile.get("age", 40) < 55:
        roth_amount = min(50000, income * 0.1)
        roth_tax_cost = roth_amount * tax_rate
        projected_growth = roth_amount * 1.07 ** 20  # 7% annual growth over 20 years
        tax_free_gains = projected_growth - roth_amount

        recommendations.append({
            "type": "roth_conversion",
            "title": "Roth Conversion Opportunity",
            "description": f"Consider converting ${roth_amount:,.0f} from Traditional IRA to Roth IRA. "
                          f"Current tax cost: ${roth_tax_cost:,.0f}, but projected tax-free growth of ${tax_free_gains:,.0f} over 20 years.",
            "details": {
                "conversion_amount": roth_amount,
                "tax_cost_now": round(roth_tax_cost, 2),
                "projected_tax_free_growth": round(tax_free_gains, 2),
                "net_benefit": round(tax_free_gains - roth_tax_cost, 2),
            },
            "projected_impact": f"${tax_free_gains - roth_tax_cost:,.0f} net long-term benefit",
            "confidence": 0.78,
            "priority": "medium",
        })

    # 3. Asset Location Optimization
    equity_in_taxable = sum(
        h.get("current_value", 0) for h in portfolio
        if h.get("asset_type") in ("US Equity", "Intl Equity") and h.get("ticker") not in ("PRIV", "F500")
    )
    bond_value = sum(h.get("current_value", 0) for h in portfolio if "Fixed Income" in h.get("asset_type", ""))

    if equity_in_taxable > 0 and bond_value > 0:
        potential_savings = bond_value * 0.03 * tax_rate  # 3% yield taxed as ordinary income
        recommendations.append({
            "type": "asset_location",
            "title": "Asset Location Optimization",
            "description": "Move bond holdings to tax-advantaged accounts (IRA/401k) and equity to taxable accounts "
                          "to benefit from lower capital gains rates on equities.",
            "details": {
                "bonds_to_relocate": round(bond_value, 2),
                "annual_tax_savings": round(potential_savings, 2),
            },
            "projected_impact": f"${potential_savings:,.0f}/year in tax savings",
            "confidence": 0.85,
            "priority": "medium",
        })

    total_savings = sum(
        float(r["projected_impact"].replace("$", "").replace(",", "").split("/")[0].split(" ")[0])
        for r in recommendations if r["projected_impact"]
    )

    reasoning = (
        f"Tax analysis for {tax_bracket} bracket (${income:,.0f} income). "
        f"Found {len(harvest_candidates)} tax-loss harvesting candidates. "
        f"Generated {len(recommendations)} tax optimization recommendations. "
        f"Total projected tax impact: ${total_savings:,.0f}."
    )

    duration = int((time.time() - start) * 1000)

    return {
        "tax_recommendations": recommendations,
        "messages": [("agent", f"[Tax Agent] {reasoning}")],
        "agent_outputs": {"tax_agent": {"recommendations": recommendations, "reasoning": reasoning, "duration_ms": duration}},
    }


def _get_replacement(ticker):
    """Get a tax-loss harvesting replacement ETF (avoids wash sale)."""
    replacements = {
        "VOO": "IVV",  # S&P 500 swap
        "QQQ": "QQQM",  # Nasdaq swap
        "VTI": "ITOT",  # Total market swap
        "AGG": "BND",  # Bond swap
        "EEM": "IEMG",  # EM swap
        "VNQ": "SCHH",  # REIT swap
        "ARKK": "KOMP",  # Innovation swap
        "IBIT": "BITO",  # Bitcoin swap
    }
    return replacements.get(ticker, "Consult advisor for suitable replacement")
