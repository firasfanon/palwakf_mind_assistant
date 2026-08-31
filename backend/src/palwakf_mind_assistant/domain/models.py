from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AuthorityType(StrEnum):
    PROJECT_CURRENT_STATE = "PROJECT_CURRENT_STATE"
    PORTFOLIO_REGISTRY = "PORTFOLIO_REGISTRY"
    DOCUMENT_AUTHORITY_INDEX = "DOCUMENT_AUTHORITY_INDEX"
    PROJECT_GOVERNANCE = "PROJECT_GOVERNANCE"
    DECISION = "DECISION"
    HANDOFF = "HANDOFF"
    EVIDENCE = "EVIDENCE"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class LifecycleStatus(StrEnum):
    CURRENT = "CURRENT"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    HISTORICAL = "HISTORICAL"
    UNKNOWN = "UNKNOWN"


class ResolutionStatus(StrEnum):
    RESOLVED = "RESOLVED"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"


class ConnectorState(StrEnum):
    READY = "READY"
    DEGRADED = "DEGRADED"
    UNKNOWN = "UNKNOWN"


class ConflictSeverity(StrEnum):
    BLOCKING = "BLOCKING"
    REVIEW = "REVIEW"
    INFO = "INFO"


class ClaimState(StrEnum):
    VERIFIED = "VERIFIED"
    INFERRED = "INFERRED"
    STALE = "STALE"
    CONFLICTED = "CONFLICTED"
    UNKNOWN = "UNKNOWN"
    UNAVAILABLE = "UNAVAILABLE"


class FreshnessState(StrEnum):
    CURRENT = "CURRENT"
    AGING = "AGING"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class SourceRef(BaseModel):
    owner_project_id: str
    authority_type: AuthorityType
    lifecycle_status: LifecycleStatus
    canonical_location: str
    source_id: str
    source_ref: str
    title: str
    supersedes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProjectAuthorityResolution(BaseModel):
    project_id: str
    status: ResolutionStatus
    authoritative_sources: tuple[SourceRef, ...] = ()
    superseded_sources: tuple[SourceRef, ...] = ()
    unknown_reasons: tuple[str, ...] = ()


class ConnectorHealth(BaseModel):
    connector: str
    mode: str
    state: ConnectorState
    mutation_mode: str = "READ_ONLY"
    source_count: int = 0
    writes_enabled: bool = False
    detail: str = ""


class ConflictCandidate(BaseModel):
    conflict_id: str
    project_id: str
    conflict_type: str
    severity: ConflictSeverity
    title: str
    detail: str
    source_refs: tuple[str, ...] = ()
    requires_human_review: bool = True


class ClaimProvenance(BaseModel):
    source_ref: str
    authority: AuthorityType
    lifecycle_status: LifecycleStatus
    version: str
    observed_at: datetime
    confidence: str
    freshness: FreshnessState
    supersession: str
    scope: str
    claim_state: ClaimState
    reason: str


class TrustedContextSource(BaseModel):
    source: SourceRef
    provenance: ClaimProvenance


class ContextRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    project_id: str | None = Field(default=None, max_length=120)
    task_id: str | None = Field(default=None, max_length=180)


class MinimalTrustedContextPackage(BaseModel):
    context_id: str
    intent: str
    project_id: str | None
    task_id: str | None
    authority_status: ResolutionStatus
    trust_state: ClaimState
    authoritative_sources: tuple[TrustedContextSource, ...] = ()
    superseded_sources: tuple[TrustedContextSource, ...] = ()
    unknown_reasons: tuple[str, ...] = ()
    decisions: tuple[str, ...] = ()
    known_lessons: tuple[str, ...] = ()
    applicable_skills: tuple[SkillSelection, ...] = ()
    lesson_regressions: tuple[LessonRegressionFinding, ...] = ()
    dependencies: tuple[str, ...] = ()
    planning_refs: tuple[str, ...] = ()
    decision_refs: tuple[str, ...] = ()
    capability_refs: tuple[str, ...] = ()
    verification_refs: tuple[str, ...] = ()
    security_findings: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    project_twin_ref: str | None = None
    project_twin_status: str | None = None
    project_twin_generated_at: datetime | None = None
    compiled_at: datetime
    mutation_mode: str = "READ_ONLY"


