import 'dart:convert';

import 'package:http/http.dart' as http;

import 'models/api_models.dart';

abstract class MindApi {
  Future<DashboardView> fetchDashboard();
  Future<AssistantAnswerView> ask(String message, {String? projectId});
  Future<ProjectMindView> fetchProjectMind(String projectId);
  Future<ProjectDigitalTwinView> fetchDigitalTwin(String projectId);
  Future<SearchResponseView> search(String query, {String? projectId});
  Future<List<ConflictView>> fetchConflicts(String projectId);
  Future<ConnectorHealthView> fetchConnectorHealth();
  Future<List<SkillView>> fetchSkills();
  Future<SkillResolutionView> resolveSkills(
    String message, {
    String? projectId,
  });

  Future<GovernedCapabilityView> fetchIntegratedSurface(
    String surface,
    String projectId,
  );
}

class MindApiClient implements MindApi {
  MindApiClient({
    this.baseUrl = const String.fromEnvironment(
      'MIND_API_BASE_URL',
      defaultValue: 'http://127.0.0.1:8000',
    ),
  });

  final String baseUrl;

  Future<Map<String, dynamic>> _getJson(Uri uri) async {
    final response = await http.get(
      uri,
      headers: const {'X-Request-ID': 'flutter-ui'},
    );
    if (response.statusCode != 200) {
      throw StateError('HTTP_${response.statusCode}:${uri.path}');
    }
    return jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> _postJson(
    Uri uri,
    Map<String, dynamic> body,
  ) async {
    final response = await http.post(
      uri,
      headers: const {
        'content-type': 'application/json; charset=utf-8',
        'X-Request-ID': 'flutter-integrated-surface',
      },
      body: jsonEncode(body),
    );
    if (response.statusCode != 200) {
      throw StateError('HTTP_${response.statusCode}:${uri.path}');
    }
    return jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
  }

  @override
  Future<DashboardView> fetchDashboard() async => DashboardView.fromJson(
    await _getJson(Uri.parse('$baseUrl/v1/dashboard')),
  );

  @override
  Future<AssistantAnswerView> ask(String message, {String? projectId}) async {
    final response = await http.post(
      Uri.parse('$baseUrl/v1/assistant/ask'),
      headers: const {
        'content-type': 'application/json; charset=utf-8',
        'X-Request-ID': 'flutter-assistant',
      },
      body: jsonEncode({
        'message': message,
        if (projectId != null) 'project_id': projectId,
      }),
    );
    if (response.statusCode != 200) {
      throw StateError('ASSISTANT_HTTP_${response.statusCode}');
    }
    return AssistantAnswerView.fromJson(
      jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>,
    );
  }

  @override
  Future<ProjectMindView> fetchProjectMind(String projectId) async =>
      ProjectMindView.fromJson(
        await _getJson(Uri.parse('$baseUrl/v1/projects/$projectId/mind')),
      );

  @override
  Future<ProjectDigitalTwinView> fetchDigitalTwin(String projectId) async =>
      ProjectDigitalTwinView.fromJson(
        await _getJson(
          Uri.parse('$baseUrl/v1/projects/$projectId/digital-twin'),
        ),
      );

  @override
  Future<SearchResponseView> search(String query, {String? projectId}) async {
    final params = <String, String>{'q': query};
    if (projectId != null && projectId.isNotEmpty) {
      params['project_id'] = projectId;
    }
    final uri = Uri.parse(
      '$baseUrl/v1/knowledge/search',
    ).replace(queryParameters: params);
    return SearchResponseView.fromJson(await _getJson(uri));
  }

  @override
  Future<List<ConflictView>> fetchConflicts(String projectId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/v1/conflicts/$projectId'),
      headers: const {'X-Request-ID': 'flutter-conflicts'},
    );
    if (response.statusCode != 200) {
      throw StateError('CONFLICTS_HTTP_${response.statusCode}');
    }
    final payload =
        jsonDecode(utf8.decode(response.bodyBytes)) as List<dynamic>;
    return payload
        .whereType<Map>()
        .map((item) => ConflictView.fromJson(item.cast<String, dynamic>()))
        .toList(growable: false);
  }

