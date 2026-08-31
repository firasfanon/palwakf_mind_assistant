from palwakf_mind_assistant.domain.models import (
    VerificationChannel,
    VerificationReceipt,
    VerificationStatus,
)
from palwakf_mind_assistant.services.verification_engine import (
    VerificationEngine,
)


def test_generated_candidate_cannot_self_certify():
    receipt = VerificationReceipt(
        receipt_id="r",
        channel=VerificationChannel.MACHINE_TEST,
        status=VerificationStatus.PASS,
        verifier_id="same",
        generator_id="same",
        detail="bad",
    )
    bundle = VerificationEngine().bundle("P", (receipt,))
    assert bundle.independent_verification is False
    assert bundle.final_status.value == "BLOCKED"


def test_negative_failure_evidence_is_retained():
    receipt = VerificationReceipt(
        receipt_id="r",
        channel=VerificationChannel.SECURITY_GATE,
        status=VerificationStatus.FAIL,
        verifier_id="security",
        generator_id="generator",
        detail="denied",
    )
    bundle = VerificationEngine().bundle("P", (receipt,))
    assert bundle.final_status.value == "FAIL"
    assert bundle.negative_evidence_preserved is True
