import 'package:flutter/material.dart';

class MindTheme {
  static const Color canvas = Color(0xFF07111E);
  static const Color surface = Color(0xFF0E1A2A);
  static const Color surfaceHigh = Color(0xFF13243A);
  static const Color accent = Color(0xFF5C9DFF);
  static const Color current = Color(0xFF49C28D);
  static const Color review = Color(0xFFFFC857);
  static const Color critical = Color(0xFFFF6B6B);
  static const Color muted = Color(0xFF93A4B8);

  static ThemeData dark() {
    final scheme = ColorScheme.fromSeed(
      seedColor: accent,
      brightness: Brightness.dark,
      surface: surface,
    );
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: scheme,
      scaffoldBackgroundColor: canvas,
      cardTheme: const CardThemeData(color: surface, margin: EdgeInsets.zero),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surface,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide.none,
        ),
      ),
      navigationBarTheme: const NavigationBarThemeData(
        backgroundColor: surface,
        indicatorColor: surfaceHigh,
      ),
      dividerTheme: const DividerThemeData(color: Color(0xFF20344E)),
    );
  }
}
