from __future__ import annotations

from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from palwakf_mind_assistant.domain.models import ContextRequest


class LearningCandidateItemV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    project_id: str
    task_id: str
    candidate_type: str
    summary: str
    evidence_refs: tuple[str, ...] = ()
    source_sha: str = Field(pattern=r"^[0-9a-fA-F]{40}$")


class LearningCandidateBundleV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: Literal["PALWAKF_INTERSYSTEM_CONTRACT_V1"] = (
        "PALWAKF_INTERSYSTEM_CONTRACT_V1"
    )
    project_id: str
    task_id: str
    run_id: str
    source_sha: str = Field(pattern=r"^[0-9a-fA-F]{40}$")
    auto_promotion: Literal[False] = False
    candidates: tuple[LearningCandidateItemV1, ...]


class CandidateReviewDecisionV1(BaseModel):
    candidate_id: str
    status: Literal["REVIEW_REQUIRED", "NEEDS_MORE_EVIDENCE", "REJECTED"]
    recommended_scope: Literal[
        "PROJECT_ONLY",
        "DOMAIN_SHARED",
        "PALWAKF_GLOBAL",
        "SECURITY_GLOBAL",
        "ENGINEERING_GLOBAL",
        "RESEARCH_GLOBAL",
    ] = "PROJECT_ONLY"
    reasons: tuple[str, ...] = ()


class MindReviewResultV1(BaseModel):
    contract_version: Literal["PALWAKF_INTERSYSTEM_CONTRACT_V1"] = (
        "PALWAKF_INTERSYSTEM_CONTRACT_V1"
    )
    review_id: str
    project_id: str
    task_id: str
    run_id: str
    candidate_reviews: tuple[CandidateReviewDecisionV1, ...]
    conflict_count: int
    conflict_refs: tuple[str, ...]
    context_authority_status: str
    promotion_recommendation: Literal["HUMAN_WORKSPACE_REVIEW_REQUIRED"] = (
        "HUMAN_WORKSPACE_REVIEW_REQUIRED"
    )
    canonical_write_allowed: Literal[False] = False
    mutation_mode: Literal["READ_ONLY"] = "READ_ONLY"


def review_learning_bundle(product: Any, bundle: LearningCandidateBundleV1) -> MindReviewResultV1:
    for candidate in bundle.candidates:
        if candidate.project_id != bundle.project_id or candidate.task_id != bundle.task_id:
            raise ValueError("LEARNING_CANDIDATE_SCOPE_MISMATCH")
        if candidate.source_sha.lower() != bundle.source_sha.lower():
            raise ValueError("LEARNING_CANDIDATE_SOURCE_SHA_MISMATCH")

    context = product.compile_context(
        ContextRequest(
            message="Review governed Agentic learning candidates without canonical promotion.",
            project_id=bundle.project_id,
            task_id=bundle.task_id,
        )
    )
    conflicts = tuple(product.conflicts(bundle.project_id))
    conflict_refs = tuple(
        sorted(
            {
                ref
                for conflict in conflicts
                for ref in getattr(conflict, "source_refs", ())
            }
        )
    )
    blocking = any(
        str(getattr(conflict, "severity", "")).upper().endswith("BLOCKING")
        for conflict in conflicts
    )

    decisions = tuple(
        CandidateReviewDecisionV1(
            candidate_id=candidate.candidate_id,
            status=(
                "NEEDS_MORE_EVIDENCE"
                if blocking or not candidate.evidence_refs
                else "REVIEW_REQUIRED"
            ),
            reasons=(
                ("BLOCKING_PROJECT_CONFLICT_PRESENT",)
                if blocking
                else (
                    ("EVIDENCE_REQUIRED",)
                    if not candidate.evidence_refs
                    else ("EXTERNAL_HUMAN_WORKSPACE_REVIEW_REQUIRED",)
                )
            ),
        )
        for candidate in bundle.candidates
    )

    authority_status = str(getattr(context, "authority_status", "UNKNOWN"))
    return MindReviewResultV1(
        review_id=f"mind-review-{uuid4()}",
        project_id=bundle.project_id,
        task_id=bundle.task_id,
        run_id=bundle.run_id,
        candidate_reviews=decisions,
        conflict_count=len(conflicts),
        conflict_refs=conflict_refs,
        context_authority_status=authority_status,
    )
