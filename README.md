# PalWakf Mind Assistant — L5 Reliable Production Candidate

`PALWAKF_MIND_ASSISTANT` is an independent knowledge-intelligence and curation product. The product has two co-equal user surfaces — **Assistant Workspace** and **Control / Knowledge surfaces** — backed by a shared authority, provenance and conflict-aware core.

## Product surfaces

- Assistant Workspace with explicit project context and current-session conversation history.
- Operational Dashboard with authority health, knowledge health, source/connector health and alerts.
- Project Mind for one-project current state, sources, supersession and review indicators.
- Knowledge Explorer for metadata-grounded search.
- Conflict Center for structural authority/lifecycle conflict candidates; it does not falsely claim semantic contradiction detection.
- Sources & Connections with read-only mode, connector state and provenance.
- Responsive desktop + narrow shell with Arabic-first RTL behavior.

## Knowledge authority

- **Google Drive / PalWakf Workspace** remains the only canonical authority for accepted durable knowledge.
- The local catalog, indexes and future derived stores are rebuildable and non-sovereign.
- `UNKNOWN != PASS`, `PROPOSAL != ACCEPTED`, `DERIVED != CANONICAL`.

## Connector modes

`MIND_SOURCE_MODE=fixture` is the default development mode and clearly reports `FIXTURE_DERIVED`.

`MIND_SOURCE_MODE=drive_rest` enables a server-side, GET-only Google Drive metadata verifier. It requires `MIND_GOOGLE_DRIVE_ACCESS_TOKEN` in the backend process environment. The token is never returned by APIs and Flutter receives no provider credential. If live mode is requested without the token, the connector becomes `DEGRADED` and source lifecycle fails closed to `UNKNOWN`.

There is no create/update/delete Drive method in this batch.

## Security foundation

- explicit local CORS allow-regex instead of wildcard CORS;
- request correlation ID + no-store/nosniff/referrer/CSP response headers;
- bounded API inputs;
- source provenance required for grounded answers;
- blocking structural authority conflicts prevent automatic Current selection;
- document/provider content is treated as data and cannot expand tool authority;
- server-side credentials only.

## Local L5 verification

Run the target-device candidate with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\RUN.ps1
```

The runner is non-mutating: it reads the exact Git HEAD/ref into runtime evidence,
executes backend and Flutter verification, checks liveness and readiness separately,
verifies repository identity readback, exercises the read-only L5 operations surface,
builds Web, and launches Chrome for human/browser UAT.

`/health` is liveness only. `/ready` evaluates authority resolution, connector
health, deterministic zero-loss rebuild, restart/resume idempotency and canonical
authority isolation. Fixture mode may be a development candidate but is never a
production-source certification.

## L5 reliability and authority boundary

The L5 candidate preserves the integrated product and hardens reliability rather than
rebuilding features. Derived-state recovery is verified by deterministic
serialize/revalidate/digest comparison; accepted knowledge loss must be zero.
Resume receipts detect stale source state and duplicate completed actions.
Repository Intelligence fails closed unless exact runtime Git HEAD/ref are supplied.

Cross-project authorization, client authority widening and out-of-scope paths are
denied. Watchers remain notify/propose-only. Workspace Drive remains the sovereign
knowledge authority; Mind cannot self-promote canonical knowledge.

A successful task-branch candidate is **not** a main merge, sovereign baseline,
production deployment, shared-database authorization or L5 certification. Those are
separate governed decisions bound to exact evidence and exact heads.
