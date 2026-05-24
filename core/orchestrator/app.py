from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request

from core.agent_registry import AgentRegistry
from core.orchestrator.run_store import AgentRunStore
from core.orchestrator.service import PlatformOrchestrator
from shared.schemas import AgentAnalyzeRequest, AgentRunSubmitResponse

app = FastAPI(title="Talend Intelligence Platform Orchestrator", version="1.0.0")
orchestrator = PlatformOrchestrator(AgentRegistry())
run_store = AgentRunStore()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "platform_orchestrator"}


@app.get("/agents")
def agents() -> dict:
    return orchestrator.registry.as_dict()


@app.post("/analyze")
def analyze(request: AgentAnalyzeRequest):
    return orchestrator.analyze_enabled(request)


@app.post("/analyze/{agent_name}")
def analyze_agent(agent_name: str, request: AgentAnalyzeRequest):
    return orchestrator.analyze_agent(agent_name, request)


@app.post("/runs")
def submit_enabled_run(request: AgentAnalyzeRequest, http_request: Request):
    run = run_store.submit(
        "platform_orchestrator",
        request,
        lambda: orchestrator.analyze_enabled(request),
    )
    return build_submit_response(run, http_request)


@app.post("/runs/{agent_name}")
def submit_agent_run(agent_name: str, request: AgentAnalyzeRequest, http_request: Request):
    run = run_store.submit(
        agent_name,
        request,
        lambda: orchestrator.analyze_agent(agent_name, request),
    )
    return build_submit_response(run, http_request)


@app.get("/runs/{run_id}")
def get_run(run_id: str):
    run = run_store.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} was not found.")
    return run


def build_submit_response(run, request: Request) -> AgentRunSubmitResponse:
    return AgentRunSubmitResponse(
        run_id=run.run_id,
        status=run.status,
        agent=run.agent,
        submitted_at=run.submitted_at,
        status_url=str(request.url_for("get_run", run_id=run.run_id)),
    )
