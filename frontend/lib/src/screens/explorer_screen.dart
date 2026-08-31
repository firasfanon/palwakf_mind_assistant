import 'package:flutter/material.dart';

import '../api_client.dart';
import '../models/api_models.dart';
import '../widgets/common.dart';

class ExplorerScreen extends StatefulWidget {
  const ExplorerScreen({
    super.key,
    required this.api,
    required this.projectId,
    required this.projects,
  });

  final MindApi api;
  final String projectId;
  final List<ProjectSummaryView> projects;

  @override
  State<ExplorerScreen> createState() => _ExplorerScreenState();
}

class _ExplorerScreenState extends State<ExplorerScreen> {
  final _controller = TextEditingController(text: 'CURRENT_STATE');
  SearchResponseView? _result;
  String? _error;
  bool _loading = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _search() async {
    final query = _controller.text.trim();
    if (query.isEmpty) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final result = await widget.api.search(
        query,
        projectId: widget.projectId,
      );
      if (mounted) setState(() => _result = result);
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => ListView(
    padding: const EdgeInsets.all(24),
    children: [
      const PageHeader(
        title: 'مستكشف المعرفة',
        subtitle:
            'بحث Metadata حاكم بالمشروع والسلطة والحالة؛ التشابه النصي لا يرقّي مصدرًا إلى حقيقة.',
      ),
      const SizedBox(height: 20),
      Row(
        children: [
          Expanded(
            child: TextField(
              controller: _controller,
              onSubmitted: (_) => _search(),
              decoration: const InputDecoration(
                labelText: 'ابحث في العنوان أو Source Ref أو نوع السلطة',
                prefixIcon: Icon(Icons.search),
              ),
            ),
          ),
          const SizedBox(width: 10),
          FilledButton.icon(
            onPressed: _loading ? null : _search,
            icon: const Icon(Icons.search),
            label: const Text('بحث'),
          ),
        ],
      ),
      if (_loading) ...[
        const SizedBox(height: 16),
        const LinearProgressIndicator(),
      ],
      if (_error != null) ...[
        const SizedBox(height: 16),
        ErrorState(message: _error!),
      ],
      const SizedBox(height: 20),
      SectionCard(
        title:
            _result == null ? 'النتائج' : 'النتائج (${_result!.hits.length})',
        icon: Icons.manage_search,
        child:
            _result == null
                ? const Text('نفّذ بحثًا لعرض النتائج.')
                : _result!.hits.isEmpty
                ? const Text('لا توجد مطابقة ضمن النطاق الحالي.')
                : Column(
                  children:
                      _result!.hits
                          .map(
                            (hit) => ListTile(
                              contentPadding: EdgeInsets.zero,
                              leading: const Icon(Icons.description_outlined),
                              title: Text(hit.title),
                              subtitle: Text(
                                '${hit.projectId} • ${hit.authorityType} • ${hit.sourceRef}',
                              ),
                              trailing: StatusPill(hit.lifecycleStatus),
                            ),
                          )
                          .toList(),
                ),
      ),
    ],
  );
}
