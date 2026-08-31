import 'package:flutter/material.dart';

import '../api_client.dart';
import '../models/api_models.dart';
import '../widgets/common.dart';

class ProjectMindScreen extends StatefulWidget {
  const ProjectMindScreen({
    super.key,
    required this.api,
    required this.projectId,
    required this.onProjectChanged,
    required this.projects,
  });

  final MindApi api;
  final String projectId;
  final ValueChanged<String> onProjectChanged;
  final List<ProjectSummaryView> projects;

  @override
  State<ProjectMindScreen> createState() => _ProjectMindScreenState();
}

class _ProjectMindScreenState extends State<ProjectMindScreen> {
  late Future<ProjectMindView> _future;

  @override
  void initState() {
    super.initState();
    _future = widget.api.fetchProjectMind(widget.projectId);
  }

  @override
  void didUpdateWidget(ProjectMindScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.projectId != widget.projectId) {
      _future = widget.api.fetchProjectMind(widget.projectId);
    }
  }

  @override
  Widget build(BuildContext context) => FutureBuilder<ProjectMindView>(
    future: _future,
    builder: (context, snapshot) {
      if (snapshot.connectionState != ConnectionState.done) {
        return const LoadingState();
      }
      if (snapshot.hasError) {
        return ErrorState(message: snapshot.error.toString());
      }
      final data = snapshot.data!;
      return ListView(
        padding: const EdgeInsets.all(24),
        children: [
          PageHeader(
            title: 'Project Mind',
            subtitle:
                'الحالة، السلطة، المصادر والتعارضات في سياق مشروع واحد دون إدارة الملفات يدويًا.',
            trailing: _ProjectSelector(
              value: widget.projectId,
              projects: widget.projects,
              onChanged: widget.onProjectChanged,
            ),
          ),
          const SizedBox(height: 20),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              StatusPill(data.authorityStatus),
              StatusPill(data.knowledgeHealth),
              const StatusPill('READ_ONLY'),
            ],
          ),
          const SizedBox(height: 18),
          if (data.digitalTwin != null) ...[
            SectionCard(
              title: 'Project Digital Twin — مشتق وقابل لإعادة البناء',
              icon: Icons.hub_outlined,
              child: _DigitalTwinSummary(twin: data.digitalTwin!),
            ),
            const SizedBox(height: 18),
          ],
          SectionCard(
            title: 'الحالة الحالية',
            icon: Icons.flag_outlined,
            child:
                data.currentState == null
                    ? const Text(
                      'لا يوجد PROJECT_CURRENT_STATE / CURRENT وحيد يمكن عرضه كحقيقة نهائية.',
                    )
                    : SourceTile(source: data.currentState!),
          ),
          const SizedBox(height: 18),
          SectionCard(
            title: 'المصادر ذات السلطة',
            icon: Icons.library_books_outlined,
            child:
                data.authoritativeSources.isEmpty
                    ? const Text('لا توجد مصادر ذات سلطة متاحة.')
                    : Column(
                      children:
                          data.authoritativeSources
                              .map((source) => SourceTile(source: source))
                              .toList(),
                    ),
          ),
          if (data.supersededSources.isNotEmpty) ...[
            const SizedBox(height: 18),
            SectionCard(
              title: 'مصادر تاريخية / Superseded',
              icon: Icons.history,
              child: Column(
                children:
                    data.supersededSources
                        .map((source) => SourceTile(source: source))
                        .toList(),
              ),
            ),
          ],
          const SizedBox(height: 18),
          SectionCard(
            title: 'التعارضات ومؤشرات المراجعة',
            icon: Icons.balance_outlined,
            child:
                data.conflicts.isEmpty
                    ? const Text(
                      'لا توجد مؤشرات تعارض هيكلي مثبتة في metadata الحالية.',
                    )
                    : Column(
                      children:
                          data.conflicts
                              .map(
                                (conflict) => ListTile(
                                  contentPadding: EdgeInsets.zero,
                                  leading: const Icon(
                                    Icons.report_problem_outlined,
                                  ),
                                  title: Text(conflict.title),
                                  subtitle: Text(conflict.detail),
                                  trailing: StatusPill(conflict.severity),
                                ),
                              )
                              .toList(),
                    ),
          ),
          if (data.unknownReasons.isNotEmpty) ...[
            const SizedBox(height: 18),
            SectionCard(
              title: 'أسباب UNKNOWN / PARTIAL',
              icon: Icons.help_outline,
              child: Text(data.unknownReasons.join('\n')),
            ),
          ],
        ],
      );
    },
  );
}

class _ProjectSelector extends StatelessWidget {
  const _ProjectSelector({
    required this.value,
    required this.projects,
    required this.onChanged,
  });

  final String value;
  final List<ProjectSummaryView> projects;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    final ids = projects.map((item) => item.projectId).toSet();
    final safeValue =
        ids.contains(value) ? value : (ids.isEmpty ? null : ids.first);
    return SizedBox(
      width: 250,
      child: DropdownButtonFormField<String>(
        initialValue: safeValue,
        isExpanded: true,
        decoration: const InputDecoration(labelText: 'المشروع'),
        items:
            projects
                .map(
                  (project) => DropdownMenuItem(
                    value: project.projectId,
                    child: Text(project.displayName),
                  ),
                )
                .toList(),
        onChanged: (next) {
          if (next != null) onChanged(next);
        },
      ),
    );
  }
}

class _DigitalTwinSummary extends StatelessWidget {
  const _DigitalTwinSummary({required this.twin});

  final ProjectDigitalTwinView twin;

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Wrap(
        spacing: 8,
        runSpacing: 8,
        children: [
          StatusPill('TWIN ${twin.status}'),
          StatusPill('TRUST ${twin.trustState}'),
          const StatusPill('DERIVED'),
          const StatusPill('READ_ONLY'),
          const StatusPill('NOT SOURCE OF TRUTH'),
        ],
      ),
      const SizedBox(height: 12),
      Text('Source mode: ${twin.sourceMode}'),
      Text('Repository: ${twin.repository ?? 'UNKNOWN'}'),
      Text('HEAD: ${twin.headSha ?? 'UNKNOWN'}'),
      Text('Task: ${twin.taskId ?? 'UNKNOWN'} / ${twin.taskStatus}'),
      Text('Baseline: ${twin.baselineRef ?? 'UNKNOWN'}'),
      Text(
        'Readiness: ${twin.productionReadinessLevel} / '
        '${twin.productionReadinessStatus}',
      ),
      const SizedBox(height: 12),
      Text(
        'Next safe action: ${twin.nextSafeAction}',
        style: Theme.of(context).textTheme.titleSmall,
      ),
      if (twin.driftIndicators.isNotEmpty) ...[
        const SizedBox(height: 12),
        const Text('Drift indicators:'),
        ...twin.driftIndicators.map(
          (item) => ListTile(
            contentPadding: EdgeInsets.zero,
            dense: true,
            leading: const Icon(Icons.warning_amber_outlined),
            title: Text(item.code),
            subtitle: Text(item.explanation),
            trailing: StatusPill(item.state),
          ),
        ),
      ],
    ],
  );
}