class ProjectSummary(BaseModel):
    project_id: str
    display_name: str
    status: str
    authority_status: ResolutionStatus
    knowledge_health: str
    current_state_title: str | None = None
    current_state_ref: str | None = None
    source_count: int = 0
    conflict_count: int = 0
    unknown_reasons: tuple[str, ...] = ()


class DashboardSnapshot(BaseModel):
    project_id: str
    product_name: str
    mutation_mode: str
    sovereign_authority: str
    provider_mode: str
    connector: ConnectorHealth
    projects: tuple[ProjectSummary, ...]
    counts: dict[str, int]
    alerts: tuple[str, ...]


class ProjectMindSnapshot(BaseModel):
    project_id: str
    display_name: str
    authority_status: ResolutionStatus
    knowledge_health: str
    current_state: SourceRef | None = None
    authoritative_sources: tuple[SourceRef, ...] = ()
    superseded_sources: tuple[SourceRef, ...] = ()
    conflicts: tuple[ConflictCandidate, ...] = ()
    unknown_reasons: tuple[str, ...] = ()
    digital_twin: ProjectDigitalTwinSnapshot | None = None
    mutation_mode: str = "READ_ONLY"


class KnowledgeSearchHit(BaseModel):
    project_id: str
    title: str
    authority_type: AuthorityType
    lifecycle_status: LifecycleStatus
    source_ref: str
    canonical_location: str
    matched_on: tuple[str, ...] = ()
    provenance: ClaimProvenance | None = None


class KnowledgeSearchResponse(BaseModel):
    query: str
    project_id: str | None = None
    hits: tuple[KnowledgeSearchHit, ...] = ()
    total: int = 0
    mutation_mode: str = "READ_ONLY"


