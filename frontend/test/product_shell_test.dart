import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:palwakf_mind_assistant/src/api_client.dart';
import 'package:palwakf_mind_assistant/src/app.dart';
import 'package:palwakf_mind_assistant/src/models/api_models.dart';

class FakeMindApi implements MindApi {
  static const connector = ConnectorHealthView(
    connector: 'GOOGLE_DRIVE',
    mode: 'FIXTURE_DERIVED',
    state: 'READY',
    mutationMode: 'READ_ONLY',
    sourceCount: 7,
    writesEnabled: false,
    detail: 'Test read-only connector.',
  );

  static const projects = [
    ProjectSummaryView(
      projectId: 'PAL_EYES',
      displayName: 'بعيون فلسطينية / Pal Eyes',
      status: 'ACTIVE',
      authorityStatus: 'RESOLVED',
      knowledgeHealth: 'HEALTHY',
      currentStateTitle: 'PAL_EYES_CURRENT_STATE_V1_20260822',
      sourceCount: 3,
      conflictCount: 0,
    ),
    ProjectSummaryView(
      projectId: 'PALWAKF_MIND_ASSISTANT',
      displayName: 'PalWakf Mind Assistant',
      status: 'ACTIVE',
      authorityStatus: 'RESOLVED',
      knowledgeHealth: 'HEALTHY',
      currentStateTitle: 'PALWAKF_MIND_ASSISTANT_CURRENT_STATE_V1_20260827',
      sourceCount: 4,
      conflictCount: 0,
    ),
  ];

  @override
  Future<DashboardView> fetchDashboard() async => const DashboardView(
    mutationMode: 'READ_ONLY',
    providerMode: 'DETERMINISTIC_GROUNDED',
    sovereignAuthority: 'PALWAKF_WORKSPACE_DRIVE',
    connector: connector,
    projects: projects,
    counts: {
      'total': 2,
      'resolved': 2,
      'partial': 0,
      'unknown': 0,
      'conflicts': 0,
    },
    alerts: ['وضع المعرفة READ_ONLY'],
  );

  @override
  Future<AssistantAnswerView> ask(String message, {String? projectId}) async =>
      const AssistantAnswerView(
        projectId: 'PAL_EYES',
        status: 'GROUNDED_READ_ONLY',
        answerKind: 'CURRENT_STATE',
        answer: 'إجابة اختبارية مقيدة بالمصدر.',
        confidence: 'VERIFIED_FROM_AVAILABLE_AUTHORITY_METADATA',
        providerMode: 'DETERMINISTIC_GROUNDED',
        mutationMode: 'READ_ONLY',
        citations: [],
        unknownReasons: [],
        context: TrustedContextView(
          contextId: 'ctx_test',
          intent: 'CURRENT_STATE',
          projectId: 'PAL_EYES',
          taskId: null,
          authorityStatus: 'RESOLVED',
          trustState: 'VERIFIED',
          unknownReasons: [],
          risks: [],
        ),
      );

  @override
  Future<List<ConflictView>> fetchConflicts(String projectId) async => const [];

  @override
  Future<ConnectorHealthView> fetchConnectorHealth() async => connector;

