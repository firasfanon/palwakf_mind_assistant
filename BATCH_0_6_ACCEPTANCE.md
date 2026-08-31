# BATCH 0.6 — Skill System V1 Acceptance

## Required invariants
- Skill registry is derived/read-only and not a canonical authority.
- Skill selection never grants execution authority.
- Superseded/deprecated skills are not selected as current.
- Unknown or unmet preconditions remain visible; no implicit PASS.
- Human-visible provenance is preserved.
- Known-lesson regression can be detected.

## Controlled selection scenarios
1. Artifact/PowerShell handoff selects the artifact handoff skill and rejects unrelated DB repair skill.
2. Flutter/browser/responsive UAT selects the Flutter first-run/UAT skill and does not select DB repair.
3. Resume/reconciliation selects durable project-state resume skill.
4. Superseded skill is rejected even when its trigger matches.

## Build-environment evidence
- Python compileall: PASS.
- Backend pytest: PASS_41.
- Python physical line length >100: ZERO.
- Dart brace sanity: PASS_NON_AUTHORITATIVE.
- Ruff: NOT_RUN_IN_BUILD_ENV.
- Dart formatter: NOT_RUN_IN_BUILD_ENV.
- Flutter analyze/test/build-web: NOT_RUN_IN_BUILD_ENV.

## Target-device acceptance still required
- Repository-native Ruff.
- Dart format write + idempotence.
- Flutter analyze.
- Flutter tests including Skills & Lessons surface.
- Flutter build web.
- Browser UAT desktop and exact 390x844 responsive view.
- Verify provenance, FIXTURE_DERIVED/read-only truth labels and `EXECUTION NOT AUTHORIZED`.
- Clean fatal runtime console.
- Knowledge/Learning Closure and final post-target package capture.
