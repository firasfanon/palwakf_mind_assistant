# First Batch Test Closeout — 2026-08-29

Observed on the user's Windows/Flutter environment:

- Backend pytest: **8 PASS** (one Starlette/httpx deprecation warning only).
- Dynamic loopback backend runtime: **PASS**.
- Backend `/health` READ_ONLY invariant: **PASS**.
- Dart format final check: **0 changed** after repair.
- `flutter analyze`: **PASS — No issues found**.
- isolated 800x600 regression widget test: **PASS** after navigation overflow and ListTile Material fixes.
- full Flutter widget test suite: **PASS**.
- Chrome debug runtime: **STARTED** and user-supplied render screenshot captured as `FIRST_BATCH_BROWSER_RENDER_20260829.png`.
- `flutter build web`: **NOT PROVEN** in first batch because Web scaffold was missing; this is explicitly repaired in Batch 2.
- full browser interaction UAT: **NOT FULLY EVIDENCED** in first batch.

Institutional learning was registered separately in the sovereign cross-project skills register as `PALWAKF_FLUTTER_PRODUCT_FIRST_RUN_GATE_V1`.
