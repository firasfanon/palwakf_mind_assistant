from __future__ import annotations

from datetime import UTC, datetime

from palwakf_mind_assistant.domain.models import (
    ClaimProvenance,
    ClaimState,
    FreshnessState,
    LifecycleStatus,
    SourceRef,
)


class TrustEngine:
    """Derive transparent claim trust metadata from authoritative source metadata.

    This engine never upgrades UNKNOWN to VERIFIED and never treats semantic
    similarity as authority. It is deliberately conservative until content-level
    evidence and richer temporal metadata are available.
    """

    def provenance_for(self, source: SourceRef, *, conflicted: bool = False) -> ClaimProvenance:
        observed_at = self._observed_at(source)
        freshness = self._freshness(source, observed_at)
        state, confidence, reason = self._claim_state(source, freshness, conflicted)
        version = str(source.metadata.get("version") or source.title)
        supersession = (
            "SUPERSEDED"
            if source.lifecycle_status is LifecycleStatus.SUPERSEDED
            else "CURRENT_OR_ACTIVE"
            if source.lifecycle_status in {LifecycleStatus.CURRENT, LifecycleStatus.ACTIVE}
            else source.lifecycle_status.value
        )
        return ClaimProvenance(
            source_ref=source.source_ref,
            authority=source.authority_type,
            lifecycle_status=source.lifecycle_status,
            version=version,
            observed_at=observed_at,
            confidence=confidence,
            freshness=freshness,
            supersession=supersession,
            scope=source.owner_project_id,
            claim_state=state,
            reason=reason,
        )

    @staticmethod
    def _observed_at(source: SourceRef) -> datetime:
        raw = source.metadata.get("observed_at")
        if isinstance(raw, str):
            try:
                parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
            except ValueError:
                pass
        return datetime.now(UTC)

    @staticmethod
    def _freshness(source: SourceRef, observed_at: datetime) -> FreshnessState:
        explicit = source.metadata.get("freshness")
        if isinstance(explicit, str):
            try:
                return FreshnessState(explicit.upper())
            except ValueError:
                return FreshnessState.UNKNOWN
        if source.lifecycle_status in {LifecycleStatus.SUPERSEDED, LifecycleStatus.HISTORICAL}:
            return FreshnessState.STALE
        if source.lifecycle_status in {LifecycleStatus.CURRENT, LifecycleStatus.ACTIVE}:
            # Lifecycle is authoritative for currentness in B0.4. Age is not guessed.
            return FreshnessState.CURRENT
        _ = observed_at
        return FreshnessState.UNKNOWN

    @staticmethod
    def _claim_state(
        source: SourceRef,
        freshness: FreshnessState,
        conflicted: bool,
    ) -> tuple[ClaimState, str, str]:
        if conflicted:
            return ClaimState.CONFLICTED, "REVIEW_REQUIRED", "STRUCTURAL_AUTHORITY_CONFLICT"
        if source.lifecycle_status is LifecycleStatus.UNKNOWN:
            return ClaimState.UNKNOWN, "UNKNOWN", "UNKNOWN_SOURCE_LIFECYCLE"
        if freshness is FreshnessState.STALE:
            return ClaimState.STALE, "STALE", "SOURCE_SUPERSEDED_OR_HISTORICAL"
        if source.lifecycle_status in {LifecycleStatus.CURRENT, LifecycleStatus.ACTIVE}:
            return ClaimState.VERIFIED, "VERIFIED_METADATA", "AUTHORITY_AND_LIFECYCLE_VERIFIED"
        return ClaimState.INFERRED, "LIMITED", "NON_CURRENT_AUTHORITY_METADATA"
