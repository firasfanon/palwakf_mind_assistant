# BATCH 0.5 — Project Digital Twin Foundation — File-Level Change Plan

Base executable package SHA256: `69A86A83134C3127E394B87783E9D6A3DE68099F80CF117DC4F5D13FF42ED2A9`.

## Scope
Build the smallest coherent `PROJECT_DIGITAL_TWIN_DERIVED_VERIFIED_VIEW_V1` on top of the accepted B0.4 context/trust foundation. The twin is read-only, derived, rebuildable, non-sovereign, and must fail closed on missing/unknown/conflicted authority.

## Changed / added files

- `backend/fixtures/project_state_catalog.json` — controlled two-project operational-state fixture with truthful `FIXTURE_DERIVED` labels and explicit unknown task state for PAL_EYES.
- `backend/src/palwakf_mind_assistant/adapters/project_state_fixture.py` — read-only fixture loader for operational twin inputs.
- `backend/src/palwakf_mind_assistant/domain/models.py` — DigitalTwinStatus, ProjectOperationalState, DriftIndicator, ProjectDigitalTwinSnapshot; optional twin reference fields on context package and ProjectMindSnapshot.
- `backend/src/palwakf_mind_assistant/services/digital_twin_builder.py` — deterministic rebuildable twin builder, drift detection, unknown preservation, next-safe-action provenance, rebuild receipt.
- `backend/src/palwakf_mind_assistant/services/context_compiler.py` — optional twin provider wiring; context carries twin ref/status/generated timestamp without promoting UNKNOWN.
- `backend/src/palwakf_mind_assistant/services/product_service.py` — constructs the twin builder; Project Mind embeds the twin; exposes digital_twin().
- `backend/src/palwakf_mind_assistant/api/app.py` — loads operational-state fixture; adds GET `/v1/projects/{project_id}/digital-twin`; bumps API version and product-surface declaration.
- `backend/tests/test_digital_twin_builder.py` — deterministic rebuild, unknown operational state, identity/current-state mismatch fail-closed, unknown task, two-project isolation, superseded-state selection proof.
- `backend/tests/test_api.py` — endpoint, invariant, product-surface, and Context Compiler twin-ref regression coverage.
- `frontend/lib/src/models/api_models.dart` — Digital Twin and drift view models; ProjectMindView embeds optional twin.
- `frontend/lib/src/api_client.dart` — read-only `fetchDigitalTwin` endpoint contract.
- `frontend/lib/src/screens/project_mind_screen.dart` — Digital Twin summary surface with DERIVED / READ_ONLY / NOT SOURCE OF TRUTH labels, repo/head/task/baseline/readiness/next-safe-action/drift presentation.
- `frontend/test/product_shell_test.dart` — FakeMindApi updated for the new non-breaking Digital Twin contract.

## Out of scope
No GitHub write, Workspace write, Drive semantic writeback, Agentic execution, canonical Twin store, Skill System, Planning Engine, Decision Engine, graph database, baseline promotion, deployment, or production mutation.
