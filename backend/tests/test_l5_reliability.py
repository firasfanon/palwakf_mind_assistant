from palwakf_mind_assistant.adapters.drive_readonly import (
    InMemoryDriveReadOnlyAdapter,
)
from palwakf_mind_assistant.adapters.fixture_loader import load_source_fixture
from palwakf_mind_assistant.api.app import FIXTURE
from palwakf_mind_assistant.services.authority_resolver import AuthorityResolver
from palwakf_mind_assistant.services.reliability_service import ReliabilityService


def _service() -> ReliabilityService:
    sources = load_source_fixture(FIXTURE)
    resolver = AuthorityResolver(InMemoryDriveReadOnlyAdapter(sources))
    return ReliabilityService(resolver)


def test_zero_loss_rebuild_is_real_deterministic_roundtrip():
    receipt = _service().rebuild_drill()
    assert receipt.status == "PASS_REBUILT_FROM_ACTIVE_SOURCES"
    assert receipt.rebuildable is True
    assert receipt.canonical_data_loss is False
    assert receipt.accepted_knowledge_loss_count == 0
    assert receipt.source_count > 0
    assert receipt.project_count >= 2
    assert receipt.before_digest == receipt.after_digest
    assert receipt.canonical_state_mutated is False
def test_restart_resume_checkpoint_is_stable_across_service_instances():
    first = _service().resume_receipt(
        "PALWAKF_MIND_ASSISTANT",
        completed_actions=("READ", "VERIFY", "CHECKPOINT"),
    )
    second = _service().resume_receipt(
        "PALWAKF_MIND_ASSISTANT",
        completed_actions=("CHECKPOINT", "VERIFY", "READ"),
        previous_source_digest=first.source_digest,
    )
    assert first.checkpoint_id == second.checkpoint_id
    assert second.resume_safe is True
    assert second.stale_checkpoint is False
    assert second.duplicate_completed_actions == 0


def test_stale_or_duplicate_resume_fails_closed():
    stale = _service().resume_receipt(
        "PALWAKF_MIND_ASSISTANT",
        completed_actions=("VERIFY",),
        previous_source_digest="stale-digest",
    )
    duplicate = _service().resume_receipt(
        "PALWAKF_MIND_ASSISTANT",
        completed_actions=("VERIFY", "VERIFY"),
    )
    assert stale.resume_safe is False
    assert stale.stale_checkpoint is True
    assert duplicate.resume_safe is False
    assert duplicate.duplicate_completed_actions == 1


def test_readiness_has_no_blocking_dimension_in_fixture_candidate_mode():
    dimensions = _service().readiness("PALWAKF_MIND_ASSISTANT")
    assert not [item for item in dimensions if item.status == "BLOCKED"]
    live = next(item for item in dimensions if item.dimension == "LIVE_SOURCE_VERIFICATION")
    assert live.status == "REVIEW"
