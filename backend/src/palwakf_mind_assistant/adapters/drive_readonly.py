from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from palwakf_mind_assistant.domain.models import (
    ConnectorHealth,
    ConnectorState,
    LifecycleStatus,
    SourceRef,
)


class DriveReadOnlyPort(Protocol):
    """Read-only boundary for sovereign Workspace/Drive knowledge.

    Intentionally exposes no create/update/delete operation. Any future write
    capability requires a different contract and explicit authorization.
    """

    def list_project_sources(self, project_id: str) -> Sequence[SourceRef]: ...

    def list_project_ids(self) -> Sequence[str]: ...

    def connector_health(self) -> ConnectorHealth: ...


class InMemoryDriveReadOnlyAdapter:
    """Deterministic adapter for tests and local derived fixtures."""

    def __init__(self, sources: Sequence[SourceRef]) -> None:
        self._sources = tuple(sources)

    def list_project_ids(self) -> tuple[str, ...]:
        return tuple(sorted({source.owner_project_id.upper() for source in self._sources}))

    def list_project_sources(self, project_id: str) -> tuple[SourceRef, ...]:
        normalized = project_id.strip().upper()
        return tuple(
            source for source in self._sources if source.owner_project_id.upper() == normalized
        )

    def connector_health(self) -> ConnectorHealth:
        return ConnectorHealth(
            connector="GOOGLE_DRIVE",
            mode="FIXTURE_DERIVED",
            state=ConnectorState.READY,
            source_count=len(self._sources),
            writes_enabled=False,
            detail="Local derived fixture; not a live sovereign Drive session.",
        )


class UnavailableDriveReadOnlyAdapter(InMemoryDriveReadOnlyAdapter):
    """Fail-closed adapter used when live Drive mode lacks required auth."""

    def connector_health(self) -> ConnectorHealth:
        return ConnectorHealth(
            connector="GOOGLE_DRIVE",
            mode="DRIVE_REST_READ_ONLY",
            state=ConnectorState.DEGRADED,
            source_count=len(self._sources),
            writes_enabled=False,
            detail="Live Drive mode requested but server-side access token is unavailable.",
        )

    def list_project_sources(self, project_id: str) -> tuple[SourceRef, ...]:
        return tuple(
            source.model_copy(
                update={
                    "lifecycle_status": LifecycleStatus.UNKNOWN,
                    "metadata": {
                        **source.metadata,
                        "live_verification": "UNAVAILABLE",
                    },
                }
            )
            for source in super().list_project_sources(project_id)
        )


DriveMetadataFetcher = Callable[[str, str, float], dict[str, object]]


def _fetch_drive_metadata(source_id: str, bearer_token: str, timeout: float) -> dict[str, object]:
    fields = quote("id,name,mimeType,modifiedTime,trashed", safe=",")
    encoded_source_id = quote(source_id, safe="")
    url = (
        f"https://www.googleapis.com/drive/v3/files/{encoded_source_id}"
        f"?fields={fields}&supportsAllDrives=true"
    )
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {bearer_token}",
            "Accept": "application/json",
            "User-Agent": "PalWakf-Mind-Assistant/0.3",
        },
        method="GET",
    )
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed Google API host
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("DRIVE_METADATA_RESPONSE_NOT_OBJECT")
    return payload


class GoogleDriveRestReadOnlyAdapter:
    """Server-side, GET-only Google Drive metadata verifier.

    The canonical source catalog remains the authority map. This adapter only
    verifies that catalog references against Drive and never exposes the bearer
    token or any write method.
    """

    def __init__(
        self,
        sources: Sequence[SourceRef],
        *,
        bearer_token: str,
        timeout_seconds: float = 5.0,
        fetcher: DriveMetadataFetcher = _fetch_drive_metadata,
    ) -> None:
        if not bearer_token.strip():
            raise ValueError("DRIVE_ACCESS_TOKEN_REQUIRED")
        self._sources = tuple(sources)
        self._bearer_token = bearer_token
        self._timeout_seconds = timeout_seconds
        self._fetcher = fetcher
        self._verified = 0
        self._failures = 0
        self._last_error_code: str | None = None

    def list_project_ids(self) -> tuple[str, ...]:
        return tuple(sorted({source.owner_project_id.upper() for source in self._sources}))

    def list_project_sources(self, project_id: str) -> tuple[SourceRef, ...]:
        normalized = project_id.strip().upper()
        output: list[SourceRef] = []
        for source in self._sources:
            if source.owner_project_id.upper() != normalized:
                continue
            try:
                metadata = self._fetcher(
                    source.source_id,
                    self._bearer_token,
                    self._timeout_seconds,
                )
                if metadata.get("trashed") is True:
                    raise ValueError("DRIVE_SOURCE_TRASHED")
                if str(metadata.get("id", "")) != source.source_id:
                    raise ValueError("DRIVE_SOURCE_ID_MISMATCH")
                self._verified += 1
                output.append(
                    source.model_copy(
                        update={
                            "metadata": {
                                **source.metadata,
                                "live_verification": "PASS",
                                "drive_name": str(metadata.get("name", source.title)),
                                "drive_mime_type": str(metadata.get("mimeType", "")),
                                "drive_modified_time": str(metadata.get("modifiedTime", "")),
                            }
                        }
                    )
                )
            except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
                self._failures += 1
                self._last_error_code = type(exc).__name__
                output.append(
                    source.model_copy(
                        update={
                            "lifecycle_status": LifecycleStatus.UNKNOWN,
                            "metadata": {
                                **source.metadata,
                                "live_verification": "FAIL_CLOSED",
                                "live_error_type": type(exc).__name__,
                            },
                        }
                    )
                )
        return tuple(output)

    def connector_health(self) -> ConnectorHealth:
        if self._failures:
            state = ConnectorState.DEGRADED
            detail = (
                f"Live Drive read-only verification had {self._failures} failure(s); "
                f"last_error={self._last_error_code}."
            )
        elif self._verified:
            state = ConnectorState.READY
            detail = (
                f"Verified {self._verified} Drive source reference(s) "
                "using GET-only metadata calls."
            )
        else:
            state = ConnectorState.UNKNOWN
            detail = "Live Drive adapter configured but not yet probed."
        return ConnectorHealth(
            connector="GOOGLE_DRIVE",
            mode="DRIVE_REST_READ_ONLY",
            state=state,
            source_count=len(self._sources),
            writes_enabled=False,
            detail=detail,
        )
