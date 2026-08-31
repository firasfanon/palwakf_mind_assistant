from __future__ import annotations

from palwakf_mind_assistant.domain.models import (
    GovernedDevelopmentLifecycle,
    LifecycleReceipt,
    LifecycleStage,
)
from palwakf_mind_assistant.services.mega_batch_core import stable_id


class GovernedDevelopmentLifecycleService:
    def simulate(self, project_id: str) -> GovernedDevelopmentLifecycle:
        receipts: list[LifecycleReceipt] = []
        for stage in LifecycleStage:
            if stage is LifecycleStage.AUTHORIZE:
                status = "REVIEW_REQUIRED"
            elif stage is LifecycleStage.EXECUTE_OR_SIMULATE:
                status = "SIMULATED_NO_MUTATION"
            else:
                status = "SIMULATED"
            receipts.append(
                LifecycleReceipt(
                    stage=stage,
                    status=status,
                    detail="Derived controlled lifecycle receipt",
                    evidence_refs=("FIXTURE_DERIVED",),
                )
            )
        return GovernedDevelopmentLifecycle(
            lifecycle_id=stable_id("life", project_id),
            project_id=project_id,
            current_stage=LifecycleStage.CHECKPOINT,
            receipts=tuple(receipts),
            blocked=False,
            mutation_mode="SIMULATION_ONLY",
        )
