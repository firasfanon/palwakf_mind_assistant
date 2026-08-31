from __future__ import annotations

import hashlib
import re

from palwakf_mind_assistant.domain.models import (
    AssistantAnswer,
    AssistantCitation,
    AssistantQuestion,
    AuthorityType,
    AuthorizationContract,
    CapabilityEnvelope,
    ChangeProposal,
    ConflictSeverity,
    ContextRequest,
    DashboardSnapshot,
    DecisionRecord,
    DryRunImpactPreview,
    EngineeringAdviceRequest,
    EngineeringAdviceResponse,
    EvaluationRecord,
    ExecutionReceipt,
    ExecutionRequest,
    GovernedDevelopmentLifecycle,
    HumanReviewPacket,
    ImpactAnalysisRequest,
    ImpactAnalysisResponse,
    KnowledgeSearchHit,
    KnowledgeSearchResponse,
    LifecycleStatus,
    MultiAgentPlan,
    OperationsSnapshot,
    PlanningRequest,
    PlanningResponse,
    ProjectDigitalTwinSnapshot,
    ProjectMindSnapshot,
    ProjectOperationalState,
    ProjectSummary,
    PromptInjectionFinding,
    ProviderEvaluation,
    RepositoryAnalysis,
    ResolutionStatus,
    SecretBoundaryFinding,
    SkillObject,
    SkillResolutionRequest,
    SkillResolutionResponse,
    SourceRef,
    ToolCapability,
    VerificationBundle,
    VerificationReceipt,
)
from palwakf_mind_assistant.services.agent_orchestrator import AgentOrchestrator
from palwakf_mind_assistant.services.authority_resolver import AuthorityResolver
from palwakf_mind_assistant.services.capability_registry import CapabilityRegistry
from palwakf_mind_assistant.services.change_proposal_service import ChangeProposalService
from palwakf_mind_assistant.services.conflict_detector import ConflictDetector
from palwakf_mind_assistant.services.context_compiler import ContextCompiler
from palwakf_mind_assistant.services.cost_intelligence import CostIntelligence
from palwakf_mind_assistant.services.decision_engine import DecisionEngine
from palwakf_mind_assistant.services.digital_twin_builder import ProjectDigitalTwinBuilder
from palwakf_mind_assistant.services.dry_run_engine import DryRunEngine
from palwakf_mind_assistant.services.engineering_advisor import EngineeringAdvisor
from palwakf_mind_assistant.services.evaluation_engine import EvaluationEngine
from palwakf_mind_assistant.services.execution_contract_service import ExecutionContractService
from palwakf_mind_assistant.services.execution_gateway import ExecutionGateway
from palwakf_mind_assistant.services.governed_development_lifecycle import (
    GovernedDevelopmentLifecycleService,
)
from palwakf_mind_assistant.services.health_service import HealthService
from palwakf_mind_assistant.services.impact_analyzer import ImpactAnalyzer
from palwakf_mind_assistant.services.mega_batch_core import envelope_for
from palwakf_mind_assistant.services.planning_engine import PlanningEngine
from palwakf_mind_assistant.services.portability_service import PortabilityService
from palwakf_mind_assistant.services.provider_evaluation_registry import ProviderEvaluationRegistry
from palwakf_mind_assistant.services.recovery_service import RecoveryService
from palwakf_mind_assistant.services.repository_analyzer import RepositoryAnalyzer
from palwakf_mind_assistant.services.security_engine import SecurityEngine
from palwakf_mind_assistant.services.skill_resolver import SkillResolver
from palwakf_mind_assistant.services.trust_engine import TrustEngine
from palwakf_mind_assistant.services.verification_engine import VerificationEngine
from palwakf_mind_assistant.services.watcher_service import WatcherService

PROJECT_NAMES = {
    "PAL_EYES": "بعيون فلسطينية / Pal Eyes",
    "PALWAKF_MIND_ASSISTANT": "PalWakf Mind Assistant",
}


