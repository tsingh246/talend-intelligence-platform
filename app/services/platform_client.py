from __future__ import annotations

import json
import os
import time
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
    submitted = submit_platform_agent_run(
        agent_name=agent_name,
        options=options,
        repo_id=repo_id,
        artifact_ids=artifact_ids,
        timeout_seconds=30,
    )
    return wait_for_platform_run(
        submitted["run_id"],
        timeout_seconds=timeout_seconds,
    )


def submit_platform_agent_run(
    agent_name: str,
    options: dict[str, Any] | None = None,
    repo_id: str = "",
    artifact_ids: list[str] | None = None,
    timeout_seconds: int = 30,
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
        f"{base_url}/runs/{agent_name}",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Platform orchestrator call failed: {exc}") from exc


def wait_for_platform_run(
    run_id: str,
    timeout_seconds: int = 180,
    poll_interval_seconds: float = 1.0,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_status: dict[str, Any] = {}
    while time.monotonic() < deadline:
        last_status = get_platform_run(run_id)
        if last_status.get("status") in {"success", "partial", "error"}:
            response = last_status.get("response")
            if response:
                return response
            raise RuntimeError(last_status.get("error") or f"Run {run_id} finished without a response.")
        time.sleep(poll_interval_seconds)

    raise TimeoutError(
        f"Platform run {run_id} did not finish within {timeout_seconds} seconds. "
        f"Last status: {last_status.get('status', 'unknown')}"
    )


def get_platform_run(run_id: str, timeout_seconds: int = 30) -> dict[str, Any]:
    base_url = get_platform_url()
    request = urllib.request.Request(
        f"{base_url}/runs/{run_id}",
        headers={"Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Platform run status call failed: {exc}") from exc
