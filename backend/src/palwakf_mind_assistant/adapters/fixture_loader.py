from __future__ import annotations

import json
from pathlib import Path

from palwakf_mind_assistant.domain.models import SourceRef


def load_source_fixture(path: Path) -> tuple[SourceRef, ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("SOURCE_FIXTURE_MUST_BE_A_LIST")
    return tuple(SourceRef.model_validate(item) for item in payload)
