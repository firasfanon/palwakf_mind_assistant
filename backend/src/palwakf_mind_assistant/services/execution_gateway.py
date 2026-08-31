from __future__ import annotations

from palwakf_mind_assistant.domain.models import (
    ExecutionReceipt,
    ExecutionRequest,
    RollbackMetadata,
)
from palwakf_mind_assistant.services.capability_authorizer import (
    CapabilityAuthorizer,
)
from palwakf_mind_assistant.services.mega_batch_core import stable_id


class ExecutionGateway:
    def __init__(self) -> None:
        self._authorizer = CapabilityAuthorizer()

    def execute(self, request: ExecutionRequest) -> ExecutionReceipt:
        decision, reason = self._authorizer.authorize(request)
        allowed = decision.value == "ALLOW"
        return ExecutionReceipt(
            execution_id=stable_id(
                "exec",
                request.project_id,
                request.capability_id,
            ),
            project_id=request.project_id,
            status="SIMULATED" if allowed else "DENIED",
            simulated=True,
            mutation_executed=False,
            authorized=allowed,
            changed_paths=(),
            blocked_reasons=() if allowed else (reason,),
            rollback=RollbackMetadata(
                strategy="NO_MUTATION_SIMULATION",
                rollback_available=True,
            ),
        )
