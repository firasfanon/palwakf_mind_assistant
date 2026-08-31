from __future__ import annotations

import json
from pathlib import Path

from palwakf_mind_assistant.domain.models import ProjectOperationalState


def load_project_state_fixture(path: Path) -> tuple[ProjectOperationalState, ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("PROJECT_STATE_FIXTURE_MUST_BE_A_LIST")
    return tuple(ProjectOperationalState.model_validate(item) for item in payload)
