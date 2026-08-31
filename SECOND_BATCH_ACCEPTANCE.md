# PalWakf Mind Assistant — Second Batch Acceptance

This candidate must be tested in an isolated local directory before any reconciliation into the working repository.

## Automated gate
Run `RUN.ps1`. Required before browser review:

- backend Ruff format/lint, compile and pytest pass;
- backend health reports `READ_ONLY`;
- Dart format is idempotent after target-device formatting;
- Flutter analyze and widget tests pass;
- `flutter build web` passes;
- Chrome runtime starts against the exact dynamic loopback API URL.

## Browser interaction UAT
While Chrome remains open:

1. **Assistant** — select `PAL_EYES`, use `ما الحالة الحالية؟`, then `ما المصادر المعتمدة؟`, then `هل توجد تعارضات؟`. Confirm the response shows grounded/read-only status and never promotes UNKNOWN into fact.
2. **Dashboard** — confirm projects, authority health, connector mode, alerts and conflict counts render.
3. **Project Mind** — switch between `PAL_EYES` and `PALWAKF_MIND_ASSISTANT`; confirm Current State and source provenance are visible.
4. **Knowledge Explorer** — search `CURRENT_STATE`; confirm results show project, authority type and lifecycle state.
5. **Conflicts** — confirm the screen explicitly distinguishes structural metadata indicators from semantic contradiction proof.
6. **Sources & Connections** — confirm `READ_ONLY`, `WRITES_OFF`, connector mode and source inventory.
7. **Responsive** — resize below 900 px (target 390x844). Confirm bottom navigation + drawer are usable and there are no yellow/black overflow stripes.
8. Check browser console for uncaught Flutter/runtime exceptions. Record any first exception exactly.

## Explicit non-claims
- default fixture mode is derived development data, not a live sovereign Drive session;
- live Drive REST mode requires a server-side token and is never configured through Flutter;
- no Drive/GitHub write tool exists in this batch;
- no merge, baseline, deployment or production approval is implied by local PASS;
- deterministic grounded mode is not a claim of live LLM reasoning.
