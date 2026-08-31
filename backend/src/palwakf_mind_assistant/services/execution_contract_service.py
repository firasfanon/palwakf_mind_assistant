from __future__ import annotations

from palwakf_mind_assistant.domain.models import (
    ApprovalState,
    AuthorizationContract,
    ExecutionScope,
)
from palwakf_mind_assistant.services.mega_batch_core import (
    envelope_for,
    repository_snapshot,
    stable_id,
)


class ExecutionContractService:
    def contract(self, project_id: str) -> AuthorizationContract:
        snapshot = repository_snapshot(project_id)
        repository = (
            snapshot.repository if snapshot is not None else "UNKNOWN"
        )
        head_sha = (
            snapshot.current_ref.head_sha
            if snapshot is not None
            else "UNKNOWN"
        )
        return AuthorizationContract(
            authorization_id=stable_id("auth", project_id),
            envelope=envelope_for(project_id),
            scope=ExecutionScope(
                project_id=project_id,
                repository=repository,
                base_sha=head_sha,
                allowed_paths=(),
                mutation_class="SIMULATION_ONLY",
            ),
            approval_state=ApprovalState.REQUIRED,
            source_ref="FIXTURE_DERIVED",
        )
