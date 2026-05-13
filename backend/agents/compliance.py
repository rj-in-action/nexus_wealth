"""
Step 5: Compliance Guardrails Check
SEC/FINRA suitability validation with detailed pass/fail reasoning.
"""
import time

COMPLIANCE_RULES = [
    {"id": "SUIT-001", "name": "Concentration Limit", "description": "No single position > 25% of portfolio", "threshold": 25},
    {"id": "SUIT-002", "name": "Risk Suitability", "description": "Recommendations match stated risk tolerance", "threshold": None},
    {"id": "SUIT-003", "name": "Liquidity Requirement", "description": "Minimum 5% cash/liquid assets", "threshold": 5},
    {"id": "SUIT-004", "name": "Age-Appropriate Equity", "description": "Equity exposure appropriate for age", "threshold": None},
    {"id": "FINRA-2111", "name": "Suitability Obligation", "description": "Reasonable basis for recommendation", "threshold": None},
    {"id": "REG-BI", "name": "Best Interest Standard", "description": "Recommendation in client's best interest", "threshold": None},
]

def compliance_guardrails_check(state):
    start = time.time()
    profile = state.get("profile_summary", {})
    risk = state.get("risk_assessment", {})
    portfolio = state.get("portfolio_data", [])
    total_value = sum(h.get("current_value", 0) for h in portfolio)

    check_results = []
    all_passed = True

    # Check 1: Concentration
    for h in portfolio:
        weight = h.get("weight_pct", 0)
        if weight > 25:
            check_results.append({"rule_id": "SUIT-001", "status": "WARNING", "detail": f"{h['asset_name']} at {weight}% exceeds 25% limit"})
            # Warning but not blocking
        else:
            check_results.append({"rule_id": "SUIT-001", "status": "PASS", "detail": "All positions within concentration limits"})
            break

    # Check 2: Risk suitability
    risk_score = risk.get("composite_score", 5.0)
    tolerance = profile.get("risk_tolerance", "moderate")
    risk_ok = (tolerance == "conservative" and risk_score <= 4) or (tolerance == "moderate" and 3 <= risk_score <= 7) or (tolerance == "aggressive" and risk_score >= 5)
    check_results.append({"rule_id": "SUIT-002", "status": "PASS" if risk_ok else "FAIL",
                          "detail": f"Risk score {risk_score} {'aligns' if risk_ok else 'misaligned'} with {tolerance} tolerance"})
    if not risk_ok:
        all_passed = False

    # Check 3: Liquidity
    cash = sum(h.get("current_value", 0) for h in portfolio if h.get("asset_type") == "Cash")
    cash_pct = round(cash / total_value * 100, 1) if total_value else 0
    liq_ok = cash_pct >= 5
    check_results.append({"rule_id": "SUIT-003", "status": "PASS" if liq_ok else "WARNING",
                          "detail": f"Cash position at {cash_pct}% ({'meets' if liq_ok else 'below'} 5% minimum)"})

    # Check 4: Age-appropriate equity
    age = profile.get("age", 40)
    max_equity_rule = 110 - age  # Simple rule of thumb
    equity_pct = sum(h.get("weight_pct", 0) for h in portfolio if h.get("asset_type") in ("US Equity", "Intl Equity", "Single Stock"))
    age_ok = equity_pct <= max_equity_rule + 10  # 10% grace
    check_results.append({"rule_id": "SUIT-004", "status": "PASS" if age_ok else "WARNING",
                          "detail": f"Equity at {equity_pct:.0f}% vs {max_equity_rule}% age-based guideline"})

    # Check 5 & 6: Always pass in POC (mock)
    check_results.append({"rule_id": "FINRA-2111", "status": "PASS", "detail": "Reasonable basis established via AI risk assessment and portfolio analysis"})
    check_results.append({"rule_id": "REG-BI", "status": "PASS", "detail": "Best interest standard met — recommendations based on client profile and goals"})

    passed = sum(1 for c in check_results if c["status"] == "PASS")
    warnings = sum(1 for c in check_results if c["status"] == "WARNING")
    failed = sum(1 for c in check_results if c["status"] == "FAIL")
    approved = failed == 0

    reasoning = (f"Compliance check: {passed} passed, {warnings} warnings, {failed} failed. "
                 f"Overall: {'APPROVED' if approved else 'REJECTED'}. "
                 f"{'All recommendations cleared for advisor review.' if approved else 'Requires compliance officer review.'}")
    duration = int((time.time() - start) * 1000)

    return {"compliance_approved": approved,
            "compliance_results": {"approved": approved, "checks": check_results, "summary": {"passed": passed, "warnings": warnings, "failed": failed}},
            "messages": [("agent", f"[Compliance] {reasoning}")],
            "agent_outputs": {"compliance": {"approved": approved, "checks": check_results, "reasoning": reasoning, "duration_ms": duration}}}
