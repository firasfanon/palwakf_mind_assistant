from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from datetime import UTC, datetime

from palwakf_mind_assistant.domain.models import (
    ClaimState,
    ConflictSeverity,
    ContextRequest,
    MinimalTrustedContextPackage,
    ResolutionStatus,
    SkillResolutionRequest,
    TrustedContextSource,
)
from palwakf_mind_assistant.services.authority_resolver import AuthorityResolver
from palwakf_mind_assistant.services.conflict_detector import ConflictDetector
from palwakf_mind_assistant.services.skill_resolver import SkillResolver
from palwakf_mind_assistant.services.trust_engine import TrustEngine


class ContextCompiler:
    """Compile the smallest trusted context package for a request.

    Pipeline:
    intent -> project -> task -> authority -> current sources -> trust ->
    minimal package. Skills/decisions/dependencies remain explicit empty fields in
    B0.4 unless source metadata carries safe structured values.
    """

    def __init__(
        self,
        resolver: AuthorityResolver,
        *,
        conflict_detector: ConflictDetector | None = None,
        trust_engine: TrustEngine | None = None,
        digital_twin_provider: Callable[[str], object] | None = None,
        skill_resolver: SkillResolver | None = None,
    ) -> None:
        self._resolver = resolver
        self._conflicts = conflict_detector or ConflictDetector()
        self._trust = trust_engine or TrustEngine()
        self._digital_twin_provider = digital_twin_provider
        self._skill_resolver = skill_resolver

    def compile(self, request: ContextRequest) -> MinimalTrustedContextPackage:
        intent = self.resolve_intent(request.message)
        project_id = self.resolve_project(request.message, request.project_id)
        task_id = request.task_id.strip() if request.task_id and request.task_id.strip() else None
        now = datetime.now(UTC)
        context_id = self._context_id(request.message, project_id, task_id, now)

        if project_id is None:
            return MinimalTrustedContextPackage(
                context_id=context_id,
                intent=intent,
                project_id=None,
                task_id=task_id,
                authority_status=ResolutionStatus.UNKNOWN,
                trust_state=ClaimState.UNKNOWN,
                unknown_reasons=("PROJECT_CONTEXT_NOT_DETERMINISTIC",),
                compiled_at=now,
                risks=("PROJECT_AUTHORITY_UNRESOLVED",),
            )

        resolution = self._resolver.resolve_project(project_id)
        raw_sources = self._resolver.list_project_sources(project_id)
        conflicts = self._conflicts.detect(project_id, raw_sources)
        blocking_refs = {
            ref
            for conflict in conflicts
            if conflict.severity is ConflictSeverity.BLOCKING
            for ref in conflict.source_refs
        }
        authoritative = tuple(
            TrustedContextSource(
                source=source,
                provenance=self._trust.provenance_for(
                    source,
                    conflicted=source.source_ref in blocking_refs,
                ),
            )
            for source in resolution.authoritative_sources
        )
        superseded = tuple(
            TrustedContextSource(
                source=source,
                provenance=self._trust.provenance_for(source),
            )
            for source in resolution.superseded_sources
        )

        unknown_reasons = list(resolution.unknown_reasons)
        risks: list[str] = []
        if blocking_refs:
            unknown_reasons.extend(
                conflict.conflict_type
                for conflict in conflicts
                if conflict.severity is ConflictSeverity.BLOCKING
            )
            risks.append("BLOCKING_AUTHORITY_CONFLICT")
        if resolution.status is ResolutionStatus.UNKNOWN:
            risks.append("AUTHORITY_UNKNOWN")
        elif resolution.status is ResolutionStatus.PARTIAL:
            risks.append("AUTHORITY_PARTIAL")

        trust_state = self._package_trust_state(
            resolution.status,
            authoritative,
            bool(blocking_refs),
        )
        twin = self._digital_twin_provider(project_id) if self._digital_twin_provider else None
        skill_resolution = (
            self._skill_resolver.resolve(
                SkillResolutionRequest(
                    message=request.message, project_id=project_id, task_id=task_id
                )
            )
            if self._skill_resolver
            else None
        )
        return MinimalTrustedContextPackage(
            context_id=context_id,
            intent=intent,
            project_id=project_id,
            task_id=task_id,
            authority_status=resolution.status,
            trust_state=trust_state,
            authoritative_sources=authoritative,
            superseded_sources=superseded,
            unknown_reasons=tuple(sorted(set(unknown_reasons))),
            decisions=self._metadata_list(authoritative, "decisions"),
            known_lessons=self._metadata_list(authoritative, "known_lessons"),
            applicable_skills=skill_resolution.selections if skill_resolution else (),
            lesson_regressions=skill_resolution.lesson_regressions if skill_resolution else (),
            dependencies=self._metadata_list(authoritative, "dependencies"),
            planning_refs=self._metadata_list(authoritative, "planning_refs"),
            decision_refs=self._metadata_list(authoritative, "decision_refs"),
            capability_refs=self._metadata_list(authoritative, "capability_refs"),
            verification_refs=self._metadata_list(authoritative, "verification_refs"),
            security_findings=self._metadata_list(authoritative, "security_findings"),
            risks=tuple(risks),
            project_twin_ref=getattr(twin, "twin_id", None),
            project_twin_status=getattr(getattr(twin, "status", None), "value", None),
            project_twin_generated_at=getattr(twin, "generated_at", None),
            compiled_at=now,
        )

    @staticmethod
    def resolve_intent(message: str) -> str:
        normalized = message.casefold()
        if any(term in normalized for term in ("تعارض", "تعارضات", "conflict")):
            return "CONFLICT"
        if any(term in normalized for term in ("مصدر", "مصادر", "source", "sources")):
            return "SOURCES"
        if any(term in normalized for term in ("مهمة", "task", "الخطوة التالية", "next action")):
            return "TASK_CONTEXT"
        return "CURRENT_STATE"

    @staticmethod
    def resolve_project(message: str, explicit_project_id: str | None) -> str | None:
        if explicit_project_id and explicit_project_id.strip():
            return explicit_project_id.strip().upper()
        normalized = re.sub(r"\s+", " ", message.strip()).lower()
        if "pal eyes" in normalized or "pal_eyes" in normalized or "بعيون فلسطينية" in normalized:
            return "PAL_EYES"
        if "mind assistant" in normalized or "palwakf_mind_assistant" in normalized:
            return "PALWAKF_MIND_ASSISTANT"
        return None

    @staticmethod
    def _metadata_list(sources: tuple[TrustedContextSource, ...], key: str) -> tuple[str, ...]:
        values: list[str] = []
        for item in sources:
            raw = item.source.metadata.get(key)
            if isinstance(raw, list):
                values.extend(str(value) for value in raw if str(value).strip())
        return tuple(dict.fromkeys(values))

    @staticmethod
    def _package_trust_state(
        status: ResolutionStatus,
        sources: tuple[TrustedContextSource, ...],
        has_blocking_conflict: bool,
    ) -> ClaimState:
        if has_blocking_conflict:
            return ClaimState.CONFLICTED
        if status is ResolutionStatus.UNKNOWN or not sources:
            return ClaimState.UNKNOWN
        if status is ResolutionStatus.PARTIAL:
            return ClaimState.INFERRED
        if any(item.provenance.claim_state is ClaimState.UNKNOWN for item in sources):
            return ClaimState.UNKNOWN
        if any(item.provenance.claim_state is ClaimState.STALE for item in sources):
            return ClaimState.STALE
        return ClaimState.VERIFIED

    @staticmethod
    def _context_id(
        message: str,
        project_id: str | None,
        task_id: str | None,
        now: datetime,
    ) -> str:
        payload = f"{project_id}|{task_id}|{message}|{now.isoformat()}".encode()
        return f"ctx_{hashlib.sha256(payload).hexdigest()[:16]}"
