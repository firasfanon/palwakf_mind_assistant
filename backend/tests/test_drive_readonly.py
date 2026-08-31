from palwakf_mind_assistant.adapters.drive_readonly import (
    GoogleDriveRestReadOnlyAdapter,
    InMemoryDriveReadOnlyAdapter,
    UnavailableDriveReadOnlyAdapter,
)
from palwakf_mind_assistant.domain.models import (
    AuthorityType,
    ConnectorState,
    LifecycleStatus,
    SourceRef,
)


def _source() -> SourceRef:
    return SourceRef(
        owner_project_id="PAL_EYES",
        authority_type=AuthorityType.PROJECT_CURRENT_STATE,
        lifecycle_status=LifecycleStatus.CURRENT,
        canonical_location="drive://current",
        source_id="source-123",
        source_ref="drive:current",
        title="PAL_EYES_CURRENT_STATE",
    )


def test_readonly_adapters_expose_no_write_methods() -> None:
    adapter = InMemoryDriveReadOnlyAdapter((_source(),))
    for forbidden in ("create", "update", "delete", "write", "put", "patch"):
        assert not hasattr(adapter, forbidden)


def test_unavailable_live_mode_fails_source_lifecycle_closed() -> None:
    adapter = UnavailableDriveReadOnlyAdapter((_source(),))
    sources = adapter.list_project_sources("PAL_EYES")
    assert sources[0].lifecycle_status is LifecycleStatus.UNKNOWN
    assert adapter.connector_health().state is ConnectorState.DEGRADED
    assert adapter.connector_health().writes_enabled is False


def test_live_drive_adapter_uses_get_only_metadata_and_never_exposes_token() -> None:
    seen: dict[str, object] = {}

    def fake_fetcher(source_id: str, token: str, timeout: float) -> dict[str, object]:
        seen.update(source_id=source_id, token=token, timeout=timeout)
        return {
            "id": source_id,
            "name": "Current State",
            "mimeType": "application/vnd.google-apps.document",
            "modifiedTime": "2026-08-29T00:00:00Z",
            "trashed": False,
        }

    token = "server-only-secret-token"
    adapter = GoogleDriveRestReadOnlyAdapter((_source(),), bearer_token=token, fetcher=fake_fetcher)
    result = adapter.list_project_sources("PAL_EYES")
    health = adapter.connector_health()

    assert seen["token"] == token
    assert result[0].metadata["live_verification"] == "PASS"
    assert health.state is ConnectorState.READY
    assert health.writes_enabled is False
    assert token not in health.model_dump_json()
    assert token not in result[0].model_dump_json()
    for forbidden in ("create", "update", "delete", "write", "put", "patch"):
        assert not hasattr(adapter, forbidden)