  @override
  Future<ProjectMindView> fetchProjectMind(String projectId) async =>
      ProjectMindView(
        projectId: projectId,
        displayName:
            projectId == 'PAL_EYES'
                ? 'بعيون فلسطينية / Pal Eyes'
                : 'PalWakf Mind Assistant',
        authorityStatus: 'RESOLVED',
        knowledgeHealth: 'HEALTHY',
        currentState: const SourceView(
          title: 'CURRENT_STATE',
          authorityType: 'PROJECT_CURRENT_STATE',
          lifecycleStatus: 'CURRENT',
          sourceRef: 'drive:current',
          canonicalLocation: 'drive://current',
        ),
        authoritativeSources: const [
          SourceView(
            title: 'CURRENT_STATE',
            authorityType: 'PROJECT_CURRENT_STATE',
            lifecycleStatus: 'CURRENT',
            sourceRef: 'drive:current',
            canonicalLocation: 'drive://current',
          ),
        ],
        supersededSources: const [],
        conflicts: const [],
        unknownReasons: const [],
        digitalTwin: const ProjectDigitalTwinView(
          twinId: 'twin_test',
          projectId: 'PAL_EYES',
          displayName: 'بعيون فلسطينية / Pal Eyes',
          status: 'PARTIAL',
          authorityStatus: 'RESOLVED',
          trustState: 'INFERRED',
          derivedView: true,
          canonicalAuthority: false,
          rebuildable: true,
          sourceMode: 'FIXTURE_DERIVED',
          currentStateRef: 'drive:current',
          repository: 'owner/pal_eyes',
          defaultBranch: 'main',
          headSha: 'abc123',
          activeBranch: null,
          taskId: null,
          taskStatus: 'UNKNOWN',
          baselineRef: null,
          dependencies: ['GITHUB', 'WORKSPACE_DRIVE'],
          risks: ['TASK_AUTHORITY_UNAVAILABLE'],
          productionReadinessLevel: 'UNKNOWN',
          productionReadinessStatus: 'NOT_CERTIFIED',
          driftIndicators: [],
          unknownReasons: ['ACTIVE_TASK_UNKNOWN'],
          nextSafeAction: 'RECONCILE_BEFORE_MUTATION',
          sourceRefs: ['drive:current'],
          rebuildReceipt: 'receipt_test',
        ),
      );

  @override
  Future<ProjectDigitalTwinView> fetchDigitalTwin(String projectId) async =>
      (await fetchProjectMind(projectId)).digitalTwin!;

  @override
  Future<List<SkillView>> fetchSkills() async => const [
    SkillView(
      skillId: 'PALWAKF_FLUTTER_PRODUCT_FIRST_RUN_GATE_V1',
      version: '1.0.0',
      status: 'ACTIVE',
      ownerScope: 'DOMAIN:FLUTTER',
      level: 'DOMAIN',
      appliesTo: ['flutter', 'browser', 'responsive', 'uat'],
      triggers: ['flutter', 'browser', 'uat'],
      preconditions: ['TARGET_DEVICE_AVAILABLE'],
      evidenceRequirements: ['ANALYZE', 'TEST', 'BUILD_WEB', 'BROWSER_UAT'],
      knownFailures: ['RENDERFLEX_OVERFLOW'],
      provenanceRef: 'drive:skills#73',
    ),
  ];

  @override
  Future<SkillResolutionView> resolveSkills(
    String message, {
    String? projectId,
  }) async => const SkillResolutionView(
    selections: [
      SkillSelectionView(
        skillId: 'PALWAKF_FLUTTER_PRODUCT_FIRST_RUN_GATE_V1',
        version: '1.0.0',
        level: 'DOMAIN',
        applicable: true,
        score: 30,
        reasons: ['TRIGGER:flutter', 'TRIGGER:browser', 'TRIGGER:uat'],
        unmetPreconditions: ['TARGET_DEVICE_AVAILABLE'],
        provenanceRef: 'drive:skills#73',
        executionAuthorized: false,
      ),
    ],
    rejected: [],
    registrySourceMode: 'FIXTURE_DERIVED',
    mutationMode: 'READ_ONLY',
    autonomousExecution: false,
  );

  @override
  Future<GovernedCapabilityView> fetchIntegratedSurface(
    String surface,
    String projectId,
  ) async => GovernedCapabilityView(
    surface: surface,
    title: switch (surface) {
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
    },
    status: 'DERIVED',
    trustLabel: 'FIXTURE_DERIVED',
    mutationMode: surface == 'execution' ? 'SIMULATION_ONLY' : 'READ_ONLY',
    authorizationLabel: 'EXECUTION NOT AUTHORIZED',
    details: const [
      'Derived controlled surface',
      'Human review required before mutation',
    ],
    sourceRefs: const ['FIXTURE_DERIVED'],
  );

