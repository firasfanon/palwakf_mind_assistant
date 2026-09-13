from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from palwakf_mind_assistant.domain.models import (
    ClaimState,
    ConflictSeverity,
    LifecycleStatus,
    ResolutionStatus,
)
from palwakf_mind_assistant.intersystem_review import (
    LearningCandidateBundleV1,
    LearningCandidateItemV1,
    review_learning_bundle_pre_l5,
)
from palwakf_mind_assistant.pre_l5_review_enforcement import (
    KnownFailureFingerprintReviewV1,
    MindPreL5ReviewContextV1,
)


PROJECT = "PALWAKF_LOCAL_AGENTS"
TASK = "TASK-PRE-L5"
RUN = "RUN-PRE-L5"
SHA = "1" * 40
DIGEST = "a" * 64


def candidate(
    candidate_id: str,
    *,
    summary="Reusable lesson.",
    evidence_refs=("drive://evidence/1",),
    project_id=PROJECT,
    task_id=TASK,
    source_sha=SHA,
):
    return LearningCandidateItemV1(
        candidate_id=candidate_id,
        project_id=project_id,
        task_id=task_id,
        candidate_type="PROJECT_LESSON",
        summary=summary,
        evidence_refs=evidence_refs,
        source_sha=source_sha,
    )


def bundle(*items):
    return LearningCandidateBundleV1(
        project_id=PROJECT,
        task_id=TASK,
        run_id=RUN,
        source_sha=SHA,
        candidates=items,
    )


def review_context(
    *,
    source_sha=SHA,
    reused=("LESSON-1",),
    fingerprint_project=PROJECT,
):
    return MindPreL5ReviewContextV1(
        project_id=PROJECT,
        task_id=TASK,
        run_id=RUN,
        source_sha=source_sha,
        active_instruction_set_sha256=DIGEST,
        active_lesson_ids=("LESSON-1",),
        reused_lesson_ids=reused,
        known_failure_fingerprints=(
            KnownFailureFingerprintReviewV1(
                fingerprint_id="FP-1",
                lesson_id="LESSON-1",
                preventive_gate_id="GATE-1",
                applies_to_projects=(
                    fingerprint_project,
                ),
            ),
        ),
    )


def trusted_source(
    source_ref="drive://current",
    lifecycle=LifecycleStatus.CURRENT,
):
    return SimpleNamespace(
        source=SimpleNamespace(
            source_ref=source_ref,
            lifecycle_status=lifecycle,
        )
    )


class Product:
    def __init__(
        self,
        *,
        context=None,
        conflicts=(),
    ):
        self._context = context or SimpleNamespace(
            project_id=PROJECT,
            task_id=TASK,
            authority_status=ResolutionStatus.RESOLVED,
            trust_state=ClaimState.VERIFIED,
            authoritative_sources=(
                trusted_source(),
            ),
            superseded_sources=(),
        )
        self._conflicts = tuple(conflicts)

    def compile_context(self, _request):
        return self._context

    def conflicts(self, _project_id):
        return self._conflicts


def test_pre_l5_review_happy_path_is_recommendation_only():
    result = review_learning_bundle_pre_l5(
        Product(),
        bundle(candidate("C-1")),
        review_context(),
    )

    assert (
        result.review.canonical_write_allowed
        is False
    )

    assert (
        result.review.promotion_recommendation
        == "HUMAN_WORKSPACE_REVIEW_REQUIRED"
    )

    assert result.assessment.lesson_reuse_review == "PASS"
    assert result.assessment.provenance_review == "PASS"
    assert result.assessment.conflict_review == "PASS"
    assert result.assessment.duplicate_review == "PASS"
    assert result.assessment.staleness_review == "PASS"

    assert (
        result.review.candidate_reviews[0].status
        == "REVIEW_REQUIRED"
    )


def test_known_relevant_failure_requires_lesson_reuse():
    with pytest.raises(
        ValidationError,
        match="KNOWN_RELEVANT_LESSON_NOT_REUSED",
    ):
        review_context(reused=())


