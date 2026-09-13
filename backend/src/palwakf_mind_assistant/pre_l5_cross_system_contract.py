from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from palwakf_mind_assistant.pre_l5_review_enforcement import (
    KnownFailureFingerprintReviewV1,
    MindPreL5ReviewContextV1,
)


class PreL5FailureFingerprintBindingV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fingerprint_id: str
    lesson_id: str
    preventive_gate_id: str
    relevant: bool = True
    applies_to_projects: tuple[str, ...] = ("*",)


class AgenticMindReviewContextWireV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: Literal[
        "PALWAKF_PRE_L5_MIND_REVIEW_CONTEXT_V1"
    ]

    project_id: str
    task_id: str
    run_id: str

    source_sha: str = Field(
        pattern=r"^[0-9a-fA-F]{40}$"
    )

    active_instruction_set_sha256: str = Field(
        pattern=r"^[0-9a-f]{64}$"
    )

    active_lesson_ids: tuple[str, ...]
    reused_lesson_ids: tuple[str, ...]

    known_failure_fingerprints: tuple[
        PreL5FailureFingerprintBindingV1, ...
    ] = ()

    review_mode: Literal[
        "CANDIDATE_ONLY_NO_AUTO_PROMOTION"
    ]

    canonical_write_allowed: Literal[False]


def bind_agentic_mind_review_context(
    wire: AgenticMindReviewContextWireV1,
) -> MindPreL5ReviewContextV1:

    return MindPreL5ReviewContextV1(
        project_id=wire.project_id,
        task_id=wire.task_id,
        run_id=wire.run_id,
        source_sha=wire.source_sha,
        active_instruction_set_sha256=(
            wire.active_instruction_set_sha256
        ),
        active_lesson_ids=wire.active_lesson_ids,
        reused_lesson_ids=wire.reused_lesson_ids,
        known_failure_fingerprints=tuple(
            KnownFailureFingerprintReviewV1(
                fingerprint_id=item.fingerprint_id,
                lesson_id=item.lesson_id,
                preventive_gate_id=(
                    item.preventive_gate_id
                ),
                relevant=item.relevant,
                applies_to_projects=(
                    item.applies_to_projects
                ),
            )
            for item in (
                wire.known_failure_fingerprints
            )
        ),
        review_mode=wire.review_mode,
        canonical_write_allowed=False,
    )
