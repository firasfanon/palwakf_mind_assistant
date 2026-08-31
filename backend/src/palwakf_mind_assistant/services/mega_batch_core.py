from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from palwakf_mind_assistant.domain.models import (
    CapabilityEnvelope,
    FreshnessState,
    RepositoryFileRef,
    RepositoryRef,
    RepositorySnapshot,
    ToolCapability,
)

NOW = datetime(2026, 8, 30, tzinfo=UTC)


def stable_id(prefix: str, *parts: str) -> str:
    raw = "|".join(parts).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(raw).hexdigest()[:12]}"


def default_capabilities() -> tuple[ToolCapability, ...]:
    return (
        ToolCapability(
            capability_id="repo.read",
            name="Repository read",
            risk_class="LOW",
            mutation_class="READ_ONLY",
            requires_explicit_approval=False,
        ),
        ToolCapability(
            capability_id="repo.patch.simulate",
            name="Patch simulation",
            risk_class="MEDIUM",
            mutation_class="SIMULATION_ONLY",
            requires_explicit_approval=False,
        ),
        ToolCapability(
            capability_id="repo.write",
            name="Repository mutation",
            risk_class="HIGH",
            mutation_class="SOURCE_MUTATION",
            requires_explicit_approval=True,
        ),
        ToolCapability(
            capability_id="canonical.write",
            name="Canonical semantic write",
            risk_class="CRITICAL",
            mutation_class="SOVEREIGN_MUTATION",
            requires_explicit_approval=True,
        ),
    )


def envelope_for(project_id: str) -> CapabilityEnvelope:
    normalized = project_id.upper()
    if normalized == "PALWAKF_MIND_ASSISTANT":
        allowed = ("repo.read", "repo.patch.simulate")
        denied = ("repo.write", "canonical.write")
        source_ref = "drive:mind:authority"
    else:
        allowed = ("repo.read",)
        denied = ("repo.patch.simulate", "repo.write", "canonical.write")
        source_ref = f"drive:{normalized.lower()}:authority"
    return CapabilityEnvelope(
        envelope_id=stable_id("env", normalized),
        project_id=normalized,
        allowed_capabilities=allowed,
        denied_capabilities=denied,
        requires_explicit_approval=True,
        source_ref=source_ref,
        client_can_widen=False,
    )


def repository_snapshot(project_id: str) -> RepositorySnapshot | None:
    normalized = project_id.upper()
    if normalized == "PALWAKF_MIND_ASSISTANT":
        ref = RepositoryRef(
            repository="firasfanon/palwakf_mind_assistant",
            ref="main",
            head_sha="8fc746291043a9de9b0b19c477a2d32ae1a06e8a",
            observed_at=NOW,
            freshness=FreshnessState.CURRENT,
        )
        return RepositorySnapshot(
            project_id=normalized,
            repository=ref.repository,
            default_branch="main",
            current_ref=ref,
            files=(
                RepositoryFileRef(
                    path="README.md",
                    repository=ref.repository,
                    ref="main",
                    head_sha=ref.head_sha,
                ),
            ),
        )
    if normalized == "PAL_EYES":
        ref = RepositoryRef(
            repository="firasfanon/palwakf_Eyes",
            ref="main",
            head_sha="UNKNOWN",
            observed_at=NOW,
            freshness=FreshnessState.UNKNOWN,
        )
        return RepositorySnapshot(
            project_id=normalized,
            repository=ref.repository,
            default_branch="main",
            current_ref=ref,
            files=(),
        )
    return None
