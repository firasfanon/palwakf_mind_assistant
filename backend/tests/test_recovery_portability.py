from palwakf_mind_assistant.adapters.drive_readonly import InMemoryDriveReadOnlyAdapter
from palwakf_mind_assistant.adapters.fixture_loader import load_source_fixture
from palwakf_mind_assistant.api.app import FIXTURE
from palwakf_mind_assistant.services.authority_resolver import AuthorityResolver
from palwakf_mind_assistant.services.portability_service import PortabilityService
from palwakf_mind_assistant.services.reliability_service import ReliabilityService


def test_rebuild_and_portability_preserve_canonical_truth_and_secrets():
    resolver = AuthorityResolver(
        InMemoryDriveReadOnlyAdapter(load_source_fixture(FIXTURE))
    )
    recovery = ReliabilityService(resolver).rebuild_drill()
    portability = PortabilityService().export()
    assert recovery.rebuildable is True
    assert recovery.canonical_data_loss is False
    assert recovery.accepted_knowledge_loss_count == 0
    assert recovery.before_digest == recovery.after_digest
    assert portability.provider_neutral is True
    assert portability.contains_secrets is False
