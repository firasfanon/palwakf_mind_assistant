from __future__ import annotations

from datetime import UTC, datetime

from palwakf_mind_assistant.domain.models import (
    CapabilityDecision,
    ExecutionRequest,
)
from palwakf_mind_assistant.services.mega_batch_core import envelope_for, repository_snapshot


class CapabilityAuthorizer:
    def authorize(
        self,
        request: ExecutionRequest,
    ) -> tuple[CapabilityDecision, str]:
        envelope = envelope_for(request.project_id)
        authorization = request.authorization
        if authorization is not None:
            normalized = request.project_id.strip().upper()
            if (
                authorization.envelope.project_id.strip().upper() != normalized
                or authorization.scope.project_id.strip().upper() != normalized
            ):
                return CapabilityDecision.DENY, "CROSS_PROJECT_AUTHORITY_MISMATCH"
            if authorization.envelope.client_can_widen:
                return CapabilityDecision.DENY, "CLIENT_AUTHORITY_WIDENING_FORBIDDEN"
            if authorization.scope.mutation_class != "SIMULATION_ONLY":
                return CapabilityDecision.DENY, "AUTHORIZATION_MUTATION_CLASS_INVALID"
            if (
                authorization.expires_at is not None
                and authorization.expires_at <= datetime.now(UTC)
            ):
                return CapabilityDecision.DENY, "AUTHORIZATION_EXPIRED"
            if request.capability_id not in authorization.envelope.allowed_capabilities:
                return CapabilityDecision.DENY, "AUTHORIZATION_CAPABILITY_MISMATCH"
            snapshot = repository_snapshot(normalized)
            if snapshot is not None:
                if authorization.scope.repository != snapshot.repository:
                    return CapabilityDecision.DENY, "AUTHORIZATION_REPOSITORY_MISMATCH"
                current_head = snapshot.current_ref.head_sha
                if (
                    current_head != "UNKNOWN"
                    and authorization.scope.base_sha != current_head
                ):
                    return CapabilityDecision.DENY, "STALE_AUTHORIZATION_BASE_SHA"
            allowed_paths = set(authorization.scope.allowed_paths)
            if request.requested_paths and not allowed_paths:
                return CapabilityDecision.DENY, "NO_AUTHORIZED_PATHS"
            if any(path not in allowed_paths for path in request.requested_paths):
                return CapabilityDecision.DENY, "PATH_OUTSIDE_AUTHORIZED_SCOPE"
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
