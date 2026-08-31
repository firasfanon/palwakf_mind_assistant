from palwakf_mind_assistant.domain.models import CostObservation


class CostIntelligence:
    def observe(self) -> tuple[CostObservation, ...]:
        return (
            CostObservation(
                observation_id="COST-1",
                provider_id="DETERMINISTIC_GROUNDED",
                unit="requests",
                amount=0.0,
                budget_state="OK",
            ),
        )