class AssistantQuestion(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    project_id: str | None = Field(default=None, max_length=120)
    task_id: str | None = Field(default=None, max_length=180)


class AssistantCitation(BaseModel):
    title: str
    authority_type: AuthorityType
    lifecycle_status: LifecycleStatus
    source_ref: str
    canonical_location: str
    provenance: ClaimProvenance | None = None


class AssistantAnswer(BaseModel):
    answer_id: str
    project_id: str | None
    status: str
    answer_kind: str = "GENERAL"
    answer_ar: str
    confidence: str
    grounding_scope: str = "AUTHORITY_METADATA_ONLY"
    provider_mode: str = "DETERMINISTIC_GROUNDED"
    citations: tuple[AssistantCitation, ...] = ()
    unknown_reasons: tuple[str, ...] = ()
    context: MinimalTrustedContextPackage | None = None
    mutation_mode: str = "READ_ONLY"


class SkillStatus(StrEnum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    DEPRECATED = "DEPRECATED"
    UNKNOWN = "UNKNOWN"


class SkillLevel(StrEnum):
    GLOBAL = "GLOBAL"
    DOMAIN = "DOMAIN"
    PROJECT = "PROJECT"
    TASK_SPECIFIC = "TASK_SPECIFIC"


class SkillObject(BaseModel):
    skill_id: str
    version: str
    status: SkillStatus
    owner_scope: str
    level: SkillLevel
    applies_to: tuple[str, ...] = ()
    triggers: tuple[str, ...] = ()
    preconditions: tuple[str, ...] = ()
    required_inputs: tuple[str, ...] = ()
    authorized_operations: tuple[str, ...] = ()
    forbidden_operations: tuple[str, ...] = ()
    execution_steps: tuple[str, ...] = ()
    fail_closed_conditions: tuple[str, ...] = ()
    expected_outputs: tuple[str, ...] = ()
    evidence_requirements: tuple[str, ...] = ()
    regression_tests: tuple[str, ...] = ()
    known_failures: tuple[str, ...] = ()
    supersedes: tuple[str, ...] = ()
    last_validated_at: datetime
    provenance_ref: str


class SkillSelection(BaseModel):
    skill_id: str
    version: str
    level: SkillLevel
    applicable: bool
    score: int
    reasons: tuple[str, ...] = ()
    unmet_preconditions: tuple[str, ...] = ()
    provenance_ref: str
    execution_authorized: bool = False


class LessonRegressionFinding(BaseModel):
    lesson_id: str
    status: str
    detail: str
    related_skill_id: str | None = None


class SkillResolutionRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    project_id: str | None = Field(default=None, max_length=120)
    task_id: str | None = Field(default=None, max_length=180)
    evidence_tags: tuple[str, ...] = ()


class SkillResolutionResponse(BaseModel):
    project_id: str | None
    task_id: str | None
    selections: tuple[SkillSelection, ...] = ()
    rejected: tuple[SkillSelection, ...] = ()
    lesson_regressions: tuple[LessonRegressionFinding, ...] = ()
    registry_source_mode: str = "FIXTURE_DERIVED"
    mutation_mode: str = "READ_ONLY"
    autonomous_execution: bool = False


class DigitalTwinStatus(StrEnum):
    RESOLVED = "RESOLVED"
    PARTIAL = "PARTIAL"
    STALE = "STALE"
    CONFLICTED = "CONFLICTED"
    UNKNOWN = "UNKNOWN"
    UNAVAILABLE = "UNAVAILABLE"


class DriftSeverity(StrEnum):
    BLOCKING = "BLOCKING"
    REVIEW = "REVIEW"
    INFO = "INFO"


class ProjectOperationalState(BaseModel):
    project_id: str
    display_name: str
    source_mode: str = "FIXTURE_DERIVED"
    observed_at: datetime
    repository: str | None = None
    default_branch: str | None = None
    head_sha: str | None = None
    active_branch: str | None = None
    task_id: str | None = None
    task_status: str = "UNKNOWN"
    baseline_ref: str | None = None
    dependencies: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    production_readiness_level: str = "UNKNOWN"
    production_readiness_status: str = "UNKNOWN"
    next_safe_action: str
    current_state_ref: str | None = None
    source_refs: dict[str, str] = Field(default_factory=dict)


class DriftIndicator(BaseModel):
    drift_code: str
    severity: DriftSeverity
    state: ClaimState
    explanation: str
    source_refs: tuple[str, ...] = ()
    detected_at: datetime


class ProjectDigitalTwinSnapshot(BaseModel):
    twin_id: str
    twin_version: str = "0.5.0"
    project_id: str
    display_name: str
    status: DigitalTwinStatus
    authority_status: ResolutionStatus
    trust_state: ClaimState
    derived_view: bool = True
    canonical_authority: bool = False
    rebuildable: bool = True
    source_mode: str
    current_state_ref: str | None = None
    repository: str | None = None
    default_branch: str | None = None
    head_sha: str | None = None
    active_branch: str | None = None
    task_id: str | None = None
    task_status: str = "UNKNOWN"
    baseline_ref: str | None = None
    dependencies: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    production_readiness_level: str = "UNKNOWN"
    production_readiness_status: str = "UNKNOWN"
    drift_indicators: tuple[DriftIndicator, ...] = ()
    unknown_reasons: tuple[str, ...] = ()
    next_safe_action: str
    next_safe_action_source_ref: str | None = None
    source_refs: tuple[str, ...] = ()
    observed_at: datetime
    generated_at: datetime
    rebuild_receipt: str
    mutation_mode: str = "READ_ONLY"

class PlanStatus(StrEnum):
    DRAFT = "DRAFT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    READY_FOR_SIMULATION = "READY_FOR_SIMULATION"
    BLOCKED = "BLOCKED"


class PlanNodeType(StrEnum):
    CONTEXT = "CONTEXT"
    ACTION = "ACTION"
    DECISION = "DECISION"
    VERIFICATION = "VERIFICATION"
    CHECKPOINT = "CHECKPOINT"


class PlanningNode(BaseModel):
    node_id: str
    node_type: PlanNodeType
    title: str
    status: str
    source_refs: tuple[str, ...] = ()
    requires_approval: bool = False


class PlanningEdge(BaseModel):
    from_node: str
    to_node: str
    relation: str


class PlanningGraph(BaseModel):
    plan_id: str
    project_id: str
    status: PlanStatus
    nodes: tuple[PlanningNode, ...]
    edges: tuple[PlanningEdge, ...]
    risks: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    derived_view: bool = True
    mutation_mode: str = "READ_ONLY"


class PlanningRequest(BaseModel):
    project_id: str
    goal: str = Field(min_length=1, max_length=1000)
    task_id: str | None = None


class PlanningResponse(BaseModel):
    graph: PlanningGraph
    applicable_skill_ids: tuple[str, ...] = ()
    unknown_reasons: tuple[str, ...] = ()
    approval_required: bool = True


class ImpactSeverity(StrEnum):
    BLOCKING = "BLOCKING"
    REVIEW = "REVIEW"
    INFORMATIONAL = "INFORMATIONAL"
    UNKNOWN = "UNKNOWN"


class DependencyImpact(BaseModel):
    dependency: str
    severity: ImpactSeverity
    classification: str
    detail: str
    source_refs: tuple[str, ...] = ()


class CrossProjectImpact(BaseModel):
    project_id: str
    affected_project_id: str
    severity: ImpactSeverity
    detail: str
    blocking: bool = False


class ImpactAnalysisRequest(BaseModel):
    project_id: str
    proposed_change: str
    dependencies: tuple[str, ...] = ()


class ImpactAnalysisResponse(BaseModel):
    project_id: str
    impacts: tuple[DependencyImpact, ...] = ()
    cross_project_impacts: tuple[CrossProjectImpact, ...] = ()
    overall_severity: ImpactSeverity
    unknown_reasons: tuple[str, ...] = ()
    mutation_mode: str = "READ_ONLY"


class DecisionStatus(StrEnum):
    PROPOSED = "PROPOSED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class ApprovalState(StrEnum):
    REQUIRED = "REQUIRED"
    NOT_REQUIRED = "NOT_REQUIRED"
    APPROVED = "APPROVED"
    DENIED = "DENIED"


class DecisionAlternative(BaseModel):
    alternative_id: str
    title: str
    benefits: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()


class DecisionLineage(BaseModel):
    parent_decision_id: str | None = None
    supersedes: tuple[str, ...] = ()
    superseded_by: str | None = None


class DecisionRecord(BaseModel):
    decision_id: str
    project_id: str
    title: str
    status: DecisionStatus
    selected_alternative_id: str | None = None
    alternatives: tuple[DecisionAlternative, ...] = ()
    rationale: str
    consequences: tuple[str, ...] = ()
    lineage: DecisionLineage = Field(default_factory=DecisionLineage)
    approval_state: ApprovalState = ApprovalState.REQUIRED
    source_refs: tuple[str, ...] = ()
    mutation_mode: str = "READ_ONLY"


class HumanReviewPacket(BaseModel):
    review_id: str
    subject_type: str
    subject_id: str
    project_id: str
    approval_state: ApprovalState
    reasons: tuple[str, ...]
    source_refs: tuple[str, ...] = ()
    execution_authorized: bool = False


class DryRunStatus(StrEnum):
    SIMULATED = "SIMULATED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class DryRunImpactPreview(BaseModel):
    dry_run_id: str
    project_id: str
    status: DryRunStatus
    planned_actions: tuple[str, ...]
    predicted_impacts: tuple[str, ...]
    blocked_reasons: tuple[str, ...] = ()
    mutation_executed: bool = False
    source_refs: tuple[str, ...] = ()


class VerificationChannel(StrEnum):
    MACHINE_TEST = "MACHINE_TEST"
    STATIC_ANALYSIS = "STATIC_ANALYSIS"
    SECURITY_GATE = "SECURITY_GATE"
    BROWSER_UAT = "BROWSER_UAT"
    AUTHORITY_READBACK = "AUTHORITY_READBACK"
    MODEL_CRITIC = "MODEL_CRITIC"


class VerificationStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_RUN = "NOT_RUN"
    BLOCKED = "BLOCKED"


class VerificationReceipt(BaseModel):
    receipt_id: str
    channel: VerificationChannel
    status: VerificationStatus
    verifier_id: str
    generator_id: str | None = None
    detail: str
    evidence_refs: tuple[str, ...] = ()


class VerificationBundle(BaseModel):
    bundle_id: str
    project_id: str
    receipts: tuple[VerificationReceipt, ...]
    final_status: VerificationStatus
    independent_verification: bool
    negative_evidence_preserved: bool = True


class EvaluationRecord(BaseModel):
    evaluation_id: str
    project_id: str
    subject_id: str
    score: int
    status: str
    criteria: tuple[str, ...]
    verification_bundle_id: str | None = None


class ProviderEvaluation(BaseModel):
    provider_id: str
    provider_neutral: bool = True
    health: str = "UNKNOWN"
    quality_score: int | None = None
    last_evaluated_at: datetime | None = None


class DataClassification(StrEnum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    SECRET = "SECRET"
    UNKNOWN = "UNKNOWN"


class CapabilityDecision(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class ToolCapability(BaseModel):
    capability_id: str
    name: str
    risk_class: str
    mutation_class: str
    requires_explicit_approval: bool
    source_mode: str = "FIXTURE_DERIVED"


class CapabilityEnvelope(BaseModel):
    envelope_id: str
    project_id: str
    allowed_capabilities: tuple[str, ...] = ()
    denied_capabilities: tuple[str, ...] = ()
    requires_explicit_approval: bool = True
    source_ref: str
    client_can_widen: bool = False


class AuditEvent(BaseModel):
    event_id: str
    event_type: str
    project_id: str
    decision: str
    detail: str
    source_refs: tuple[str, ...] = ()


class PromptInjectionFinding(BaseModel):
    finding_id: str
    detected: bool
    severity: str
    detail: str


class SecretBoundaryFinding(BaseModel):
    finding_id: str
    detected: bool
    redacted: bool
    detail: str


class EngineeringRisk(BaseModel):
    risk_id: str
    severity: str
    title: str
    mitigation: str


class VerificationPlan(BaseModel):
    channels: tuple[VerificationChannel, ...]
    browser_uat_required: bool = True
    authority_readback_required: bool = True


class NextSafeAction(BaseModel):
    action_id: str
    title: str
    reason: str
    mutation_ready: bool
    requires_approval: bool


class EngineeringAdviceRequest(BaseModel):
    project_id: str
    request: str
    task_id: str | None = None


class EngineeringAdviceResponse(BaseModel):
    project_id: str
    status: str
    summary: str
    risks: tuple[EngineeringRisk, ...]
    verification_plan: VerificationPlan
    next_safe_action: NextSafeAction
    source_refs: tuple[str, ...]
    applicable_skill_ids: tuple[str, ...] = ()
    mutation_mode: str = "READ_ONLY"


class RepositoryRef(BaseModel):
    repository: str
    ref: str
    head_sha: str
    observed_at: datetime
    freshness: FreshnessState = FreshnessState.CURRENT


class RepositoryFileRef(BaseModel):
    path: str
    repository: str
    ref: str
    head_sha: str


class RepositorySnapshot(BaseModel):
    project_id: str
    repository: str
    default_branch: str
    current_ref: RepositoryRef
    files: tuple[RepositoryFileRef, ...] = ()
    source_mode: str = "FIXTURE_DERIVED"
    derived_view: bool = True
    mutation_mode: str = "READ_ONLY"


class PatchProposal(BaseModel):
    path: str
    change_type: str
    rationale: str


class ChangeProposal(BaseModel):
    proposal_id: str
    project_id: str
    repository: str
    base_sha: str
    patches: tuple[PatchProposal, ...]
    impact_summary: str
    execution_authorized: bool = False


class RepositoryAnalysis(BaseModel):
    project_id: str
    status: str
    snapshot: RepositorySnapshot | None = None
    risks: tuple[str, ...] = ()
    unknown_reasons: tuple[str, ...] = ()
    mutation_ready: bool = False


class ExecutionScope(BaseModel):
    project_id: str
    repository: str
    base_sha: str
    allowed_paths: tuple[str, ...] = ()
    mutation_class: str = "SIMULATION_ONLY"


class AuthorizationContract(BaseModel):
    authorization_id: str
    envelope: CapabilityEnvelope
    scope: ExecutionScope
    approval_state: ApprovalState
    expires_at: datetime | None = None
    source_ref: str


class CapabilityToken(BaseModel):
    token_id: str
    capability_id: str
    scope_hash: str
    simulation_only: bool = True


class ExecutionRequest(BaseModel):
    project_id: str
    capability_id: str
    requested_paths: tuple[str, ...] = ()
    simulate: bool = True
    authorization: AuthorizationContract | None = None


class RollbackMetadata(BaseModel):
    strategy: str
    preimage_ref: str | None = None
    rollback_available: bool = True


class ExecutionReceipt(BaseModel):
    execution_id: str
    project_id: str
    status: str
    simulated: bool
    mutation_executed: bool
    authorized: bool
    changed_paths: tuple[str, ...] = ()
    blocked_reasons: tuple[str, ...] = ()
    rollback: RollbackMetadata
    verification_bundle_id: str | None = None


class AgentRole(StrEnum):
    PLANNER = "PLANNER"
    REVIEWER = "REVIEWER"
    TESTER = "TESTER"
    SECURITY = "SECURITY"


class AgentTask(BaseModel):
    agent_task_id: str
    role: AgentRole
    objective: str
    authority_envelope_id: str
    may_expand_authority: bool = False


class AgentRunReceipt(BaseModel):
    agent_task_id: str
    role: AgentRole
    status: str
    evidence_refs: tuple[str, ...] = ()


class AgentConflict(BaseModel):
    conflict_id: str
    roles: tuple[AgentRole, ...]
    detail: str
    resolution: str


class MultiAgentPlan(BaseModel):
    plan_id: str
    project_id: str
    tasks: tuple[AgentTask, ...]
    receipts: tuple[AgentRunReceipt, ...] = ()
    conflicts: tuple[AgentConflict, ...] = ()
    execution_runtime: str = "EXTERNAL_AGENTIC_AI_CONTRACT"
    authority_expanded: bool = False


class LifecycleStage(StrEnum):
    UNDERSTAND = "UNDERSTAND"
    RESTORE_STATE = "RESTORE_STATE"
    COMPILE_CONTEXT = "COMPILE_CONTEXT"
    LOAD_SKILLS = "LOAD_SKILLS"
    PLAN = "PLAN"
    IMPACT = "IMPACT"
    AUTHORIZE = "AUTHORIZE"
    EXECUTE_OR_SIMULATE = "EXECUTE_OR_SIMULATE"
    VERIFY = "VERIFY"
    UAT_RECEIPT = "UAT_RECEIPT"
    LEARN = "LEARN"
    CHECKPOINT = "CHECKPOINT"


class LifecycleReceipt(BaseModel):
    stage: LifecycleStage
    status: str
    detail: str
    evidence_refs: tuple[str, ...] = ()


class GovernedDevelopmentLifecycle(BaseModel):
    lifecycle_id: str
    project_id: str
    current_stage: LifecycleStage
    receipts: tuple[LifecycleReceipt, ...]
    blocked: bool
    blocked_reason: str | None = None
    derived_view: bool = True
    mutation_mode: str = "SIMULATION_ONLY"


class WatcherDefinition(BaseModel):
    watcher_id: str
    project_id: str
    condition: str
    action: str = "NOTIFY_OR_PROPOSE_ONLY"
    may_mutate_canonical_state: bool = False


class WatcherEvent(BaseModel):
    event_id: str
    watcher_id: str
    state: str
    detail: str


class DriftAlert(BaseModel):
    alert_id: str
    project_id: str
    severity: str
    detail: str
    requires_reconciliation: bool


class ConnectorHealthObservation(BaseModel):
    connector_id: str
    status: str
    detail: str


class ModelHealth(BaseModel):
    provider_id: str
    status: str
    detail: str


class CostObservation(BaseModel):
    observation_id: str
    provider_id: str
    unit: str
    amount: float
    budget_state: str


class RecoveryReceipt(BaseModel):
    recovery_id: str
    status: str
    rebuildable: bool
    canonical_data_loss: bool
    detail: str


class PortabilityExportReceipt(BaseModel):
    export_id: str
    status: str
    provider_neutral: bool
    contains_secrets: bool
    detail: str


class OperationsSnapshot(BaseModel):
    project_id: str
    watchers: tuple[WatcherDefinition, ...]
    watcher_events: tuple[WatcherEvent, ...]
    connector_health: tuple[ConnectorHealthObservation, ...]
    model_health: tuple[ModelHealth, ...]
    costs: tuple[CostObservation, ...]
    recovery: RecoveryReceipt
    portability: PortabilityExportReceipt
    mutation_mode: str = "READ_ONLY"

