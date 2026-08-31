# Engineering Mode Contract

Engineering Mode compiles trusted context, relevant skills/lessons, repository
identity, risks, verification requirements, and a next-safe-action. It is advisory.

Invariants:

- stale/unknown repository identity never becomes mutation-ready;
- advice does not create source-control authority;
- exact repo/ref/HEAD must be re-resolved before mutation;
- Workspace authority is the upper bound;
- next-safe-action can narrow or defer, never widen authorization;
- Browser/runtime verification remains independent from code-generation advice.

