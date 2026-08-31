from __future__ import annotations

import re

from palwakf_mind_assistant.domain.models import (
    LessonRegressionFinding,
    SkillObject,
    SkillResolutionRequest,
    SkillResolutionResponse,
    SkillSelection,
    SkillStatus,
)


class SkillResolver:
    """Read-only skill applicability resolver; selection never grants execution authority."""

    def __init__(self, skills: tuple[SkillObject, ...]) -> None:
        self._skills = skills

    def list_skills(self, *, include_superseded: bool = False) -> tuple[SkillObject, ...]:
        if include_superseded:
            return self._skills
        return tuple(skill for skill in self._skills if skill.status is SkillStatus.ACTIVE)

    def resolve(self, request: SkillResolutionRequest) -> SkillResolutionResponse:
        haystack = self._normalize(
            " ".join(filter(None, (request.message, request.project_id, request.task_id)))
        )
        evidence = {item.strip().upper() for item in request.evidence_tags}
        selected: list[SkillSelection] = []
        rejected: list[SkillSelection] = []
        regressions: list[LessonRegressionFinding] = []

        for skill in self._skills:
            if skill.status is not SkillStatus.ACTIVE:
                rejected.append(
                    self._selection(skill, False, 0, (f"STATUS_{skill.status.value}",), ())
                )
                continue
            matches = tuple(
                trigger
                for trigger in skill.triggers
                if self._normalize(trigger) in haystack
            )
            score = len(matches) * 10
            project_match = bool(
                request.project_id
                and request.project_id.upper() in {x.upper() for x in skill.applies_to}
            )
            if project_match:
                score += 5
            unmet = tuple(p for p in skill.preconditions if p.upper() not in evidence)
            applicable = score > 0
            reasons = tuple(f"TRIGGER:{m}" for m in matches) or ("NO_CONTEXT_TRIGGER_MATCH",)
            selection = self._selection(skill, applicable, score, reasons, unmet)
            (selected if applicable else rejected).append(selection)
            if applicable and any(
                failure.casefold() in request.message.casefold()
                for failure in skill.known_failures
            ):
                regressions.append(LessonRegressionFinding(
                    lesson_id=skill.known_failures[0],
                    status="KNOWN_LESSON_REGRESSION_RISK",
                    detail=f"Request matches a known failure pattern for {skill.skill_id}.",
                    related_skill_id=skill.skill_id,
                ))

        selected.sort(key=lambda item: (-item.score, item.skill_id, item.version))
        rejected.sort(key=lambda item: (item.skill_id, item.version))
        return SkillResolutionResponse(
            project_id=request.project_id,
            task_id=request.task_id,
            selections=tuple(selected),
            rejected=tuple(rejected),
            lesson_regressions=tuple(regressions),
        )

    @staticmethod
    def _selection(
        skill: SkillObject,
        applicable: bool,
        score: int,
        reasons: tuple[str, ...],
        unmet: tuple[str, ...],
    ) -> SkillSelection:
        return SkillSelection(
            skill_id=skill.skill_id, version=skill.version, level=skill.level,
            applicable=applicable, score=score, reasons=reasons,
            unmet_preconditions=unmet, provenance_ref=skill.provenance_ref,
            execution_authorized=False,
        )

    @staticmethod
    def _normalize(value: str) -> str:
        return re.sub(r"\s+", " ", value.strip().casefold())
