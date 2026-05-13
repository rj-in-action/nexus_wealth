"""
Step 6: Advisor Review Agent (Human-in-the-Loop)
Packages recommendations for advisor approval before client delivery.
"""
import time

def advisor_review_agent(state):
    start = time.time()
    compliance = state.get("compliance_results", {})
    tax_recs = state.get("tax_recommendations", [])
    port_recs = state.get("portfolio_recommendations", [])
    alt_recs = state.get("alt_asset_recommendations", [])
    outside = state.get("outside_asset_analysis", {})
    profile = state.get("profile_summary", {})

    all_recs = tax_recs + port_recs + alt_recs
    high_priority = [r for r in all_recs if r.get("priority") == "high"]
    total_recs = len(all_recs)

    review_package = {
        "client_name": profile.get("client_name", "Unknown"),
        "total_aum": profile.get("total_aum", 0),
        "risk_tolerance": profile.get("risk_tolerance", ""),
        "compliance_status": "Approved" if compliance.get("approved") else "Requires Review",
        "total_recommendations": total_recs,
        "high_priority_count": len(high_priority),
        "outside_asset_opportunity": outside.get("total_outside_value", 0),
        "recommendations_summary": [{"title": r["title"], "type": r["type"], "priority": r.get("priority", "medium"),
                                      "projected_impact": r.get("projected_impact", "")} for r in all_recs],
        "requires_approval": True,
        "approval_status": "pending",
    }

    reasoning = (f"Review package prepared for {profile.get('client_name')}. "
                 f"{total_recs} recommendations ({len(high_priority)} high priority). "
                 f"Outside asset opportunity: ${outside.get('total_outside_value', 0):,.0f}. "
                 f"Compliance: {review_package['compliance_status']}. Awaiting advisor approval.")
    duration = int((time.time() - start) * 1000)

    return {"advisor_review": review_package, "messages": [("agent", f"[Advisor Review] {reasoning}")],
            "agent_outputs": {"advisor_review": {"package": review_package, "reasoning": reasoning, "duration_ms": duration}}}
