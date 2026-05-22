"""
Nexus Wealth — FastAPI Backend
REST API + SSE for the Advisor Dashboard POC.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import json
import uuid
import asyncio
import threading
import time

from db import (
    get_all_clients, get_client, get_client_portfolio,
    get_client_outside_assets, get_pipeline_run, create_pipeline_run,
    update_pipeline_run, add_audit_entry, get_audit_trail,
    get_client_audit_trail, save_recommendation, get_recommendations,
    init_db
)
from graph import run_pipeline_sync
from seed_data import seed

# Initialize DB and seed data on startup
init_db()
seed()

app = FastAPI(
    title="Nexus Wealth API",
    description="Agentic Execution Engine for Wealth Management",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for pipeline SSE events
pipeline_events: Dict[str, List[dict]] = {}
pipeline_states: Dict[str, dict] = {}


# --- Models ---

class PipelineRequest(BaseModel):
    client_id: str

class ApprovalRequest(BaseModel):
    approved: bool
    advisor_notes: Optional[str] = ""


# --- Client Endpoints ---

@app.get("/")
def read_root():
    return {"status": "Nexus Wealth API v2.0 — Agentic Execution Engine", "agents": 10, "clients": 5}


@app.get("/api/clients")
def list_clients():
    """List all clients with portfolio summaries."""
    clients = get_all_clients()
    for c in clients:
        portfolio = get_client_portfolio(c["id"])
        outside = get_client_outside_assets(c["id"])
        c["portfolio_count"] = len(portfolio)
        c["outside_assets_count"] = len(outside)
        c["outside_assets_value"] = sum(a.get("estimated_value", 0) for a in outside)
        # Parse JSON fields for frontend
        c["life_events"] = json.loads(c.get("life_events", "[]")) if isinstance(c.get("life_events"), str) else []
        c["goals"] = json.loads(c.get("goals", "[]")) if isinstance(c.get("goals"), str) else []
    return {"clients": clients}


@app.get("/api/clients/{client_id}")
def get_client_detail(client_id: str):
    """Get full client profile with portfolio and outside assets."""
    client = get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    portfolio = get_client_portfolio(client_id)
    outside_assets = get_client_outside_assets(client_id)

    client["life_events"] = json.loads(client.get("life_events", "[]")) if isinstance(client.get("life_events"), str) else []
    client["goals"] = json.loads(client.get("goals", "[]")) if isinstance(client.get("goals"), str) else []

    # Parse outside asset details
    for a in outside_assets:
        a["asset_details"] = json.loads(a.get("asset_details", "{}")) if isinstance(a.get("asset_details"), str) else {}

    # Portfolio summary
    total_value = sum(h.get("current_value", 0) for h in portfolio)
    total_gain = sum(h.get("unrealized_gain_loss", 0) for h in portfolio)
    allocation = {}
    for h in portfolio:
        t = h.get("asset_type", "Other")
        allocation[t] = allocation.get(t, 0) + h.get("current_value", 0)
    allocation_pct = {k: round(v / total_value * 100, 1) if total_value else 0 for k, v in allocation.items()}

    return {
        "client": client,
        "portfolio": portfolio,
        "outside_assets": outside_assets,
        "summary": {
            "total_value": total_value,
            "total_unrealized_gain": total_gain,
            "allocation": allocation_pct,
            "outside_assets_total": sum(a.get("estimated_value", 0) for a in outside_assets),
        }
    }


@app.get("/api/clients/{client_id}/outside-assets")
def get_outside_assets(client_id: str):
    """Get detected outside assets for a client."""
    assets = get_client_outside_assets(client_id)
    for a in assets:
        a["asset_details"] = json.loads(a.get("asset_details", "{}")) if isinstance(a.get("asset_details"), str) else {}
    total = sum(a.get("estimated_value", 0) for a in assets)
    return {"outside_assets": assets, "total_value": total}


# --- Pipeline Endpoints ---

@app.post("/api/pipeline/run/{client_id}")
async def run_pipeline(client_id: str, background_tasks: BackgroundTasks):
    """Trigger the full 8-step agentic pipeline for a client."""
    client = get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
    pipeline_events[run_id] = []
    pipeline_states[run_id] = {"status": "starting"}

    create_pipeline_run(run_id, client_id)

    # Run pipeline in background thread
    background_tasks.add_task(_execute_pipeline, run_id, client_id)

    return {"run_id": run_id, "client_id": client_id, "status": "started"}


def _execute_pipeline(run_id: str, client_id: str):
    """Execute the pipeline in a background thread."""
    client = get_client(client_id)
    portfolio = get_client_portfolio(client_id)
    outside_assets = get_client_outside_assets(client_id)

    # Parse JSON fields
    for a in outside_assets:
        a["asset_details"] = json.loads(a.get("asset_details", "{}")) if isinstance(a.get("asset_details"), str) else {}

    def progress_callback(step_num, step_name, result):
        event = {
            "step": step_num,
            "name": step_name,
            "status": "error" if "error" in result else "completed",
            "timestamp": time.strftime("%H:%M:%S"),
        }

        # Extract reasoning from agent outputs
        for agent_key, agent_data in result.get("agent_outputs", {}).items():
            event["reasoning"] = agent_data.get("reasoning", "")
            event["duration_ms"] = agent_data.get("duration_ms", 0)

        pipeline_events[run_id].append(event)
        update_pipeline_run(run_id, current_step=step_num, status="running")

        # Save audit trail
        add_audit_entry(
            run_id=run_id, client_id=client_id, agent_name=step_name,
            step_number=step_num, status=event["status"],
            output_summary=event.get("reasoning", ""),
            duration_ms=event.get("duration_ms", 0)
        )

    try:
        final_state = run_pipeline_sync(
            client_data=client,
            portfolio_data=portfolio,
            outside_assets_data=outside_assets,
            client_id=client_id,
            progress_callback=progress_callback,
        )

        pipeline_states[run_id] = final_state

        # Save recommendations to DB
        all_recs = (
            final_state.get("tax_recommendations", []) +
            final_state.get("portfolio_recommendations", []) +
            final_state.get("alt_asset_recommendations", []) +
            final_state.get("estate_recommendations", [])
        )
        for rec in all_recs:
            save_recommendation(
                client_id=client_id, run_id=run_id,
                agent_name=rec.get("type", "unknown"),
                rec_type=rec.get("type", ""), title=rec.get("title", ""),
                description=rec.get("description", ""),
                projected_impact=rec.get("projected_impact", ""),
                confidence=rec.get("confidence", 0),
                reasoning_chain=json.dumps(rec.get("details", {})),
            )

        # Mark pipeline complete
        pipeline_events[run_id].append({
            "step": 0, "name": "Pipeline Complete", "status": "done",
            "timestamp": time.strftime("%H:%M:%S"),
        })
        update_pipeline_run(run_id, status="completed", completed_at=time.strftime("%Y-%m-%dT%H:%M:%S"))

    except Exception as e:
        pipeline_events[run_id].append({
            "step": -1, "name": "Pipeline Error", "status": "error",
            "reasoning": str(e), "timestamp": time.strftime("%H:%M:%S"),
        })
        update_pipeline_run(run_id, status="failed")


@app.get("/api/pipeline/status/{run_id}")
async def pipeline_status_sse(run_id: str):
    """SSE endpoint for real-time pipeline progress."""
    if run_id not in pipeline_events:
        raise HTTPException(status_code=404, detail="Run not found")

    async def event_generator():
        last_index = 0
        while True:
            events = pipeline_events.get(run_id, [])
            while last_index < len(events):
                event = events[last_index]
                yield f"data: {json.dumps(event)}\n\n"
                last_index += 1
                if event.get("status") == "done" or event.get("status") == "error" and event.get("step", 0) < 0:
                    return
            await asyncio.sleep(0.3)

    return StreamingResponse(event_generator(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "Connection": "keep-alive"})


@app.get("/api/pipeline/result/{run_id}")
def get_pipeline_result(run_id: str):
    """Get the full pipeline result after completion."""
    state = pipeline_states.get(run_id)
    if not state:
        run = get_pipeline_run(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        return {"run": run, "status": run.get("status", "unknown")}

    return {
        "status": "completed",
        "run_id": run_id,
        "profile_summary": state.get("profile_summary", {}),
        "outside_asset_analysis": state.get("outside_asset_analysis", {}),
        "risk_assessment": state.get("risk_assessment", {}),
        "tax_recommendations": state.get("tax_recommendations", []),
        "portfolio_recommendations": state.get("portfolio_recommendations", []),
        "alt_asset_recommendations": state.get("alt_asset_recommendations", []),
        "estate_recommendations": state.get("estate_recommendations", []),
        "compliance_results": state.get("compliance_results", {}),
        "advisor_review": state.get("advisor_review", {}),
        "delivery_package": state.get("delivery_package", {}),
        "monitoring_config": state.get("monitoring_config", {}),
        "messages": state.get("messages", []),
    }


@app.post("/api/pipeline/approve/{run_id}")
def approve_pipeline(run_id: str, request: ApprovalRequest):
    """Advisor approval endpoint (human-in-the-loop)."""
    run = get_pipeline_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    update_pipeline_run(run_id, advisor_approved=1 if request.approved else 0)

    add_audit_entry(
        run_id=run_id, client_id=run["client_id"],
        agent_name="Advisor Approval",
        step_number=8,
        status="approved" if request.approved else "rejected",
        output_summary=request.advisor_notes or ("Approved by advisor" if request.approved else "Rejected by advisor"),
    )

    return {"status": "approved" if request.approved else "rejected", "run_id": run_id}


# --- Recommendation & Audit Endpoints ---

@app.get("/api/recommendations/{client_id}")
def client_recommendations(client_id: str, run_id: Optional[str] = None):
    """Get recommendations for a client."""
    recs = get_recommendations(client_id, run_id)
    for r in recs:
        r["reasoning_chain"] = json.loads(r.get("reasoning_chain", "{}")) if isinstance(r.get("reasoning_chain"), str) else {}
    return {"recommendations": recs}


@app.get("/api/audit-trail/{run_id}")
def audit_trail(run_id: str):
    """Get full audit trail for a pipeline run."""
    trail = get_audit_trail(run_id)
    return {"audit_trail": trail, "run_id": run_id}


@app.get("/api/audit-trail/client/{client_id}")
def client_audit(client_id: str):
    """Get audit trail for a client."""
    trail = get_client_audit_trail(client_id)
    return {"audit_trail": trail}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
