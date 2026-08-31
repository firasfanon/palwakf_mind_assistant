from __future__ import annotations

from palwakf_mind_assistant.domain.models import (
    VerificationBundle,
    VerificationReceipt,
    VerificationStatus,
)
from palwakf_mind_assistant.services.mega_batch_core import stable_id


class VerificationEngine:
    def bundle(
        self,
        project_id: str,
        receipts: tuple[VerificationReceipt, ...],
    ) -> VerificationBundle:
        independent = all(
            receipt.generator_id is None
            or receipt.generator_id != receipt.verifier_id
            for receipt in receipts
        )
        has_failure = any(
            receipt.status is VerificationStatus.FAIL for receipt in receipts
        )
        all_pass = bool(receipts) and all(
            receipt.status is VerificationStatus.PASS for receipt in receipts
        )
        if has_failure:
            status = VerificationStatus.FAIL
        elif not independent:
            status = VerificationStatus.BLOCKED
        elif all_pass:
            status = VerificationStatus.PASS
        else:
            status = VerificationStatus.NOT_RUN

        return VerificationBundle(
            bundle_id=stable_id(
                "verify",
                project_id,
                *(receipt.receipt_id for receipt in receipts),
            ),
            project_id=project_id,
            receipts=receipts,
            final_status=status,
            independent_verification=independent,
            negative_evidence_preserved=True,
        )
