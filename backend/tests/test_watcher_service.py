from palwakf_mind_assistant.services.watcher_service import WatcherService


def test_watcher_cannot_mutate_canonical_state():
    w=WatcherService().definitions("P")[0]
    assert w.may_mutate_canonical_state is False
    assert w.action=="NOTIFY_OR_PROPOSE_ONLY"

