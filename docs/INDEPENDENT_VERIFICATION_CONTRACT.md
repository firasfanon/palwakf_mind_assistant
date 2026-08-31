# Independent Verification Contract

`GENERATOR != FINAL_VERIFIER` is mandatory. A candidate cannot self-certify.

Verification bundles may contain machine tests, static analysis, security gates,
Browser UAT, authority readback and an optional model critic. Deterministic failure
cannot be overridden by an optional critic. Negative evidence is preserved.

