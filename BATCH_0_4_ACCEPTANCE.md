# PalWakf Mind Assistant — BATCH_0_4 Context + Trust Foundation

Status: LOCAL_CANDIDATE — target-device Flutter gates pending.

## Goal
Build a deterministic, read-only Context Compiler foundation and claim-level trust model. The batch must improve authority, provenance, freshness, uncertainty, supersession handling, and user-visible trust labeling without autonomous execution or canonical semantic write-back.

## In scope
- Intent resolution.
- Explicit/inferred project resolution with fail-closed ambiguity.
- Optional task context passthrough; no task invention.
- `MinimalTrustedContextPackage`.
- Claim provenance: source, authority, version, observed-at, confidence, freshness, supersession, scope, claim state, reason.
- Claim states: VERIFIED / INFERRED / STALE / CONFLICTED / UNKNOWN / UNAVAILABLE.
- Authority-aware retrieval metadata.
- Temporal/lifecycle and supersession handling.
- Read-only trust status in Assistant UI.
- Regression tests for unknown, stale, conflict, and provenance scenarios.

## Out of scope
- Autonomous execution.
- Canonical Drive semantic writes.
- Workspace Manager control-plane duplication.
- Agentic AI runtime absorption.
- Full Project Digital Twin (BATCH_0_5).
- Skill System V1 (BATCH_0_6).
- Planning / impact / decision engine (BATCH_0_7).
- GitHub mutation, merge, baseline promotion, deployment, production.

## Exit gate
1. Backend compile/lint/test PASS.
2. Context regression scenarios PASS: deterministic project, missing project, multiple-current conflict, superseded/stale source.
3. Provenance readback visible in API payloads.
4. No authority leakage and no write capability.
5. Flutter format/analyze/test PASS on target device.
6. `flutter build web` PASS on target device.
7. Browser UAT PASS for Assistant trust labels and project switching.
8. Responsive browser UAT PASS at 800x600 and 390x844 contracts.
9. Knowledge/Learning Closure PASS.
10. Current State + evidence checkpoint.
