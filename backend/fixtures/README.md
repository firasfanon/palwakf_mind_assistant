# Derived authority catalog fixture

`authority_catalog.json` is a local development/test snapshot of source references observed from sovereign PalWakf Workspace Drive governance. It is **not** a canonical knowledge store and must not be treated as live Drive truth.

When `MIND_SOURCE_MODE=drive_rest`, the server-side adapter verifies these references using GET-only Google Drive metadata calls. A failed live verification changes the affected lifecycle to `UNKNOWN` for that request path rather than trusting stale fixture state.
