import 'package:flutter/material.dart';

import '../api_client.dart';
import 'integrated_capability_screen.dart';

class OperationsScreen extends StatelessWidget {
  const OperationsScreen({
    super.key,
    required this.api,
    required this.projectId,
  });

  final MindApi api;
  final String projectId;

  @override
  Widget build(BuildContext context) => IntegratedCapabilityScreen(
    api: api,
    projectId: projectId,
    surface: 'operations',
  );
}
