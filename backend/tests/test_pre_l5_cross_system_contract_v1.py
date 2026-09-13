import pytest
from pydantic import ValidationError

from palwakf_mind_assistant.pre_l5_cross_system_contract import (
    AgenticMindReviewContextWireV1,
    bind_agentic_mind_review_context,
)


PROJECT = "PALWAKF_LOCAL_AGENTS"


def payload():
    return {
        "contract_version":
            "PALWAKF_PRE_L5_MIND_REVIEW_CONTEXT_V1",
        "project_id": PROJECT,
        "task_id": "TASK-CROSS-SYSTEM",
        "run_id": "run-proof",
        "source_sha": "2" * 40,
        "active_instruction_set_sha256":
            "a" * 64,
        "active_lesson_ids": ["LESSON-1"],
        "reused_lesson_ids": ["LESSON-1"],
        "known_failure_fingerprints": [
            {
                "fingerprint_id": "FP-1",
                "lesson_id": "LESSON-1",
                "preventive_gate_id": "GATE-1",
                "relevant": True,
                "applies_to_projects": [PROJECT],
            }
        ],
        "review_mode":
            "CANDIDATE_ONLY_NO_AUTO_PROMOTION",
        "canonical_write_allowed": False,
    }


def test_agentic_context_binds_to_mind_enforcement():
    wire = (
        AgenticMindReviewContextWireV1
        .model_validate(payload())
    )

    context = bind_agentic_mind_review_context(
        wire
    )

    assert context.project_id == PROJECT
    assert context.task_id == "TASK-CROSS-SYSTEM"
    assert context.run_id == "run-proof"
    assert context.reused_lesson_ids == (
        "LESSON-1",
    )

    assert context.canonical_write_allowed is False


def test_agentic_auto_promotion_flag_cannot_cross_boundary():
    value = payload()
    value["canonical_write_allowed"] = True

    with pytest.raises(ValidationError):
        (
            AgenticMindReviewContextWireV1
            .model_validate(value)
        )


def test_foreign_failure_fingerprint_fails_in_mind_binding():
    value = payload()

    value[
        "known_failure_fingerprints"
    ][0]["applies_to_projects"] = [
        "OTHER_PROJECT"
    ]

    wire = (
        AgenticMindReviewContextWireV1
        .model_validate(value)
    )

    with pytest.raises(
        ValidationError,
        match="FAILURE_FINGERPRINT_PROJECT_SCOPE_MISMATCH",
    ):
        bind_agentic_mind_review_context(wire)


def test_unreused_known_lesson_fails_in_mind_binding():
    value = payload()
    value["reused_lesson_ids"] = []

    wire = (
        AgenticMindReviewContextWireV1
        .model_validate(value)
    )

    with pytest.raises(
        ValidationError,
        match="KNOWN_RELEVANT_LESSON_NOT_REUSED",
    ):
        bind_agentic_mind_review_context(wire)
