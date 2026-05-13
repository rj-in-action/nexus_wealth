# Nexus Wealth

Nexus Wealth is a next-generation wealth management platform utilizing Agentic AI to automate the advisory lifecycle from client ingestion to outside asset detection and compliance checks.

## Architecture (POC)
- **Frontend**: Vanilla HTML/JS/CSS (Simulating Advisor Dashboard).
- **Backend Orchestrator**: Python, LangGraph, FastAPI.
- **AI/ML Layer**: Open-source/commercial LLMs via LangChain.
- **Data Layer**: SQLite (simulated Client 360 data).

## Getting Started

### Backend
1. Navigate to the `backend/` directory.
2. Install dependencies: `pip install -r requirements.txt`.
3. Rename `.env.example` to `.env` and add your API keys.
4. Run the API: `uvicorn main:app --reload`.

### Frontend
1. Navigate to the `frontend/` directory.
2. Open `index.html` in your browser.
