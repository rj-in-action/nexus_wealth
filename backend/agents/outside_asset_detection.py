"""
Step 2: Outside Asset Detection Agent ★ NEW
Analyzes Client 360 data to identify assets at competing institutions
and generates migration strategies.
"""
import time


def outside_asset_detection_agent(state):
    """
    Detects outside assets at competitor institutions and creates
    migration opportunity assessments.
    """
    start = time.time()
    outside_assets = state.get("outside_assets_data", [])
    profile = state.get("profile_summary", {})
    risk_tolerance = profile.get("risk_tolerance", "moderate")

    total_outside = sum(a.get("estimated_value", 0) for a in outside_assets)

    migration_strategies = []
    for asset in outside_assets:
        institution = asset.get("institution", "Unknown")
        acct_type = asset.get("account_type", "Unknown")
        value = asset.get("estimated_value", 0)

        # Generate migration strategy based on account type
        if "401" in acct_type or "403" in acct_type:
            strategy = {
                "institution": institution,
                "account_type": acct_type,
                "value": value,
                "recommended_action": "Direct Rollover to Citi IRA",
                "tax_impact": "Tax-free if direct rollover",
                "timeline": "5-7 business days",
                "priority": "high",
                "fee_savings": round(value * 0.005, 2),  # 50bps potential savings
            }
        elif "IRA" in acct_type:
            strategy = {
                "institution": institution,
                "account_type": acct_type,
                "value": value,
                "recommended_action": "ACAT Transfer to Citi",
                "tax_impact": "No tax impact for like-kind transfer",
                "timeline": "3-5 business days",
                "priority": "high",
                "fee_savings": round(value * 0.003, 2),
            }
        elif "Robo" in acct_type or "Betterment" in institution or "Wealthfront" in institution:
            strategy = {
                "institution": institution,
                "account_type": acct_type,
                "value": value,
                "recommended_action": "Liquidate & Transfer (tax-aware)",
                "tax_impact": "Capital gains review required before liquidation",
                "timeline": "7-10 business days",
                "priority": "medium",
                "fee_savings": round(value * 0.004, 2),
            }
        else:
            strategy = {
                "institution": institution,
                "account_type": acct_type,
                "value": value,
                "recommended_action": "ACAT Transfer to Citi Brokerage",
                "tax_impact": "No tax impact for in-kind transfer",
                "timeline": "5-7 business days",
                "priority": "medium",
                "fee_savings": round(value * 0.003, 2),
            }

        migration_strategies.append(strategy)

    # Sort by priority and value
    migration_strategies.sort(key=lambda x: (0 if x["priority"] == "high" else 1, -x["value"]))

    total_fee_savings = sum(s["fee_savings"] for s in migration_strategies)

    reasoning = (
        f"Detected {len(outside_assets)} outside accounts totaling ${total_outside:,.0f} "
        f"across {len(set(a.get('institution') for a in outside_assets))} competing institutions. "
        f"Generated {len(migration_strategies)} migration strategies. "
        f"Estimated annual fee savings from consolidation: ${total_fee_savings:,.0f}. "
        f"High-priority migrations: {sum(1 for s in migration_strategies if s['priority'] == 'high')}."
    )

    duration = int((time.time() - start) * 1000)

    return {
        "outside_asset_analysis": {
            "total_outside_value": total_outside,
            "num_accounts": len(outside_assets),
            "migration_strategies": migration_strategies,
            "total_fee_savings": total_fee_savings,
        },
        "messages": [("agent", f"[Outside Asset Detection] {reasoning}")],
        "agent_outputs": {"outside_asset_detection": {"strategies": migration_strategies, "total_value": total_outside, "reasoning": reasoning, "duration_ms": duration}},
    }
