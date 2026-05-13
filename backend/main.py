from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
from graph import app as langgraph_app

app = FastAPI(title="Nexus Wealth API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    client_id: str

@app.get("/")
def read_root():
    return {"status": "Nexus Wealth API is running"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to trigger the LangGraph orchestration layer.
    """
    initial_state = {
        "messages": [("user", request.message)],
        "client_profile": {"client_id": request.client_id},
        "risk_score": 0.0,
        "outside_assets": [],
        "compliance_approved": False
    }
    
    # In a production app, we would use streaming (SSE) here.
    # For the POC, we return the final state or prompt for human-in-the-loop.
    result = langgraph_app.invoke(initial_state)
    
    return {
        "response": result["messages"][-1] if result.get("messages") else "No response generated.",
        "state": result
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
