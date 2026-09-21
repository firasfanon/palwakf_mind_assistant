# Operability, Recovery and Portability

The L5 operations surface is read-only and evidence-oriented. It exposes source mode,
watcher state, connector/model health, cost observations, deterministic recovery,
restart/resume receipts, readiness dimensions and provider-neutral portability.

## Recovery
Derived Mind state is rebuilt from the active read-only source boundary. The drill
serializes the source set, revalidates it through the domain model, hashes before and
after representations, and counts missing source references. PASS requires identical
digests and zero accepted-knowledge loss. The drill never mutates Workspace Drive.

## Restart / resume
Resume receipts bind project identity, source digest and completed-action digest.
Stale source digests or duplicate completed actions fail closed and require
reconciliation before resume.

## Health and readiness
`/health` reports process liveness. `/ready` evaluates authority resolution,
connector health, zero-loss rebuild, restart/resume idempotency and canonical
authority isolation. A degraded live connector produces a blocking readiness result.

## Runtime identity
Repository Intelligence does not carry a baked-in Git SHA. Exact runtime HEAD/ref may
be injected by the local runner or hosting environment. Without exact identity the
repository surface becomes PARTIAL/UNKNOWN rather than claiming stale CURRENT state.

Watchers remain notify/propose-only. Portability exports describe derived-state
contracts, are provider-neutral and contain no secrets. Production readiness and L5
certification remain separate governed decisions.
