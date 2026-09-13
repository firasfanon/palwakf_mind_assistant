from __future__ import annotations

import hashlib
import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from palwakf_mind_assistant.domain.models import (
    ClaimState,
    ConflictSeverity,
    LifecycleStatus,
    ResolutionStatus,
)


def _enum_value(value: Any) -> str:
    raw = getattr(value, "value", value)
    return str(raw).upper()


def _candidate_fingerprint(candidate: Any) -> str:
    payload = {
        "project_id": candidate.project_id,
        "task_id": candidate.task_id,
        "candidate_type": candidate.candidate_type,
        "summary": " ".join(
            str(candidate.summary).casefold().split()
        ),
        "source_sha": candidate.source_sha.lower(),
    }

    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


class KnownFailureFingerprintReviewV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fingerprint_id: str
    lesson_id: str
    preventive_gate_id: str
    relevant: bool = True
    applies_to_projects: tuple[str, ...] = ("*",)


class MindPreL5ReviewContextV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str
    task_id: str
    run_id: str

    source_sha: str = Field(
        pattern=r"^[0-9a-fA-F]{40}$"
    )

    active_instruction_set_sha256: str = Field(
        pattern=r"^[0-9a-f]{64}$"
    )

    active_lesson_ids: tuple[str, ...]
    reused_lesson_ids: tuple[str, ...]

    known_failure_fingerprints: tuple[
        KnownFailureFingerprintReviewV1, ...
    ] = ()

    review_mode: Literal[
        "CANDIDATE_ONLY_NO_AUTO_PROMOTION"
    ] = "CANDIDATE_ONLY_NO_AUTO_PROMOTION"

    canonical_write_allowed: Literal[False] = False

    @model_validator(mode="after")
    def enforce_known_lesson_reuse(self):
        active = set(self.active_lesson_ids)
        reused = set(self.reused_lesson_ids)

        for fingerprint in self.known_failure_fingerprints:
            if not fingerprint.relevant:
                continue

            projects = set(
                fingerprint.applies_to_projects
            )

            if (
                "*" not in projects
                and self.project_id not in projects
            ):
                raise ValueError(
                    "FAILURE_FINGERPRINT_PROJECT_SCOPE_MISMATCH"
                )

            if fingerprint.lesson_id not in active:
                raise ValueError(
                    "KNOWN_RELEVANT_LESSON_NOT_ACTIVE"
                )

            if fingerprint.lesson_id not in reused:
                raise ValueError(
                    "KNOWN_RELEVANT_LESSON_NOT_REUSED"
                )

        return self


class MindPreL5ReviewAssessmentV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    guard_id: Literal[
        "PALWAKF_MIND_PRE_L5_REVIEW_ENFORCEMENT_V1"
    ] = "PALWAKF_MIND_PRE_L5_REVIEW_ENFORCEMENT_V1"

    project_id: str
    task_id: str
    run_id: str

    active_instruction_set_sha256: str = Field(
        pattern=r"^[0-9a-f]{64}$"
    )

    provenance_review: Literal[
        "PASS",
        "REVIEW_REQUIRED",
    ]

    conflict_review: Literal[
        "PASS",
        "REVIEW_REQUIRED",
    ]

    duplicate_review: Literal[
        "PASS",
        "REVIEW_REQUIRED",
    ]

    staleness_review: Literal[
        "PASS",
        "REVIEW_REQUIRED",
    ]

    lesson_reuse_review: Literal["PASS"] = "PASS"

    blocking_conflict_refs: tuple[str, ...] = ()
    non_current_context_refs: tuple[str, ...] = ()

    duplicate_candidate_ids: tuple[str, ...] = ()

    force_more_evidence_candidate_ids: tuple[
        str, ...
    ] = ()

    reject_candidate_ids: tuple[str, ...] = ()

    promotion_recommendation: Literal[
        "HUMAN_WORKSPACE_REVIEW_REQUIRED"
    ] = "HUMAN_WORKSPACE_REVIEW_REQUIRED"

    canonical_write_allowed: Literal[False] = False
    mutation_mode: Literal["READ_ONLY"] = "READ_ONLY"


