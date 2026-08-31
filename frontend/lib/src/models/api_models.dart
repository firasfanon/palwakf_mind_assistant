class TrustProvenanceView {
  const TrustProvenanceView({
    required this.sourceRef,
    required this.authority,
    required this.lifecycleStatus,
    required this.version,
    required this.confidence,
    required this.freshness,
    required this.supersession,
    required this.scope,
    required this.claimState,
    required this.reason,
  });

  factory TrustProvenanceView.fromJson(Map<String, dynamic> json) =>
      TrustProvenanceView(
        sourceRef: json['source_ref'] as String? ?? '',
        authority: json['authority'] as String? ?? 'UNKNOWN',
        lifecycleStatus: json['lifecycle_status'] as String? ?? 'UNKNOWN',
        version: json['version'] as String? ?? 'UNKNOWN',
        confidence: json['confidence'] as String? ?? 'UNKNOWN',
        freshness: json['freshness'] as String? ?? 'UNKNOWN',
        supersession: json['supersession'] as String? ?? 'UNKNOWN',
        scope: json['scope'] as String? ?? 'UNKNOWN',
        claimState: json['claim_state'] as String? ?? 'UNKNOWN',
        reason: json['reason'] as String? ?? '',
      );

  final String sourceRef;
  final String authority;
  final String lifecycleStatus;
  final String version;
  final String confidence;
  final String freshness;
  final String supersession;
  final String scope;
  final String claimState;
  final String reason;
}

class TrustedContextView {
  const TrustedContextView({
    required this.contextId,
    required this.intent,
    required this.projectId,
    required this.taskId,
    required this.authorityStatus,
    required this.trustState,
    required this.unknownReasons,
    required this.risks,
  });

  factory TrustedContextView.fromJson(Map<String, dynamic> json) =>
      TrustedContextView(
        contextId: json['context_id'] as String? ?? '',
        intent: json['intent'] as String? ?? 'UNKNOWN',
        projectId: json['project_id'] as String?,
        taskId: json['task_id'] as String?,
        authorityStatus: json['authority_status'] as String? ?? 'UNKNOWN',
        trustState: json['trust_state'] as String? ?? 'UNKNOWN',
        unknownReasons: ((json['unknown_reasons'] as List?) ?? const [])
            .map((item) => item.toString())
            .toList(growable: false),
        risks: ((json['risks'] as List?) ?? const [])
            .map((item) => item.toString())
            .toList(growable: false),
      );

  final String contextId;
  final String intent;
  final String? projectId;
  final String? taskId;
  final String authorityStatus;
  final String trustState;
  final List<String> unknownReasons;
  final List<String> risks;
}

class SourceView {
  const SourceView({
    required this.title,
    required this.authorityType,
    required this.lifecycleStatus,
    required this.sourceRef,
    required this.canonicalLocation,
  });

  factory SourceView.fromJson(Map<String, dynamic> json) => SourceView(
    title: json['title'] as String? ?? 'UNKNOWN_SOURCE',
    authorityType: json['authority_type'] as String? ?? 'UNKNOWN',
    lifecycleStatus: json['lifecycle_status'] as String? ?? 'UNKNOWN',
    sourceRef: json['source_ref'] as String? ?? '',
    canonicalLocation: json['canonical_location'] as String? ?? '',
  );

  final String title;
  final String authorityType;
  final String lifecycleStatus;
  final String sourceRef;
  final String canonicalLocation;
}

class ConnectorHealthView {
  const ConnectorHealthView({
    required this.connector,
    required this.mode,
    required this.state,
    required this.mutationMode,
    required this.sourceCount,
    required this.writesEnabled,
    required this.detail,
  });

  factory ConnectorHealthView.fromJson(Map<String, dynamic> json) =>
      ConnectorHealthView(
        connector: json['connector'] as String? ?? 'UNKNOWN',
        mode: json['mode'] as String? ?? 'UNKNOWN',
        state: json['state'] as String? ?? 'UNKNOWN',
        mutationMode: json['mutation_mode'] as String? ?? 'READ_ONLY',
        sourceCount: json['source_count'] as int? ?? 0,
        writesEnabled: json['writes_enabled'] as bool? ?? false,
        detail: json['detail'] as String? ?? '',
      );

