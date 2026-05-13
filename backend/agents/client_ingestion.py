"""
Step 1: Client Profile Ingestion Agent
Loads Client 360 data and enriches the pipeline state with client context.
"""
import json
import time


def client_ingestion_agent(state):
    """
    Ingests client profile from Client 360 database.
    Identifies key financial indicators, life events, and advisory triggers.
    """
    start = time.time()
    client = state.get("client_data", {})
    portfolio = state.get("portfolio_data", [])

    # Calculate portfolio metrics
    total_value = sum(h.get("current_value", 0) for h in portfolio)
    total_unrealized = sum(h.get("unrealized_gain_loss", 0) for h in portfolio)
    asset_types = {}
    for h in portfolio:
        t = h.get("asset_type", "Other")
        asset_types[t] = asset_types.get(t, 0) + h.get("current_value", 0)

    # Identify concentration risks
    concentration_warnings = []
    for h in portfolio:
        weight = h.get("weight_pct", 0)
        if weight > 20 and h.get("asset_type") == "Single Stock":
            concentration_warnings.append(
                f"Single stock '{h['asset_name']}' at {weight}% — exceeds 20% concentration threshold"
            )

    # Parse life events
    life_events = json.loads(client.get("life_events", "[]")) if isinstance(client.get("life_events"), str) else client.get("life_events", [])
    goals = json.loads(client.get("goals", "[]")) if isinstance(client.get("goals"), str) else client.get("goals", [])

    profile_summary = {
        "client_name": f"{client.get('first_name', '')} {client.get('last_name', '')}",
        "age": client.get("age"),
        "risk_tolerance": client.get("risk_tolerance"),
        "tax_bracket": client.get("tax_bracket"),
        "annual_income": client.get("annual_income"),
        "total_aum": total_value,
        "total_unrealized_gains": total_unrealized,
        "asset_allocation": {k: round(v / total_value * 100, 1) if total_value else 0 for k, v in asset_types.items()},
        "concentration_warnings": concentration_warnings,
        "life_events": life_events,
        "goals": goals,
        "investment_horizon": client.get("investment_horizon"),
    }

    reasoning = (
        f"Ingested Client 360 profile for {profile_summary['client_name']}. "
        f"AUM: ${total_value:,.0f}, Risk Tolerance: {client.get('risk_tolerance', 'unknown')}, "
        f"Tax Bracket: {client.get('tax_bracket', 'unknown')}. "
        f"Found {len(concentration_warnings)} concentration warning(s). "
        f"Identified {len(life_events)} upcoming life events affecting advisory strategy."
    )

    duration = int((time.time() - start) * 1000)

    return {
        "profile_summary": profile_summary,
        "messages": [("agent", f"[Client Ingestion] {reasoning}")],
        "agent_outputs": {"client_ingestion": {"summary": profile_summary, "reasoning": reasoning, "duration_ms": duration}},
    }
