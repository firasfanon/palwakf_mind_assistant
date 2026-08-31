# Architecture — Second Product Foundation

## Product surfaces

```text
Assistant Workspace ─┐
Dashboard            ├── ProductService / Shared Intelligence Core
Project Mind         │        ├── AuthorityResolver
Knowledge Explorer  │        ├── ConflictDetector
Conflict Center     │        └── DriveReadOnlyPort
Sources & Health   ─┘                  ├── Fixture derived adapter
                                       └── Google Drive REST GET-only adapter
```

The UI never calls Google Drive directly. Flutter receives only product API responses and never receives Drive/provider credentials.

## Authority invariants

1. Workspace Drive remains sovereign for accepted durable knowledge.
2. Resolver output preserves source identity and lifecycle status.
3. Multiple CURRENT sources of one authority class produce PARTIAL + a blocking structural conflict; the Assistant does not silently choose one.
4. UNKNOWN lifecycle is never promoted to Current.
5. Derived fixtures/indexes are explicitly marked non-sovereign.
6. No write method exists on `DriveReadOnlyPort` in this batch.

## Provider boundary

The default provider mode is `DETERMINISTIC_GROUNDED`. A future LLM/model implementation must sit behind the same source/provenance/authority boundary and may narrow or abstain but may not expand authorization.

## Local/runtime boundary

Local UAT selects dynamic loopback ports for API and Flutter Web. Fixed-port ownership is not a product invariant. Existing processes are never terminated merely to claim a port.

## Final Integrated Mega Batch V1

The architecture now includes Planning/Impact/Decision, Independent Verification,
Security/Capability Control, Engineering Mode, Repository Intelligence, Governed
Execution contracts, Multi-Agent orchestration, Governed Development Lifecycle and
Operations/Recovery/Portability. Workspace Drive remains sovereign and all new state
is derived/rebuildable unless explicitly owned elsewhere.
