import 'package:flutter/material.dart';

import '../api_client.dart';
import '../design/mind_theme.dart';
import '../models/api_models.dart';
import '../screens/assistant_screen.dart';
import '../screens/conflicts_screen.dart';
import '../screens/dashboard_screen.dart';
import '../screens/explorer_screen.dart';
import '../screens/project_mind_screen.dart';
import '../screens/sources_screen.dart';
import '../screens/skills_screen.dart';
import '../screens/planning_screen.dart';
import '../screens/decisions_screen.dart';
import '../screens/verification_screen.dart';
import '../screens/security_capabilities_screen.dart';
import '../screens/engineering_mode_screen.dart';
import '../screens/repository_intelligence_screen.dart';
import '../screens/execution_studio_screen.dart';
import '../screens/agent_orchestration_screen.dart';
import '../screens/development_lifecycle_screen.dart';
import '../screens/operations_screen.dart';
import '../widgets/common.dart';

enum ProductSection {
  assistant,
  dashboard,
  projects,
  explorer,
  conflicts,
  skills,
  sources,
  planning,
  decisions,
  verification,
  security,
  engineering,
  repository,
  execution,
  agents,
  lifecycle,
  operations,
}

class ProductShell extends StatefulWidget {
  const ProductShell({super.key, required this.api});

  final MindApi api;

  @override
  State<ProductShell> createState() => _ProductShellState();
}

class _ProductShellState extends State<ProductShell> {
  ProductSection _section = ProductSection.assistant;
  String _projectId = 'PAL_EYES';
  late Future<DashboardView> _catalogFuture;

  @override
  void initState() {
    super.initState();
    _catalogFuture = widget.api.fetchDashboard();
  }

  void _select(ProductSection section) => setState(() => _section = section);
  void _selectProject(String projectId) =>
      setState(() => _projectId = projectId);

  @override
  Widget build(BuildContext context) => FutureBuilder<DashboardView>(
    future: _catalogFuture,
    builder: (context, snapshot) {
      if (snapshot.connectionState != ConnectionState.done) {
        return const Scaffold(
          body: LoadingState(label: 'جارٍ تحميل كتالوج المشاريع…'),
        );
      }
      if (snapshot.hasError) {
        return Scaffold(
          body: ErrorState(
            message: snapshot.error.toString(),
            onRetry:
                () => setState(
                  () => _catalogFuture = widget.api.fetchDashboard(),
                ),
          ),
        );
      }
      final dashboard = snapshot.data!;
      if (dashboard.projects.isNotEmpty &&
          !dashboard.projects.any((item) => item.projectId == _projectId)) {
        _projectId = dashboard.projects.first.projectId;
      }
      return LayoutBuilder(
        builder: (context, constraints) {
          final compact = constraints.maxWidth < 720;
          return compact ? _mobileShell(dashboard) : _desktopShell(dashboard);
        },
      );
    },
  );

  Widget _body(DashboardView dashboard) {
    return switch (_section) {
      ProductSection.assistant => AssistantScreen(
        api: widget.api,
        projectId: _projectId,
        onProjectChanged: _selectProject,
        projects: dashboard.projects,
      ),
      ProductSection.dashboard => DashboardScreen(api: widget.api),
      ProductSection.projects => ProjectMindScreen(
        api: widget.api,
        projectId: _projectId,
        onProjectChanged: _selectProject,
        projects: dashboard.projects,
      ),
      ProductSection.explorer => ExplorerScreen(
        api: widget.api,
        projectId: _projectId,
        projects: dashboard.projects,
      ),
      ProductSection.skills => SkillsScreen(
        api: widget.api,
        projectId: _projectId,
      ),
      ProductSection.conflicts => ConflictsScreen(
        api: widget.api,
        projectId: _projectId,
      ),
      ProductSection.sources => SourcesScreen(
        api: widget.api,
        projectId: _projectId,
      ),
      ProductSection.planning => PlanningScreen(
        api: widget.api,
        projectId: _projectId,
      ),
      ProductSection.decisions => DecisionsScreen(
        api: widget.api,
        projectId: _projectId,
      ),
      ProductSection.verification => VerificationScreen(
        api: widget.api,
        projectId: _projectId,
      ),
      ProductSection.security => SecurityCapabilitiesScreen(
        api: widget.api,
        projectId: _projectId,
      ),
      ProductSection.engineering => EngineeringModeScreen(
        api: widget.api,
        projectId: _projectId,
      ),
      ProductSection.repository => RepositoryIntelligenceScreen(
        api: widget.api,
        projectId: _projectId,
      ),
      ProductSection.execution => ExecutionStudioScreen(
        api: widget.api,
        projectId: _projectId,
      ),
      ProductSection.agents => AgentOrchestrationScreen(
        api: widget.api,
        projectId: _projectId,
      ),
      ProductSection.lifecycle => DevelopmentLifecycleScreen(
        api: widget.api,
        projectId: _projectId,
      ),
      ProductSection.operations => OperationsScreen(
        api: widget.api,
        projectId: _projectId,
      ),
    };
  }

  Widget _desktopShell(DashboardView dashboard) => Scaffold(
    body: Row(
      textDirection: TextDirection.rtl,
      children: [
        SizedBox(
          width: 270,
          child: _DesktopNavigation(
            selected: _section,
            onSelected: _select,
            connectorState: dashboard.connector.state,
          ),
        ),
        const VerticalDivider(width: 1),
        Expanded(child: _body(dashboard)),
      ],
    ),
  );

