from __future__ import annotations

from datetime import UTC, datetime

from palwakf_mind_assistant.domain.models import ProviderEvaluation


class ProviderEvaluationRegistry:
    def list(self) -> tuple[ProviderEvaluation, ...]:
        return (
            ProviderEvaluation(
                provider_id="DETERMINISTIC_GROUNDED",
                provider_neutral=True,
                health="READY",
                quality_score=100,
                last_evaluated_at=datetime.now(UTC),
            ),
        )
