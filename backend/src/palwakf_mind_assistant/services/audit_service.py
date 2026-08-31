from __future__ import annotations

from palwakf_mind_assistant.domain.models import AuditEvent
from palwakf_mind_assistant.services.mega_batch_core import stable_id


class AuditService:
    def event(
        self,
        project_id: str,
        event_type: str,
        decision: str,
        detail: str,
    ) -> AuditEvent:
        return AuditEvent(
            event_id=stable_id("audit", project_id, event_type, decision),
            event_type=event_type,
            project_id=project_id,
            decision=decision,
            detail=detail,
            source_refs=("FIXTURE_DERIVED",),
        )
