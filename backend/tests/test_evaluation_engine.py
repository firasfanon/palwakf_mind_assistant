from palwakf_mind_assistant.domain.models import (
    VerificationBundle,
    VerificationStatus,
)
from palwakf_mind_assistant.services.evaluation_engine import EvaluationEngine


def test_evaluation_follows_verification_bundle():
    bundle = VerificationBundle(
        bundle_id="b",
        project_id="P",
        receipts=(),
        final_status=VerificationStatus.FAIL,
        independent_verification=True,
    )
    evaluation = EvaluationEngine().evaluate("P", "subject", bundle)
    assert evaluation.score == 0
    assert evaluation.status == "FAIL"
