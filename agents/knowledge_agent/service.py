from __future__ import annotations

from agents._runtime import configure_import_paths

configure_import_paths()

from core.base_agent import BaseAgent
from db.init_db import init_db
from db.session import SessionLocal
from repositories.artifact_repository import insert_artifacts, search_artifacts
from services.artifact_summarization_service import summarize_all_artifacts
from services.scan_service import scan_repositories
from shared.schemas import AgentAnalyzeRequest, AgentAnalyzeResponse


class KnowledgeAgent(BaseAgent):
    name = "knowledge_agent"
    version = "1.0.0"
    description = "Discovers, summarizes, indexes, and searches Talend repository artifacts."
    supported_inputs = ["talend_repo"]
    supported_outputs = ["artifact_inventory", "summaries", "search_results"]
    required_dependencies = ["postgres", "pgvector"]

    def analyze(self, request: AgentAnalyzeRequest) -> AgentAnalyzeResponse:
        init_db()
        mode = str(request.options.get("mode", "scan_and_summarize"))
        results: list[dict] = []
        metadata: dict = {"mode": mode}

        if mode in {"scan", "scan_and_summarize"}:
            discovered = scan_repositories()
            with SessionLocal() as db:
                inserted, updated, skipped = insert_artifacts(db, discovered)
            results.append(
                {
                    "step": "scan",
                    "discovered": len(discovered),
                    "inserted": inserted,
                    "updated": updated,
                    "skipped_unchanged": skipped,
                }
            )

        if mode in {"summarize", "scan_and_summarize"}:
            processed, skipped_unchanged, failed = summarize_all_artifacts()
            results.append(
                {
                    "step": "summarize",
                    "processed": processed,
                    "skipped_unchanged": skipped_unchanged,
                    "failed": failed,
                }
            )
            if failed:
                metadata["failed"] = failed

        if mode == "search":
            query = str(request.options.get("query", ""))
            artifact_type = str(request.options.get("artifact_type", "All"))
            limit = int(request.options.get("limit", 25))
            with SessionLocal() as db:
                artifacts = search_artifacts(db, query=query, artifact_type=artifact_type)[:limit]
            results.extend(
                {
                    "id": artifact.id,
                    "artifact_id": artifact.artifact_id,
                    "name": artifact.name,
                    "artifact_type": artifact.artifact_type,
                    "repo_name": artifact.repo_name,
                    "project_name": artifact.project_name,
                    "summary": artifact.summary,
                    "file_path": artifact.file_path,
                }
                for artifact in artifacts
            )

        status = "partial" if metadata.get("failed") else "success"
        return AgentAnalyzeResponse(
            agent=self.name,
            version=self.version,
            status=status,
            results=results,
            summary=build_summary(results, mode),
            metadata=metadata,
        )


def build_summary(results: list[dict], mode: str) -> str:
    if mode == "search":
        return f"Returned {len(results)} artifact search result(s)."
    return "Knowledge analysis complete."

