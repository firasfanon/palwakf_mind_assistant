from __future__ import annotations

from palwakf_mind_assistant.domain.models import (
    ApprovalState,
    DecisionAlternative,
    DecisionLineage,
    DecisionRecord,
    DecisionStatus,
    HumanReviewPacket,
)
from palwakf_mind_assistant.services.mega_batch_core import stable_id


class DecisionEngine:
    def propose(
        self,
        project_id: str,
        title: str,
        *,
        source_refs: tuple[str, ...] = (),
    ) -> tuple[DecisionRecord, HumanReviewPacket]:
        decision_id = stable_id("decision", project_id, title)
        record = DecisionRecord(
            decision_id=decision_id,
            project_id=project_id,
            title=title,
            status=DecisionStatus.REVIEW_REQUIRED,
            alternatives=(
                DecisionAlternative(
                    alternative_id="A",
                    title="Proceed under current authority",
                    benefits=("Governed",),
                    risks=("Requires review",),
                ),
                DecisionAlternative(
                    alternative_id="B",
                    title="Defer and reconcile",
                    benefits=("Lower risk",),
                    risks=("Delay",),
                ),
            ),
            rationale=(
                "No autonomous semantic or execution decision is permitted."
            ),
            consequences=("Human approval required before mutation",),
            lineage=DecisionLineage(),
            approval_state=ApprovalState.REQUIRED,
            source_refs=source_refs,
        )
        review = HumanReviewPacket(
            review_id=stable_id("review", decision_id),
            subject_type="DECISION",
            subject_id=decision_id,
            project_id=project_id,
            approval_state=ApprovalState.REQUIRED,
            reasons=("Decision may affect governed development state",),
            source_refs=source_refs,
            execution_authorized=False,
        )
        return record, review
