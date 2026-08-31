from __future__ import annotations

import json
from pathlib import Path

from palwakf_mind_assistant.domain.models import SkillObject


def load_skill_fixture(path: Path) -> tuple[SkillObject, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return tuple(SkillObject.model_validate(item) for item in data.get("skills", []))
