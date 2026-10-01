from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MindSovereignChannelError(RuntimeError):
    pass


MIND_CAPABILITY_CLASSES: Mapping[str, str] = {
    "github.repo.read": "READ_ONLY",
    "github.branch.read": "READ_ONLY",
    "github.diff.read": "READ_ONLY",
    "github.file.read": "READ_ONLY",
    "workspace_drive.search": "READ_ONLY",
    "workspace_drive.list": "READ_ONLY",
    "workspace_drive.read": "READ_ONLY",
    "workspace_drive.document.find": "READ_ONLY",
    "workspace_drive.write_learning_candidate": "SOURCE_WRITE",
    "workspace_drive.write_memory_candidate": "SOURCE_WRITE",
    "workspace_drive.write_knowledge_candidate": "SOURCE_WRITE",
    "health.check": "READ_ONLY",
}


class MindRemoteIntentRequestV1(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    intent_id: str = Field(pattern=r"^[A-Za-z0-9_.:-]{8,200}$")
    project_id: str = Field(min_length=3, max_length=200)
    repository_id: str = Field(min_length=3, max_length=240)
    capability_id: str = Field(min_length=3, max_length=160)
    arguments: dict[str, Any] = Field(default_factory=dict)
    task_branch: str = Field(min_length=5, max_length=240)
    expected_head: str = Field(pattern=r"^[0-9a-fA-F]{40}$")
    scope_paths: tuple[str, ...] = Field(default=(), max_length=128)
    ttl_seconds: int = Field(default=900, ge=30, le=3600)

    @model_validator(mode="after")
    def validate_scope(self) -> MindRemoteIntentRequestV1:
        mutation_class = MIND_CAPABILITY_CLASSES.get(self.capability_id)
        if mutation_class is None:
            raise ValueError("MIND_CAPABILITY_NOT_ALLOWED")
        if mutation_class != "READ_ONLY":
            if not self.task_branch.startswith("task/"):
                raise ValueError("MIND_WRITE_REQUIRES_TASK_BRANCH")
            if not self.scope_paths:
                raise ValueError("MIND_WRITE_REQUIRES_SCOPE")
            if not all(
                item.startswith(("drive:folder:", "drive:doc:"))
                for item in self.scope_paths
            ):
                raise ValueError("MIND_WRITE_SCOPE_MUST_BE_WORKSPACE_DRIVE")
        return self


class SovereignChannelTransport(Protocol):
    def submit(self, payload: Mapping[str, Any]) -> Mapping[str, Any]: ...
    def result(self, task_id: str) -> Mapping[str, Any] | None: ...


class UnavailableSovereignChannelTransportV1:
    def submit(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        raise MindSovereignChannelError("SOVEREIGN_CHANNEL_NOT_CONFIGURED")

    def result(self, task_id: str) -> Mapping[str, Any] | None:
        raise MindSovereignChannelError("SOVEREIGN_CHANNEL_NOT_CONFIGURED")


class InMemorySovereignChannelTransportV1:
    def __init__(self) -> None:
        self.submitted: list[dict[str, Any]] = []
        self.results: dict[str, dict[str, Any]] = {}

    def submit(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        value = dict(payload)
        self.submitted.append(value)
        return {
            "state": "PUBLISHED",
            "task_id": f"SOV-MIND-{value['intent_id']}",
            "principal_id": "MIND",
        }

    def result(self, task_id: str) -> Mapping[str, Any] | None:
        return self.results.get(task_id)


class MindSovereignChannelClientV1:
    principal_id = "MIND"
    executor_id = "Futuer-IT"

    def __init__(self, transport: SovereignChannelTransport) -> None:
        self.transport = transport

    def submit(self, request: MindRemoteIntentRequestV1) -> Mapping[str, Any]:
        mutation_class = MIND_CAPABILITY_CLASSES.get(request.capability_id)
        if mutation_class is None:
            raise MindSovereignChannelError("MIND_CAPABILITY_NOT_ALLOWED")
        now = datetime.now(UTC)
        expires = now + timedelta(seconds=request.ttl_seconds)
        payload = {
            "schema_id": "palwakf.sovereign_remote_intent.v1",
            "intent_id": request.intent_id,
            "principal_id": self.principal_id,
            "project_id": request.project_id,
            "repository_id": request.repository_id,
            "executor_id": self.executor_id,
            "requested_capability_id": request.capability_id,
            "mutation_class": mutation_class,
            "arguments": request.arguments,
            "task_branch": request.task_branch,
            "expected_remote_head": request.expected_head,
            "expected_base_sha": request.expected_head,
            "scope_paths": list(request.scope_paths),
            "evidence_requirements": [
                "authority",
                "principal",
                "lease",
                "drift",
                "result",
            ],
            "approval_class": "SOVEREIGN_REMOTE_EXECUTION",
            "max_duration_seconds": min(request.ttl_seconds, 1800),
            "idempotency_key": f"mind:{request.intent_id}",
            "nonce": f"mind:{request.intent_id}:nonce",
            "issued_at": now.isoformat(),
            "expires_at": expires.isoformat(),
        }
        receipt = dict(self.transport.submit(payload))
        if receipt.get("principal_id") not in {None, "MIND"}:
            raise MindSovereignChannelError("MIND_RECEIPT_PRINCIPAL_MISMATCH")
        return receipt

    def result(self, task_id: str) -> Mapping[str, Any] | None:
        return self.transport.result(task_id)
