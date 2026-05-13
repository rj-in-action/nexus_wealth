"""
Step 8: Continuous Monitoring Agent
Sets up ongoing portfolio monitoring and rebalancing triggers.
"""
import time

def monitoring_agent(state):
    start = time.time()
    profile = state.get("profile_summary", {})
    risk = state.get("risk_assessment", {})
    port_recs = state.get("portfolio_recommendations", [])

    # Define monitoring rules based on risk profile
    risk_score = risk.get("composite_score", 5.0)
    if risk_score >= 7:
        rebalance_threshold, review_freq, drift_alert = 7.0, "Monthly", 5.0
    elif risk_score >= 4:
        rebalance_threshold, review_freq, drift_alert = 5.0, "Quarterly", 4.0
    else:
        rebalance_threshold, review_freq, drift_alert = 3.0, "Quarterly", 3.0

    monitoring_config = {
        "rebalance_threshold_pct": rebalance_threshold,
        "review_frequency": review_freq,
        "drift_alert_threshold_pct": drift_alert,
        "tax_loss_scan_frequency": "Daily during market hours",
        "market_event_triggers": ["S&P 500 drops > 5%", "Fed rate change", "Client life event detected"],
        "alerts_enabled": True,
        "auto_rebalance": False,  # Requires advisor approval
        "next_review_date": "2026-06-15",
        "monitoring_status": "active",
    }

    reasoning = (f"Monitoring configured for {profile.get('client_name')}. "
                 f"Rebalance trigger: {rebalance_threshold}% drift. Review: {review_freq}. "
                 f"Tax-loss harvesting scan: daily. Auto-rebalance: disabled (HITL required).")
    duration = int((time.time() - start) * 1000)

    return {"monitoring_config": monitoring_config, "messages": [("agent", f"[Monitoring] {reasoning}")],
            "agent_outputs": {"monitoring": {"config": monitoring_config, "reasoning": reasoning, "duration_ms": duration}}}