def test_foreign_failure_fingerprint_is_rejected():
    with pytest.raises(
        ValidationError,
        match="FAILURE_FINGERPRINT_PROJECT_SCOPE_MISMATCH",
    ):
        review_context(
            fingerprint_project="OTHER_PROJECT"
        )


def test_stale_learning_source_fails_closed():
    with pytest.raises(
        ValueError,
        match="STALE_LEARNING_SOURCE_SHA",
    ):
        review_learning_bundle_pre_l5(
            Product(),
            bundle(candidate("C-1")),
            review_context(
                source_sha="2" * 40
            ),
        )


def test_duplicate_candidates_are_rejected():
    result = review_learning_bundle_pre_l5(
        Product(),
        bundle(
            candidate("C-1"),
            candidate("C-2"),
        ),
        review_context(),
    )

    statuses = {
        item.candidate_id: item.status
        for item in result.review.candidate_reviews
    }

    assert statuses == {
        "C-1": "REJECTED",
        "C-2": "REJECTED",
    }

    assert result.assessment.duplicate_review == (
        "REVIEW_REQUIRED"
    )


def test_blocking_conflict_forces_more_evidence():
    conflict = SimpleNamespace(
        severity=ConflictSeverity.BLOCKING,
        source_refs=("drive://current",),
    )

    result = review_learning_bundle_pre_l5(
        Product(conflicts=(conflict,)),
        bundle(candidate("C-1")),
        review_context(),
    )

    assert (
        result.review.candidate_reviews[0].status
        == "NEEDS_MORE_EVIDENCE"
    )

    assert result.assessment.conflict_review == (
        "REVIEW_REQUIRED"
    )


def test_non_current_authoritative_context_cannot_promote():
    stale_context = SimpleNamespace(
        project_id=PROJECT,
        task_id=TASK,
        authority_status=ResolutionStatus.RESOLVED,
        trust_state=ClaimState.STALE,
        authoritative_sources=(
            trusted_source(
                source_ref="drive://historical",
                lifecycle=LifecycleStatus.HISTORICAL,
            ),
        ),
        superseded_sources=(),
    )

    result = review_learning_bundle_pre_l5(
        Product(context=stale_context),
        bundle(candidate("C-1")),
        review_context(),
    )

    assert (
        result.review.candidate_reviews[0].status
        == "NEEDS_MORE_EVIDENCE"
    )

    assert result.assessment.provenance_review == (
        "REVIEW_REQUIRED"
    )

    assert result.assessment.staleness_review == (
        "REVIEW_REQUIRED"
    )


def test_superseded_source_reentry_forces_more_evidence():
    shared = "drive://old"

    context = SimpleNamespace(
        project_id=PROJECT,
        task_id=TASK,
        authority_status=ResolutionStatus.RESOLVED,
        trust_state=ClaimState.VERIFIED,
        authoritative_sources=(
            trusted_source(
                source_ref=shared,
                lifecycle=LifecycleStatus.CURRENT,
            ),
        ),
        superseded_sources=(
            trusted_source(
                source_ref=shared,
                lifecycle=LifecycleStatus.SUPERSEDED,
            ),
        ),
    )

    result = review_learning_bundle_pre_l5(
        Product(context=context),
        bundle(
            candidate(
                "C-1",
                evidence_refs=(shared,),
            )
        ),
        review_context(),
    )

    assert (
        result.review.candidate_reviews[0].status
        == "NEEDS_MORE_EVIDENCE"
    )

    assert shared in (
        result
        .assessment
        .non_current_context_refs
    )


def test_missing_evidence_never_reaches_review_required():
    result = review_learning_bundle_pre_l5(
        Product(),
        bundle(
            candidate(
                "C-1",
                evidence_refs=(),
            )
        ),
        review_context(),
    )

    assert (
        result.review.candidate_reviews[0].status
        == "NEEDS_MORE_EVIDENCE"
    )


def test_project_binding_leakage_fails_closed():
    bad_context = review_context().model_copy(
        update={
            "project_id": "OTHER_PROJECT",
        }
    )

    with pytest.raises(
        ValueError,
        match="MIND_REVIEW_PROJECT_BINDING_MISMATCH",
    ):
        review_learning_bundle_pre_l5(
            Product(),
            bundle(candidate("C-1")),
            bad_context,
        )