  Widget _mobileShell(DashboardView dashboard) {
    final coreSections = const [
      ProductSection.assistant,
      ProductSection.dashboard,
      ProductSection.projects,
      ProductSection.explorer,
    ];
    final selectedIndex = coreSections.indexOf(_section);
    return Scaffold(
      appBar: AppBar(
        title: const Text('PalWakf Mind Assistant'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(left: 12),
            child: StatusPill(dashboard.connector.state),
          ),
        ],
      ),
      drawer: Drawer(
        child: SafeArea(
          child: _DestinationList(
            selected: _section,
            onSelected: (section) {
              Navigator.pop(context);
              _select(section);
            },
          ),
        ),
      ),
      body: _body(dashboard),
      bottomNavigationBar: NavigationBar(
        selectedIndex: selectedIndex < 0 ? 0 : selectedIndex,
        onDestinationSelected: (index) => _select(coreSections[index]),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.smart_toy_outlined),
            label: 'المساعد',
          ),
          NavigationDestination(
            icon: Icon(Icons.dashboard_outlined),
            label: 'التحكم',
          ),
          NavigationDestination(
            icon: Icon(Icons.folder_outlined),
            label: 'المشاريع',
          ),
          NavigationDestination(
            icon: Icon(Icons.manage_search),
            label: 'المعرفة',
          ),
        ],
      ),
    );
  }
}

class _DesktopNavigation extends StatelessWidget {
  const _DesktopNavigation({
    required this.selected,
    required this.onSelected,
    required this.connectorState,
  });

  final ProductSection selected;
  final ValueChanged<ProductSection> onSelected;
  final String connectorState;

  @override
  Widget build(BuildContext context) => Material(
    color: MindTheme.surface,
    child: SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const _Brand(),
            const SizedBox(height: 18),
            Expanded(
              child: SingleChildScrollView(
                child: _DestinationList(
                  selected: selected,
                  onSelected: onSelected,
                ),
              ),
            ),
            const Divider(),
            const SizedBox(height: 8),
            Row(
              children: [
                const CircleAvatar(child: Text('FF')),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'مدير النظام',
                        style: TextStyle(fontWeight: FontWeight.w700),
                      ),
                      const Text(
                        'READ ONLY',
                        style: TextStyle(color: MindTheme.muted, fontSize: 12),
                      ),
                      Text(
                        'Connector $connectorState',
                        style: const TextStyle(
                          color: MindTheme.muted,
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    ),
  );
}

class _Brand extends StatelessWidget {
  const _Brand();

  @override
  Widget build(BuildContext context) => const Row(
    children: [
      CircleAvatar(radius: 22, child: Icon(Icons.psychology_alt_outlined)),
      SizedBox(width: 10),
      Expanded(
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'PalWakf',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
              ),
              Text(
                'Mind Assistant',
                style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700),
              ),
            ],
          ),
        ),
      ),
    ],
  );
}

class _DestinationList extends StatelessWidget {
  const _DestinationList({required this.selected, required this.onSelected});

  final ProductSection selected;
  final ValueChanged<ProductSection> onSelected;

  @override
  Widget build(BuildContext context) {
    const destinations = [
      (ProductSection.assistant, Icons.smart_toy_outlined, 'المساعد الذكي'),
      (ProductSection.dashboard, Icons.dashboard_outlined, 'لوحة التحكم'),
      (ProductSection.projects, Icons.folder_outlined, 'Project Mind'),
      (ProductSection.explorer, Icons.manage_search, 'مستكشف المعرفة'),
      (ProductSection.skills, Icons.psychology_outlined, 'المهارات والدروس'),
      (ProductSection.planning, Icons.account_tree_outlined, 'التخطيط والأثر'),
      (
        ProductSection.decisions,
        Icons.fact_check_outlined,
        'القرارات والموافقات',
      ),
      (ProductSection.verification, Icons.verified_outlined, 'التحقق المستقل'),
      (ProductSection.security, Icons.security_outlined, 'الأمن والصلاحيات'),
      (
        ProductSection.engineering,
        Icons.engineering_outlined,
        'Engineering Mode',
      ),
      (
        ProductSection.repository,
        Icons.source_outlined,
        'Repository Intelligence',
      ),
      (
        ProductSection.execution,
        Icons.play_circle_outline,
        'Governed Execution',
      ),
      (ProductSection.agents, Icons.groups_outlined, 'Multi-Agent'),
      (ProductSection.lifecycle, Icons.route_outlined, 'Development Lifecycle'),
      (ProductSection.operations, Icons.monitor_heart_outlined, 'Operations'),
      (ProductSection.conflicts, Icons.balance_outlined, 'التعارضات'),
      (ProductSection.sources, Icons.hub_outlined, 'المصادر والاتصالات'),
    ];
    return SingleChildScrollView(
      child: Column(
        children:
            destinations
                .map(
                  (destination) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 3),
                    child: Material(
                      color: Colors.transparent,
                      child: ListTile(
                        selected: selected == destination.$1,
                        selectedTileColor: MindTheme.surfaceHigh,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        leading: Icon(destination.$2),
                        title: Text(destination.$3),
                        onTap: () => onSelected(destination.$1),
                      ),
                    ),
                  ),
                )
                .toList(),
      ),
    );
  }
}
