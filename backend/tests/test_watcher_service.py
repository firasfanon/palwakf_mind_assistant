from palwakf_mind_assistant.adapters.drive_readonly import (
    InMemoryDriveReadOnlyAdapter,
    UnavailableDriveReadOnlyAdapter,
)
from palwakf_mind_assistant.adapters.fixture_loader import load_source_fixture
from palwakf_mind_assistant.api.app import FIXTURE
from palwakf_mind_assistant.services.authority_resolver import AuthorityResolver
from palwakf_mind_assistant.services.watcher_service import WatcherService


def _sources():
    return load_source_fixture(FIXTURE)


def test_watcher_cannot_mutate_canonical_state():
    resolver = AuthorityResolver(InMemoryDriveReadOnlyAdapter(_sources()))
    service = WatcherService(resolver)
    watcher = service.definitions("PALWAKF_MIND_ASSISTANT")[0]
    event = service.evaluate("PALWAKF_MIND_ASSISTANT")[0]
    assert watcher.may_mutate_canonical_state is False
    assert watcher.action == "NOTIFY_OR_PROPOSE_ONLY"
    assert event.state == "STABLE_NO_AUTONOMOUS_MUTATION"


def test_watcher_surfaces_degraded_connector_without_mutation():
    resolver = AuthorityResolver(UnavailableDriveReadOnlyAdapter(_sources()))
    event = WatcherService(resolver).evaluate("PALWAKF_MIND_ASSISTANT")[0]
    assert event.state == "RECONCILE_REQUIRED"
    assert "connector=DEGRADED" in event.detail
