from __future__ import annotations

from palwakf_mind_assistant.domain.models import (
    EngineeringAdviceRequest,
    EngineeringAdviceResponse,
    EngineeringRisk,
    NextSafeAction,
    VerificationChannel,
    VerificationPlan,
)
from palwakf_mind_assistant.services.repository_analyzer import RepositoryAnalyzer


class EngineeringAdvisor:
    def __init__(self) -> None:
        self._repositories = RepositoryAnalyzer()

    def advise(
        self,
        request: EngineeringAdviceRequest,
        *,
        skill_ids: tuple[str, ...] = (),
    ) -> EngineeringAdviceResponse:
        analysis = self._repositories.analyze(request.project_id)
        ready = analysis.status == "RESOLVED" and not analysis.unknown_reasons
        source_refs = (
            (analysis.snapshot.current_ref.head_sha,)
            if analysis.snapshot is not None
            else ()
        )
        return EngineeringAdviceResponse(
            project_id=request.project_id,
            status=(
                "ADVISORY_READY"
                if ready
                else "RECONCILIATION_REQUIRED"
            ),
            summary="Derived engineering advice; no execution authority.",
            risks=(
                EngineeringRisk(
                    risk_id="R1",
                    severity="REVIEW",
                    title="Authority freshness",
                    mitigation="Re-read live GitHub/Drive before mutation",
                ),
            ),
            verification_plan=VerificationPlan(
                channels=(
                    VerificationChannel.STATIC_ANALYSIS,
                    VerificationChannel.MACHINE_TEST,
                    VerificationChannel.BROWSER_UAT,
                    VerificationChannel.AUTHORITY_READBACK,
                ),
                browser_uat_required=True,
                authority_readback_required=True,
            ),
            next_safe_action=NextSafeAction(
                action_id="NEXT",
                title="Reconcile then simulate",
                reason=(
                    "Mutation is not authorized by this advisory surface."
                ),
                mutation_ready=False,
                requires_approval=True,
            ),
            source_refs=source_refs,
            applicable_skill_ids=skill_ids,
        )
