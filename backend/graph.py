"""
Nexus Wealth — LangGraph Pipeline Orchestrator
Full 8-step agentic pipeline for automated wealth advisory.

Pipeline Flow:
1. Client Profile Ingestion → 2. Outside Asset Detection → 3. Risk Assessment
→ 4a. Tax Agent | 4b. Portfolio Agent | 4c. Alt Assets Agent (parallel)
→ 5. Compliance Guardrails → 6. Advisor Review (HITL) → 7. Client Delivery
→ 8. Continuous Monitoring
"""
from typing import TypedDict, Annotated, List, Dict, Any, Optional
import operator
import time
import asyncio

from agents.client_ingestion import client_ingestion_agent
from agents.outside_asset_detection import outside_asset_detection_agent
from agents.risk_assessment import risk_assessment_agent
from agents.tax_agent import tax_agent
from agents.portfolio_agent import portfolio_agent
from agents.alt_assets_agent import alt_assets_agent
from agents.estate_agent import estate_agent
from agents.compliance import compliance_guardrails_check
from agents.advisor_review import advisor_review_agent
from agents.client_delivery import client_delivery_agent
from agents.monitoring import monitoring_agent


# --- State Schema ---
class PipelineState(TypedDict):
    # Input data
    client_id: str
    client_data: Dict[str, Any]
    portfolio_data: List[Dict[str, Any]]
    outside_assets_data: List[Dict[str, Any]]

    # Pipeline tracking
    messages: Annotated[List[tuple], operator.add]
    agent_outputs: Annotated[Dict[str, Any], lambda a, b: {**a, **b}]
    current_step: int

    # Agent outputs
    profile_summary: Dict[str, Any]
    outside_asset_analysis: Dict[str, Any]
    risk_score: float
    risk_assessment: Dict[str, Any]
    tax_recommendations: List[Dict[str, Any]]
    portfolio_recommendations: List[Dict[str, Any]]
    alt_asset_recommendations: List[Dict[str, Any]]
    estate_recommendations: List[Dict[str, Any]]
    compliance_approved: bool
    compliance_results: Dict[str, Any]
    advisor_review: Dict[str, Any]
    delivery_package: Dict[str, Any]
    monitoring_config: Dict[str, Any]


# --- Step Wrappers (add delays for demo effect) ---

STEP_NAMES = [
    "Client Profile Ingestion",
    "Outside Asset Detection",
    "AI Risk Assessment",
    "Tax Optimization",
    "Portfolio Rebalancing",
    "Alternative Assets",
    "Compliance Guardrails",
    "Advisor Review",
    "Client Delivery",
    "Continuous Monitoring",
]


def _wrap(agent_fn, step_num, delay=0.3):
    """Wrap an agent function with step tracking and optional delay."""
    def wrapped(state):
        time.sleep(delay)  # Simulate processing for demo
        result = agent_fn(state)
        result["current_step"] = step_num
        return result
    return wrapped


# Wrapped agents with step numbers
step_1_ingestion = _wrap(client_ingestion_agent, 1, delay=0.4)
step_2_outside_assets = _wrap(outside_asset_detection_agent, 2, delay=0.5)
step_3_risk = _wrap(risk_assessment_agent, 3, delay=0.4)
step_4a_tax = _wrap(tax_agent, 4, delay=0.5)
step_4b_portfolio = _wrap(portfolio_agent, 5, delay=0.4)
step_4c_alts = _wrap(alt_assets_agent, 6, delay=0.3)
step_4d_estate = _wrap(estate_agent, 7, delay=0.4)
step_5_compliance = _wrap(compliance_guardrails_check, 8, delay=0.4)
step_6_review = _wrap(advisor_review_agent, 9, delay=0.2)
step_7_delivery = _wrap(client_delivery_agent, 10, delay=0.3)
step_8_monitoring = _wrap(monitoring_agent, 11, delay=0.2)


def run_pipeline_sync(client_data, portfolio_data, outside_assets_data, client_id="unknown",
                      progress_callback=None):
    """
    Run the full pipeline synchronously, calling each agent in sequence.
    Returns the final state. Optionally calls progress_callback(step_num, step_name, result)
    after each step.
    """
    state = {
        "client_id": client_id,
        "client_data": client_data,
        "portfolio_data": portfolio_data,
        "outside_assets_data": outside_assets_data,
        "messages": [],
        "agent_outputs": {},
        "current_step": 0,
        "profile_summary": {},
        "outside_asset_analysis": {},
        "risk_score": 0.0,
        "risk_assessment": {},
        "tax_recommendations": [],
        "portfolio_recommendations": [],
        "alt_asset_recommendations": [],
        "estate_recommendations": [],
        "compliance_approved": False,
        "compliance_results": {},
        "advisor_review": {},
        "delivery_package": {},
        "monitoring_config": {},
    }

    steps = [
        (1, "Client Profile Ingestion", step_1_ingestion),
        (2, "Outside Asset Detection", step_2_outside_assets),
        (3, "AI Risk Assessment", step_3_risk),
        (4, "Tax Optimization", step_4a_tax),
        (5, "Portfolio Rebalancing", step_4b_portfolio),
        (6, "Alternative Assets", step_4c_alts),
        (7, "Estate & Legacy Planning", step_4d_estate),
        (8, "Compliance Guardrails", step_5_compliance),
        (9, "Advisor Review", step_6_review),
        (10, "Client Delivery", step_7_delivery),
        (11, "Continuous Monitoring", step_8_monitoring),
    ]

    for step_num, step_name, agent_fn in steps:
        try:
            result = agent_fn(state)
            # Merge result into state
            for key, value in result.items():
                if key == "messages":
                    state["messages"] = state.get("messages", []) + value
                elif key == "agent_outputs":
                    state["agent_outputs"] = {**state.get("agent_outputs", {}), **value}
                else:
                    state[key] = value

            if progress_callback:
                progress_callback(step_num, step_name, result)

        except Exception as e:
            error_msg = f"Error in {step_name}: {str(e)}"
            state["messages"] = state.get("messages", []) + [("error", error_msg)]
            if progress_callback:
                progress_callback(step_num, step_name, {"error": str(e)})

    return state
