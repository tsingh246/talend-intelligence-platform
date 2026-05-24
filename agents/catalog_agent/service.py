from __future__ import annotations

from pathlib import Path

from agents._runtime import configure_import_paths

configure_import_paths()

from core.base_agent import BaseAgent
from db.init_db import init_db
from services.catalog_scan_service import run_data_catalog_scan
from shared.schemas import AgentAnalyzeRequest, AgentAnalyzeResponse


class CatalogAgent(BaseAgent):
    name = "catalog_agent"
    version = "1.0.0"
    description = "Extracts catalog, schema, field, SQL, and lineage-like metadata from Talend artifacts."
    supported_inputs = ["talend_repo"]
    supported_outputs = ["catalog_findings", "schema_metadata", "lineage_signals"]
    required_dependencies = ["postgres"]

    def analyze(self, request: AgentAnalyzeRequest) -> AgentAnalyzeResponse:
        init_db()
        input_path = request.options.get("input_path")
        stats = (
            run_data_catalog_scan(Path(input_path))
            if input_path
            else run_data_catalog_scan()
        )
        return AgentAnalyzeResponse(
            agent=self.name,
            version=self.version,
            status="partial" if stats.get("failed") else "success",
            results=[stats],
            summary=(
                f"Catalog scan produced {stats.get('findings', 0)} finding(s); "
                f"skipped unchanged: {stats.get('skipped_unchanged', 0)}."
            ),
            metadata={"input_path": str(input_path or "data/repos")},
        )
