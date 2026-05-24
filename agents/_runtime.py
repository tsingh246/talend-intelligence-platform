from __future__ import annotations

import sys
from pathlib import Path


def configure_import_paths() -> None:
    root_dir = Path(__file__).resolve().parents[1]
    app_dir = root_dir / "app"
    for path in (root_dir, app_dir):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))

