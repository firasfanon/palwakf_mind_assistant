from pathlib import Path

from palwakf_mind_assistant.four_system_l4 import (
    FourSystemL4MindRequest,
    FourSystemL4MindService,
    MindL4Journal,
)
from palwakf_mind_assistant.intersystem_review import (
    LearningCandidateBundleV1,
    MindReviewResultV1,
)

HEAD = "2" * 40


def bundle() -> LearningCandidateBundleV1:
    return LearningCandidateBundleV1(
        project_id="PALWAKF_LOCAL_AGENTS",
        task_id="task-1",
        run_id="agentic-run-1",
        source_sha=HEAD,
        candidates=(),
    )


def review_result() -> MindReviewResultV1:
    return MindReviewResultV1(
        review_id="mind-review-1",
        project_id="PALWAKF_LOCAL_AGENTS",
        task_id="task-1",
        run_id="agentic-run-1",
        candidate_reviews=(),
        conflict_count=0,
        conflict_refs=(),
        context_authority_status="CURRENT",
    )


def test_l4_mind_review_is_durable_and_idempotent(tmp_path: Path):
    calls = 0

    def reviewer(_):
        nonlocal calls
        calls += 1
        return review_result()

    service = FourSystemL4MindService(
        journal=MindL4Journal(tmp_path),
        reviewer=reviewer,
    )
    request = FourSystemL4MindRequest(
        workspace_run_id="l4-run-1",
        correlation_id="corr-1",
        learning_bundle=bundle(),
        evaluation={"run_id": "agentic-run-1", "passed": True},
        execution_summary={"run_id": "agentic-run-1", "final_result": "PASS"},
    )

    first = service.review(request)
    second = service.review(request)

    assert first == second
    assert calls == 1
    assert first.review_result.canonical_write_allowed is False
    assert first.review_result.mutation_mode == "READ_ONLY"

    resumed = FourSystemL4MindService(
        journal=MindL4Journal(tmp_path),
        reviewer=reviewer,
    ).resume("l4-run-1")
    assert resumed.status == "COMPLETED"


def test_l4_mind_rejects_run_lineage_mismatch(tmp_path: Path):
    service = FourSystemL4MindService(
        journal=MindL4Journal(tmp_path),
        reviewer=lambda _: review_result(),
    )

    try:
        service.review(
            FourSystemL4MindRequest(
                workspace_run_id="l4-run-2",
                correlation_id="corr-2",
                learning_bundle=bundle(),
                evaluation={"run_id": "other-run", "passed": True},
                execution_summary={"run_id": "agentic-run-1"},
            )
        )
    except ValueError as error:
        assert "EVALUATION_RUN_MISMATCH" in str(error)
    else:
        raise AssertionError("lineage mismatch must fail closed")
