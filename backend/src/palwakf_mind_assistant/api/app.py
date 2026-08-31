from __future__ import annotations

import os
import re
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import Body, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from palwakf_mind_assistant.adapters.drive_readonly import (
    DriveReadOnlyPort,
    GoogleDriveRestReadOnlyAdapter,
    InMemoryDriveReadOnlyAdapter,
    UnavailableDriveReadOnlyAdapter,
)
from palwakf_mind_assistant.adapters.fixture_loader import load_source_fixture
from palwakf_mind_assistant.adapters.project_state_fixture import load_project_state_fixture
from palwakf_mind_assistant.adapters.skill_fixture import load_skill_fixture
from palwakf_mind_assistant.domain.models import (
    AssistantAnswer,
    AssistantQuestion,
    AuthorizationContract,
    CapabilityEnvelope,
    ChangeProposal,
    ConflictCandidate,
    ConnectorHealth,
    ContextRequest,
    DashboardSnapshot,
    DryRunImpactPreview,
    EngineeringAdviceRequest,
    EngineeringAdviceResponse,
    EvaluationRecord,
    ExecutionReceipt,
    ExecutionRequest,
    GovernedDevelopmentLifecycle,
    ImpactAnalysisRequest,
    ImpactAnalysisResponse,
    KnowledgeSearchResponse,
    MinimalTrustedContextPackage,
    MultiAgentPlan,
    OperationsSnapshot,
    PlanningRequest,
    PlanningResponse,
    ProjectDigitalTwinSnapshot,
    ProjectMindSnapshot,
    ProjectOperationalState,
    ProviderEvaluation,
    RepositoryAnalysis,
    SkillObject,
    SkillResolutionRequest,
    SkillResolutionResponse,
    SourceRef,
    ToolCapability,
    VerificationBundle,
    VerificationReceipt,
)
from palwakf_mind_assistant.services.authority_resolver import AuthorityResolver
from palwakf_mind_assistant.services.product_service import ProductService

FIXTURE = Path(__file__).resolve().parents[3] / "fixtures" / "authority_catalog.json"
SKILL_FIXTURE = Path(__file__).resolve().parents[3] / "fixtures" / "skill_catalog.json"
PROJECT_STATE_FIXTURE = (
    Path(__file__).resolve().parents[3] / "fixtures" / "project_state_catalog.json"
)
_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,96}$")
_LOCAL_ORIGIN_RE = r"^http://(?:127\.0\.0\.1|localhost)(?::\d+)?$"


def _build_drive_adapter(
    sources: tuple[SourceRef, ...],
    *,
    source_mode: str,
    access_token: str | None,
) -> DriveReadOnlyPort:
    normalized = source_mode.strip().lower()
    if normalized == "drive_rest":
        if not access_token:
            return UnavailableDriveReadOnlyAdapter(sources)
        return GoogleDriveRestReadOnlyAdapter(sources, bearer_token=access_token)
    return InMemoryDriveReadOnlyAdapter(sources)


