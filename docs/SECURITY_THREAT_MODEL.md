# Security Threat Model — Batch 2 Foundation

| Threat | Current control | Residual / next gate |
|---|---|---|
| Cross-project knowledge leakage | project-scoped source catalog + API project context | enforce user/document ACL before any multi-user/live-content release |
| Prompt/document injection | no document content becomes tool instruction; deterministic metadata grounding only | future model gateway must isolate retrieved text as untrusted data |
| Privilege expansion | no write tool; Drive port has no create/update/delete; writes_enabled=false | separate human-approved write contract required in future phase |
| Secret leakage | Drive token is server environment only and omitted from response models/log detail | managed secret store + rotation before hosted deployment |
| Stale/ambiguous authority | UNKNOWN/PARTIAL fail-closed; structural conflict detection | live sync/freshness receipts and supersession revalidation |
| Forged citation | citations originate from catalog/resolver source refs | verify content/version hashes when full-text ingestion begins |
| Browser/API abuse | bounded Pydantic inputs, explicit local CORS, no-store/nosniff/referrer/CSP headers, request IDs | authentication, rate limits and abuse controls before shared hosting |
| Dependency compromise | pinned compatibility ranges + CI checks | lockfiles/SBOM/advisory scanning before production |
| Local fixed-port collision | dynamic loopback port selection | keep as permanent UAT regression gate |
| UI state hiding important status | text + icon/status pill semantics; color is not sole status signal | accessibility audit/WCAG 2.2 AA before product release |

This document does not certify production security. It defines the Batch 2 security boundary and the gates required for later hosted/multi-user operation.

## Final Mega Batch threat extensions

New threat cases include capability-envelope widening, prompt injection attempting
tool escalation, secret leakage into evidence, executor self-certification,
agent authority expansion, stale repository identity, and watcher-triggered
unauthorized mutation. The candidate defaults to read-only/simulation-only.
