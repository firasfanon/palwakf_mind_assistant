# PalWakf Mind Assistant — Second Integrated Product Batch

`PALWAKF_MIND_ASSISTANT` is an independent knowledge-intelligence and curation product. The product has two co-equal user surfaces — **Assistant Workspace** and **Control / Knowledge surfaces** — backed by a shared authority, provenance and conflict-aware core.

## Second-batch product surfaces

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

## Local second-batch test

Extract this ZIP into a **new sibling directory** (do not overwrite the already-tested first-batch project yet), then run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\RUN.ps1
```

The runner uses dynamic loopback ports for both API and Flutter Web, formats the candidate on the target Flutter toolchain, executes backend and Flutter gates, builds Web explicitly, then launches Chrome for the interaction checklist in `SECOND_BATCH_ACCEPTANCE.md`.

## Current remote boundary

The authoritative GitHub repository remained bootstrap-only at `main@8fc746291043a9de9b0b19c477a2d32ae1a06e8a` when this local batch was activated. This package is **local candidate source only**. It does not represent remote WIP, integration, baseline, deployment or production.

## Final Integrated Development Mega Batch V1

The current local candidate integrates the remaining roadmap capabilities B0.7–B1.5
into one governed product increment. It adds planning/impact/decision intelligence,
independent verification, security/capability control, Engineering Mode,
repository-aware analysis, simulation-only governed execution, multi-agent
orchestration contracts, end-to-end governed lifecycle, and operability/recovery
surfaces.

This candidate is **not remote, not integrated, not baseline-promoted, not deployed,
and not production**. Workspace Drive remains the sovereign knowledge authority and
GitHub remains the code authority once integration is separately authorized.
