from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_AGENTS = {
    "knowledge_agent": {"url": "http://knowledge-agent:8001", "enabled": True},
    "vulnerability_agent": {"url": "http://vulnerability-agent:8002", "enabled": True},
    "catalog_agent": {"url": "http://catalog-agent:8003", "enabled": True},
}


@dataclass
class RegisteredAgent:
    name: str
    url: str
    enabled: bool = True


class AgentRegistry:
    def __init__(self, agents: dict[str, dict] | None = None):
        self._agents = self._load_agents(agents)

    def enabled_agents(self) -> list[RegisteredAgent]:
        return [agent for agent in self._agents.values() if agent.enabled]

    def get(self, name: str) -> RegisteredAgent | None:
        return self._agents.get(name)

    def as_dict(self) -> dict[str, dict]:
        return {
            name: {"url": agent.url, "enabled": agent.enabled}
            for name, agent in self._agents.items()
        }

    def _load_agents(self, agents: dict[str, dict] | None) -> dict[str, RegisteredAgent]:
        raw_agents = agents or load_registry_from_env() or DEFAULT_AGENTS
        return {
            name: RegisteredAgent(
                name=name,
                url=str(config.get("url", "")).rstrip("/"),
                enabled=bool(config.get("enabled", True)),
            )
            for name, config in raw_agents.items()
        }


def load_registry_from_env() -> dict[str, dict] | None:
    registry_json = os.getenv("AGENT_REGISTRY_JSON", "").strip()
    if registry_json:
        return json.loads(registry_json)

    registry_path = os.getenv("AGENT_REGISTRY_PATH", "").strip()
    if registry_path:
        path = Path(registry_path)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))

    return None

