from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Lock
from uuid import uuid4

from shared.schemas import AgentAnalyzeRequest, AgentAnalyzeResponse, AgentRunStatus


class AgentRunStore:
    def __init__(self, max_workers: int = 4):
        self._runs: dict[str, AgentRunStatus] = {}
        self._lock = Lock()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit(
        self,
        agent_name: str,
        request: AgentAnalyzeRequest,
        handler,
    ) -> AgentRunStatus:
        run_id = uuid4().hex
        run = AgentRunStatus(
            run_id=run_id,
            agent=agent_name,
            status="queued",
            submitted_at=datetime.utcnow(),
            request=request,
        )
        with self._lock:
            self._runs[run_id] = run
        self._executor.submit(self._execute, run_id, handler)
        return run

    def get(self, run_id: str) -> AgentRunStatus | None:
        with self._lock:
            return self._runs.get(run_id)

    def _execute(self, run_id: str, handler) -> None:
        self._patch(run_id, status="running", started_at=datetime.utcnow())
        try:
            response = handler()
            status = response.status if response.status in {"success", "partial"} else "error"
            self._patch(
                run_id,
                status=status,
                response=response,
                completed_at=datetime.utcnow(),
            )
        except Exception as exc:
            self._patch(
                run_id,
                status="error",
                response=AgentAnalyzeResponse(
                    agent="platform_orchestrator",
                    version="1.0.0",
                    status="error",
                    summary=f"Run failed: {exc}",
                ),
                error=str(exc),
                completed_at=datetime.utcnow(),
            )

    def _patch(self, run_id: str, **changes) -> None:
        with self._lock:
            run = self._runs.get(run_id)
            if not run:
                return
            for key, value in changes.items():
                setattr(run, key, value)
