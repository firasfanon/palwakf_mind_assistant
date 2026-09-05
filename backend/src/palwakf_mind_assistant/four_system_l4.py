from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from palwakf_mind_assistant.intersystem_review import (
    LearningCandidateBundleV1,
    MindReviewResultV1,
    review_learning_bundle,
)

CONTRACT_ID = "PALWAKF_FOUR_SYSTEM_L4_OPERATIONAL_CONTRACT_V1"


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


class FourSystemL4MindRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_id: Literal["PALWAKF_FOUR_SYSTEM_L4_OPERATIONAL_CONTRACT_V1"] = CONTRACT_ID
    workspace_run_id: str = Field(min_length=1, max_length=200)
    correlation_id: str = Field(min_length=1, max_length=200)
    learning_bundle: LearningCandidateBundleV1
    evaluation: dict[str, Any]
    execution_summary: dict[str, Any]


class FourSystemL4MindEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_id: Literal["PALWAKF_FOUR_SYSTEM_L4_OPERATIONAL_CONTRACT_V1"] = CONTRACT_ID
    workspace_run_id: str
    correlation_id: str
    request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    result_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    review_result: MindReviewResultV1
    resume_token: str


class MindL4JournalRecord(BaseModel):
    workspace_run_id: str
    correlation_id: str
    request_sha256: str
    status: Literal["STARTED", "COMPLETED", "FAIL_CLOSED"]
    result: dict | None = None
    error: str | None = None


class MindL4Journal:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (
            root
            or Path(
                os.getenv(
                    "PALWAKF_MIND_L4_STATE_ROOT",
                    str(Path(tempfile.gettempdir()) / "palwakf_mind_l4_state"),
                )
            )
        ).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, workspace_run_id: str) -> Path:
        safe = hashlib.sha256(workspace_run_id.encode("utf-8")).hexdigest()
        return self.root / f"{safe}.json"

    def load(self, workspace_run_id: str) -> MindL4JournalRecord | None:
        path = self._path(workspace_run_id)
        if not path.exists():
            return None
        return MindL4JournalRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self, record: MindL4JournalRecord) -> None:
        path = self._path(record.workspace_run_id)
        temp = path.with_suffix(".tmp")
        temp.write_text(record.model_dump_json(indent=2), encoding="utf-8")
        temp.replace(path)


class FourSystemL4MindService:
    def __init__(
        self,
        *,
        journal: MindL4Journal,
        reviewer: Callable[[LearningCandidateBundleV1], MindReviewResultV1],
    ) -> None:
        self.journal = journal
        self.reviewer = reviewer

    def review(self, request: FourSystemL4MindRequest) -> FourSystemL4MindEnvelope:
        request_dict = request.model_dump(mode="json")
        request_sha = _sha(request_dict)
        existing = self.journal.load(request.workspace_run_id)

        if existing is not None:
            if (
                existing.correlation_id != request.correlation_id
                or existing.request_sha256 != request_sha
            ):
                raise ValueError("FOUR_SYSTEM_L4_MIND_IDEMPOTENCY_CONFLICT")
            if existing.status == "COMPLETED" and existing.result is not None:
                return FourSystemL4MindEnvelope.model_validate(existing.result)
            raise ValueError("FOUR_SYSTEM_L4_MIND_INCOMPLETE_PREVIOUS_ATTEMPT_REQUIRES_REVIEW")

        self.journal.save(
            MindL4JournalRecord(
                workspace_run_id=request.workspace_run_id,
                correlation_id=request.correlation_id,
                request_sha256=request_sha,
                status="STARTED",
            )
        )

        try:
            if request.evaluation.get("run_id") != request.learning_bundle.run_id:
                raise ValueError("FOUR_SYSTEM_L4_MIND_EVALUATION_RUN_MISMATCH")
            if request.execution_summary.get("run_id") != request.learning_bundle.run_id:
                raise ValueError("FOUR_SYSTEM_L4_MIND_EXECUTION_RUN_MISMATCH")

            review = self.reviewer(request.learning_bundle)
            if review.canonical_write_allowed is not False:
                raise ValueError("FOUR_SYSTEM_L4_MIND_CANONICAL_WRITE_DENIED")
            if review.mutation_mode != "READ_ONLY":
                raise ValueError("FOUR_SYSTEM_L4_MIND_MUTATION_MODE_DENIED")
            if review.run_id != request.learning_bundle.run_id:
                raise ValueError("FOUR_SYSTEM_L4_MIND_REVIEW_RUN_MISMATCH")

            result_dict = review.model_dump(mode="json")
            result_sha = _sha(result_dict)
            envelope = FourSystemL4MindEnvelope(
                workspace_run_id=request.workspace_run_id,
                correlation_id=request.correlation_id,
                request_sha256=request_sha,
                result_sha256=result_sha,
                review_result=review,
                resume_token=f"mind-l4:{request.workspace_run_id}:{result_sha[:16]}",
            )
            self.journal.save(
                MindL4JournalRecord(
                    workspace_run_id=request.workspace_run_id,
                    correlation_id=request.correlation_id,
                    request_sha256=request_sha,
                    status="COMPLETED",
                    result=envelope.model_dump(mode="json"),
                )
            )
            return envelope
        except Exception as error:
            self.journal.save(
                MindL4JournalRecord(
                    workspace_run_id=request.workspace_run_id,
                    correlation_id=request.correlation_id,
                    request_sha256=request_sha,
                    status="FAIL_CLOSED",
                    error=f"{type(error).__name__}:{error}",
                )
            )
            raise

    def resume(self, workspace_run_id: str) -> MindL4JournalRecord:
        record = self.journal.load(workspace_run_id)
        if record is None:
            raise ValueError("FOUR_SYSTEM_L4_MIND_RUN_NOT_FOUND")
        return record


def mount_four_system_l4_mind(app: FastAPI, *, product: Any) -> None:
    journal = MindL4Journal()
    service = FourSystemL4MindService(
        journal=journal,
        reviewer=lambda bundle: review_learning_bundle(product, bundle),
    )
    app.state.four_system_l4_mind_service = service

    @app.post(
        "/v1/integration/l4/review",
        response_model=FourSystemL4MindEnvelope,
    )
    def l4_review(request: FourSystemL4MindRequest) -> FourSystemL4MindEnvelope:
        try:
            return service.review(request)
        except ValueError as error:
            raise HTTPException(
                status_code=409,
                detail={"code": str(error), "fail_closed": True},
            ) from error

    @app.get(
        "/v1/integration/l4/resume/{workspace_run_id}",
        response_model=MindL4JournalRecord,
    )
    def l4_resume(workspace_run_id: str) -> MindL4JournalRecord:
        try:
            return service.resume(workspace_run_id)
        except ValueError as error:
            raise HTTPException(
                status_code=404,
                detail={"code": str(error), "fail_closed": True},
            ) from error
