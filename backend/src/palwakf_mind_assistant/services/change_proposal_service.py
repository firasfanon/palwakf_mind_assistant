from __future__ import annotations

from palwakf_mind_assistant.domain.models import (
    ChangeProposal,
    PatchProposal,
    RepositoryAnalysis,
)
from palwakf_mind_assistant.services.mega_batch_core import stable_id


class ChangeProposalService:
    def propose(
        self,
        analysis: RepositoryAnalysis,
        paths: tuple[str, ...],
    ) -> ChangeProposal:
        if analysis.snapshot is None:
            raise ValueError("REPOSITORY_SNAPSHOT_REQUIRED")
        snapshot = analysis.snapshot
        return ChangeProposal(
            proposal_id=stable_id("change", analysis.project_id, *paths),
            project_id=analysis.project_id,
            repository=snapshot.repository,
            base_sha=snapshot.current_ref.head_sha,
            patches=tuple(
                PatchProposal(
                    path=path,
                    change_type="MODIFY",
                    rationale="Proposed only; no mutation",
                )
                for path in paths
            ),
            impact_summary="Requires impact analysis and verification",
            execution_authorized=False,
        )
