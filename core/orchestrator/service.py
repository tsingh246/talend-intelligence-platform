from __future__ import annotations

import json
import urllib.error
import urllib.request

from core.agent_registry import AgentRegistry, RegisteredAgent
from shared.schemas import AgentAnalyzeRequest, AgentAnalyzeResponse


class PlatformOrchestrator:
    def __init__(self, registry: AgentRegistry | None = None):
        self.registry = registry or AgentRegistry()

    def analyze_agent(
        self,
        agent_name: str,
        request: AgentAnalyzeRequest,
    ) -> AgentAnalyzeResponse:
        agent = self.registry.get(agent_name)
        if not agent:
            return AgentAnalyzeResponse(
                agent=agent_name,
                version="unknown",
                status="error",
                summary=f"Agent {agent_name} is not registered.",
            )
        if not agent.enabled:
            return AgentAnalyzeResponse(
                agent=agent_name,
                version="unknown",
                status="error",
                summary=f"Agent {agent_name} is disabled.",
            )
        return call_agent(agent, request)

    def analyze_enabled(self, request: AgentAnalyzeRequest) -> AgentAnalyzeResponse:
        child_results = [
            self.analyze_agent(agent.name, request).dict()
            for agent in self.registry.enabled_agents()
        ]
        status = "success"
        if any(result["status"] == "error" for result in child_results):
            status = "partial"
        return AgentAnalyzeResponse(
            agent="platform_orchestrator",
            version="1.0.0",
            status=status,
            results=child_results,
            summary=f"Ran {len(child_results)} enabled agent(s).",
            metadata={"registry": self.registry.as_dict()},
        )


def call_agent(
    agent: RegisteredAgent,
    request: AgentAnalyzeRequest,
    timeout_seconds: int = 120,
) -> AgentAnalyzeResponse:
    payload = json.dumps(request.dict()).encode("utf-8")
    http_request = urllib.request.Request(
        f"{agent.url}/analyze",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(http_request, timeout=timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
        return AgentAnalyzeResponse(**body)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return AgentAnalyzeResponse(
            agent=agent.name,
            version="unknown",
            status="error",
            summary=f"Agent call failed: {exc}",
            metadata={"url": agent.url},
        )