  final String connector;
  final String mode;
  final String state;
  final String mutationMode;
  final int sourceCount;
  final bool writesEnabled;
  final String detail;
}

class ProjectSummaryView {
  const ProjectSummaryView({
    required this.projectId,
    required this.displayName,
    required this.status,
    required this.authorityStatus,
    required this.knowledgeHealth,
    required this.currentStateTitle,
    required this.sourceCount,
    required this.conflictCount,
  });

  factory ProjectSummaryView.fromJson(Map<String, dynamic> json) =>
      ProjectSummaryView(
        projectId: json['project_id'] as String? ?? 'UNKNOWN',
        displayName: json['display_name'] as String? ?? 'UNKNOWN',
        status: json['status'] as String? ?? 'UNKNOWN',
        authorityStatus: json['authority_status'] as String? ?? 'UNKNOWN',
        knowledgeHealth: json['knowledge_health'] as String? ?? 'UNKNOWN',
        currentStateTitle: json['current_state_title'] as String?,
        sourceCount: json['source_count'] as int? ?? 0,
        conflictCount: json['conflict_count'] as int? ?? 0,
      );

  final String projectId;
  final String displayName;
  final String status;
  final String authorityStatus;
  final String knowledgeHealth;
  final String? currentStateTitle;
  final int sourceCount;
  final int conflictCount;
}

class DashboardView {
  const DashboardView({
    required this.mutationMode,
    required this.providerMode,
    required this.sovereignAuthority,
    required this.connector,
    required this.projects,
    required this.counts,
    required this.alerts,
  });

  factory DashboardView.fromJson(Map<String, dynamic> json) => DashboardView(
    mutationMode: json['mutation_mode'] as String? ?? 'READ_ONLY',
    providerMode: json['provider_mode'] as String? ?? 'UNKNOWN',
    sovereignAuthority: json['sovereign_authority'] as String? ?? 'UNKNOWN',
    connector: ConnectorHealthView.fromJson(
      (json['connector'] as Map?)?.cast<String, dynamic>() ?? const {},
    ),
    projects: ((json['projects'] as List?) ?? const [])
        .whereType<Map>()
        .map(
          (item) => ProjectSummaryView.fromJson(item.cast<String, dynamic>()),
        )
        .toList(growable: false),
    counts: ((json['counts'] as Map?) ?? const {}).map(
      (key, value) => MapEntry(key.toString(), value is int ? value : 0),
    ),
    alerts: ((json['alerts'] as List?) ?? const [])
        .map((item) => item.toString())
        .toList(growable: false),
  );

  final String mutationMode;
  final String providerMode;
  final String sovereignAuthority;
  final ConnectorHealthView connector;
  final List<ProjectSummaryView> projects;
  final Map<String, int> counts;
  final List<String> alerts;
}

class ConflictView {
  const ConflictView({
    required this.conflictId,
    required this.conflictType,
    required this.severity,
    required this.title,
    required this.detail,
    required this.sourceRefs,
  });

  factory ConflictView.fromJson(Map<String, dynamic> json) => ConflictView(
    conflictId: json['conflict_id'] as String? ?? '',
    conflictType: json['conflict_type'] as String? ?? 'UNKNOWN',
    severity: json['severity'] as String? ?? 'REVIEW',
    title: json['title'] as String? ?? 'تعارض يحتاج مراجعة',
    detail: json['detail'] as String? ?? '',
    sourceRefs: ((json['source_refs'] as List?) ?? const [])
        .map((item) => item.toString())
        .toList(growable: false),
  );

  final String conflictId;
  final String conflictType;
  final String severity;
  final String title;
  final String detail;
  final List<String> sourceRefs;
}

