import 'package:flutter/material.dart';

import '../api_client.dart';
import '../models/api_models.dart';
import '../widgets/common.dart';

class AssistantScreen extends StatefulWidget {
  const AssistantScreen({
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
  State<AssistantScreen> createState() => _AssistantScreenState();
}

class _AssistantScreenState extends State<AssistantScreen> {
  final _controller = TextEditingController(
    text: 'ما آخر حالة معتمدة للمشروع؟',
  );
  final List<_ConversationItem> _history = [];
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _send([String? suggested]) async {
    final message = (suggested ?? _controller.text).trim();
    if (message.isEmpty || _loading) return;
    setState(() {
      _loading = true;
      _error = null;
      _history.add(_ConversationItem.user(message));
      _controller.clear();
    });
    try {
      final answer = await widget.api.ask(message, projectId: widget.projectId);
      if (!mounted) return;
      setState(() => _history.add(_ConversationItem.assistant(answer)));
    } catch (error) {
      if (!mounted) return;
      setState(() => _error = error.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.all(24),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        PageHeader(
          title: 'مساعد PalWakf الذكي',
          subtitle:
              'حوار معرفي مقيد بالسلطة والمصدر. UNKNOWN يبقى UNKNOWN ولا توجد كتابة إلى المصادر السيادية.',
          trailing: SizedBox(
            width: 250,
            child: DropdownButtonFormField<String>(
              initialValue:
                  widget.projects.any(
                        (item) => item.projectId == widget.projectId,
                      )
                      ? widget.projectId
                      : null,
              isExpanded: true,
              decoration: const InputDecoration(labelText: 'سياق المشروع'),
              items:
                  widget.projects
                      .map(
                        (project) => DropdownMenuItem(
                          value: project.projectId,
                          child: Text(project.displayName),
                        ),
                      )
                      .toList(),
              onChanged: (value) {
                if (value != null) widget.onProjectChanged(value);
              },
            ),
          ),
        ),
        const SizedBox(height: 14),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            ActionChip(
              label: const Text('ما الحالة الحالية؟'),
              onPressed: () => _send('ما الحالة الحالية؟'),
            ),
            ActionChip(
              label: const Text('ما المصادر؟'),
              onPressed: () => _send('ما المصادر المعتمدة؟'),
            ),
            ActionChip(
              label: const Text('هل توجد تعارضات؟'),
              onPressed: () => _send('هل توجد تعارضات؟'),
            ),
          ],
        ),
        const SizedBox(height: 14),
        Expanded(
          child:
              _history.isEmpty
                  ? const _AssistantWelcome()
                  : ListView.separated(
                    itemCount: _history.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 12),
                    itemBuilder:
                        (context, index) =>
                            _ConversationBubble(item: _history[index]),
                  ),
        ),
        if (_error != null) ...[
          const SizedBox(height: 8),
          Text(
            _error!,
            style: TextStyle(color: Theme.of(context).colorScheme.error),
          ),
        ],
        if (_loading) const LinearProgressIndicator(),
        const SizedBox(height: 10),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _controller,
                minLines: 1,
                maxLines: 4,
                onSubmitted: (_) => _send(),
                decoration: const InputDecoration(
                  hintText: 'ناقش حالة، قرارًا، مصدرًا أو تعارضًا…',
                  prefixIcon: Icon(Icons.attach_file),
                ),
              ),
            ),
            const SizedBox(width: 10),
            FilledButton.icon(
              onPressed: _loading ? null : _send,
              icon: const Icon(Icons.send),
              label: const Text('إرسال'),
            ),
          ],
        ),
      ],
    ),
  );
}

class _AssistantWelcome extends StatelessWidget {
  const _AssistantWelcome();

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder:
        (context, constraints) => SingleChildScrollView(
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 700),
                child: const SectionCard(
                  title: 'ابدأ من المعرفة وليس من الملفات',
                  icon: Icons.psychology_outlined,
                  child: Text(
                    'اختر مشروعًا ثم اسأل عن حالته أو مصادره أو التعارضات. الوضع الحالي Deterministic Grounded؛ '
                    'أي نموذج ذكاء لاحق سيبقى خلف نفس حدود السلطة والمصدر.',
                    textAlign: TextAlign.center,
                  ),
                ),
              ),
            ),
          ),
        ),
  );
}

class _ConversationItem {
  const _ConversationItem._({
    required this.user,
    required this.text,
    this.answer,
  });

  factory _ConversationItem.user(String text) =>
      _ConversationItem._(user: true, text: text);
  factory _ConversationItem.assistant(AssistantAnswerView answer) =>
      _ConversationItem._(user: false, text: answer.answer, answer: answer);

  final bool user;
  final String text;
  final AssistantAnswerView? answer;
}

class _ConversationBubble extends StatelessWidget {
  const _ConversationBubble({required this.item});

  final _ConversationItem item;

  @override
  Widget build(BuildContext context) {
    final answer = item.answer;
    return Align(
      alignment: item.user ? Alignment.centerRight : Alignment.centerLeft,
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 780),
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(item.text, style: const TextStyle(height: 1.6)),
                if (answer != null) ...[
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      StatusPill(answer.status),
                      StatusPill(answer.confidence),
                      StatusPill(answer.mutationMode),
                      StatusPill(answer.providerMode),
                    ],
                  ),
                  if (answer.context != null) ...[
                    const SizedBox(height: 10),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        StatusPill('TRUST ${answer.context!.trustState}'),
                        StatusPill('AUTH ${answer.context!.authorityStatus}'),
                        StatusPill(answer.context!.intent),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Context: ${answer.context!.contextId}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    if (answer.context!.risks.isNotEmpty)
                      Text('مخاطر الثقة: ${answer.context!.risks.join(' | ')}'),
                  ],
                  if (answer.unknownReasons.isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Text('أسباب التحفظ: ${answer.unknownReasons.join(' | ')}'),
                  ],
                  if (answer.citations.isNotEmpty) ...[
                    const Divider(height: 28),
                    const Text(
                      'المصادر',
                      style: TextStyle(fontWeight: FontWeight.w800),
                    ),
                    ...answer.citations.map(
                      (source) => SourceTile(source: source),
                    ),
                  ],
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
