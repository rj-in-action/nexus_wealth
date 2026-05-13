"""
Step 7: Client Delivery Agent
Formats the final recommendation package for client-facing delivery (or Citi Sky).
"""
import time

def client_delivery_agent(state):
    start = time.time()
    profile = state.get("profile_summary", {})
    tax_recs = state.get("tax_recommendations", [])
    port_recs = state.get("portfolio_recommendations", [])
    alt_recs = state.get("alt_asset_recommendations", [])
    outside = state.get("outside_asset_analysis", {})
    risk = state.get("risk_assessment", {})

    all_recs = tax_recs + port_recs + alt_recs

    delivery_package = {
        "client_name": profile.get("client_name", ""),
        "generated_date": time.strftime("%Y-%m-%d"),
        "executive_summary": (
            f"Based on our comprehensive analysis of your ${profile.get('total_aum', 0):,.0f} portfolio, "
            f"we've identified {len(all_recs)} optimization opportunities. "
            f"Your risk profile is {risk.get('category', 'Moderate')} (score: {risk.get('composite_score', 5)}/10)."
        ),
        "key_actions": [{"title": r["title"], "description": r.get("description", ""), "priority": r.get("priority", "medium"),
                         "impact": r.get("projected_impact", "")} for r in all_recs],
        "outside_asset_summary": {
            "total_value": outside.get("total_outside_value", 0),
            "num_accounts": outside.get("num_accounts", 0),
            "migration_benefit": f"${outside.get('total_fee_savings', 0):,.0f}/year in fee savings",
        },
        "next_steps": [
            "Schedule follow-up meeting to discuss recommendations",
            "Review and sign account transfer forms for outside assets",
            "Confirm tax-loss harvesting preferences",
            "Set up automatic rebalancing schedule",
        ],
        "citi_sky_hook": {"available": True, "message": "These recommendations can be discussed via Citi Sky conversational interface."},
    }

    reasoning = (f"Delivery package assembled for {profile.get('client_name')}. "
                 f"{len(all_recs)} recommendations formatted. "
                 f"Outside asset migration plan included (${outside.get('total_outside_value', 0):,.0f}). "
                 f"Citi Sky integration hook enabled.")
    duration = int((time.time() - start) * 1000)

    return {"delivery_package": delivery_package, "messages": [("agent", f"[Client Delivery] {reasoning}")],
            "agent_outputs": {"client_delivery": {"package": delivery_package, "reasoning": reasoning, "duration_ms": duration}}}
