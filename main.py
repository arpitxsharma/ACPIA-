from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

from services.data_loader import load_case, load_evidence, load_entities
from agents.evidence_agent import run_evidence_agent, get_processed_evidence
from agents.correlation_agent import run_correlation_agent, get_correlation_result
from agents.timeline_agent import run_timeline_agent, get_timeline_result
from agents.risk_agent import run_risk_agent, get_risk_result
from agents.copilot import answer_question
from services.review_status import get_review_status, submit_review_decision
from agents.graph import run_pipeline

app = FastAPI(title="ACPIA+ API")

# Frontend runs on a different port during development (Vite default 5173),
# so we need CORS enabled or the browser blocks the requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "ACPIA+ backend"}


# We only have one demo case for the PoC, so case_id is currently ignored
# beyond checking it matches. Real multi-case support would mean looking
# this up in a proper database instead of a fixed JSON file.
DEMO_CASE_ID = "ACPIA-1024"


@app.get("/api/cases/{case_id}")
def get_case(case_id: str):
    if case_id != DEMO_CASE_ID:
        raise HTTPException(status_code=404, detail="Case not found")
    return load_case()


@app.get("/api/cases/{case_id}/evidence")
def get_case_evidence(case_id: str):
    if case_id != DEMO_CASE_ID:
        raise HTTPException(status_code=404, detail="Case not found")
    return load_evidence()


@app.get("/api/cases/{case_id}/entities")
def get_case_entities(case_id: str):
    if case_id != DEMO_CASE_ID:
        raise HTTPException(status_code=404, detail="Case not found")
    return load_entities()


# --- Evidence Agent ---
# GET returns cached results (fast, used on normal page load).
# POST actually re-runs the agent (used by the "Run Evidence Agent"
# button during the live demo, so the judge sees it process for real).

@app.get("/api/cases/{case_id}/evidence/processed")
def get_evidence_processed(case_id: str):
    if case_id != DEMO_CASE_ID:
        raise HTTPException(status_code=404, detail="Case not found")
    return get_processed_evidence()


@app.post("/api/cases/{case_id}/agents/evidence/run")
def run_evidence_agent_route(case_id: str):
    if case_id != DEMO_CASE_ID:
        raise HTTPException(status_code=404, detail="Case not found")
    return run_evidence_agent()


# --- Correlation Agent ---

@app.get("/api/cases/{case_id}/correlation")
def get_correlation(case_id: str):
    if case_id != DEMO_CASE_ID:
        raise HTTPException(status_code=404, detail="Case not found")
    return get_correlation_result()


@app.post("/api/cases/{case_id}/agents/correlation/run")
def run_correlation_agent_route(case_id: str):
    if case_id != DEMO_CASE_ID:
        raise HTTPException(status_code=404, detail="Case not found")
    return run_correlation_agent()


# --- Timeline Agent ---

@app.get("/api/cases/{case_id}/timeline")
def get_timeline(case_id: str):
    if case_id != DEMO_CASE_ID:
        raise HTTPException(status_code=404, detail="Case not found")
    return get_timeline_result()


@app.post("/api/cases/{case_id}/agents/timeline/run")
def run_timeline_agent_route(case_id: str):
    if case_id != DEMO_CASE_ID:
        raise HTTPException(status_code=404, detail="Case not found")
    return run_timeline_agent()


# --- Risk Agent ---

@app.get("/api/cases/{case_id}/risk")
def get_risk(case_id: str):
    if case_id != DEMO_CASE_ID:
        raise HTTPException(status_code=404, detail="Case not found")
    return get_risk_result()


@app.post("/api/cases/{case_id}/agents/risk/run")
def run_risk_agent_route(case_id: str):
    if case_id != DEMO_CASE_ID:
        raise HTTPException(status_code=404, detail="Case not found")
    return run_risk_agent()


# --- AI Copilot ---

class CopilotQuestion(BaseModel):
    question: str


@app.post("/api/cases/{case_id}/copilot/ask")
def copilot_ask(case_id: str, payload: CopilotQuestion):
    if case_id != DEMO_CASE_ID:
        raise HTTPException(status_code=404, detail="Case not found")
    return answer_question(payload.question)


# --- Human-in-the-Loop ---
# The AI never makes the final call - these routes just record what the
# human investigator decided. There's no AI logic here at all.

class ReviewDecision(BaseModel):
    decision: str  # "approved" | "rejected" | "more_evidence_requested"
    notes: str | None = None


@app.get("/api/cases/{case_id}/review")
def get_review(case_id: str):
    if case_id != DEMO_CASE_ID:
        raise HTTPException(status_code=404, detail="Case not found")
    return get_review_status()


@app.post("/api/cases/{case_id}/review")
def post_review(case_id: str, payload: ReviewDecision):
    if case_id != DEMO_CASE_ID:
        raise HTTPException(status_code=404, detail="Case not found")
    try:
        return submit_review_decision(payload.decision, payload.notes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Run the full pipeline in one call ---
# Used by the "LOAD DEMO CASE" button - runs all 4 agents through the
# LangGraph pipeline (agents/graph.py), matching the architecture diagram.
# Returns a short summary of what each agent found.

@app.post("/api/cases/{case_id}/agents/run-all")
def run_all_agents(case_id: str):
    if case_id != DEMO_CASE_ID:
        raise HTTPException(status_code=404, detail="Case not found")

    result = run_pipeline()
    evidence = result["evidence_result"]
    correlation = result["correlation_result"]
    timeline = result["timeline_result"]
    risk = result["risk_result"]

    return {
        "evidence_processed": len(evidence),
        "correlation_edges_found": len(correlation["edges"]),
        "timeline_events_found": len(timeline["events"]),
        "risk_level": risk["risk_level"],
        "risk_score": risk["risk_score"],
    }
