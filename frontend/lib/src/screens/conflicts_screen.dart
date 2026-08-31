import 'package:flutter/material.dart';

import '../api_client.dart';
import '../models/api_models.dart';
import '../widgets/common.dart';

class ConflictsScreen extends StatefulWidget {
  const ConflictsScreen({
    super.key,
    required this.api,
    required this.projectId,
  });

  final MindApi api;
  final String projectId;

  @override
  State<ConflictsScreen> createState() => _ConflictsScreenState();
}

class _ConflictsScreenState extends State<ConflictsScreen> {
  late Future<List<ConflictView>> _future;

  @override
  void initState() {
    super.initState();
    _future = widget.api.fetchConflicts(widget.projectId);
  }

  @override
  void didUpdateWidget(ConflictsScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.projectId != widget.projectId) {
      _future = widget.api.fetchConflicts(widget.projectId);
    }
  }

  @override
  Widget build(BuildContext context) => FutureBuilder<List<ConflictView>>(
    future: _future,
    builder: (context, snapshot) {
      if (snapshot.connectionState != ConnectionState.done) {
        return const LoadingState();
      }
      if (snapshot.hasError) {
        return ErrorState(message: snapshot.error.toString());
      }
      final conflicts = snapshot.data!;
      return ListView(
        padding: const EdgeInsets.all(24),
        children: [
          const PageHeader(
            title: 'مركز التعارضات',
            subtitle:
                'يفصل بين مؤشرات التعارض الهيكلي والتعارض الدلالي. لا يوجد حسم آلي للمعرفة السيادية.',
          ),
          const SizedBox(height: 20),
          if (conflicts.isEmpty)
            const SectionCard(
              title: 'لا يوجد تعارض هيكلي مثبت',
              icon: Icons.verified_outlined,
              child: Text(
                'هذه النتيجة لا تثبت غياب التعارض الدلالي داخل محتوى الوثائق؛ فقط لا يوجد نمط Metadata متعارض مكتشف.',
              ),
            )
          else
            ...conflicts.map(
              (conflict) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: SectionCard(
                  title: conflict.title,
                  icon: Icons.report_problem_outlined,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(conflict.detail),
                      const SizedBox(height: 10),
                      Wrap(
                        spacing: 8,
                        children: [
                          StatusPill(conflict.severity),
                          StatusPill(conflict.conflictType),
                        ],
                      ),
                      if (conflict.sourceRefs.isNotEmpty) ...[
                        const SizedBox(height: 10),
                        Text(conflict.sourceRefs.join('\n')),
                      ],
                    ],
                  ),
                ),
              ),
            ),
        ],
      );
    },
  );
}
