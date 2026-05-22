"""
Step 4d: Estate & Legacy Planning Agent
Evaluates multi-generational wealth transfer, trust structures, 
529 college savings, and charitable giving strategies.
"""
import time
import json

def estate_agent(state):
    start = time.time()
    profile = state.get("profile_summary", {})
    age = profile.get("age", 40)
    income = profile.get("annual_income", 0)
    aum = profile.get("total_aum", 0)
    life_events = profile.get("life_events", [])
    goals = profile.get("goals", [])
    
    # Flatten life events and goals to a single string for simple keyword matching
    context_text = " ".join(life_events + goals).lower()
    
    recommendations = []
    
    # 1. 529 College Savings
    if "child" in context_text or "college" in context_text or "grandchild" in context_text:
        recommendations.append({
            "type": "estate_planning",
            "title": "529 College Savings Optimization",
            "description": "Life events indicate college funding goals. Recommend establishing or optimizing a 529 Plan to allow tax-free growth for education expenses.",
            "details": {
                "strategy": "529 Plan Contribution",
                "tax_benefit": "Tax-free growth and withdrawals for qualified education expenses.",
                "front_loading_option": "Allows up to 5 years of gift tax exclusion ($90,000 per individual) to be contributed at once."
            },
            "projected_impact": "Tax-free multi-generational growth",
            "confidence": 0.95,
            "priority": "medium"
        })
        
    # 2. Basic Trust & Beneficiary Review (Age or Wealth based)
    if age > 55 or aum > 500000:
        recommendations.append({
            "type": "estate_planning",
            "title": "Revocable Living Trust Setup",
            "description": f"Given your AUM of ${aum:,.0f} and profile, establishing a Revocable Living Trust is recommended to avoid probate and ensure seamless asset transition.",
            "details": {
                "strategy": "Revocable Living Trust",
                "probate_avoidance": True,
                "asset_protection": "Provides structure for beneficiaries."
            },
            "projected_impact": "Probate avoidance & seamless transition",
            "confidence": 0.88,
            "priority": "high" if age > 60 else "medium"
        })

    # 3. Charitable Giving / Donor-Advised Fund (High Income)
    if income > 300000:
        recommendations.append({
            "type": "estate_planning",
            "title": "Donor-Advised Fund (DAF) Strategy",
            "description": "In your tax bracket, utilizing a Donor-Advised Fund allows you to bunch charitable contributions, maximizing itemized deductions while distributing grants over time.",
            "details": {
                "strategy": "Donor-Advised Fund (DAF)",
                "tax_deduction": "Immediate deduction in the year of contribution.",
                "funding_source": "Recommend funding with highly appreciated stock to avoid capital gains tax."
            },
            "projected_impact": "Immediate tax deduction & capital gains avoidance",
            "confidence": 0.92,
            "priority": "medium"
        })

    reasoning = (
        f"Estate analysis for {age}-year-old with ${aum:,.0f} AUM. "
        f"Context keywords triggered {len(recommendations)} legacy strategies. "
        f"Generated recommendations for: {', '.join([r['title'] for r in recommendations])}."
    )

    duration = int((time.time() - start) * 1000)

    return {
        "estate_recommendations": recommendations,
        "messages": [("agent", f"[Estate Agent] {reasoning}")],
        "agent_outputs": {
            "estate_agent": {
                "recommendations": recommendations,
                "reasoning": reasoning,
                "duration_ms": duration
            }
        }
    }
