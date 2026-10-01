from __future__ import annotations

import pytest
from pydantic import ValidationError

from palwakf_mind_assistant.services.sovereign_channel_client_v1 import (
    InMemorySovereignChannelTransportV1,
    MindRemoteIntentRequestV1,
    MindSovereignChannelClientV1,
)


HEAD = "1" * 40


def request(**updates):
    values = {
        "intent_id": "mind-intent-001",
        "project_id": "PALWAKF_MIND_ASSISTANT",
        "repository_id": "firasfanon/palwakf_mind_assistant",
        "capability_id": "github.file.read",
        "arguments": {"path": "README.md"},
        "task_branch": "task/MIND-SOVEREIGN-TEST-V1",
        "expected_head": HEAD,
        "scope_paths": (),
    }
    values.update(updates)
    return MindRemoteIntentRequestV1(**values)


def test_mind_client_emits_fixed_principal_and_executor() -> None:
    transport = InMemorySovereignChannelTransportV1()
    client = MindSovereignChannelClientV1(transport)

    receipt = client.submit(request())

    assert receipt["principal_id"] == "MIND"
    payload = transport.submitted[0]
    assert payload["principal_id"] == "MIND"
    assert payload["executor_id"] == "Futuer-IT"
    assert payload["mutation_class"] == "READ_ONLY"
    assert payload["expected_remote_head"] == HEAD
    assert payload["expected_base_sha"] == HEAD


def test_mind_candidate_write_requires_drive_scope() -> None:
    with pytest.raises(ValidationError, match="MIND_WRITE_REQUIRES_SCOPE"):
        request(
            capability_id="workspace_drive.write_memory_candidate",
            scope_paths=(),
        )

    with pytest.raises(
        ValidationError,
        match="MIND_WRITE_SCOPE_MUST_BE_WORKSPACE_DRIVE",
    ):
        request(
            capability_id="workspace_drive.write_memory_candidate",
            scope_paths=("src/",),
        )


def test_mind_candidate_write_is_source_write_but_not_code_mutation() -> None:
    transport = InMemorySovereignChannelTransportV1()
    client = MindSovereignChannelClientV1(transport)

    client.submit(
        request(
            capability_id="workspace_drive.write_learning_candidate",
            arguments={
                "folder_id": "learning",
                "title": "candidate",
                "body": "bounded",
            },
            scope_paths=("drive:folder:learning",),
        )
    )

    payload = transport.submitted[0]
    assert payload["mutation_class"] == "SOURCE_WRITE"
    assert payload["scope_paths"] == ["drive:folder:learning"]


@pytest.mark.parametrize(
    "capability",
    [
        "service.restart",
        "runtime.repair",
        "github.file.write_bounded",
        "engineering.codex.edit_bounded",
    ],
)
def test_mind_cannot_request_operational_or_code_mutation(capability: str) -> None:
    with pytest.raises(ValidationError, match="MIND_CAPABILITY_NOT_ALLOWED"):
        request(capability_id=capability, scope_paths=("drive:folder:x",))
