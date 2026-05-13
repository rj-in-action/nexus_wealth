from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
import operator

# 1. Define State Schema
class AgentState(TypedDict):
    messages: Annotated[List[tuple], operator.add]
    client_profile: Dict[str, Any]
    risk_score: float
    outside_assets: List[Dict[str, Any]]
    compliance_approved: bool

# 2. Define Specialist Nodes (Mocks for POC)

def outside_asset_detection_agent(state: AgentState):
    """Mocks the Outside Asset Detection Agent (identifies assets at competitors)."""
    # Simulate analyzing client 360 data to find outside assets
    detected_assets = [
        {"institution": "Fidelity", "type": "401k", "value": 250000},
        {"institution": "Charles Schwab", "type": "Brokerage", "value": 75000}
    ]
    return {"outside_assets": detected_assets, "messages": [("assistant", "Detected outside assets from Fidelity and Charles Schwab.")]}

def risk_assessment_agent(state: AgentState):
    """Mocks the AI Risk Assessment Agent."""
    return {"risk_score": 8.5, "messages": [("assistant", "Risk assessment completed. High risk tolerance identified.")]}

def compliance_guardrails_check(state: AgentState):
    """Mocks the Compliance Guardrails Check."""
    # In a real app, this would pause and wait for human-in-the-loop approval.
    # For the POC, we automatically approve if risk score is < 9.0
    approved = state.get("risk_score", 0) < 9.0
    status_msg = "approved" if approved else "rejected due to high risk"
    return {"compliance_approved": approved, "messages": [("assistant", f"Compliance check {status_msg}.")]}

def supervisor_agent(state: AgentState):
    """Mocks the Master Orchestrator."""
    last_msg = state["messages"][-1][1] if state["messages"] else ""
    return {"messages": [("assistant", "Supervisor: Routing tasks based on intent.")]}

# 3. Define the Graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("outside_asset_detector", outside_asset_detection_agent)
workflow.add_node("risk_assessor", risk_assessment_agent)
workflow.add_node("compliance", compliance_guardrails_check)

# Add edges
workflow.set_entry_point("supervisor")
workflow.add_edge("supervisor", "outside_asset_detector")
workflow.add_edge("outside_asset_detector", "risk_assessor")
workflow.add_edge("risk_assessor", "compliance")
workflow.add_edge("compliance", END)

# Compile graph
app = workflow.compile()
