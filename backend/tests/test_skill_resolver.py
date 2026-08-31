from datetime import UTC, datetime

from palwakf_mind_assistant.domain.models import (
    SkillLevel,
    SkillObject,
    SkillResolutionRequest,
    SkillStatus,
)
from palwakf_mind_assistant.services.skill_resolver import SkillResolver


def _skill(
    skill_id: str,
    triggers: tuple[str, ...],
    *,
    status=SkillStatus.ACTIVE,
    version="1.0.0",
) -> SkillObject:
    return SkillObject(
        skill_id=skill_id, version=version, status=status, owner_scope="GLOBAL",
        level=SkillLevel.GLOBAL, applies_to=(), triggers=triggers, preconditions=(),
        required_inputs=(), authorized_operations=("ADVISE",), forbidden_operations=("MUTATE",),
        execution_steps=(), fail_closed_conditions=(), expected_outputs=(),
        evidence_requirements=(), regression_tests=(), known_failures=(), supersedes=(),
        last_validated_at=datetime(2026, 8, 29, tzinfo=UTC), provenance_ref=f"drive:{skill_id}"
    )


def test_selects_artifact_skill_for_packaging_context() -> None:
    resolver = SkillResolver(
        (
            _skill("PACKAGE", ("artifact", "zip", "powershell")),
            _skill("DB", ("database", "sql")),
        )
    )
    result = resolver.resolve(
        SkillResolutionRequest(message="Build a ZIP artifact with a PowerShell runner")
    )
    assert [s.skill_id for s in result.selections] == ["PACKAGE"]
    assert result.selections[0].execution_authorized is False
    assert any(item.skill_id == "DB" for item in result.rejected)


def test_selects_flutter_skill_and_rejects_database_skill_for_browser_uat() -> None:
    resolver = SkillResolver(
        (
            _skill("FLUTTER", ("flutter", "browser", "uat")),
            _skill("DB", ("database", "sql")),
        )
    )
    result = resolver.resolve(
        SkillResolutionRequest(message="Run Flutter browser UAT at responsive viewport")
    )
    assert result.selections[0].skill_id == "FLUTTER"
    assert all(item.skill_id != "DB" for item in result.selections)


def test_selects_resume_skill_for_project_reconciliation() -> None:
    resolver = SkillResolver((_skill("RESUME", ("resume", "reconcile", "استئناف")),))
    result = resolver.resolve(
        SkillResolutionRequest(message="استئناف المشروع ثم reconcile GitHub و Drive")
    )
    assert result.selections[0].skill_id == "RESUME"


def test_superseded_skill_never_selected_even_when_trigger_matches() -> None:
    resolver = SkillResolver((
        _skill("CURRENT", ("flutter",), version="1.0.0"),
        _skill("OLD", ("flutter",), status=SkillStatus.SUPERSEDED, version="0.9.0"),
    ))
    result = resolver.resolve(SkillResolutionRequest(message="flutter"))
    assert [s.skill_id for s in result.selections] == ["CURRENT"]
    old = next(item for item in result.rejected if item.skill_id == "OLD")
    assert "STATUS_SUPERSEDED" in old.reasons


def test_known_failure_pattern_is_detected() -> None:
    base = _skill("FLUTTER", ("flutter",))
    skill = base.model_copy(update={"known_failures": ("RENDERFLEX_OVERFLOW",)})
    result = SkillResolver((skill,)).resolve(
        SkillResolutionRequest(message="flutter RENDERFLEX_OVERFLOW regression")
    )
    assert result.lesson_regressions[0].status == "KNOWN_LESSON_REGRESSION_RISK"
