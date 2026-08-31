from palwakf_mind_assistant.services.decision_engine import DecisionEngine


def test_decision_preserves_alternatives_and_requires_approval():
    record, review = DecisionEngine().propose(
        "PALWAKF_MIND_ASSISTANT",
        "Choose path",
        source_refs=("drive:x",),
    )
    assert len(record.alternatives) == 2
    assert record.approval_state.value == "REQUIRED"
    assert review.execution_authorized is False
