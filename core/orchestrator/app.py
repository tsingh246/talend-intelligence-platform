from __future__ import annotations

from fastapi import FastAPI

from core.agent_registry import AgentRegistry
from core.orchestrator.service import PlatformOrchestrator
from shared.schemas import AgentAnalyzeRequest

app = FastAPI(title="Talend Intelligence Platform Orchestrator", version="1.0.0")
orchestrator = PlatformOrchestrator(AgentRegistry())


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