  @override
  Future<List<SkillView>> fetchSkills() async {
    final response = await http.get(
      Uri.parse('$baseUrl/v1/skills'),
      headers: const {'X-Request-ID': 'flutter-skills'},
    );
    if (response.statusCode != 200) {
      throw StateError('SKILLS_HTTP_${response.statusCode}');
    }
    final payload =
        jsonDecode(utf8.decode(response.bodyBytes)) as List<dynamic>;
    return payload
        .whereType<Map>()
        .map((item) => SkillView.fromJson(item.cast<String, dynamic>()))
        .toList(growable: false);
  }

  @override
  Future<SkillResolutionView> resolveSkills(
    String message, {
    String? projectId,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/v1/skills/resolve'),
      headers: const {
        'content-type': 'application/json; charset=utf-8',
        'X-Request-ID': 'flutter-skill-resolver',
      },
      body: jsonEncode({
        'message': message,
        if (projectId != null) 'project_id': projectId,
      }),
    );
    if (response.statusCode != 200) {
      throw StateError('SKILL_RESOLVE_HTTP_${response.statusCode}');
    }
    return SkillResolutionView.fromJson(
      jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>,
    );
  }

  @override
  Future<GovernedCapabilityView> fetchIntegratedSurface(
    String surface,
    String projectId,
  ) async {
    final Map<String, dynamic> payload;
    if (surface == 'planning') {
      payload = await _postJson(Uri.parse('$baseUrl/v1/planning'), {
        'project_id': projectId,
        'goal': 'Build a governed project development plan',
      });
    } else if (surface == 'decisions') {
      payload = await _postJson(Uri.parse('$baseUrl/v1/decisions'), {
        'project_id': projectId,
        'title': 'Review next governed action',
      });
    } else if (surface == 'verification') {
      payload = await _postJson(Uri.parse('$baseUrl/v1/verification'), {
        'project_id': projectId,
        'receipts': [
          {
            'receipt_id': 'ui-authority-readback',
            'channel': 'AUTHORITY_READBACK',
            'status': 'PASS',
            'verifier_id': 'ui-independent-verifier',
            'generator_id': 'planning-engine',
            'detail': 'Controlled fixture readback',
            'evidence_refs': ['FIXTURE_DERIVED'],
          },
        ],
      });
    } else if (surface == 'security') {
      payload = await _getJson(
        Uri.parse('$baseUrl/v1/capabilities/$projectId/envelope'),
      );
    } else if (surface == 'engineering') {
      payload = await _postJson(Uri.parse('$baseUrl/v1/engineering/advice'), {
        'project_id': projectId,
        'request': 'Assess the next safe engineering action',
      });
    } else if (surface == 'repository') {
      payload = await _getJson(
        Uri.parse('$baseUrl/v1/repositories/$projectId'),
      );
    } else if (surface == 'execution') {
      payload = await _postJson(Uri.parse('$baseUrl/v1/execution/simulate'), {
        'project_id': projectId,
        'capability_id': 'repo.patch.simulate',
        'requested_paths': ['README.md'],
        'simulate': true,
      });
    } else if (surface == 'agents') {
      payload = await _getJson(Uri.parse('$baseUrl/v1/agents/$projectId'));
    } else if (surface == 'lifecycle') {
      payload = await _getJson(Uri.parse('$baseUrl/v1/lifecycle/$projectId'));
    } else if (surface == 'operations') {
      payload = await _getJson(Uri.parse('$baseUrl/v1/operations/$projectId'));
    } else {
      throw ArgumentError.value(surface, 'surface', 'Unknown surface');
    }
    return GovernedCapabilityView.fromJson(surface, payload);
  }

  @override
  Future<ConnectorHealthView> fetchConnectorHealth() async =>
      ConnectorHealthView.fromJson(
        await _getJson(Uri.parse('$baseUrl/v1/system/connector')),
      );
}
