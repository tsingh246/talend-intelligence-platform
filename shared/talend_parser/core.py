from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = ROOT_DIR / "app"
for path in (ROOT_DIR, APP_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from parsers.item_parser import parse_item_file as _parse_item_file


@dataclass
class TalendArtifact:
    artifact_id: str
    artifact_type: str
    name: str
    repo_name: str
    project_name: str
    file_path: str
    relative_path: str = ""
    parsed: dict[str, Any] = field(default_factory=dict)


def parse_item_file(file_path: str | Path, artifact_type: str) -> dict[str, Any]:
    return _parse_item_file(str(file_path), artifact_type)


def classify_artifact(relative_path: str) -> str | None:
    normalized = relative_path.replace("\\", "/").lower()
    if normalized.startswith("process/"):
        return "job"
    if normalized.startswith("code/routines/"):
        return "routine"
    return None


def normalize_artifact(
    file_path: str | Path,
    artifact_type: str,
    repo_name: str = "",
    project_name: str = "",
    relative_path: str = "",
) -> TalendArtifact:
    path = Path(file_path)
    parsed = parse_item_file(path, artifact_type)
    parsed["name"] = path.stem
    return TalendArtifact(
        artifact_id=f"{repo_name}-{project_name}-{path.stem}".strip("-"),
        artifact_type=artifact_type,
        name=path.stem,
        repo_name=repo_name,
        project_name=project_name,
        file_path=str(path),
        relative_path=relative_path,
        parsed=parsed,
    )

