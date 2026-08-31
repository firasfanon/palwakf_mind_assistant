import 'package:flutter/material.dart';

import '../api_client.dart';
import '../models/api_models.dart';
import '../widgets/common.dart';

class SkillsScreen extends StatefulWidget {
  const SkillsScreen({super.key, required this.api, required this.projectId});

  final MindApi api;
  final String projectId;

  @override
  State<SkillsScreen> createState() => _SkillsScreenState();
}

class _SkillsScreenState extends State<SkillsScreen> {
  late Future<List<SkillView>> _skills;
  SkillResolutionView? _resolution;
  bool _resolving = false;

  @override
  void initState() {
    super.initState();
    _skills = widget.api.fetchSkills();
  }

  Future<void> _resolve(String message) async {
    setState(() => _resolving = true);
    try {
      final result = await widget.api.resolveSkills(
        message,
        projectId: widget.projectId,
      );
      if (mounted) setState(() => _resolution = result);
    } finally {
      if (mounted) setState(() => _resolving = false);
    }
  }

  @override
  Widget build(BuildContext context) => FutureBuilder<List<SkillView>>(
    future: _skills,
    builder: (context, snapshot) {
      if (snapshot.connectionState != ConnectionState.done) {
        return const LoadingState(label: 'جارٍ تحميل سجل المهارات…');
      }
      if (snapshot.hasError) {
        return ErrorState(message: snapshot.error.toString());
      }
      final skills = snapshot.data ?? const <SkillView>[];
      return ListView(
        padding: const EdgeInsets.all(24),
        children: [
          const PageHeader(
            title: 'Skills & Lessons',
            subtitle:
                'سجل مشتق للقراءة فقط. اختيار المهارة لا يمنح صلاحية تنفيذ أو تعديل.',
          ),
          const SizedBox(height: 18),
          SectionCard(
            title: 'اختبار Applicability',
            icon: Icons.rule_folder_outlined,
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                FilledButton.tonal(
                  onPressed:
                      _resolving
                          ? null
                          : () => _resolve('Flutter browser responsive UAT'),
                  child: const Text('Flutter UAT'),
                ),
                FilledButton.tonal(
                  onPressed:
                      _resolving
                          ? null
                          : () => _resolve(
                            'Build ZIP artifact with PowerShell runner',
                          ),
                  child: const Text('Artifact handoff'),
                ),
                FilledButton.tonal(
                  onPressed:
                      _resolving
                          ? null
                          : () => _resolve(
                            'استئناف المشروع reconcile GitHub Drive',
                          ),
                  child: const Text('Resume / Reconcile'),
                ),
              ],
            ),
          ),
          if (_resolution != null) ...[
            const SizedBox(height: 14),
            SectionCard(
              title: 'Applicable Skills',
              icon: Icons.fact_check_outlined,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      StatusPill(_resolution!.registrySourceMode),
                      StatusPill(_resolution!.mutationMode),
                      const StatusPill('EXECUTION NOT AUTHORIZED'),
                    ],
                  ),
                  const SizedBox(height: 12),
                  for (final item in _resolution!.selections)
                    ListTile(
                      contentPadding: EdgeInsets.zero,
                      leading: const Icon(Icons.psychology_outlined),
                      title: Text(item.skillId),
                      subtitle: Text(
                        '${item.level} • score ${item.score} • ${item.reasons.join(', ')}',
                      ),
                      trailing: const StatusPill('READ ONLY'),
                    ),
                ],
              ),
            ),
          ],
          const SizedBox(height: 14),
          SectionCard(
            title: 'Skill Registry',
            icon: Icons.library_books_outlined,
            child: Column(
              children: [
                for (final skill in skills)
                  ListTile(
                    contentPadding: EdgeInsets.zero,
                    title: Text(skill.skillId),
                    subtitle: Text(
                      '${skill.level} • ${skill.ownerScope} • ${skill.provenanceRef}',
                    ),
                    trailing: StatusPill(skill.status),
                  ),
              ],
            ),
          ),
        ],
      );
    },
  );
}
