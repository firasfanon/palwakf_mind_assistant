from datetime import UTC, datetime, timedelta

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


def test_cross_project_authorization_cannot_leak():
    foreign = ExecutionContractService().contract("PAL_EYES")
    request = ExecutionRequest(
        project_id="PALWAKF_MIND_ASSISTANT",
        capability_id="repo.read",
        requested_paths=("README.md",),
        simulate=True,
        authorization=foreign,
    )
    receipt = ExecutionGateway().execute(request)
    assert receipt.status == "DENIED"
    assert receipt.authorized is False
    assert receipt.blocked_reasons == ("CROSS_PROJECT_AUTHORITY_MISMATCH",)


def test_authorization_scope_cannot_be_widened_by_requested_path():
    service = ExecutionContractService()
    base = service.contract("PALWAKF_MIND_ASSISTANT")
    scoped = base.model_copy(
        update={
            "scope": base.scope.model_copy(
                update={"allowed_paths": ("README.md",)}
            )
        }
    )
    request = ExecutionRequest(
        project_id="PALWAKF_MIND_ASSISTANT",
        capability_id="repo.patch.simulate",
        requested_paths=("backend/unsafe.py",),
        simulate=True,
        authorization=scoped,
    )
    receipt = ExecutionGateway().execute(request)
    assert receipt.status == "DENIED"
    assert receipt.blocked_reasons == ("PATH_OUTSIDE_AUTHORIZED_SCOPE",)


def test_empty_authorized_path_set_fails_closed():
    base = ExecutionContractService().contract("PALWAKF_MIND_ASSISTANT")
    request = ExecutionRequest(
        project_id="PALWAKF_MIND_ASSISTANT",
        capability_id="repo.patch.simulate",
        requested_paths=("README.md",),
        simulate=True,
        authorization=base,
    )
    receipt = ExecutionGateway().execute(request)
    assert receipt.status == "DENIED"
    assert receipt.blocked_reasons == ("NO_AUTHORIZED_PATHS",)


def test_expired_authorization_is_denied():
    base = ExecutionContractService().contract("PALWAKF_MIND_ASSISTANT")
    expired = base.model_copy(
        update={"expires_at": datetime.now(UTC) - timedelta(seconds=1)}
    )
    request = ExecutionRequest(
        project_id="PALWAKF_MIND_ASSISTANT",
        capability_id="repo.read",
        simulate=True,
        authorization=expired,
    )
    receipt = ExecutionGateway().execute(request)
    assert receipt.status == "DENIED"
    assert receipt.blocked_reasons == ("AUTHORIZATION_EXPIRED",)


def test_stale_authorization_base_sha_is_denied(monkeypatch):
    monkeypatch.setenv("MIND_REPOSITORY_REF", "task/MIND-L5-ONE-MEGA-BATCH-V1")
    monkeypatch.setenv("MIND_REPOSITORY_HEAD_SHA", "a" * 40)
    base = ExecutionContractService().contract("PALWAKF_MIND_ASSISTANT")
    scoped = base.model_copy(
        update={
            "scope": base.scope.model_copy(
                update={"allowed_paths": ("README.md",)}
            )
        }
    )
    monkeypatch.setenv("MIND_REPOSITORY_HEAD_SHA", "b" * 40)
    request = ExecutionRequest(
        project_id="PALWAKF_MIND_ASSISTANT",
        capability_id="repo.patch.simulate",
        requested_paths=("README.md",),
        simulate=True,
        authorization=scoped,
    )
    receipt = ExecutionGateway().execute(request)
    assert receipt.status == "DENIED"
    assert receipt.blocked_reasons == ("STALE_AUTHORIZATION_BASE_SHA",)