def create_app(
    *,
    sources: tuple[SourceRef, ...] | None = None,
    source_mode: str | None = None,
    access_token: str | None = None,
    operational_states: tuple[ProjectOperationalState, ...] | None = None,
    skills: tuple[SkillObject, ...] | None = None,
) -> FastAPI:
    catalog = sources if sources is not None else load_source_fixture(FIXTURE)
    state_catalog = (
        operational_states
        if operational_states is not None
        else load_project_state_fixture(PROJECT_STATE_FIXTURE)
    )
    skill_catalog = skills if skills is not None else load_skill_fixture(SKILL_FIXTURE)
    configured_source_mode = source_mode or os.getenv("MIND_SOURCE_MODE", "fixture")
    configured_token = (
        access_token if access_token is not None else os.getenv("MIND_GOOGLE_DRIVE_ACCESS_TOKEN")
    )
    provider_mode = os.getenv("MIND_PROVIDER_MODE", "DETERMINISTIC_GROUNDED")
    adapter = _build_drive_adapter(
        catalog,
        source_mode=configured_source_mode,
        access_token=configured_token,
    )
    resolver = AuthorityResolver(adapter)
    product = ProductService(
        resolver,
        provider_mode=provider_mode,
        operational_states=state_catalog,
        skills=skill_catalog,
    )

    application = FastAPI(
        title="PalWakf Mind Assistant",
        version="1.5.0-final-integrated-mega-batch-candidate",
    )
    allowed_origins = tuple(
        origin.strip()
        for origin in os.getenv("MIND_ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(allowed_origins),
        allow_origin_regex=_LOCAL_ORIGIN_RE,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    @application.middleware("http")
    async def security_headers(request: Request, call_next):
        incoming = request.headers.get("X-Request-ID", "")
        request_id = incoming if _REQUEST_ID_RE.fullmatch(incoming) else uuid.uuid4().hex
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        return response

    @application.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "project_id": "PALWAKF_MIND_ASSISTANT",
            "mutation_mode": "READ_ONLY",
                        "product_surface": (
                "ASSISTANT_DASHBOARD_PROJECT_MIND_DIGITAL_TWIN_SKILLS_EXPLORER_"
                "PLANNING_DECISIONS_VERIFICATION_SECURITY_ENGINEERING_REPOSITORY_"
                "EXECUTION_AGENTS_LIFECYCLE_OPERATIONS"
            ),
            "provider_mode": provider_mode,
            "source_mode": configured_source_mode.upper(),
        }

    @application.get("/v1/authority/projects/{project_id}")
    def resolve_project(project_id: str):
        return resolver.resolve_project(project_id)

    @application.get("/v1/dashboard", response_model=DashboardSnapshot)
    def dashboard() -> DashboardSnapshot:
        return product.dashboard()

    @application.get("/v1/projects/{project_id}/mind", response_model=ProjectMindSnapshot)
    def project_mind(project_id: str) -> ProjectMindSnapshot:
        return product.project_mind(project_id)

    @application.get(
        "/v1/projects/{project_id}/digital-twin", response_model=ProjectDigitalTwinSnapshot
    )
    def project_digital_twin(project_id: str) -> ProjectDigitalTwinSnapshot:
        return product.digital_twin(project_id)

    @application.post("/v1/context/compile", response_model=MinimalTrustedContextPackage)
    def compile_context(request: ContextRequest) -> MinimalTrustedContextPackage:
        return product.compile_context(request)

    @application.get("/v1/knowledge/search", response_model=KnowledgeSearchResponse)
    def knowledge_search(
        q: str = Query(min_length=1, max_length=300),
        project_id: str | None = Query(default=None, max_length=120),
    ) -> KnowledgeSearchResponse:
        return product.search(q, project_id)

    @application.get("/v1/conflicts/{project_id}", response_model=tuple[ConflictCandidate, ...])
    def conflicts(project_id: str):
        return product.conflicts(project_id)


    @application.get("/v1/skills", response_model=tuple[SkillObject, ...])
    def skills_registry() -> tuple[SkillObject, ...]:
        return product.list_skills()

    @application.post("/v1/skills/resolve", response_model=SkillResolutionResponse)
    def resolve_skills(request: SkillResolutionRequest) -> SkillResolutionResponse:
        return product.resolve_skills(request)

    @application.post("/v1/planning", response_model=PlanningResponse)
    def planning(request: PlanningRequest) -> PlanningResponse:
        return product.planning(request)

    @application.post("/v1/impact", response_model=ImpactAnalysisResponse)
    def impact(request: ImpactAnalysisRequest) -> ImpactAnalysisResponse:
        return product.impact(request)

    @application.post("/v1/decisions")
    def decisions(payload: Annotated[dict, Body()]) -> dict:
        record, review = product.decision(
            str(payload.get("project_id", "")),
            str(payload.get("title", "Governed decision")),
        )
        return {"decision": record, "review": review, "mutation_mode": "READ_ONLY"}

    @application.post("/v1/dry-run", response_model=DryRunImpactPreview)
    def dry_run(payload: Annotated[dict, Body()]) -> DryRunImpactPreview:
        return product.dry_run(
            str(payload.get("project_id", "")),
            tuple(str(item) for item in payload.get("actions", [])),
        )

    @application.post("/v1/verification", response_model=VerificationBundle)
    def verification(payload: Annotated[dict, Body()]) -> VerificationBundle:
        receipts = tuple(
            VerificationReceipt.model_validate(item)
            for item in payload.get("receipts", [])
        )
        return product.verification(str(payload.get("project_id", "")), receipts)

    @application.post("/v1/evaluations", response_model=EvaluationRecord)
    def evaluations(payload: Annotated[dict, Body()]) -> EvaluationRecord:
        bundle = VerificationBundle.model_validate(payload.get("bundle", {}))
        return product.evaluate(
            str(payload.get("project_id", "")),
            str(payload.get("subject_id", "")),
            bundle,
        )

    @application.get("/v1/evaluations/providers", response_model=tuple[ProviderEvaluation, ...])
    def provider_evaluations() -> tuple[ProviderEvaluation, ...]:
        return product.provider_evaluations()

    @application.get("/v1/capabilities", response_model=tuple[ToolCapability, ...])
    def capabilities() -> tuple[ToolCapability, ...]:
        return product.capabilities()

    @application.get("/v1/capabilities/{project_id}/envelope", response_model=CapabilityEnvelope)
    def capability_envelope(project_id: str) -> CapabilityEnvelope:
        return product.capability_envelope(project_id)

    @application.post("/v1/security/inspect")
    def security_inspect(payload: Annotated[dict, Body()]) -> dict:
        injection, secret = product.security_inspect(str(payload.get("text", "")))
        return {
            "prompt_injection": injection,
            "secret_boundary": secret,
            "mutation_mode": "READ_ONLY",
        }

    @application.post("/v1/engineering/advice", response_model=EngineeringAdviceResponse)
    def engineering_advice(request: EngineeringAdviceRequest) -> EngineeringAdviceResponse:
        return product.engineering_advice(request)

    @application.get("/v1/repositories/{project_id}", response_model=RepositoryAnalysis)
    def repository_analysis(project_id: str) -> RepositoryAnalysis:
        return product.repository_analysis(project_id)

    @application.post(
        "/v1/repositories/{project_id}/change-proposal",
        response_model=ChangeProposal,
    )
    def change_proposal(
        project_id: str,
        payload: Annotated[dict, Body()],
    ) -> ChangeProposal:
        return product.change_proposal(
            project_id,
            tuple(str(item) for item in payload.get("paths", [])),
        )

    @application.get("/v1/execution/{project_id}/contract", response_model=AuthorizationContract)
    def execution_contract(project_id: str) -> AuthorizationContract:
        return product.execution_contract(project_id)

    @application.post("/v1/execution/simulate", response_model=ExecutionReceipt)
    def execution_simulate(request: ExecutionRequest) -> ExecutionReceipt:
        return product.execute(request)

    @application.get("/v1/agents/{project_id}", response_model=MultiAgentPlan)
    def agent_plan(project_id: str) -> MultiAgentPlan:
        return product.agent_plan(project_id)

    @application.get("/v1/lifecycle/{project_id}", response_model=GovernedDevelopmentLifecycle)
    def lifecycle(project_id: str) -> GovernedDevelopmentLifecycle:
        return product.lifecycle(project_id)

    @application.get("/v1/operations/{project_id}", response_model=OperationsSnapshot)
    def operations(project_id: str) -> OperationsSnapshot:
        return product.operations(project_id)

    @application.get("/v1/system/connector", response_model=ConnectorHealth)
    def connector_health() -> ConnectorHealth:
        return resolver.connector_health()

    @application.post("/v1/assistant/ask", response_model=AssistantAnswer)
    def ask(question: AssistantQuestion) -> AssistantAnswer:
        return product.ask(question)

    return application


app = create_app()
