from palwakf_mind_assistant.external_skill_review import (
    ExternalSkillReviewDecision,
    ExternalSkillReviewRequest,
    review_external_skill,
)


def request(**updates):
    payload = dict(
        skill_id="supabase.readonly",
        repository="supabase/agent-skills",
        commit_sha="a" * 40,
        path="skills/supabase/SKILL.md",
        license="MIT",
        provenance_verified=True,
        source_hash_verified=True,
        security_findings=(),
        overlapping_skill_ids=(),
        conflicting_skill_ids=(),
        eval_passed=True,
        regression_passed=True,
        requested_execution_authority=False,
    )
    payload.update(updates)
    return ExternalSkillReviewRequest(**payload)


def test_mind_can_recommend_project_proof_but_never_promotes_or_authorizes() -> None:
    result = review_external_skill(request(requested_execution_authority=True))
    assert result.decision == ExternalSkillReviewDecision.recommend_project_proven
    assert result.auto_promotion is False
    assert result.canonical_write_allowed is False
    assert result.execution_authority_granted is False
    assert "EXTERNAL_SKILL_EXECUTION_AUTHORITY_NOT_GRANTED_BY_MIND" in result.reasons


def test_unverified_or_unsafe_skill_fails_review() -> None:
    unverified = review_external_skill(request(provenance_verified=False))
    assert unverified.decision == ExternalSkillReviewDecision.reject

    unsafe = review_external_skill(request(security_findings=("PROMPT_INJECTION_PATTERN",)))
    assert unsafe.decision == ExternalSkillReviewDecision.hold


def test_overlap_or_conflict_requires_adaptation_not_canonical_promotion() -> None:
    overlap = review_external_skill(request(overlapping_skill_ids=("PALWAKF_EXISTING_SKILL",)))
    assert overlap.decision == ExternalSkillReviewDecision.require_adaptation
    conflict = review_external_skill(request(conflicting_skill_ids=("PALWAKF_CONFLICTING_SKILL",)))
    assert conflict.decision == ExternalSkillReviewDecision.require_adaptation
    assert conflict.auto_promotion is False


def test_sensitive_capability_requires_palwakf_adapter() -> None:
    result = review_external_skill(
        request(sensitive_capability_flags=("NETWORK_ACCESS", "SECRET_ACCESS"))
    )
    assert result.decision == ExternalSkillReviewDecision.require_adaptation
    assert "SENSITIVE_CAPABILITY_REQUIRES_PALWAKF_ADAPTER" in result.reasons
    assert result.auto_promotion is False
    assert result.execution_authority_granted is False
