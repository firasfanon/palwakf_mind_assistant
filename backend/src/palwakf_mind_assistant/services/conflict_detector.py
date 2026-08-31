from __future__ import annotations

import hashlib
from collections import defaultdict
from collections.abc import Sequence

from palwakf_mind_assistant.domain.models import (
    AuthorityType,
    ConflictCandidate,
    ConflictSeverity,
    LifecycleStatus,
    SourceRef,
)


class ConflictDetector:
    """Structural conflict detector.

    It intentionally does not claim semantic contradiction detection. It only
    reports authority/lifecycle patterns that are provable from source metadata.
    """

    def detect(
        self, project_id: str, sources: Sequence[SourceRef]
    ) -> tuple[ConflictCandidate, ...]:
        normalized = project_id.strip().upper()
        by_authority: dict[AuthorityType, list[SourceRef]] = defaultdict(list)
        for source in sources:
            by_authority[source.authority_type].append(source)

        conflicts: list[ConflictCandidate] = []
        for authority_type, candidates in by_authority.items():
            current = [
                item for item in candidates if item.lifecycle_status is LifecycleStatus.CURRENT
            ]
            if len(current) > 1:
                conflicts.append(
                    self._candidate(
                        normalized,
                        "MULTIPLE_CURRENT_SOURCES",
                        ConflictSeverity.BLOCKING,
                        f"أكثر من مصدر CURRENT لنوع السلطة {authority_type}",
                        "لا يمكن اختيار Current وحيد بأمان قبل مراجعة بشرية أو Supersession صريح.",
                        current,
                    )
                )

            unknown = [
                item for item in candidates if item.lifecycle_status is LifecycleStatus.UNKNOWN
            ]
            if unknown:
                conflicts.append(
                    self._candidate(
                        normalized,
                        "UNKNOWN_LIFECYCLE",
                        ConflictSeverity.REVIEW,
                        f"Lifecycle غير محسوم لنوع السلطة {authority_type}",
                        "المصدر موجود لكن حالته الزمنية/الاعتمادية UNKNOWN، "
                        "لذلك لا يجوز ترقيته إلى Current.",
                        unknown,
                    )
                )

        return tuple(sorted(conflicts, key=lambda item: (item.severity, item.conflict_id)))

    @staticmethod
    def _candidate(
        project_id: str,
        conflict_type: str,
        severity: ConflictSeverity,
        title: str,
        detail: str,
        sources: Sequence[SourceRef],
    ) -> ConflictCandidate:
        refs = tuple(sorted(source.source_ref for source in sources))
        raw = "|".join((project_id, conflict_type, *refs)).encode("utf-8")
        conflict_id = hashlib.sha256(raw).hexdigest()[:14]
        return ConflictCandidate(
            conflict_id=conflict_id,
            project_id=project_id,
            conflict_type=conflict_type,
            severity=severity,
            title=title,
            detail=detail,
            source_refs=refs,
        )
