import 'package:flutter/material.dart';

import '../design/mind_theme.dart';
import '../models/api_models.dart';

class PageHeader extends StatelessWidget {
  const PageHeader({
    super.key,
    required this.title,
    required this.subtitle,
    this.trailing,
  });

  final String title;
  final String subtitle;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, constraints) {
      final heading = Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(
              context,
            ).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 6),
          Text(
            subtitle,
            style: const TextStyle(color: MindTheme.muted, height: 1.5),
          ),
        ],
      );
      if (constraints.maxWidth < 620 && trailing != null) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [heading, const SizedBox(height: 12), trailing!],
        );
      }
      return Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(child: heading),
          if (trailing != null) ...[const SizedBox(width: 12), trailing!],
        ],
      );
    },
  );
}

class StatusPill extends StatelessWidget {
  const StatusPill(this.label, {super.key});

  final String label;

  Color _color() {
    final value = label.toUpperCase();
    if (value.contains('CURRENT') ||
        value.contains('RESOLVED') ||
        value.contains('READY') ||
        value.contains('HEALTHY')) {
      return MindTheme.current;
    }
    if (value.contains('BLOCK') ||
        value.contains('CONFLICT') ||
        value.contains('FAIL')) {
      return MindTheme.critical;
    }
    if (value.contains('UNKNOWN') ||
        value.contains('REVIEW') ||
        value.contains('PARTIAL') ||
        value.contains('DEGRADED')) {
      return MindTheme.review;
    }
    return MindTheme.accent;
  }

  @override
  Widget build(BuildContext context) {
    final color = _color();
    return Semantics(
      label: 'الحالة $label',
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: color.withValues(alpha: 0.55)),
          color: color.withValues(alpha: 0.12),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: color,
            fontSize: 12,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    );
  }
}

class SectionCard extends StatelessWidget {
  const SectionCard({
    super.key,
    required this.title,
    required this.child,
    this.icon,
  });

  final String title;
  final Widget child;
  final IconData? icon;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              if (icon != null) ...[
                Icon(icon, size: 20),
                const SizedBox(width: 8),
              ],
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          child,
        ],
      ),
    ),
  );
}

class MetricCard extends StatelessWidget {
  const MetricCard({
    super.key,
    required this.label,
    required this.value,
    required this.icon,
  });

  final String label;
  final String value;
  final IconData icon;

  @override
  Widget build(BuildContext context) => SizedBox(
    width: 190,
    child: Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon),
            const SizedBox(height: 10),
            Text(
              value,
              style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w800),
            ),
            Text(label, style: const TextStyle(color: MindTheme.muted)),
          ],
        ),
      ),
    ),
  );
}

class SourceTile extends StatelessWidget {
  const SourceTile({super.key, required this.source});

  final SourceView source;

  @override
  Widget build(BuildContext context) => Material(
    color: Colors.transparent,
    child: ListTile(
      contentPadding: EdgeInsets.zero,
      leading: const Icon(Icons.description_outlined),
      title: Text(source.title, maxLines: 2, overflow: TextOverflow.ellipsis),
      subtitle: Text(
        '${source.authorityType} • ${source.sourceRef}',
        maxLines: 2,
        overflow: TextOverflow.ellipsis,
      ),
      trailing: StatusPill(source.lifecycleStatus),
    ),
  );
}

class ErrorState extends StatelessWidget {
  const ErrorState({super.key, required this.message, this.onRetry});

  final String message;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) => Center(
    child: ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 560),
      child: SectionCard(
        title: 'تعذر تحميل السطح',
        icon: Icons.error_outline,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(message, style: const TextStyle(color: MindTheme.muted)),
            if (onRetry != null) ...[
              const SizedBox(height: 12),
              Align(
                alignment: Alignment.centerRight,
                child: OutlinedButton.icon(
                  onPressed: onRetry,
                  icon: const Icon(Icons.refresh),
                  label: const Text('إعادة المحاولة'),
                ),
              ),
            ],
          ],
        ),
      ),
    ),
  );
}

class LoadingState extends StatelessWidget {
  const LoadingState({
    super.key,
    this.label = 'جارٍ تحميل المعرفة المصرح بها…',
  });

  final String label;

  @override
  Widget build(BuildContext context) => Center(
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const CircularProgressIndicator(),
        const SizedBox(height: 14),
        Text(label, style: const TextStyle(color: MindTheme.muted)),
      ],
    ),
  );
}
