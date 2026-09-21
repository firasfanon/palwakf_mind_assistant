from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ExternalSkillReviewDecision(StrEnum):
    recommend_project_proven = "RECOMMEND_PROJECT_PROVEN"
    require_adaptation = "REQUIRE_ADAPTATION"
    hold = "HOLD"
    reject = "REJECT"


class ExternalSkillReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_id: str = Field(min_length=3, max_length=160)
    repository: str = Field(min_length=3, max_length=240)
    commit_sha: str = Field(pattern=r"^[0-9a-fA-F]{40}$")
    path: str = Field(min_length=1, max_length=500)
    license: str = Field(min_length=1, max_length=160)
    provenance_verified: bool
    source_hash_verified: bool
    security_findings: tuple[str, ...] = ()
    overlapping_skill_ids: tuple[str, ...] = ()
    conflicting_skill_ids: tuple[str, ...] = ()
    sensitive_capability_flags: tuple[str, ...] = ()
    eval_passed: bool = False
    regression_passed: bool = False
    requested_execution_authority: bool = False


class ExternalSkillReviewResult(BaseModel):
    skill_id: str
    decision: ExternalSkillReviewDecision
    reasons: tuple[str, ...]
    reusable: bool
    canonical_write_allowed: bool = False
    auto_promotion: bool = False
    execution_authority_granted: bool = False
    promotion_recommendation: str = "WORKSPACE_GOVERNED_DECISION_REQUIRED"


def review_external_skill(request: ExternalSkillReviewRequest) -> ExternalSkillReviewResult:
    reasons: list[str] = []
    decision = ExternalSkillReviewDecision.recommend_project_proven

    if not request.provenance_verified or not request.source_hash_verified:
        decision = ExternalSkillReviewDecision.reject
        reasons.append("SOURCE_PROVENANCE_OR_HASH_NOT_VERIFIED")
    elif request.security_findings:
        decision = ExternalSkillReviewDecision.hold
        reasons.append("SECURITY_FINDINGS_OPEN")
    elif request.conflicting_skill_ids:
        decision = ExternalSkillReviewDecision.require_adaptation
        reasons.append("CONFLICT_WITH_EXISTING_SKILL")
    elif not request.eval_passed or not request.regression_passed:
        decision = ExternalSkillReviewDecision.hold
        reasons.append("EVAL_AND_REGRESSION_PASS_REQUIRED")
    elif request.sensitive_capability_flags:
        decision = ExternalSkillReviewDecision.require_adaptation
        reasons.append("SENSITIVE_CAPABILITY_REQUIRES_PALWAKF_ADAPTER")
    elif request.overlapping_skill_ids:
        decision = ExternalSkillReviewDecision.require_adaptation
        reasons.append("DUPLICATE_OR_OVERLAP_REVIEW_REQUIRED")
    else:
        reasons.append("PROJECT_PROOF_CANDIDATE_ONLY")

    if request.requested_execution_authority:
        reasons.append("EXTERNAL_SKILL_EXECUTION_AUTHORITY_NOT_GRANTED_BY_MIND")

    return ExternalSkillReviewResult(
        skill_id=request.skill_id,
        decision=decision,
        reasons=tuple(reasons),
        reusable=decision
        in {
            ExternalSkillReviewDecision.recommend_project_proven,
            ExternalSkillReviewDecision.require_adaptation,
        },
    )
