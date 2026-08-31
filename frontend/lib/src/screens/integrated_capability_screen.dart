import 'package:flutter/material.dart';

import '../api_client.dart';
import '../design/mind_theme.dart';
import '../models/api_models.dart';
import '../widgets/common.dart';

class IntegratedCapabilityScreen extends StatefulWidget {
  const IntegratedCapabilityScreen({
    super.key,
    required this.api,
    required this.projectId,
    required this.surface,
  });

  final MindApi api;
  final String projectId;
  final String surface;

  @override
  State<IntegratedCapabilityScreen> createState() =>
      _IntegratedCapabilityScreenState();
}

class _IntegratedCapabilityScreenState
    extends State<IntegratedCapabilityScreen> {
  late Future<GovernedCapabilityView> _future;

  @override
  void initState() {
    super.initState();
    _future = widget.api.fetchIntegratedSurface(
      widget.surface,
      widget.projectId,
    );
  }

  @override
  void didUpdateWidget(covariant IntegratedCapabilityScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.projectId != widget.projectId ||
        oldWidget.surface != widget.surface) {
      _future = widget.api.fetchIntegratedSurface(
        widget.surface,
        widget.projectId,
      );
    }
  }

  @override
  Widget build(BuildContext context) => FutureBuilder<GovernedCapabilityView>(
    future: _future,
    builder: (context, snapshot) {
      if (snapshot.connectionState != ConnectionState.done) {
        return const LoadingState(label: 'جارٍ تحميل السطح المحكوم…');
      }
      if (snapshot.hasError) {
        return ErrorState(
          message: snapshot.error.toString(),
          onRetry:
              () => setState(
                () =>
                    _future = widget.api.fetchIntegratedSurface(
                      widget.surface,
                      widget.projectId,
                    ),
              ),
        );
      }
      final view = snapshot.data!;
      return ListView(
        padding: const EdgeInsets.all(20),
        children: [
          PageHeader(
            title: view.title,
            subtitle:
                'سطح مشتق ومحكوم. لا يمنح وجود الخطة أو المهارة أو الأداة '
                'صلاحية تنفيذ أو كتابة سيادية.',
            trailing: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                StatusPill(view.trustLabel),
                StatusPill(view.mutationMode),
                StatusPill(view.authorizationLabel),
              ],
            ),
          ),
          const SizedBox(height: 18),
          SectionCard(
            title: 'Authority & Trust Boundary',
            icon: Icons.verified_user_outlined,
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: const [
                StatusPill('DERIVED'),
                StatusPill('FIXTURE_DERIVED'),
                StatusPill('NOT SOURCE OF TRUTH'),
                StatusPill('HUMAN REVIEW'),
              ],
            ),
          ),
          const SizedBox(height: 14),
          SectionCard(
            title: 'Governed capability',
            icon: Icons.account_tree_outlined,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                for (final detail in view.details) ...[
                  SelectableText(
                    detail,
                    style: const TextStyle(color: MindTheme.muted, height: 1.5),
                  ),
                  const SizedBox(height: 8),
                ],
              ],
            ),
          ),
          const SizedBox(height: 14),
          SectionCard(
            title: 'Execution boundary',
            icon: Icons.lock_outline,
            child: Text(
              view.authorizationLabel == 'EXECUTION AUTHORIZED'
                  ? 'Authorization is visible and scoped; independent post-run '
                      'verification remains mandatory.'
                  : 'No real external mutation is authorized from this surface. '
                      'Simulation, review and evidence are allowed only within '
                      'the displayed envelope.',
              style: const TextStyle(color: MindTheme.muted, height: 1.5),
            ),
          ),
        ],
      );
    },
  );
}
