from types import SimpleNamespace

import pytest

from palwakf_mind_assistant.intersystem_review import (
    LearningCandidateBundleV1,
    LearningCandidateItemV1,
    review_learning_bundle,
)


SHA = "1" * 40


class StubProduct:
    def __init__(self, conflicts=()):
        self._conflicts = conflicts

    def compile_context(self, request):
        return SimpleNamespace(authority_status="RESOLVED")

    def conflicts(self, project_id):
        return self._conflicts


def _bundle(*, candidate_project="PALWAKF_LOCAL_AGENTS", evidence=("evidence://run",)):
    return LearningCandidateBundleV1(
        project_id="PALWAKF_LOCAL_AGENTS",
        task_id="FOUR_SYSTEM_READ_ONLY_INTEGRATION_PILOT_V1",
        run_id="run-001",
        source_sha=SHA,
        candidates=(
            LearningCandidateItemV1(
                candidate_id="candidate-001",
                project_id=candidate_project,
                task_id="FOUR_SYSTEM_READ_ONLY_INTEGRATION_PILOT_V1",
                candidate_type="PROJECT_LESSON",
                summary="Remote WIP head differs from historical base.",
                evidence_refs=evidence,
                source_sha=SHA,
            ),
        ),
    )


def test_review_is_candidate_only_and_never_canonical_write():
    result = review_learning_bundle(StubProduct(), _bundle())
    assert result.canonical_write_allowed is False
    assert result.mutation_mode == "READ_ONLY"
    assert result.promotion_recommendation == "HUMAN_WORKSPACE_REVIEW_REQUIRED"
    assert result.candidate_reviews[0].status == "REVIEW_REQUIRED"


def test_missing_evidence_requires_more_evidence():
    result = review_learning_bundle(StubProduct(), _bundle(evidence=()))
    assert result.candidate_reviews[0].status == "NEEDS_MORE_EVIDENCE"


def test_cross_project_candidate_fails_closed():
    with pytest.raises(ValueError, match="LEARNING_CANDIDATE_SCOPE_MISMATCH"):
        review_learning_bundle(StubProduct(), _bundle(candidate_project="OTHER_PROJECT"))
