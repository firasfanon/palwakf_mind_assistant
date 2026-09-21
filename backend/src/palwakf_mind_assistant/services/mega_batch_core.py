from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime

from palwakf_mind_assistant.domain.models import (
    CapabilityEnvelope,
    FreshnessState,
    RepositoryFileRef,
    RepositoryRef,
    RepositorySnapshot,
    ToolCapability,
)


def _runtime_git_identity() -> tuple[str, str, FreshnessState]:
    head_sha = (
        os.getenv("MIND_REPOSITORY_HEAD_SHA")
        or os.getenv("VERCEL_GIT_COMMIT_SHA")
        or "UNKNOWN"
    )
    ref = (
        os.getenv("MIND_REPOSITORY_REF")
        or os.getenv("VERCEL_GIT_COMMIT_REF")
        or "UNKNOWN"
    )
    freshness = (
        FreshnessState.CURRENT
        if head_sha != "UNKNOWN" and ref != "UNKNOWN"
        else FreshnessState.UNKNOWN
    )
    return ref, head_sha, freshness


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
        runtime_ref, head_sha, freshness = _runtime_git_identity()
        ref = RepositoryRef(
            repository="firasfanon/palwakf_mind_assistant",
            ref=runtime_ref,
            head_sha=head_sha,
            observed_at=datetime.now(UTC),
            freshness=freshness,
        )
        return RepositorySnapshot(
            project_id=normalized,
            repository=ref.repository,
            default_branch="main",
            current_ref=ref,
            source_mode=(
                "RUNTIME_GIT_IDENTITY"
                if freshness is FreshnessState.CURRENT
                else "RUNTIME_GIT_IDENTITY_REQUIRED"
            ),
            files=(
                RepositoryFileRef(
                    path="README.md",
                    repository=ref.repository,
                    ref=runtime_ref,
                    head_sha=head_sha,
                ),
            ),
        )
    if normalized == "PAL_EYES":
        ref = RepositoryRef(
            repository="firasfanon/palwakf_Eyes",
            ref="UNKNOWN",
            head_sha="UNKNOWN",
            observed_at=datetime.now(UTC),
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