class ProjectMindView {
  const ProjectMindView({
    required this.projectId,
    required this.displayName,
    required this.authorityStatus,
    required this.knowledgeHealth,
    required this.currentState,
    required this.authoritativeSources,
    required this.supersededSources,
    required this.conflicts,
    required this.unknownReasons,
    required this.digitalTwin,
  });

  factory ProjectMindView.fromJson(Map<String, dynamic> json) =>
      ProjectMindView(
        projectId: json['project_id'] as String? ?? 'UNKNOWN',
        displayName: json['display_name'] as String? ?? 'UNKNOWN',
        authorityStatus: json['authority_status'] as String? ?? 'UNKNOWN',
        knowledgeHealth: json['knowledge_health'] as String? ?? 'UNKNOWN',
        currentState:
            json['current_state'] is Map
                ? SourceView.fromJson(
                  (json['current_state'] as Map).cast<String, dynamic>(),
                )
                : null,
        authoritativeSources: ((json['authoritative_sources'] as List?) ??
                const [])
            .whereType<Map>()
            .map((item) => SourceView.fromJson(item.cast<String, dynamic>()))
            .toList(growable: false),
        supersededSources: ((json['superseded_sources'] as List?) ?? const [])
            .whereType<Map>()
            .map((item) => SourceView.fromJson(item.cast<String, dynamic>()))
            .toList(growable: false),
        conflicts: ((json['conflicts'] as List?) ?? const [])
            .whereType<Map>()
            .map((item) => ConflictView.fromJson(item.cast<String, dynamic>()))
            .toList(growable: false),
        unknownReasons: ((json['unknown_reasons'] as List?) ?? const [])
            .map((item) => item.toString())
            .toList(growable: false),
        digitalTwin:
            json['digital_twin'] is Map
                ? ProjectDigitalTwinView.fromJson(
                  (json['digital_twin'] as Map).cast<String, dynamic>(),
                )
                : null,
      );

  final String projectId;
  final String displayName;
  final String authorityStatus;
  final String knowledgeHealth;
  final SourceView? currentState;
  final List<SourceView> authoritativeSources;
  final List<SourceView> supersededSources;
  final List<ConflictView> conflicts;
  final List<String> unknownReasons;
  final ProjectDigitalTwinView? digitalTwin;
}

class AssistantAnswerView {
  const AssistantAnswerView({
    required this.projectId,
    required this.status,
    required this.answerKind,
    required this.answer,
    required this.confidence,
    required this.providerMode,
    required this.mutationMode,
    required this.citations,
    required this.unknownReasons,
    required this.context,
  });

  factory AssistantAnswerView.fromJson(Map<String, dynamic> json) =>
      AssistantAnswerView(
        projectId: json['project_id'] as String?,
        status: json['status'] as String? ?? 'UNKNOWN',
        answerKind: json['answer_kind'] as String? ?? 'GENERAL',
        answer: json['answer_ar'] as String? ?? '',
        confidence: json['confidence'] as String? ?? 'UNKNOWN',
        providerMode: json['provider_mode'] as String? ?? 'UNKNOWN',
        mutationMode: json['mutation_mode'] as String? ?? 'READ_ONLY',
        citations: ((json['citations'] as List?) ?? const [])
            .whereType<Map>()
            .map((item) => SourceView.fromJson(item.cast<String, dynamic>()))
            .toList(growable: false),
        unknownReasons: ((json['unknown_reasons'] as List?) ?? const [])
            .map((item) => item.toString())
            .toList(growable: false),
        context:
            json['context'] is Map
                ? TrustedContextView.fromJson(
                  (json['context'] as Map).cast<String, dynamic>(),
                )
                : null,
      );

  final String? projectId;
  final String status;
  final String answerKind;
  final String answer;
  final String confidence;
  final String providerMode;
  final String mutationMode;
  final List<SourceView> citations;
  final List<String> unknownReasons;
  final TrustedContextView? context;
}

class SearchHitView {
  const SearchHitView({
    required this.projectId,
    required this.title,
    required this.authorityType,
    required this.lifecycleStatus,
    required this.sourceRef,
    required this.canonicalLocation,
    required this.matchedOn,
  });

