from palwakf_mind_assistant.services.portability_service import PortabilityService
from palwakf_mind_assistant.services.recovery_service import RecoveryService


def test_rebuild_and_portability_preserve_canonical_truth_and_secrets():
    recovery = RecoveryService().drill()
    portability = PortabilityService().export()
    assert recovery.rebuildable is True
    assert recovery.canonical_data_loss is False
    assert portability.provider_neutral is True
    assert portability.contains_secrets is False
