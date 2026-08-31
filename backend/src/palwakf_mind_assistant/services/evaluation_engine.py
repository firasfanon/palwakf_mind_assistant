from __future__ import annotations

from palwakf_mind_assistant.domain.models import (
    EvaluationRecord,
    VerificationBundle,
)
from palwakf_mind_assistant.services.mega_batch_core import stable_id


class EvaluationEngine:
    def evaluate(
        self,
        project_id: str,
        subject_id: str,
        bundle: VerificationBundle,
    ) -> EvaluationRecord:
        score = 100 if bundle.final_status.value == "PASS" else 0
        return EvaluationRecord(
            evaluation_id=stable_id("eval", project_id, subject_id),
            project_id=project_id,
            subject_id=subject_id,
            score=score,
            status=bundle.final_status.value,
            criteria=(
                "INDEPENDENT_VERIFICATION",
                "NEGATIVE_EVIDENCE_PRESERVED",
            ),
            verification_bundle_id=bundle.bundle_id,
        )
