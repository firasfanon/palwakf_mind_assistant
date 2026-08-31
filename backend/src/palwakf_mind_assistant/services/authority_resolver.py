from __future__ import annotations

from collections import defaultdict

from palwakf_mind_assistant.adapters.drive_readonly import DriveReadOnlyPort
from palwakf_mind_assistant.domain.models import (
    AuthorityType,
    ConnectorHealth,
    LifecycleStatus,
    ProjectAuthorityResolution,
    ResolutionStatus,
    SourceRef,
)

_LIFECYCLE_PRIORITY = {
    LifecycleStatus.CURRENT: 40,
    LifecycleStatus.ACTIVE: 30,
    LifecycleStatus.HISTORICAL: 20,
    LifecycleStatus.SUPERSEDED: 10,
    LifecycleStatus.UNKNOWN: 0,
}

_AUTHORITY_PRIORITY = {
    AuthorityType.PROJECT_CURRENT_STATE: 90,
    AuthorityType.PROJECT_GOVERNANCE: 80,
    AuthorityType.DECISION: 70,
    AuthorityType.HANDOFF: 60,
    AuthorityType.PORTFOLIO_REGISTRY: 50,
    AuthorityType.DOCUMENT_AUTHORITY_INDEX: 40,
    AuthorityType.EVIDENCE: 30,
    AuthorityType.OTHER: 10,
    AuthorityType.UNKNOWN: 0,
}


class AuthorityResolver:
    def __init__(self, drive: DriveReadOnlyPort) -> None:
        self._drive = drive

    def list_project_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._drive.list_project_ids()))

    def list_project_sources(self, project_id: str) -> tuple[SourceRef, ...]:
        return tuple(self._drive.list_project_sources(project_id.strip().upper()))

    def connector_health(self) -> ConnectorHealth:
        return self._drive.connector_health()

    def resolve_project(self, project_id: str) -> ProjectAuthorityResolution:
        normalized = project_id.strip().upper()
        if not normalized:
            return ProjectAuthorityResolution(
                project_id="UNKNOWN",
                status=ResolutionStatus.UNKNOWN,
                authoritative_sources=(),
                superseded_sources=(),
                unknown_reasons=("PROJECT_ID_EMPTY",),
            )

        sources = self.list_project_sources(normalized)
        if not sources:
            return ProjectAuthorityResolution(
                project_id=normalized,
                status=ResolutionStatus.UNKNOWN,
                authoritative_sources=(),
                superseded_sources=(),
                unknown_reasons=("NO_AUTHORITATIVE_SOURCE_FOUND",),
            )

        grouped: dict[AuthorityType, list[SourceRef]] = defaultdict(list)
        for source in sources:
            grouped[source.authority_type].append(source)

        selected: list[SourceRef] = []
        superseded: list[SourceRef] = []
        unknown_reasons: list[str] = []

        for authority_type, candidates in grouped.items():
            current_count = sum(
                item.lifecycle_status is LifecycleStatus.CURRENT for item in candidates
            )
            if current_count > 1:
                unknown_reasons.append(f"MULTIPLE_CURRENT:{authority_type}")

            ordered = sorted(
                candidates,
                key=lambda item: (
                    _LIFECYCLE_PRIORITY[item.lifecycle_status],
                    _AUTHORITY_PRIORITY[item.authority_type],
                    item.source_id,
                ),
                reverse=True,
            )
            winner = ordered[0]
            if winner.lifecycle_status is LifecycleStatus.UNKNOWN:
                unknown_reasons.append(f"UNKNOWN_LIFECYCLE:{authority_type}")
                continue

            selected.append(winner)
            superseded.extend(
                candidate
                for candidate in ordered[1:]
                if candidate.lifecycle_status
                in {LifecycleStatus.SUPERSEDED, LifecycleStatus.HISTORICAL}
            )

        selected.sort(
            key=lambda item: (
                _AUTHORITY_PRIORITY[item.authority_type],
                _LIFECYCLE_PRIORITY[item.lifecycle_status],
                item.source_id,
            ),
            reverse=True,
        )
        superseded.sort(key=lambda item: (item.authority_type, item.source_id))

        if not selected:
            status = ResolutionStatus.UNKNOWN
            unknown_reasons.append("NO_CURRENT_OR_ACTIVE_SOURCE")
        elif unknown_reasons:
            status = ResolutionStatus.PARTIAL
        else:
            status = ResolutionStatus.RESOLVED

        return ProjectAuthorityResolution(
            project_id=normalized,
            status=status,
            authoritative_sources=tuple(selected),
            superseded_sources=tuple(superseded),
            unknown_reasons=tuple(sorted(set(unknown_reasons))),
        )