class ProductService:
    """Shared application layer for Assistant + Dashboard + Knowledge surfaces.

    Deterministic mode is intentionally metadata-grounded and read-only. It does
    not impersonate live LLM reasoning and does not contain any write capability.
    """

    def __init__(
        self,
        resolver: AuthorityResolver,
        *,
        conflict_detector: ConflictDetector | None = None,
        provider_mode: str = "DETERMINISTIC_GROUNDED",
        operational_states: tuple[ProjectOperationalState, ...] = (),
        skills: tuple[SkillObject, ...] = (),
    ) -> None:
        self._resolver = resolver
        self._conflicts = conflict_detector or ConflictDetector()
        self._provider_mode = provider_mode
        self._trust = TrustEngine()
        self._skills = SkillResolver(skills)
        self._digital_twin = ProjectDigitalTwinBuilder(
            resolver, operational_states, conflict_detector=self._conflicts
        )
        self._context = ContextCompiler(
            resolver,
            conflict_detector=self._conflicts,
            trust_engine=self._trust,
            digital_twin_provider=self._digital_twin.build,
            skill_resolver=self._skills,
        )
        self._planning = PlanningEngine()
        self._impact = ImpactAnalyzer()
        self._decision = DecisionEngine()
        self._dry_run = DryRunEngine()
        self._verification = VerificationEngine()
        self._evaluation = EvaluationEngine()
        self._providers = ProviderEvaluationRegistry()
        self._capabilities = CapabilityRegistry()
        self._security = SecurityEngine()
        self._engineering = EngineeringAdvisor()
        self._repositories = RepositoryAnalyzer()
        self._changes = ChangeProposalService()
        self._execution_contracts = ExecutionContractService()
        self._execution = ExecutionGateway()
        self._agents = AgentOrchestrator()
        self._lifecycle = GovernedDevelopmentLifecycleService()
        self._watchers = WatcherService()
        self._health = HealthService()
        self._cost = CostIntelligence()
        self._recovery = RecoveryService()
        self._portability = PortabilityService()

    def list_skills(self) -> tuple[SkillObject, ...]:
        return self._skills.list_skills()

    def resolve_skills(self, request: SkillResolutionRequest) -> SkillResolutionResponse:
        return self._skills.resolve(request)

    def planning(self, request: PlanningRequest) -> PlanningResponse:
        context = self._context.compile(
            ContextRequest(
                message=request.goal,
                project_id=request.project_id,
                task_id=request.task_id,
            )
        )
        return self._planning.plan(
            request,
            source_refs=tuple(item.source.source_ref for item in context.authoritative_sources),
            skill_ids=tuple(item.skill_id for item in context.applicable_skills),
        )

    def impact(self, request: ImpactAnalysisRequest) -> ImpactAnalysisResponse:
        twin = self._digital_twin.build(request.project_id)
        deps = request.dependencies or twin.dependencies
        return self._impact.analyze(request.model_copy(update={"dependencies": deps}))

    def decision(self, project_id: str, title: str) -> tuple[DecisionRecord, HumanReviewPacket]:
        resolution = self._resolver.resolve_project(project_id)
        refs = tuple(source.source_ref for source in resolution.authoritative_sources)
        return self._decision.propose(project_id, title, source_refs=refs)

    def dry_run(self, project_id: str, actions: tuple[str, ...]) -> DryRunImpactPreview:
        return self._dry_run.preview(project_id, actions, ("SIMULATION_ONLY", "NO_MUTATION",))

    def verification(
        self,
        project_id: str,
        receipts: tuple[VerificationReceipt, ...],
    ) -> VerificationBundle:
        return self._verification.bundle(project_id, receipts)

    def evaluate(
        self,
        project_id: str,
        subject_id: str,
        bundle: VerificationBundle,
    ) -> EvaluationRecord:
        return self._evaluation.evaluate(project_id, subject_id, bundle)

    def provider_evaluations(self) -> tuple[ProviderEvaluation, ...]:
        return self._providers.list()

    def capabilities(self) -> tuple[ToolCapability, ...]:
        return self._capabilities.list()

    def capability_envelope(self, project_id: str) -> CapabilityEnvelope:
        return envelope_for(project_id)

    def security_inspect(self, text: str) -> tuple[PromptInjectionFinding, SecretBoundaryFinding]:
        return self._security.inspect(text)

    def engineering_advice(self, request: EngineeringAdviceRequest) -> EngineeringAdviceResponse:
        skills = self._skills.resolve(
            SkillResolutionRequest(
                message=request.request,
                project_id=request.project_id,
                task_id=request.task_id,
            )
        )
        return self._engineering.advise(
            request,
            skill_ids=tuple(
                selection.skill_id for selection in skills.selections
            ),
        )

    def repository_analysis(self, project_id: str) -> RepositoryAnalysis:
        return self._repositories.analyze(project_id)

    def change_proposal(self, project_id: str, paths: tuple[str, ...]) -> ChangeProposal:
        return self._changes.propose(self._repositories.analyze(project_id), paths)

    def execution_contract(self, project_id: str) -> AuthorizationContract:
        return self._execution_contracts.contract(project_id)

    def execute(self, request: ExecutionRequest) -> ExecutionReceipt:
        injection, secret = self._security.inspect(" ".join(request.requested_paths))
        if injection.detected or secret.detected:
            from palwakf_mind_assistant.domain.models import RollbackMetadata
            return ExecutionReceipt(
                execution_id="SECURITY-BLOCKED",
                project_id=request.project_id,
                status="DENIED",
                simulated=True,
                mutation_executed=False,
                authorized=False,
                blocked_reasons=("SECURITY_BOUNDARY",),
                rollback=RollbackMetadata(
                    strategy="NO_MUTATION_SECURITY_BLOCK",
                    rollback_available=True,
                ),
            )
        return self._execution.execute(request)

    def agent_plan(self, project_id: str) -> MultiAgentPlan:
        return self._agents.plan(project_id)

    def lifecycle(self, project_id: str) -> GovernedDevelopmentLifecycle:
        return self._lifecycle.simulate(project_id)

    def operations(self, project_id: str) -> OperationsSnapshot:
        return OperationsSnapshot(
            project_id=project_id,
            watchers=self._watchers.definitions(project_id),
            watcher_events=self._watchers.evaluate(project_id),
            connector_health=self._health.connector_health(),
            model_health=self._health.model_health(),
            costs=self._cost.observe(),
            recovery=self._recovery.drill(),
            portability=self._portability.export(),
        )

    def dashboard(self) -> DashboardSnapshot:
        project_ids = self._resolver.list_project_ids()
        summaries = tuple(self._summary(project_id) for project_id in project_ids)
        resolved = sum(s.authority_status is ResolutionStatus.RESOLVED for s in summaries)
        unknown = sum(s.authority_status is ResolutionStatus.UNKNOWN for s in summaries)
        partial = sum(s.authority_status is ResolutionStatus.PARTIAL for s in summaries)
        conflict_count = sum(s.conflict_count for s in summaries)
        alerts: list[str] = []
        if unknown:
            alerts.append(f"يوجد {unknown} مشروع بحالة سلطة UNKNOWN ويحتاج مراجعة بشرية.")
        if partial:
            alerts.append(f"يوجد {partial} مشروع بحالة PARTIAL؛ لا تُعرض كحقيقة مكتملة.")
        if conflict_count:
            alerts.append(f"يوجد {conflict_count} تعارض/مؤشر هيكلي يحتاج المراجعة.")
        connector = self._resolver.connector_health()
        if connector.state != "READY":
            alerts.append(f"حالة موصل المعرفة: {connector.state} — {connector.detail}")
        alerts.append("وضع المعرفة READ_ONLY — لا توجد كتابة إلى Workspace Drive.")
        return DashboardSnapshot(
            project_id="PALWAKF_MIND_ASSISTANT",
            product_name="PalWakf Mind Assistant",
            mutation_mode="READ_ONLY",
            sovereign_authority="PALWAKF_WORKSPACE_DRIVE",
            provider_mode=self._provider_mode,
            connector=connector,
            projects=summaries,
            counts={
                "total": len(summaries),
                "resolved": resolved,
                "partial": partial,
                "unknown": unknown,
                "conflicts": conflict_count,
            },
            alerts=tuple(alerts),
        )

    def project_mind(self, project_id: str) -> ProjectMindSnapshot:
        normalized = project_id.strip().upper()
        resolution = self._resolver.resolve_project(normalized)
        raw_sources = self._resolver.list_project_sources(normalized)
        conflicts = self._conflicts.detect(normalized, raw_sources)
        current = self._current_state(resolution.authoritative_sources)
        return ProjectMindSnapshot(
            project_id=normalized,
            display_name=PROJECT_NAMES.get(normalized, normalized),
            authority_status=resolution.status,
            knowledge_health=self._knowledge_health(resolution.status, conflicts),
            current_state=current,
            authoritative_sources=resolution.authoritative_sources,
            superseded_sources=resolution.superseded_sources,
            conflicts=conflicts,
            unknown_reasons=resolution.unknown_reasons,
            digital_twin=self._digital_twin.build(normalized),
        )

    def digital_twin(self, project_id: str) -> ProjectDigitalTwinSnapshot:
        return self._digital_twin.build(project_id)

    def compile_context(self, request: ContextRequest):
        return self._context.compile(request)

    def conflicts(self, project_id: str):
        normalized = project_id.strip().upper()
        return self._conflicts.detect(
            normalized,
            self._resolver.list_project_sources(normalized),
        )

    def search(self, query: str, project_id: str | None = None) -> KnowledgeSearchResponse:
        clean_query = re.sub(r"\s+", " ", query.strip())
        if not clean_query:
            return KnowledgeSearchResponse(query="", project_id=project_id, hits=(), total=0)

        needle = clean_query.casefold()
        project_ids = (
            (project_id.strip().upper(),)
            if project_id and project_id.strip()
            else self._resolver.list_project_ids()
        )
        hits: list[KnowledgeSearchHit] = []
        for current_project in project_ids:
            for source in self._resolver.list_project_sources(current_project):
                fields = {
                    "title": source.title,
                    "source_ref": source.source_ref,
                    "canonical_location": source.canonical_location,
                    "authority_type": source.authority_type.value,
                    "lifecycle_status": source.lifecycle_status.value,
                }
                matched = tuple(
                    key for key, value in fields.items() if needle in str(value).casefold()
                )
                if matched:
                    hits.append(
                        KnowledgeSearchHit(
                            project_id=current_project,
                            title=source.title,
                            authority_type=source.authority_type,
                            lifecycle_status=source.lifecycle_status,
                            source_ref=source.source_ref,
                            canonical_location=source.canonical_location,
                            matched_on=matched,
                            provenance=self._trust.provenance_for(source),
                        )
                    )
        hits.sort(
            key=lambda item: (
                item.project_id,
                item.authority_type.value,
                item.lifecycle_status.value,
                item.title,
            )
        )
        return KnowledgeSearchResponse(
            query=clean_query,
            project_id=project_id.strip().upper() if project_id else None,
            hits=tuple(hits),
            total=len(hits),
        )

    def ask(self, question: AssistantQuestion) -> AssistantAnswer:
        context = self._context.compile(
            ContextRequest(
                message=question.message,
                project_id=question.project_id,
                task_id=question.task_id,
            )
        )
        target = context.project_id
        answer_id = hashlib.sha256(question.message.encode("utf-8")).hexdigest()[:12]
        if not target:
            return AssistantAnswer(
                answer_id=answer_id,
                project_id=None,
                status="NEEDS_PROJECT_CONTEXT",
                answer_kind="CONTEXT_REQUIRED",
                answer_ar=(
                    "لم أستطع تحديد المشروع المقصود بصورة حتمية. اختر المشروع أو اذكر Project ID؛ "
                    "لن أحوّل الغموض إلى حقيقة."
                ),
                confidence="UNKNOWN",
                provider_mode=self._provider_mode,
                unknown_reasons=context.unknown_reasons,
                context=context,
            )

        resolution = self._resolver.resolve_project(target)
        raw_sources = self._resolver.list_project_sources(target)
        conflicts = self._conflicts.detect(target, raw_sources)
        blocking = tuple(c for c in conflicts if c.severity is ConflictSeverity.BLOCKING)
        answer_kind = context.intent

        if blocking:
            blocking_refs = {ref for conflict in blocking for ref in conflict.source_refs}
            citations = self._citations(
                raw_sources,
                blocking_refs=blocking_refs,
            )
            return AssistantAnswer(
                answer_id=answer_id,
                project_id=target,
                status="CONFLICT_REVIEW_REQUIRED",
                answer_kind="CONFLICT",
                answer_ar=(
                    f"وجدت مؤشرات سلطة متعارضة في {PROJECT_NAMES.get(target, target)}. "
                    "لن أختار Current تلقائيًا؛ يلزم حسم بشري أو Supersession صريح."
                ),
                confidence="REVIEW_REQUIRED",
                provider_mode=self._provider_mode,
                citations=citations,
                unknown_reasons=context.unknown_reasons,
                context=context,
            )

        if resolution.status is ResolutionStatus.UNKNOWN:
            return AssistantAnswer(
                answer_id=answer_id,
                project_id=target,
                status="UNKNOWN_FAIL_CLOSED",
                answer_kind=answer_kind,
                answer_ar=(
                    f"لا توجد لدي حاليًا سلطة معرفية كافية لإعطاء جواب معتمد عن {target}. "
                    "أبقي النتيجة UNKNOWN حتى تُستعاد/تُراجع المصادر السيادية."
                ),
                confidence="UNKNOWN",
                provider_mode=self._provider_mode,
                unknown_reasons=context.unknown_reasons,
                context=context,
            )

        citations = self._citations(resolution.authoritative_sources)
        display_name = PROJECT_NAMES.get(target, target)
        current = self._current_state(resolution.authoritative_sources)

        if answer_kind == "SOURCES":
            answer = (
                f"لدى {display_name} {len(citations)} مصدر/مرجع سلطة حالي "
                "قابل للعرض في هذا السياق. "
                "أعرض المرجع والنوع والحالة والثقة فقط، ولا أنقل "
                "المحتوى المقبول إلى مخزن سيادي ثانٍ."
            )
        elif answer_kind == "CONFLICT":
            if conflicts:
                answer = (
                    f"وجدت {len(conflicts)} مؤشرًا هيكليًا يحتاج المراجعة في {display_name}. "
                    "هذه مؤشرات metadata وليست إثباتًا آليًا لتعارض دلالي."
                )
            else:
                answer = (
                    f"لم يكتشف الفاحص الهيكلي الحالي تعارض سلطة مثبتًا في {display_name}. "
                    "هذا لا يساوي إثبات غياب أي تعارض دلالي في محتوى الوثائق."
                )
        elif answer_kind == "TASK_CONTEXT":
            answer = (
                f"تم تجميع سياق موثوق للمهمة ضمن {display_name}. "
                f"حالة الثقة {context.trust_state.value} "
                f"وحالة السلطة {context.authority_status.value}. "
                "لا تُستنتج مهمة أو صلاحية غير موجودة في المصادر."
            )
        elif current:
            answer = (
                f"حالة {display_name} قابلة للحسم من المصادر الحالية. مرجع الحالة السيادي هو "
                f"«{current.title}». حزمة السياق صنفت الثقة {context.trust_state.value}. "
                "هذه إجابة قراءة فقط؛ لا ينتج عنها أي تعديل في Drive أو GitHub."
            )
        else:
            answer = (
                f"تم العثور على مصادر معتمدة لـ{display_name}، لكن لا يوجد "
                "PROJECT_CURRENT_STATE/CURRENT وحيد يمكن تقديمه كحالة نهائية. "
                "لذلك لا أستنتج Current State من مصادر أخرى."
            )

        return AssistantAnswer(
            answer_id=answer_id,
            project_id=target,
            status="GROUNDED_READ_ONLY",
            answer_kind=answer_kind,
            answer_ar=answer,
            confidence=f"{context.trust_state.value}_FROM_AVAILABLE_AUTHORITY_METADATA",
            provider_mode=self._provider_mode,
            citations=citations,
            unknown_reasons=context.unknown_reasons,
            context=context,
        )

    def _summary(self, project_id: str) -> ProjectSummary:
        mind = self.project_mind(project_id)
        return ProjectSummary(
            project_id=mind.project_id,
            display_name=mind.display_name,
            status="ACTIVE" if mind.authority_status is not ResolutionStatus.UNKNOWN else "UNKNOWN",
            authority_status=mind.authority_status,
            knowledge_health=mind.knowledge_health,
            current_state_title=mind.current_state.title if mind.current_state else None,
            current_state_ref=mind.current_state.source_ref if mind.current_state else None,
            source_count=len(mind.authoritative_sources),
            conflict_count=len(mind.conflicts),
            unknown_reasons=mind.unknown_reasons,
        )

    @staticmethod
    def _current_state(sources: tuple[SourceRef, ...]) -> SourceRef | None:
        return next(
            (
                source
                for source in sources
                if source.authority_type is AuthorityType.PROJECT_CURRENT_STATE
                and source.lifecycle_status is LifecycleStatus.CURRENT
            ),
            None,
        )

    @staticmethod
    def _knowledge_health(status: ResolutionStatus, conflicts) -> str:
        if any(c.severity is ConflictSeverity.BLOCKING for c in conflicts):
            return "CONFLICT_REVIEW_REQUIRED"
        if status is ResolutionStatus.UNKNOWN:
            return "UNKNOWN"
        if status is ResolutionStatus.PARTIAL:
            return "PARTIAL_REVIEW_REQUIRED"
        if conflicts:
            return "REVIEW_REQUIRED"
        return "HEALTHY"

    def _citations(
        self, sources, *, blocking_refs: set[str] | None = None
    ) -> tuple[AssistantCitation, ...]:
        blocked = blocking_refs or set()
        return tuple(
            AssistantCitation(
                title=source.title,
                authority_type=source.authority_type,
                lifecycle_status=source.lifecycle_status,
                source_ref=source.source_ref,
                canonical_location=source.canonical_location,
                provenance=self._trust.provenance_for(
                    source, conflicted=source.source_ref in blocked
                ),
            )
            for source in sources
        )

    @staticmethod
    def _infer_project(message: str) -> str | None:
        normalized = re.sub(r"\s+", " ", message.strip()).lower()
        if "pal eyes" in normalized or "pal_eyes" in normalized or "بعيون فلسطينية" in normalized:
            return "PAL_EYES"
        if "mind assistant" in normalized or "palwakf_mind_assistant" in normalized:
            return "PALWAKF_MIND_ASSISTANT"
        return None

    @staticmethod
    def _intent(message: str) -> str:
        normalized = message.casefold()
        if any(term in normalized for term in ("تعارض", "تعارضات", "conflict")):
            return "CONFLICT"
        if any(term in normalized for term in ("مصدر", "مصادر", "source", "sources")):
            return "SOURCES"
        return "CURRENT_STATE"
