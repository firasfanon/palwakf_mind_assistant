from __future__ import annotations

from palwakf_mind_assistant.domain.models import (
    CapabilityDecision,
    ExecutionRequest,
)
from palwakf_mind_assistant.services.mega_batch_core import envelope_for


class CapabilityAuthorizer:
    def authorize(
        self,
        request: ExecutionRequest,
    ) -> tuple[CapabilityDecision, str]:
        envelope = envelope_for(request.project_id)
        if request.capability_id in envelope.denied_capabilities:
            return (
                CapabilityDecision.DENY,
                "CAPABILITY_DENIED_BY_ENVELOPE",
            )
        if request.capability_id not in envelope.allowed_capabilities:
            return CapabilityDecision.DENY, "CAPABILITY_NOT_ALLOWED"
        if not request.simulate:
            return (
                CapabilityDecision.REQUIRE_APPROVAL,
                "REAL_MUTATION_NOT_AUTHORIZED_IN_MEGA_BATCH",
            )
        return CapabilityDecision.ALLOW, "SIMULATION_ALLOWED"
