from __future__ import annotations

from palwakf_mind_assistant.domain.models import (
    DryRunImpactPreview,
    DryRunStatus,
)
from palwakf_mind_assistant.services.mega_batch_core import stable_id


class DryRunEngine:
    def preview(
        self,
        project_id: str,
        actions: tuple[str, ...],
        impacts: tuple[str, ...] = (),
    ) -> DryRunImpactPreview:
        return DryRunImpactPreview(
            dry_run_id=stable_id("dry", project_id, *actions),
            project_id=project_id,
            status=DryRunStatus.SIMULATED,
            planned_actions=actions,
            predicted_impacts=impacts,
            mutation_executed=False,
            source_refs=("FIXTURE_DERIVED",),
        )