  factory SearchHitView.fromJson(Map<String, dynamic> json) => SearchHitView(
    projectId: json['project_id'] as String? ?? 'UNKNOWN',
    title: json['title'] as String? ?? 'UNKNOWN',
    authorityType: json['authority_type'] as String? ?? 'UNKNOWN',
    lifecycleStatus: json['lifecycle_status'] as String? ?? 'UNKNOWN',
    sourceRef: json['source_ref'] as String? ?? '',
    canonicalLocation: json['canonical_location'] as String? ?? '',
    matchedOn: ((json['matched_on'] as List?) ?? const [])
        .map((item) => item.toString())
        .toList(growable: false),
  );

  final String projectId;
  final String title;
  final String authorityType;
  final String lifecycleStatus;
  final String sourceRef;
  final String canonicalLocation;
  final List<String> matchedOn;
}

class SearchResponseView {
  const SearchResponseView({required this.query, required this.hits});

  factory SearchResponseView.fromJson(Map<String, dynamic> json) =>
      SearchResponseView(
        query: json['query'] as String? ?? '',
        hits: ((json['hits'] as List?) ?? const [])
            .whereType<Map>()
            .map((item) => SearchHitView.fromJson(item.cast<String, dynamic>()))
            .toList(growable: false),
      );

  final String query;
  final List<SearchHitView> hits;
}

class DriftIndicatorView {
  const DriftIndicatorView({
    required this.code,
    required this.severity,
    required this.state,
    required this.explanation,
    required this.sourceRefs,
  });

  factory DriftIndicatorView.fromJson(Map<String, dynamic> json) =>
      DriftIndicatorView(
        code: json['drift_code'] as String? ?? 'UNKNOWN',
        severity: json['severity'] as String? ?? 'REVIEW',
        state: json['state'] as String? ?? 'UNKNOWN',
        explanation: json['explanation'] as String? ?? '',
        sourceRefs: ((json['source_refs'] as List?) ?? const [])
            .map((item) => item.toString())
            .toList(growable: false),
      );

  final String code;
  final String severity;
  final String state;
  final String explanation;
  final List<String> sourceRefs;
}

class ProjectDigitalTwinView {
  const ProjectDigitalTwinView({
    required this.twinId,
    required this.projectId,
    required this.displayName,
    required this.status,
    required this.authorityStatus,
    required this.trustState,
    required this.derivedView,
    required this.canonicalAuthority,
    required this.rebuildable,
    required this.sourceMode,
    required this.currentStateRef,
    required this.repository,
    required this.defaultBranch,
    required this.headSha,
    required this.activeBranch,
    required this.taskId,
    required this.taskStatus,
    required this.baselineRef,
    required this.dependencies,
    required this.risks,
    required this.productionReadinessLevel,
    required this.productionReadinessStatus,
    required this.driftIndicators,
    required this.unknownReasons,
    required this.nextSafeAction,
    required this.sourceRefs,
    required this.rebuildReceipt,
  });

