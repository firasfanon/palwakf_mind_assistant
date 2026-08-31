from __future__ import annotations

from palwakf_mind_assistant.domain.models import (
    CrossProjectImpact,
    DependencyImpact,
    ImpactAnalysisRequest,
    ImpactAnalysisResponse,
    ImpactSeverity,
)


class ImpactAnalyzer:
    def analyze(self, request: ImpactAnalysisRequest) -> ImpactAnalysisResponse:
        dependencies = request.dependencies or ("WORKSPACE_DRIVE", "GITHUB")
        impacts = tuple(
            DependencyImpact(
                dependency=dependency,
                severity=ImpactSeverity.REVIEW,
                classification="TYPED_DEPENDENCY",
                detail=f"Revalidate {dependency} before mutation",
            )
            for dependency in dependencies
        )
        cross_project_impacts: tuple[CrossProjectImpact, ...] = ()
        normalized_change = request.proposed_change.casefold()
        if "contract" in normalized_change or "shared" in normalized_change:
            cross_project_impacts = (
                CrossProjectImpact(
                    project_id=request.project_id,
                    affected_project_id="DEPENDENT_PROJECTS",
                    severity=ImpactSeverity.REVIEW,
                    detail=(
                        "Potential shared-contract impact; human review "
                        "is required before propagation."
                    ),
                ),
            )
        return ImpactAnalysisResponse(
            project_id=request.project_id,
            impacts=impacts,
            cross_project_impacts=cross_project_impacts,
            overall_severity=ImpactSeverity.REVIEW,
        )
