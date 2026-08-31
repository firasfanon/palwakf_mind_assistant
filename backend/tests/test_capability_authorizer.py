from palwakf_mind_assistant.domain.models import ExecutionRequest
from palwakf_mind_assistant.services.capability_authorizer import (
    CapabilityAuthorizer,
)


def test_client_cannot_widen_capability_envelope():
    request = ExecutionRequest(
        project_id="PALWAKF_MIND_ASSISTANT",
        capability_id="repo.write",
        simulate=True,
    )
    decision, _ = CapabilityAuthorizer().authorize(request)
    assert decision.value == "DENY"


def test_real_execution_requires_approval_even_for_simulation_capability():
    request = ExecutionRequest(
        project_id="PALWAKF_MIND_ASSISTANT",
        capability_id="repo.patch.simulate",
        simulate=False,
    )
    decision, _ = CapabilityAuthorizer().authorize(request)
    assert decision.value == "REQUIRE_APPROVAL"