  factory ProjectDigitalTwinView.fromJson(Map<String, dynamic> json) =>
      ProjectDigitalTwinView(
        twinId: json['twin_id'] as String? ?? '',
        projectId: json['project_id'] as String? ?? 'UNKNOWN',
        displayName: json['display_name'] as String? ?? 'UNKNOWN',
        status: json['status'] as String? ?? 'UNKNOWN',
        authorityStatus: json['authority_status'] as String? ?? 'UNKNOWN',
        trustState: json['trust_state'] as String? ?? 'UNKNOWN',
        derivedView: json['derived_view'] as bool? ?? true,
        canonicalAuthority: json['canonical_authority'] as bool? ?? false,
        rebuildable: json['rebuildable'] as bool? ?? true,
        sourceMode: json['source_mode'] as String? ?? 'UNKNOWN',
        currentStateRef: json['current_state_ref'] as String?,
        repository: json['repository'] as String?,
        defaultBranch: json['default_branch'] as String?,
        headSha: json['head_sha'] as String?,
        activeBranch: json['active_branch'] as String?,
        taskId: json['task_id'] as String?,
        taskStatus: json['task_status'] as String? ?? 'UNKNOWN',
        baselineRef: json['baseline_ref'] as String?,
        dependencies: ((json['dependencies'] as List?) ?? const [])
            .map((item) => item.toString())
            .toList(growable: false),
        risks: ((json['risks'] as List?) ?? const [])
            .map((item) => item.toString())
            .toList(growable: false),
        productionReadinessLevel:
            json['production_readiness_level'] as String? ?? 'UNKNOWN',
        productionReadinessStatus:
            json['production_readiness_status'] as String? ?? 'UNKNOWN',
        driftIndicators: ((json['drift_indicators'] as List?) ?? const [])
            .whereType<Map>()
            .map(
              (item) =>
                  DriftIndicatorView.fromJson(item.cast<String, dynamic>()),
            )
            .toList(growable: false),
        unknownReasons: ((json['unknown_reasons'] as List?) ?? const [])
            .map((item) => item.toString())
            .toList(growable: false),
        nextSafeAction: json['next_safe_action'] as String? ?? 'UNKNOWN',
        sourceRefs: ((json['source_refs'] as List?) ?? const [])
            .map((item) => item.toString())
            .toList(growable: false),
        rebuildReceipt: json['rebuild_receipt'] as String? ?? '',
      );

  final String twinId;
  final String projectId;
  final String displayName;
  final String status;
  final String authorityStatus;
  final String trustState;
  final bool derivedView;
  final bool canonicalAuthority;
  final bool rebuildable;
  final String sourceMode;
  final String? currentStateRef;
  final String? repository;
  final String? defaultBranch;
  final String? headSha;
  final String? activeBranch;
  final String? taskId;
  final String taskStatus;
  final String? baselineRef;
  final List<String> dependencies;
  final List<String> risks;
  final String productionReadinessLevel;
  final String productionReadinessStatus;
  final List<DriftIndicatorView> driftIndicators;
  final List<String> unknownReasons;
  final String nextSafeAction;
  final List<String> sourceRefs;
  final String rebuildReceipt;
}

class SkillView {
  const SkillView({
    required this.skillId,
    required this.version,
    required this.status,
    required this.ownerScope,
    required this.level,
    required this.appliesTo,
    required this.triggers,
    required this.preconditions,
    required this.evidenceRequirements,
    required this.knownFailures,
    required this.provenanceRef,
  });

  factory SkillView.fromJson(Map<String, dynamic> json) => SkillView(
    skillId: json['skill_id'] as String? ?? 'UNKNOWN',
    version: json['version'] as String? ?? 'UNKNOWN',
    status: json['status'] as String? ?? 'UNKNOWN',
    ownerScope: json['owner_scope'] as String? ?? 'UNKNOWN',
    level: json['level'] as String? ?? 'UNKNOWN',
    appliesTo: ((json['applies_to'] as List?) ?? const [])
        .map((item) => item.toString())
        .toList(growable: false),
    triggers: ((json['triggers'] as List?) ?? const [])
        .map((item) => item.toString())
        .toList(growable: false),
    preconditions: ((json['preconditions'] as List?) ?? const [])
        .map((item) => item.toString())
        .toList(growable: false),
    evidenceRequirements: ((json['evidence_requirements'] as List?) ?? const [])
        .map((item) => item.toString())
        .toList(growable: false),
    knownFailures: ((json['known_failures'] as List?) ?? const [])
        .map((item) => item.toString())
        .toList(growable: false),
    provenanceRef: json['provenance_ref'] as String? ?? '',
  );

  final String skillId;
  final String version;
  final String status;
  final String ownerScope;
  final String level;
  final List<String> appliesTo;
  final List<String> triggers;
  final List<String> preconditions;
  final List<String> evidenceRequirements;
  final List<String> knownFailures;
  final String provenanceRef;
}

