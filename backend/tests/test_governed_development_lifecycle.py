from palwakf_mind_assistant.services.governed_development_lifecycle import (
    GovernedDevelopmentLifecycleService,
)


def test_lifecycle_includes_all_stages_and_simulation_only():
    lifecycle = GovernedDevelopmentLifecycleService().simulate(
        "PALWAKF_MIND_ASSISTANT"
    )
    assert len(lifecycle.receipts) == 12
    assert lifecycle.mutation_mode == "SIMULATION_ONLY"
    assert any(
        receipt.stage.value == "AUTHORIZE"
        and receipt.status == "REVIEW_REQUIRED"
        for receipt in lifecycle.receipts
    )


def test_lifecycle_can_be_simulated_for_second_project_profile():
    lifecycle = GovernedDevelopmentLifecycleService().simulate("PAL_EYES")
    assert lifecycle.project_id == "PAL_EYES"
    assert lifecycle.blocked is False
    assert lifecycle.mutation_mode == "SIMULATION_ONLY"
