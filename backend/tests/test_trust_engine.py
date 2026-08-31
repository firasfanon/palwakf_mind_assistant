from palwakf_mind_assistant.domain.models import (
    AuthorityType,
    ClaimState,
    FreshnessState,
    LifecycleStatus,
    SourceRef,
)
from palwakf_mind_assistant.services.trust_engine import TrustEngine


def _source(lifecycle: LifecycleStatus) -> SourceRef:
    return SourceRef(
        owner_project_id="PAL_EYES",
        authority_type=AuthorityType.PROJECT_GOVERNANCE,
        lifecycle_status=lifecycle,
        canonical_location="drive://x",
        source_id="x",
        source_ref="drive:x",
        title="X",
    )


def test_unknown_lifecycle_stays_unknown() -> None:
    provenance = TrustEngine().provenance_for(_source(LifecycleStatus.UNKNOWN))
    assert provenance.claim_state is ClaimState.UNKNOWN
    assert provenance.freshness is FreshnessState.UNKNOWN


def test_historical_source_is_stale() -> None:
    provenance = TrustEngine().provenance_for(_source(LifecycleStatus.HISTORICAL))
    assert provenance.claim_state is ClaimState.STALE
    assert provenance.freshness is FreshnessState.STALE


def test_conflict_overrides_current_verification() -> None:
    provenance = TrustEngine().provenance_for(_source(LifecycleStatus.CURRENT), conflicted=True)
    assert provenance.claim_state is ClaimState.CONFLICTED
    assert provenance.confidence == "REVIEW_REQUIRED"
