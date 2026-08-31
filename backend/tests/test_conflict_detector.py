from palwakf_mind_assistant.domain.models import (
    AuthorityType,
    ConflictSeverity,
    LifecycleStatus,
    SourceRef,
)
from palwakf_mind_assistant.services.conflict_detector import ConflictDetector


def _source(source_id: str, lifecycle: LifecycleStatus) -> SourceRef:
    return SourceRef(
        owner_project_id="PAL_EYES",
        authority_type=AuthorityType.PROJECT_CURRENT_STATE,
        lifecycle_status=lifecycle,
        canonical_location=f"drive://{source_id}",
        source_id=source_id,
        source_ref=f"drive:{source_id}",
        title=source_id,
    )


def test_multiple_current_is_blocking_structural_conflict() -> None:
    conflicts = ConflictDetector().detect(
        "PAL_EYES",
        (_source("a", LifecycleStatus.CURRENT), _source("b", LifecycleStatus.CURRENT)),
    )
    assert len(conflicts) == 1
    assert conflicts[0].conflict_type == "MULTIPLE_CURRENT_SOURCES"
    assert conflicts[0].severity is ConflictSeverity.BLOCKING
    assert conflicts[0].requires_human_review is True


def test_unknown_lifecycle_is_review_candidate_not_semantic_claim() -> None:
    conflicts = ConflictDetector().detect(
        "PAL_EYES",
        (_source("unknown", LifecycleStatus.UNKNOWN),),
    )
    assert conflicts[0].conflict_type == "UNKNOWN_LIFECYCLE"
    assert conflicts[0].severity is ConflictSeverity.REVIEW
    assert "UNKNOWN" in conflicts[0].detail
