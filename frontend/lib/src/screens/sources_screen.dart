import 'package:flutter/material.dart';

import '../api_client.dart';
import '../models/api_models.dart';
import '../widgets/common.dart';

class SourcesScreen extends StatefulWidget {
  const SourcesScreen({super.key, required this.api, required this.projectId});

  final MindApi api;
  final String projectId;

  @override
  State<SourcesScreen> createState() => _SourcesScreenState();
}

class _SourcesScreenState extends State<SourcesScreen> {
  late Future<(ConnectorHealthView, ProjectMindView)> _future;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void didUpdateWidget(SourcesScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.projectId != widget.projectId) _load();
  }

  void _load() {
    _future = Future.wait<dynamic>([
      widget.api.fetchConnectorHealth(),
      widget.api.fetchProjectMind(widget.projectId),
    ]).then(
      (values) => (
        values[0] as ConnectorHealthView,
        values[1] as ProjectMindView,
      ),
    );
  }

  @override
  Widget build(
    BuildContext context,
  ) => FutureBuilder<(ConnectorHealthView, ProjectMindView)>(
    future: _future,
    builder: (context, snapshot) {
      if (snapshot.connectionState != ConnectionState.done) {
        return const LoadingState();
      }
      if (snapshot.hasError) {
        return ErrorState(message: snapshot.error.toString());
      }
      final (connector, mind) = snapshot.data!;
      return ListView(
        padding: const EdgeInsets.all(24),
        children: [
          const PageHeader(
            title: 'المصادر والاتصالات',
            subtitle:
                'شفافية كاملة حول مصدر المعرفة، وضع الموصل وحدود القراءة. لا توجد أدوات كتابة في هذه الدفعة.',
          ),
          const SizedBox(height: 20),
          SectionCard(
            title: 'حالة الموصل',
            icon: Icons.hub_outlined,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    StatusPill(connector.state),
                    StatusPill(connector.mutationMode),
                    StatusPill(
                      connector.writesEnabled ? 'WRITES_ON' : 'WRITES_OFF',
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Text('${connector.connector} / ${connector.mode}'),
                Text(connector.detail),
              ],
            ),
          ),
          const SizedBox(height: 18),
          SectionCard(
            title: 'مصادر المشروع',
            icon: Icons.source_outlined,
            child:
                mind.authoritativeSources.isEmpty
                    ? const Text('لا توجد مصادر متاحة في النطاق الحالي.')
                    : Column(
                      children:
                          mind.authoritativeSources
                              .map((source) => SourceTile(source: source))
                              .toList(),
                    ),
          ),
        ],
      );
    },
  );
}