class MindPreL5ReviewEnforcer:
    def assess(
        self,
        *,
        bundle: Any,
        review_context: MindPreL5ReviewContextV1,
        compiled_context: Any,
        conflicts: tuple[Any, ...],
    ) -> MindPreL5ReviewAssessmentV1:

        # ------------------------------------------------------
        # Cross-system binding
        # ------------------------------------------------------

        if bundle.project_id != review_context.project_id:
            raise ValueError(
                "MIND_REVIEW_PROJECT_BINDING_MISMATCH"
            )

        if bundle.task_id != review_context.task_id:
            raise ValueError(
                "MIND_REVIEW_TASK_BINDING_MISMATCH"
            )

        if bundle.run_id != review_context.run_id:
            raise ValueError(
                "MIND_REVIEW_RUN_BINDING_MISMATCH"
            )

        if (
            bundle.source_sha.lower()
            != review_context.source_sha.lower()
        ):
            raise ValueError(
                "STALE_LEARNING_SOURCE_SHA"
            )

        if bundle.auto_promotion is not False:
            raise ValueError(
                "AUTOMATIC_CANONICAL_PROMOTION_FORBIDDEN"
            )

        if (
            getattr(compiled_context, "project_id", None)
            != bundle.project_id
        ):
            raise ValueError(
                "COMPILED_CONTEXT_PROJECT_LEAKAGE"
            )

        compiled_task = getattr(
            compiled_context,
            "task_id",
            None,
        )

        if (
            compiled_task is not None
            and compiled_task != bundle.task_id
        ):
            raise ValueError(
                "COMPILED_CONTEXT_TASK_LEAKAGE"
            )

        # ------------------------------------------------------
        # Candidate scope/source
        # ------------------------------------------------------

        for candidate in bundle.candidates:
            if candidate.project_id != bundle.project_id:
                raise ValueError(
                    "LEARNING_CANDIDATE_PROJECT_LEAKAGE"
                )

            if candidate.task_id != bundle.task_id:
                raise ValueError(
                    "LEARNING_CANDIDATE_TASK_LEAKAGE"
                )

            if (
                candidate.source_sha.lower()
                != bundle.source_sha.lower()
            ):
                raise ValueError(
                    "LEARNING_CANDIDATE_STALE_SOURCE"
                )

        # ------------------------------------------------------
        # Provenance + staleness
        # ------------------------------------------------------

        authoritative = tuple(
            getattr(
                compiled_context,
                "authoritative_sources",
                (),
            )
            or ()
        )

        superseded = tuple(
            getattr(
                compiled_context,
                "superseded_sources",
                (),
            )
            or ()
        )

        authoritative_refs: set[str] = set()
        non_current_refs: set[str] = set()

        for trusted in authoritative:
            source = getattr(trusted, "source", trusted)

            source_ref = str(
                getattr(source, "source_ref", "")
            )

            if source_ref:
                authoritative_refs.add(source_ref)

            lifecycle = _enum_value(
                getattr(
                    source,
                    "lifecycle_status",
                    "UNKNOWN",
                )
            )

            if lifecycle not in {
                LifecycleStatus.CURRENT.value,
                LifecycleStatus.ACTIVE.value,
            }:
                if source_ref:
                    non_current_refs.add(source_ref)

        superseded_refs = {
            str(
                getattr(
                    getattr(trusted, "source", trusted),
                    "source_ref",
                    "",
                )
            )
            for trusted in superseded
        }

        superseded_refs.discard("")

        non_current_refs.update(
            authoritative_refs.intersection(
                superseded_refs
            )
        )

        # ------------------------------------------------------
        # Conflicts
        # ------------------------------------------------------

        blocking_conflicts = tuple(
            conflict
            for conflict in conflicts
            if _enum_value(
                getattr(conflict, "severity", "")
            )
            == ConflictSeverity.BLOCKING.value
        )

        blocking_refs = {
            str(ref)
            for conflict in blocking_conflicts
            for ref in getattr(
                conflict,
                "source_refs",
                (),
            )
        }

        # ------------------------------------------------------
        # Candidate duplicate detection
        # ------------------------------------------------------

        by_fingerprint: dict[str, list[str]] = {}

        for candidate in bundle.candidates:
            key = _candidate_fingerprint(candidate)

            by_fingerprint.setdefault(
                key,
                [],
            ).append(candidate.candidate_id)

        duplicate_ids = {
            candidate_id
            for ids in by_fingerprint.values()
            if len(ids) > 1
            for candidate_id in ids
        }

        # ------------------------------------------------------
        # Determine review restrictions
        # ------------------------------------------------------

        force_more_evidence: set[str] = set()
        reject: set[str] = set(duplicate_ids)

        authority_status = _enum_value(
            getattr(
                compiled_context,
                "authority_status",
                "UNKNOWN",
            )
        )

        trust_state = _enum_value(
            getattr(
                compiled_context,
                "trust_state",
                "UNKNOWN",
            )
        )

        context_unresolved = (
            authority_status
            != ResolutionStatus.RESOLVED.value
            or trust_state
            != ClaimState.VERIFIED.value
            or not authoritative_refs
            or bool(non_current_refs)
            or bool(blocking_conflicts)
        )

        if context_unresolved:
            force_more_evidence.update(
                candidate.candidate_id
                for candidate in bundle.candidates
            )

        restricted_refs = (
            superseded_refs
            | non_current_refs
            | blocking_refs
        )

        for candidate in bundle.candidates:
            evidence_refs = set(
                candidate.evidence_refs
            )

            if evidence_refs.intersection(
                restricted_refs
            ):
                force_more_evidence.add(
                    candidate.candidate_id
                )

            if not candidate.evidence_refs:
                force_more_evidence.add(
                    candidate.candidate_id
                )

        provenance_review = (
            "PASS"
            if authoritative_refs
            and not non_current_refs
            else "REVIEW_REQUIRED"
        )

        conflict_review = (
            "REVIEW_REQUIRED"
            if blocking_conflicts
            else "PASS"
        )

        duplicate_review = (
            "REVIEW_REQUIRED"
            if duplicate_ids
            else "PASS"
        )

        staleness_review = (
            "REVIEW_REQUIRED"
            if non_current_refs
            else "PASS"
        )

        return MindPreL5ReviewAssessmentV1(
            project_id=bundle.project_id,
            task_id=bundle.task_id,
            run_id=bundle.run_id,
            active_instruction_set_sha256=(
                review_context
                .active_instruction_set_sha256
            ),
            provenance_review=provenance_review,
            conflict_review=conflict_review,
            duplicate_review=duplicate_review,
            staleness_review=staleness_review,
            blocking_conflict_refs=tuple(
                sorted(blocking_refs)
            ),
            non_current_context_refs=tuple(
                sorted(non_current_refs)
            ),
            duplicate_candidate_ids=tuple(
                sorted(duplicate_ids)
            ),
            force_more_evidence_candidate_ids=tuple(
                sorted(force_more_evidence)
            ),
            reject_candidate_ids=tuple(
                sorted(reject)
            ),
        )