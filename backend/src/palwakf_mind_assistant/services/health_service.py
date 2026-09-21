from palwakf_mind_assistant.domain.models import (
    ConnectorHealthObservation,
    ModelHealth,
)
from palwakf_mind_assistant.services.authority_resolver import AuthorityResolver


class HealthService:
    def __init__(
        self,
        resolver: AuthorityResolver,
        *,
        provider_mode: str,
    ) -> None:
        self._resolver = resolver
        self._provider_mode = provider_mode

    def connector_health(
        self,
    ) -> tuple[ConnectorHealthObservation, ...]:
        observed = self._resolver.connector_health()
        return (
            ConnectorHealthObservation(
                connector_id=observed.connector,
                status=observed.state.value,
                detail=(
                    f"{observed.mode}; writes_enabled="
                    f"{str(observed.writes_enabled).lower()}; {observed.detail}"
                ),
            ),
        )

    def model_health(self) -> tuple[ModelHealth, ...]:
        ready = bool(self._provider_mode.strip())
        return (
            ModelHealth(
                provider_id=self._provider_mode or "UNKNOWN",
                status="READY" if ready else "UNKNOWN",
                detail="Configured provider mode; no silent provider substitution.",
            ),
        )
