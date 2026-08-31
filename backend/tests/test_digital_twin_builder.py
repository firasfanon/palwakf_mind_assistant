from datetime import UTC, datetime

from palwakf_mind_assistant.adapters.drive_readonly import InMemoryDriveReadOnlyAdapter
from palwakf_mind_assistant.domain.models import (
    AuthorityType,
    ClaimState,
    DigitalTwinStatus,
    LifecycleStatus,
    ProjectOperationalState,
    SourceRef,
)
from palwakf_mind_assistant.services.authority_resolver import AuthorityResolver
from palwakf_mind_assistant.services.digital_twin_builder import ProjectDigitalTwinBuilder


def _source(project_id: str, source_ref: str = "drive:current") -> SourceRef:
    return SourceRef(
        owner_project_id=project_id,
        authority_type=AuthorityType.PROJECT_CURRENT_STATE,
        lifecycle_status=LifecycleStatus.CURRENT,
        canonical_location="drive://current",
        source_id="current",
        source_ref=source_ref,
        title="CURRENT_STATE",
    )


def _state(project_id: str, *, current_ref: str = "drive:current") -> ProjectOperationalState:
    return ProjectOperationalState(
        project_id=project_id,
        display_name=project_id,
        observed_at=datetime(2026, 8, 29, tzinfo=UTC),
        repository=f"owner/{project_id.lower()}",
        default_branch="main",
        head_sha="abc123",
        task_id="TASK-1",
        task_status="ACTIVE",
        baseline_ref="BASELINE-1",
        dependencies=("DRIVE", "GITHUB"),
        risks=(),
        production_readiness_level="L2_PRODUCT",
        production_readiness_status="NOT_PRODUCTION",
        next_safe_action="VERIFY_BEFORE_MUTATION",
        current_state_ref=current_ref,
        source_refs={"github": "fixture:github", "task": "fixture:task"},
    )


def test_rebuild_receipt_is_deterministic_for_same_authoritative_inputs() -> None:
    resolver = AuthorityResolver(InMemoryDriveReadOnlyAdapter((_source("PAL_EYES"),)))
    builder = ProjectDigitalTwinBuilder(resolver, (_state("PAL_EYES"),))
    now = datetime(2026, 8, 29, 23, 0, tzinfo=UTC)
    first = builder.build("PAL_EYES", now=now)
    second = builder.build("PAL_EYES", now=now)
    assert first.rebuild_receipt == second.rebuild_receipt
    assert first.twin_id == second.twin_id
    assert first.derived_view is True
    assert first.canonical_authority is False
    assert first.rebuildable is True


def test_missing_operational_state_is_partial_not_false_resolved() -> None:
    resolver = AuthorityResolver(InMemoryDriveReadOnlyAdapter((_source("PAL_EYES"),)))
    twin = ProjectDigitalTwinBuilder(resolver, ()).build("PAL_EYES")
    assert twin.status is DigitalTwinStatus.PARTIAL
    assert twin.trust_state is ClaimState.UNKNOWN
    assert "PROJECT_OPERATIONAL_STATE_UNAVAILABLE" in twin.unknown_reasons


def test_current_state_reference_mismatch_fails_closed_as_conflicted() -> None:
    resolver = AuthorityResolver(InMemoryDriveReadOnlyAdapter((_source("PAL_EYES"),)))
    state = _state("PAL_EYES", current_ref="drive:old")
    twin = ProjectDigitalTwinBuilder(resolver, (state,)).build("PAL_EYES")
    assert twin.status is DigitalTwinStatus.CONFLICTED
    assert twin.trust_state is ClaimState.CONFLICTED
    assert any(item.drift_code == "CURRENT_STATE_REF_MISMATCH" for item in twin.drift_indicators)


def test_unknown_task_remains_unknown_and_visible() -> None:
    resolver = AuthorityResolver(InMemoryDriveReadOnlyAdapter((_source("PAL_EYES"),)))
    state = _state("PAL_EYES").model_copy(update={"task_id": None, "task_status": "UNKNOWN"})
    twin = ProjectDigitalTwinBuilder(resolver, (state,)).build("PAL_EYES")
    assert twin.status is DigitalTwinStatus.PARTIAL
    assert twin.task_id is None
    assert "ACTIVE_TASK_UNKNOWN" in twin.unknown_reasons


def test_two_project_builds_do_not_leak_authority_or_repository_state() -> None:
    sources = (_source("PAL_EYES", "drive:eyes"), _source("PALWAKF_MIND_ASSISTANT", "drive:mind"))
    states = (
        _state("PAL_EYES", current_ref="drive:eyes"),
        _state("PALWAKF_MIND_ASSISTANT", current_ref="drive:mind").model_copy(
            update={"repository": "owner/mind"}
        ),
    )
    builder = ProjectDigitalTwinBuilder(
        AuthorityResolver(InMemoryDriveReadOnlyAdapter(sources)), states
    )
    eyes = builder.build("PAL_EYES")
    mind = builder.build("PALWAKF_MIND_ASSISTANT")
    assert eyes.project_id != mind.project_id
    assert eyes.current_state_ref == "drive:eyes"
    assert mind.current_state_ref == "drive:mind"
    assert eyes.repository != mind.repository
    assert "drive:mind" not in eyes.source_refs
    assert "drive:eyes" not in mind.source_refs


def test_superseded_current_state_never_becomes_twin_current_state() -> None:
    current = _source("PAL_EYES", "drive:current")
    old = SourceRef(
        owner_project_id="PAL_EYES",
        authority_type=AuthorityType.PROJECT_CURRENT_STATE,
        lifecycle_status=LifecycleStatus.SUPERSEDED,
        canonical_location="drive://old",
        source_id="old",
        source_ref="drive:old",
        title="OLD_STATE",
    )
    resolver = AuthorityResolver(InMemoryDriveReadOnlyAdapter((old, current)))
    twin = ProjectDigitalTwinBuilder(
        resolver,
        (_state("PAL_EYES", current_ref="drive:current"),),
    ).build("PAL_EYES")
    assert twin.current_state_ref == "drive:current"
    assert "drive:old" in twin.source_refs
    assert twin.status is DigitalTwinStatus.RESOLVED
