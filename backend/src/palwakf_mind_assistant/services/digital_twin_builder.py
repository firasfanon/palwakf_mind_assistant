from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from palwakf_mind_assistant.domain.models import (
    ClaimState,
    ConflictSeverity,
    DigitalTwinStatus,
    DriftIndicator,
    DriftSeverity,
    ProjectDigitalTwinSnapshot,
    ProjectOperationalState,
    ResolutionStatus,
)
from palwakf_mind_assistant.services.authority_resolver import AuthorityResolver
from palwakf_mind_assistant.services.conflict_detector import ConflictDetector


class ProjectDigitalTwinBuilder:
    """Build a rebuildable, non-sovereign project state view from trusted inputs."""

    def __init__(
        self,
        resolver: AuthorityResolver,
        operational_states: tuple[ProjectOperationalState, ...],
        *,
        conflict_detector: ConflictDetector | None = None,
    ) -> None:
        self._resolver = resolver
        self._states = {item.project_id.strip().upper(): item for item in operational_states}
        self._conflicts = conflict_detector or ConflictDetector()

    def build(
        self, project_id: str, *, now: datetime | None = None
    ) -> ProjectDigitalTwinSnapshot:
        generated_at = now or datetime.now(UTC)
        normalized = project_id.strip().upper()
        resolution = self._resolver.resolve_project(normalized)
        sources = self._resolver.list_project_sources(normalized)
        conflicts = self._conflicts.detect(normalized, sources)
        state = self._states.get(normalized)
        current = next(
            (
                s
                for s in resolution.authoritative_sources
                if s.authority_type.value == "PROJECT_CURRENT_STATE"
            ),
            None,
        )

        unknown = list(resolution.unknown_reasons)
        drift: list[DriftIndicator] = []
        blocking = any(c.severity is ConflictSeverity.BLOCKING for c in conflicts)

        if state is None:
            unknown.append("PROJECT_OPERATIONAL_STATE_UNAVAILABLE")
            status = (
                DigitalTwinStatus.UNKNOWN
                if resolution.status is ResolutionStatus.UNKNOWN
                else DigitalTwinStatus.PARTIAL
            )
            trust = ClaimState.UNKNOWN
            display_name = normalized
            source_mode = "UNAVAILABLE"
            observed_at = generated_at
            next_safe_action = "RESTORE_AUTHORIZED_PROJECT_STATE_INPUTS_BEFORE_MUTATION"
            source_refs: tuple[str, ...] = tuple(s.source_ref for s in sources)
            fields = {}
        else:
            display_name = state.display_name
            source_mode = state.source_mode
            observed_at = state.observed_at
            source_refs = tuple(
                sorted({s.source_ref for s in sources} | set(state.source_refs.values()))
            )
            fields = state.model_dump(mode="json")
            next_safe_action = state.next_safe_action

            if (
                state.current_state_ref
                and current
                and state.current_state_ref != current.source_ref
            ):
                drift.append(
                    DriftIndicator(
                        drift_code="CURRENT_STATE_REF_MISMATCH",
                        severity=DriftSeverity.BLOCKING,
                        state=ClaimState.CONFLICTED,
                        explanation=(
                            "Operational state points to a different current-state "
                            "authority reference."
                        ),
                        source_refs=(state.current_state_ref, current.source_ref),
                        detected_at=generated_at,
                    )
                )
                blocking = True

            if state.task_id is None or state.task_status == "UNKNOWN":
                unknown.append("ACTIVE_TASK_UNKNOWN")
                drift.append(
                    DriftIndicator(
                        drift_code="ACTIVE_TASK_UNKNOWN",
                        severity=DriftSeverity.REVIEW,
                        state=ClaimState.UNKNOWN,
                        explanation=(
                            "No authoritative active-task identity is available "
                            "to the twin."
                        ),
                        source_refs=tuple(filter(None, [state.source_refs.get("task")])),
                        detected_at=generated_at,
                    )
                )

            if state.head_sha is None:
                unknown.append("GITHUB_HEAD_UNKNOWN")
                drift.append(
                    DriftIndicator(
                        drift_code="GITHUB_HEAD_UNKNOWN",
                        severity=DriftSeverity.REVIEW,
                        state=ClaimState.UNKNOWN,
                        explanation=(
                            "GitHub HEAD is unavailable; the twin cannot claim "
                            "repository currency."
                        ),
                        source_refs=tuple(filter(None, [state.source_refs.get("github")])),
                        detected_at=generated_at,
                    )
                )

            if blocking:
                status = DigitalTwinStatus.CONFLICTED
                trust = ClaimState.CONFLICTED
            elif resolution.status is ResolutionStatus.UNKNOWN:
                status = DigitalTwinStatus.UNKNOWN
                trust = ClaimState.UNKNOWN
            elif resolution.status is ResolutionStatus.PARTIAL or unknown:
                status = DigitalTwinStatus.PARTIAL
                trust = ClaimState.INFERRED
            else:
                status = DigitalTwinStatus.RESOLVED
                trust = ClaimState.VERIFIED

        receipt_payload = {
            "project_id": normalized,
            "authority_status": resolution.status.value,
            "sources": sorted(s.source_ref for s in sources),
            "fields": fields,
            "unknown": sorted(set(unknown)),
            "drift": [d.model_dump(mode="json") for d in drift],
        }
        receipt = hashlib.sha256(
            json.dumps(receipt_payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        twin_id = f"twin_{normalized.lower()}_{receipt[:12]}"

        return ProjectDigitalTwinSnapshot(
            twin_id=twin_id,
            project_id=normalized,
            display_name=display_name,
            status=status,
            authority_status=resolution.status,
            trust_state=trust,
            source_mode=source_mode,
            current_state_ref=current.source_ref if current else None,
            repository=state.repository if state else None,
            default_branch=state.default_branch if state else None,
            head_sha=state.head_sha if state else None,
            active_branch=state.active_branch if state else None,
            task_id=state.task_id if state else None,
            task_status=state.task_status if state else "UNKNOWN",
            baseline_ref=state.baseline_ref if state else None,
            dependencies=state.dependencies if state else (),
            risks=state.risks if state else (),
            production_readiness_level=(
                state.production_readiness_level if state else "UNKNOWN"
            ),
            production_readiness_status=(
                state.production_readiness_status if state else "UNKNOWN"
            ),
            drift_indicators=tuple(drift),
            unknown_reasons=tuple(sorted(set(unknown))),
            next_safe_action=next_safe_action,
            next_safe_action_source_ref=(
                state.source_refs.get("task") if state else None
            ),
            source_refs=source_refs,
            observed_at=observed_at,
            generated_at=generated_at,
            rebuild_receipt=receipt,
        )
