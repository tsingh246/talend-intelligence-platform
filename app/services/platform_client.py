from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def get_platform_url() -> str:
    return os.getenv("PLATFORM_ORCHESTRATOR_URL", "http://localhost:8010").strip().rstrip("/")


def call_platform_agent(
    agent_name: str,
    options: dict[str, Any] | None = None,
    repo_id: str = "",
    artifact_ids: list[str] | None = None,
    timeout_seconds: int = 180,
) -> dict[str, Any]:
    base_url = get_platform_url()

    payload = json.dumps(
        {
            "repo_id": repo_id,
            "artifact_ids": artifact_ids or [],
            "options": options or {},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/analyze/{agent_name}",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Platform orchestrator call failed: {exc}") from exc
