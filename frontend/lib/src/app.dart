import 'package:flutter/material.dart';

import 'api_client.dart';
import 'design/mind_theme.dart';
import 'shell/product_shell.dart';

class MindAssistantApp extends StatelessWidget {
  const MindAssistantApp({super.key, MindApi? api}) : _api = api;

  final MindApi? _api;

  @override
  Widget build(BuildContext context) => MaterialApp(
    debugShowCheckedModeBanner: false,
    title: 'PalWakf Mind Assistant',
    theme: MindTheme.dark(),
    locale: const Locale('ar'),
    builder:
        (context, child) => Directionality(
          textDirection: TextDirection.rtl,
          child: child ?? const SizedBox.shrink(),
        ),
    home: ProductShell(api: _api ?? MindApiClient()),
  );
}
