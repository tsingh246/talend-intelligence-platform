from __future__ import annotations

from fastapi import FastAPI

from agents.knowledge_agent.service import KnowledgeAgent
from shared.schemas import AgentAnalyzeRequest

agent = KnowledgeAgent()
app = FastAPI(title="Talend Knowledge Agent", version=agent.version)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "agent": agent.name, "version": agent.version}


@app.get("/metadata")
def metadata():
    return agent.metadata()


@app.post("/analyze")
def analyze(request: AgentAnalyzeRequest):
    return agent.analyze(request)

