from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentAnalyzeRequest(BaseModel):
    repo_id: str = Field(default="", description="Repository or project identifier.")
    artifact_ids: list[str] = Field(default_factory=list)
    options: dict[str, Any] = Field(default_factory=dict)


class AgentAnalyzeResponse(BaseModel):
    agent: str
    version: str
    status: Literal["success", "partial", "error"]
    results: list[dict[str, Any]] = Field(default_factory=list)
    summary: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentMetadata(BaseModel):
    name: str
    version: str
    description: str
    supported_inputs: list[str] = Field(default_factory=list)
    supported_outputs: list[str] = Field(default_factory=list)
    required_dependencies: list[str] = Field(default_factory=list)


class AgentRunSubmitResponse(BaseModel):
    run_id: str
    status: Literal["queued", "running", "success", "partial", "error"]
    agent: str
    submitted_at: datetime
    status_url: str


class AgentRunStatus(BaseModel):
    run_id: str
    agent: str
    status: Literal["queued", "running", "success", "partial", "error"]
    submitted_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    request: AgentAnalyzeRequest
    response: AgentAnalyzeResponse | None = None
    error: str = ""
