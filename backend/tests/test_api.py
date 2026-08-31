from fastapi.testclient import TestClient

from palwakf_mind_assistant.api.app import app, create_app

client = TestClient(app)


def test_health_declares_read_only_mode_and_product_surface() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["project_id"] == "PALWAKF_MIND_ASSISTANT"
    assert body["mutation_mode"] == "READ_ONLY"
    surface = body["product_surface"]
    assert "ASSISTANT_DASHBOARD_PROJECT_MIND_DIGITAL_TWIN_SKILLS_EXPLORER" in surface
    assert "PLANNING_DECISIONS_VERIFICATION_SECURITY_ENGINEERING_REPOSITORY" in surface
    assert "EXECUTION_AGENTS_LIFECYCLE_OPERATIONS" in surface
    assert body["provider_mode"] == "DETERMINISTIC_GROUNDED"


def test_security_headers_and_request_id_are_present() -> None:
    response = client.get("/health", headers={"X-Request-ID": "test-request-123"})
    assert response.headers["X-Request-ID"] == "test-request-123"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Cache-Control"] == "no-store"


def test_local_cors_is_allowed_but_arbitrary_origin_is_not() -> None:
    local = client.options(
        "/v1/dashboard",
        headers={
            "Origin": "http://localhost:7357",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert local.headers["access-control-allow-origin"] == "http://localhost:7357"

    external = client.get("/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in external.headers


def test_authority_dashboard_project_mind_search_conflicts_and_assistant() -> None:
    authority = client.get("/v1/authority/projects/PAL_EYES")
    assert authority.status_code == 200
    assert authority.json()["status"] == "RESOLVED"

    dashboard = client.get("/v1/dashboard")
    assert dashboard.status_code == 200
    assert dashboard.json()["counts"]["resolved"] >= 2
    assert dashboard.json()["connector"]["writes_enabled"] is False

    mind = client.get("/v1/projects/PAL_EYES/mind")
    assert mind.status_code == 200
    assert mind.json()["current_state"]["title"] == "PAL_EYES_CURRENT_STATE_V1_20260822"

    twin = client.get("/v1/projects/PAL_EYES/digital-twin")
    assert twin.status_code == 200
    twin_body = twin.json()
    assert twin_body["project_id"] == "PAL_EYES"
    assert twin_body["derived_view"] is True
    assert twin_body["canonical_authority"] is False
    assert twin_body["rebuildable"] is True

    search = client.get(
        "/v1/knowledge/search",
        params={"q": "CURRENT_STATE", "project_id": "PAL_EYES"},
    )
    assert search.status_code == 200
    assert search.json()["total"] >= 1

    conflicts = client.get("/v1/conflicts/PAL_EYES")
    assert conflicts.status_code == 200
    assert conflicts.json() == []

    answer = client.post(
        "/v1/assistant/ask",
        json={"message": "ما آخر حالة معتمدة لمشروع Pal Eyes؟"},
    )
    assert answer.status_code == 200
    body = answer.json()
    assert body["project_id"] == "PAL_EYES"
    assert body["status"] == "GROUNDED_READ_ONLY"
    assert body["provider_mode"] == "DETERMINISTIC_GROUNDED"
    assert len(body["citations"]) == 3


def test_live_mode_without_server_token_is_degraded_and_fails_closed() -> None:
    live_app = create_app(source_mode="drive_rest", access_token="")
    live = TestClient(live_app)
    connector = live.get("/v1/system/connector")
    assert connector.status_code == 200
    assert connector.json()["state"] == "DEGRADED"
    assert connector.json()["writes_enabled"] is False

    answer = live.post(
        "/v1/assistant/ask",
        json={"message": "ما آخر حالة معتمدة لمشروع Pal Eyes؟"},
    )
    assert answer.status_code == 200
    assert answer.json()["status"] == "UNKNOWN_FAIL_CLOSED"


def test_context_compile_endpoint_exposes_trust_without_write_capability() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/v1/context/compile",
        json={"message": "ما الحالة الحالية؟", "project_id": "PAL_EYES"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == "PAL_EYES"
    assert payload["trust_state"] == "VERIFIED"
    assert payload["mutation_mode"] == "READ_ONLY"
    assert payload["authoritative_sources"][0]["provenance"]["source_ref"].startswith("drive:")
    assert payload["project_twin_ref"].startswith("twin_pal_eyes_")
    assert payload["project_twin_status"] in {"RESOLVED", "PARTIAL"}


def test_skill_registry_is_read_only_and_excludes_superseded() -> None:
    response = client.get('/v1/skills')
    assert response.status_code == 200
    body = response.json()
    assert body
    assert all(item['status'] == 'ACTIVE' for item in body)
    assert any(item['skill_id'] == 'PALWAKF_FLUTTER_PRODUCT_FIRST_RUN_GATE_V1' for item in body)


def test_skill_resolver_selects_flutter_without_execution_authority() -> None:
    response = client.post(
        '/v1/skills/resolve',
        json={
            'message': 'Flutter browser responsive UAT',
            'project_id': 'PALWAKF_MIND_ASSISTANT',
        },
    )
    assert response.status_code == 200
    body = response.json()
    selected = {item['skill_id']: item for item in body['selections']}
    assert 'PALWAKF_FLUTTER_PRODUCT_FIRST_RUN_GATE_V1' in selected
    assert selected['PALWAKF_FLUTTER_PRODUCT_FIRST_RUN_GATE_V1']['execution_authorized'] is False
    assert body['autonomous_execution'] is False
    assert body['mutation_mode'] == 'READ_ONLY'