class SkillSelectionView {
  const SkillSelectionView({
    required this.skillId,
    required this.version,
    required this.level,
    required this.applicable,
    required this.score,
    required this.reasons,
    required this.unmetPreconditions,
    required this.provenanceRef,
    required this.executionAuthorized,
  });

  factory SkillSelectionView.fromJson(Map<String, dynamic> json) =>
      SkillSelectionView(
        skillId: json['skill_id'] as String? ?? 'UNKNOWN',
        version: json['version'] as String? ?? 'UNKNOWN',
        level: json['level'] as String? ?? 'UNKNOWN',
        applicable: json['applicable'] as bool? ?? false,
        score: json['score'] as int? ?? 0,
        reasons: ((json['reasons'] as List?) ?? const [])
            .map((item) => item.toString())
            .toList(growable: false),
        unmetPreconditions: ((json['unmet_preconditions'] as List?) ?? const [])
            .map((item) => item.toString())
            .toList(growable: false),
        provenanceRef: json['provenance_ref'] as String? ?? '',
        executionAuthorized: json['execution_authorized'] as bool? ?? false,
      );

  final String skillId;
  final String version;
  final String level;
  final bool applicable;
  final int score;
  final List<String> reasons;
  final List<String> unmetPreconditions;
  final String provenanceRef;
  final bool executionAuthorized;
}

class SkillResolutionView {
  const SkillResolutionView({
    required this.selections,
    required this.rejected,
    required this.registrySourceMode,
    required this.mutationMode,
    required this.autonomousExecution,
  });

  factory SkillResolutionView.fromJson(
    Map<String, dynamic> json,
  ) => SkillResolutionView(
    selections: ((json['selections'] as List?) ?? const [])
        .whereType<Map>()
        .map(
          (item) => SkillSelectionView.fromJson(item.cast<String, dynamic>()),
        )
        .toList(growable: false),
    rejected: ((json['rejected'] as List?) ?? const [])
        .whereType<Map>()
        .map(
          (item) => SkillSelectionView.fromJson(item.cast<String, dynamic>()),
        )
        .toList(growable: false),
    registrySourceMode: json['registry_source_mode'] as String? ?? 'UNKNOWN',
    mutationMode: json['mutation_mode'] as String? ?? 'READ_ONLY',
    autonomousExecution: json['autonomous_execution'] as bool? ?? false,
  );

  final List<SkillSelectionView> selections;
  final List<SkillSelectionView> rejected;
  final String registrySourceMode;
  final String mutationMode;
  final bool autonomousExecution;
}

class GovernedCapabilityView {
  const GovernedCapabilityView({
    required this.surface,
    required this.title,
    required this.status,
    required this.trustLabel,
    required this.mutationMode,
    required this.authorizationLabel,
    required this.details,
    required this.sourceRefs,
  });

  factory GovernedCapabilityView.fromJson(
    String surface,
    Map<String, dynamic> json,
  ) {
    final encoded = json.toString();
    final status =
        json['status']?.toString() ??
        json['mutation_mode']?.toString() ??
        'DERIVED';
    final mutationMode =
        json['mutation_mode']?.toString() ??
        (encoded.contains('SIMULATION_ONLY') ? 'SIMULATION_ONLY' : 'READ_ONLY');
    final authorized =
        encoded.contains('mutation_executed: true') &&
        encoded.contains('authorized: true');
    return GovernedCapabilityView(
      surface: surface,
      title: _surfaceTitle(surface),
      status: status,
      trustLabel: 'FIXTURE_DERIVED',
      mutationMode: mutationMode,
      authorizationLabel:
          authorized ? 'EXECUTION AUTHORIZED' : 'EXECUTION NOT AUTHORIZED',
      details: _surfaceDetails(surface, json),
      sourceRefs: const ['FIXTURE_DERIVED'],
    );
  }

