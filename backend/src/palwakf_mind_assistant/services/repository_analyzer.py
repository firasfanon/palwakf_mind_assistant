from __future__ import annotations

from palwakf_mind_assistant.domain.models import RepositoryAnalysis
from palwakf_mind_assistant.services.mega_batch_core import repository_snapshot


class RepositoryAnalyzer:
    def analyze(self, project_id: str) -> RepositoryAnalysis:
        snapshot = repository_snapshot(project_id)
        if snapshot is None:
            return RepositoryAnalysis(
                project_id=project_id,
                status="UNKNOWN",
                unknown_reasons=("REPOSITORY_UNKNOWN",),
                mutation_ready=False,
            )
        if snapshot.current_ref.head_sha == "UNKNOWN":
            return RepositoryAnalysis(
                project_id=project_id,
                status="PARTIAL",
                snapshot=snapshot,
                risks=("HEAD_UNKNOWN",),
                unknown_reasons=("LIVE_HEAD_REQUIRED_BEFORE_MUTATION",),
                mutation_ready=False,
            )
        return RepositoryAnalysis(
            project_id=project_id,
            status="RESOLVED",
            snapshot=snapshot,
            risks=("FIXTURE_DERIVED_NOT_LIVE",),
            mutation_ready=False,
        )
