from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class AgentFixtureAdapter:
    """Read-only fixture adapter for the final integrated Mega Batch."""

    def __init__(self, path: Path) -> None:
        self._path = path
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("source_mode") != "FIXTURE_DERIVED":
            raise ValueError("FIXTURE_SOURCE_MODE_INVALID")
        self._payload: dict[str, Any] = payload

    @property
    def source_mode(self) -> str:
        return "FIXTURE_DERIVED"

    def payload(self) -> dict[str, Any]:
        return json.loads(json.dumps(self._payload))