  static String _surfaceTitle(String surface) => switch (surface) {
    'planning' => 'Planning & Impact',
    'decisions' => 'Human Approval Studio',
    'verification' => 'Independent Verification',
    'security' => 'Security & Capabilities',
    'engineering' => 'Engineering Mode',
    'repository' => 'Repository Intelligence',
    'execution' => 'Governed Execution Studio',
    'agents' => 'Multi-Agent Orchestration',
    'lifecycle' => 'Development Lifecycle',
    'operations' => 'Operations & Recovery',
    _ => surface,
  };

  static List<String> _surfaceDetails(
    String surface,
    Map<String, dynamic> json,
  ) {
    switch (surface) {
      case 'planning':
        final graph =
            (json['graph'] as Map?)?.cast<String, dynamic>() ?? const {};
        return [
          'PLAN ${graph['plan_id'] ?? 'UNKNOWN'}',
          'STATUS ${graph['status'] ?? 'UNKNOWN'}',
          'Human approval required before mutation',
          'Impact analysis is read-only and dependency-aware',
        ];
      case 'decisions':
        final decision =
            (json['decision'] as Map?)?.cast<String, dynamic>() ?? const {};
        final review =
            (json['review'] as Map?)?.cast<String, dynamic>() ?? const {};
        return [
          'DECISION ${decision['decision_id'] ?? 'UNKNOWN'}',
          'STATE ${decision['status'] ?? 'UNKNOWN'}',
          'APPROVAL ${review['approval_state'] ?? 'REQUIRED'}',
          'Alternatives and lineage preserved',
        ];
      case 'verification':
        return [
          'Generator is not the final verifier',
          'Deterministic failure cannot be overridden by model critic',
          'Negative evidence is preserved',
        ];
      case 'security':
        final denied = ((json['denied_capabilities'] as List?) ?? const [])
            .map((item) => item.toString())
            .join(', ');
        return [
          'Least privilege',
          'DENIED ${denied.isEmpty ? 'NONE' : denied}',
          'Prompt injection blocks high-risk capabilities',
          'Secret values are redacted from evidence',
          'Client cannot widen authority envelope',
        ];
      case 'engineering':
        return [
          'Derived engineering advice',
          'Exact source refs required before mutation',
          'Next safe action remains approval-gated',
        ];
      case 'repository':
        final snapshot =
            (json['snapshot'] as Map?)?.cast<String, dynamic>() ?? const {};
        final current =
            (snapshot['current_ref'] as Map?)?.cast<String, dynamic>() ??
            const {};
        return [
          'REPO ${snapshot['repository'] ?? 'UNKNOWN'}',
          'REF ${current['ref'] ?? 'UNKNOWN'}',
          'HEAD ${current['head_sha'] ?? 'UNKNOWN'}',
          'Fixture-derived snapshot is not live Git authority',
        ];
      case 'execution':
        return [
          'STATUS ${json['status'] ?? 'UNKNOWN'}',
          'SIMULATED ${json['simulated'] ?? true}',
          'MUTATION EXECUTED ${json['mutation_executed'] ?? false}',
          'Authorization envelope + scope required',
          'Rollback metadata preserved',
          'No real external mutation in this Mega Batch',
        ];
      case 'agents':
        return [
          'Planner • Reviewer • Tester • Security',
          'Agentic AI remains an external runtime',
          'Agent plan cannot expand authority',
        ];
      case 'lifecycle':
        return [
          'UNDERSTAND → RESTORE_STATE → COMPILE_CONTEXT → LOAD_SKILLS',
          'PLAN → IMPACT → AUTHORIZE → EXECUTE_OR_SIMULATE → VERIFY',
          'UAT_RECEIPT → LEARN → CHECKPOINT',
          'Blocked gates cannot be skipped',
        ];
      case 'operations':
        return [
          'Watchers notify/propose only',
          'Model and connector health',
          'Derived-store rebuild/restore drill',
          'Provider-neutral portability and cost observations',
        ];
      default:
        return [json.toString()];
    }
  }

  final String surface;
  final String title;
  final String status;
  final String trustLabel;
  final String mutationMode;
  final String authorizationLabel;
  final List<String> details;
  final List<String> sourceRefs;
}
