import 'package:flutter/material.dart';

import '../api_client.dart';
import '../models/api_models.dart';
import '../widgets/common.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key, required this.api});

  final MindApi api;

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  late Future<DashboardView> _future;

  @override
  void initState() {
    super.initState();
    _future = widget.api.fetchDashboard();
  }

  void _reload() => setState(() => _future = widget.api.fetchDashboard());

  @override
  Widget build(BuildContext context) => FutureBuilder<DashboardView>(
    future: _future,
    builder: (context, snapshot) {
      if (snapshot.connectionState != ConnectionState.done) {
        return const LoadingState();
      }
      if (snapshot.hasError) {
        return ErrorState(message: snapshot.error.toString(), onRetry: _reload);
      }
      final data = snapshot.data!;
      return ListView(
        padding: const EdgeInsets.all(24),
        children: [
          PageHeader(
            title: 'لوحة التحكم والمعرفة',
            subtitle:
                'صورة تشغيلية واحدة للسلطة المعرفية، صحة المصادر، التعارضات وحالة الموصل.',
            trailing: StatusPill(data.mutationMode),
          ),
          const SizedBox(height: 20),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              MetricCard(
                label: 'المشاريع',
                value: '${data.counts['total'] ?? 0}',
                icon: Icons.folder_outlined,
              ),
              MetricCard(
                label: 'محسومة السلطة',
                value: '${data.counts['resolved'] ?? 0}',
                icon: Icons.verified_outlined,
              ),
              MetricCard(
                label: 'UNKNOWN / PARTIAL',
                value:
                    '${(data.counts['unknown'] ?? 0) + (data.counts['partial'] ?? 0)}',
                icon: Icons.help_outline,
              ),
              MetricCard(
                label: 'مؤشرات التعارض',
                value: '${data.counts['conflicts'] ?? 0}',
                icon: Icons.balance_outlined,
              ),
            ],
          ),
          const SizedBox(height: 18),
          SectionCard(
            title: 'المشاريع وحالة المعرفة',
            icon: Icons.account_tree_outlined,
            child: Column(
              children:
                  data.projects
                      .map(
                        (project) => Material(
                          color: Colors.transparent,
                          child: ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.folder_copy_outlined),
                            title: Text(project.displayName),
                            subtitle: Text(
                              '${project.currentStateTitle ?? 'لا يوجد Current State محسوم'}\n${project.knowledgeHealth}',
                            ),
                            trailing: StatusPill(project.authorityStatus),
                          ),
                        ),
                      )
                      .toList(),
            ),
          ),
          const SizedBox(height: 18),
          SectionCard(
            title: 'الموصل ومصدر الحقيقة',
            icon: Icons.hub_outlined,
            child: Wrap(
              spacing: 12,
              runSpacing: 10,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                StatusPill(data.connector.state),
                StatusPill(data.connector.mutationMode),
                Text('${data.connector.connector} / ${data.connector.mode}'),
                Text('المصادر: ${data.connector.sourceCount}'),
                Text(data.connector.detail),
              ],
            ),
          ),
          const SizedBox(height: 18),
          SectionCard(
            title: 'التنبيهات',
            icon: Icons.notifications_active_outlined,
            child:
                data.alerts.isEmpty
                    ? const Text('لا توجد تنبيهات حالية.')
                    : Column(
                      children:
                          data.alerts
                              .map(
                                (alert) => Material(
                                  color: Colors.transparent,
                                  child: ListTile(
                                    contentPadding: EdgeInsets.zero,
                                    leading: const Icon(Icons.info_outline),
                                    title: Text(alert),
                                  ),
                                ),
                              )
                              .toList(),
                    ),
          ),
        ],
      );
    },
  );
}
