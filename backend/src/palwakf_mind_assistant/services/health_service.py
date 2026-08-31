from palwakf_mind_assistant.domain.models import (
    ConnectorHealthObservation,
    ModelHealth,
)


class HealthService:
    def connector_health(
        self,
    ) -> tuple[ConnectorHealthObservation, ...]:
        return (
            ConnectorHealthObservation(
                connector_id="GOOGLE_DRIVE",
                status="READY",
                detail="Fixture-derived read-only",
            ),
        )

    def model_health(self) -> tuple[ModelHealth, ...]:
        return (
            ModelHealth(
                provider_id="DETERMINISTIC_GROUNDED",
                status="READY",
                detail="Provider-neutral mode",
            ),
        )