  @override
  Future<SearchResponseView> search(String query, {String? projectId}) async =>
      SearchResponseView(
        query: query,
        hits: const [
          SearchHitView(
            projectId: 'PAL_EYES',
            title: 'CURRENT_STATE',
            authorityType: 'PROJECT_CURRENT_STATE',
            lifecycleStatus: 'CURRENT',
            sourceRef: 'drive:current',
            canonicalLocation: 'drive://current',
            matchedOn: ['title'],
          ),
        ],
      );
}

Future<void> _pumpAt(WidgetTester tester, Size size) async {
  tester.view.physicalSize = size;
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);
  await tester.pumpWidget(MindAssistantApp(api: FakeMindApi()));
  await tester.pumpAndSettle();
}

void main() {
  testWidgets(
    'desktop 800x600 exposes assistant and dashboard without framework exception',
    (tester) async {
      await _pumpAt(tester, const Size(800, 600));

      expect(find.text('PalWakf'), findsOneWidget);
      expect(find.text('المساعد الذكي'), findsOneWidget);
      expect(find.text('لوحة التحكم'), findsOneWidget);
      expect(find.text('READ ONLY'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('narrow 390x844 uses mobile navigation without overflow', (
    tester,
  ) async {
    await _pumpAt(tester, const Size(390, 844));

    expect(find.text('PalWakf Mind Assistant'), findsOneWidget);
    expect(find.text('المساعد'), findsOneWidget);
    expect(find.text('التحكم'), findsOneWidget);
    expect(find.text('المشاريع'), findsOneWidget);
    expect(find.text('المعرفة'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('skills surface exposes provenance and no execution authority', (
    tester,
  ) async {
    await _pumpAt(tester, const Size(1200, 800));

    await tester.tap(find.text('المهارات والدروس'));
    await tester.pumpAndSettle();

    expect(find.text('Skills & Lessons'), findsOneWidget);
    expect(
      find.text('PALWAKF_FLUTTER_PRODUCT_FIRST_RUN_GATE_V1'),
      findsOneWidget,
    );
    await tester.tap(find.text('Flutter UAT'));
    await tester.pumpAndSettle();
    expect(find.text('EXECUTION NOT AUTHORIZED'), findsOneWidget);
    expect(find.text('FIXTURE_DERIVED'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets(
    'final mega batch governed surfaces are reachable and read-only',
    (tester) async {
      await _pumpAt(tester, const Size(1200, 900));

      for (final label in [
        'التخطيط والأثر',
        'القرارات والموافقات',
        'التحقق المستقل',
        'الأمن والصلاحيات',
        'Engineering Mode',
        'Repository Intelligence',
        'Governed Execution',
        'Multi-Agent',
        'Development Lifecycle',
        'Operations',
      ]) {
        await tester.ensureVisible(find.text(label));
        await tester.pumpAndSettle();
        await tester.tap(find.text(label));
        await tester.pumpAndSettle();
        expect(find.text('FIXTURE_DERIVED'), findsWidgets);
        expect(find.text('EXECUTION NOT AUTHORIZED'), findsOneWidget);
        expect(tester.takeException(), isNull);
      }
    },
  );

  testWidgets('assistant can return a grounded read-only answer', (
    tester,
  ) async {
    await _pumpAt(tester, const Size(1200, 800));

    await tester.tap(find.text('ما الحالة الحالية؟'));
    await tester.pumpAndSettle();

    expect(find.text('إجابة اختبارية مقيدة بالمصدر.'), findsOneWidget);
    expect(find.text('GROUNDED_READ_ONLY'), findsOneWidget);
    expect(find.text('TRUST VERIFIED'), findsOneWidget);
    expect(find.text('AUTH RESOLVED'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
