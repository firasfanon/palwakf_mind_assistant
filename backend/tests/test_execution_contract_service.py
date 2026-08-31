from palwakf_mind_assistant.domain.models import ExecutionRequest
from palwakf_mind_assistant.services.execution_contract_service import (
    ExecutionContractService,
)
from palwakf_mind_assistant.services.execution_gateway import ExecutionGateway


def test_contract_is_simulation_only_and_approval_required():
    contract = ExecutionContractService().contract(
        "PALWAKF_MIND_ASSISTANT"
    )
    assert contract.scope.mutation_class == "SIMULATION_ONLY"
    assert contract.approval_state.value == "REQUIRED"


def test_denied_execution_creates_no_mutation():
    request = ExecutionRequest(
        project_id="PALWAKF_MIND_ASSISTANT",
        capability_id="repo.write",
        requested_paths=("x",),
        simulate=True,
    )
    receipt = ExecutionGateway().execute(request)
    assert receipt.status == "DENIED"
    assert receipt.mutation_executed is False
