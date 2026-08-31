# BATCH_0_4 Implementation Slice — Context + Trust Foundation

## Architecture mapping
This slice implements the first coherent subset of the accepted target architecture:

`USER_REQUEST -> INTENT_RESOLUTION -> PROJECT_RESOLUTION -> TASK_RESOLUTION -> AUTHORITY_RESOLUTION -> CURRENT_STATE -> TRUST/PROVENANCE -> MINIMAL_TRUSTED_CONTEXT_PACKAGE`

The fields for decisions, known lessons, and dependencies exist in the context package but remain empty unless safe structured metadata is actually present. This prevents the compiler from inventing state not present in the source catalog.

## Backend components
- `services/context_compiler.py`: deterministic trusted-context compilation.
- `services/trust_engine.py`: source-to-claim provenance/freshness/uncertainty classification.
- `domain/models.py`: trust, provenance, context request/package schemas.
- `POST /v1/context/compile`: read-only context compilation endpoint.
- Assistant responses now carry a context receipt and provenance-aware citations.
- Search hits expose provenance when available.

## Trust invariants
- `UNKNOWN` cannot become `VERIFIED` by inference.
- A blocking structural authority conflict produces `CONFLICTED`.
- Superseded/historical source state produces `STALE` provenance.
- `CURRENT`/`ACTIVE` lifecycle can establish metadata-level verification only; it does not claim semantic truth beyond available authority metadata.
- Semantic similarity never outranks authority or supersession.
- All outputs are `READ_ONLY`.

## Frontend slice
Assistant response bubbles expose:
- Context ID.
- Trust state.
- Authority status.
- Resolved intent.
- Explicit trust risks when present.

This is a status/readback surface only and does not add write controls.

## Base reconstruction note
The local build environment contains the original V0.3 package rather than the byte-identical Windows post-target PASS ZIP. Before B0.4 work, the known accepted V0.3 target-device repairs were reconstructed in the candidate where applicable: Drive E501 split, 720 responsive breakpoint, and constrained Assistant welcome scrolling. The authoritative Windows post-target package/hash remains the evidence reference for B0.3. A target-device comparison is required before any later Git reconciliation.
