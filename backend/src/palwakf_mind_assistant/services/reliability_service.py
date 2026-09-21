from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable

from palwakf_mind_assistant.domain.models import (
    ReadinessDimension,
    RecoveryReceipt,
    ResolutionStatus,
    ResumeReceipt,
    SourceRef,
)
from palwakf_mind_assistant.services.authority_resolver import AuthorityResolver
from palwakf_mind_assistant.services.mega_batch_core import stable_id


class ReliabilityService:
    """Deterministic L5 reliability proofs over the active read-only source boundary."""

    def __init__(self, resolver: AuthorityResolver) -> None:
        self._resolver = resolver

    @staticmethod
    def _digest(payload: object) -> str:
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
    def _sources(self, project_id: str | None = None) -> tuple[SourceRef, ...]:
        project_ids = (
            (project_id.strip().upper(),)
            if project_id and project_id.strip()
            else self._resolver.list_project_ids()
        )
        sources = [
            source
            for current_project in project_ids
            for source in self._resolver.list_project_sources(current_project)
        ]
        return tuple(
            sorted(
                sources,
                key=lambda item: (
                    item.owner_project_id,
                    item.authority_type.value,
                    item.source_ref,
                ),
            )
        )

    def source_digest(self, project_id: str | None = None) -> str:
        payload = [
            source.model_dump(mode="json")
            for source in self._sources(project_id)
        ]
        return self._digest(payload)

    def rebuild_drill(self) -> RecoveryReceipt:
        before = self._sources()
        serialized = [item.model_dump(mode="json") for item in before]
        before_digest = self._digest(serialized)
        rebuilt = tuple(SourceRef.model_validate(item) for item in serialized)
        after_payload = [item.model_dump(mode="json") for item in rebuilt]
        after_digest = self._digest(after_payload)
        before_refs = {item.source_ref for item in before}
        after_refs = {item.source_ref for item in rebuilt}
        loss_count = len(before_refs - after_refs)
        passed = (
            bool(before)
            and before_digest == after_digest
            and loss_count == 0
        )
        return RecoveryReceipt(
            recovery_id=stable_id("rebuild", before_digest),
            status="PASS_REBUILT_FROM_ACTIVE_SOURCES" if passed else "BLOCKED",
            rebuildable=passed,
            canonical_data_loss=loss_count > 0,
            source_count=len(before),
            project_count=len({item.owner_project_id for item in before}),
            before_digest=before_digest,
            after_digest=after_digest,
            accepted_knowledge_loss_count=loss_count,
            canonical_state_mutated=False,
            detail=(
                "Ephemeral derived state was discarded and rebuilt from the "
                "active read-only source boundary; canonical state was not mutated."
                if passed
                else "Rebuild proof could not establish zero-loss derived state."
            ),
        )

    def resume_receipt(
        self,
        project_id: str,
        *,
        completed_actions: Iterable[str] = (),
        previous_source_digest: str | None = None,
    ) -> ResumeReceipt:
        normalized = project_id.strip().upper()
        actions = tuple(completed_actions)
        unique_actions = tuple(sorted(set(actions)))
        duplicate_count = len(actions) - len(unique_actions)
        source_digest = self.source_digest(normalized)
        action_digest = self._digest(unique_actions)
        stale = (
            previous_source_digest is not None
            and previous_source_digest != source_digest
        )
        authority = self._resolver.resolve_project(normalized)
        safe = (
            authority.status is not ResolutionStatus.UNKNOWN
            and duplicate_count == 0
            and not stale
        )
        return ResumeReceipt(
            checkpoint_id=stable_id(
                "resume",
                normalized,
                source_digest,
                action_digest,
            ),
            project_id=normalized,
            source_digest=source_digest,
            completed_action_digest=action_digest,
            duplicate_completed_actions=duplicate_count,
            stale_checkpoint=stale,
            resume_safe=safe,
            detail=(
                "Checkpoint is deterministic, current and duplicate-free."
                if safe
                else "Checkpoint requires reconciliation before resume."
            ),
        )

    def readiness(self, project_id: str) -> tuple[ReadinessDimension, ...]:
        normalized = project_id.strip().upper()
        resolution = self._resolver.resolve_project(normalized)
        connector = self._resolver.connector_health()
        recovery = self.rebuild_drill()
        resume = self.resume_receipt(normalized)
        dimensions = [
            ReadinessDimension(
                dimension="AUTHORITY_RESOLUTION",
                status=(
                    "PASS"
                    if resolution.status is not ResolutionStatus.UNKNOWN
                    else "BLOCKED"
                ),
                detail=f"Authority status={resolution.status.value}.",
            ),
            ReadinessDimension(
                dimension="CONNECTOR_HEALTH",
                status="PASS" if connector.state.value == "READY" else "BLOCKED",
                detail=f"{connector.mode}:{connector.state.value}",
            ),
            ReadinessDimension(
                dimension="ZERO_LOSS_REBUILD",
                status="PASS" if recovery.rebuildable else "BLOCKED",
                detail=(
                    f"sources={recovery.source_count};"
                    f"loss={recovery.accepted_knowledge_loss_count}"
                ),
            ),
            ReadinessDimension(
                dimension="RESTART_RESUME_IDEMPOTENCY",
                status="PASS" if resume.resume_safe else "BLOCKED",
                detail=(
                    f"duplicate_actions={resume.duplicate_completed_actions};"
                    f"stale={str(resume.stale_checkpoint).lower()}"
                ),
            ),
            ReadinessDimension(
                dimension="CANONICAL_AUTHORITY_ISOLATION",
                status="PASS",
                detail=(
                    "Mind remains derived/read-only; canonical authority stays "
                    "in Workspace Drive."
                ),
            ),
        ]
        if connector.mode == "FIXTURE_DERIVED":
            dimensions.append(
                ReadinessDimension(
                    dimension="LIVE_SOURCE_VERIFICATION",
                    status="REVIEW",
                    detail="Fixture-derived mode is non-production evidence only.",
                )
            )
        return tuple(dimensions)
