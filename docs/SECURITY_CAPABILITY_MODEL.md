# Security and Capability Model

The product applies least privilege and explicit authority boundaries.

- capability discovery/selection does not imply authorization;
- client payloads cannot widen the server authority envelope;
- an attached authorization must match the request project and scoped paths;
- cross-project authorization reuse fails closed;
- prompt-injection indicators block high-risk capability use;
- Arabic and English authority-bypass markers are treated as untrusted input;
- secret-like values are detected without echoing the detected secret;
- denied capabilities do not create execution state transitions;
- canonical semantic writes remain outside the default authority;
- watchers may notify/propose only and cannot mutate canonical state;
- runtime Git identity is evidence only and never grants mutation authority;
- audit/evidence semantics remain provider-neutral.

The L5 candidate does not authorize production, shared-database mutation,
canonical knowledge promotion, or cross-project source mutation. Those require
separate exact-scope authority and independent post-action verification.
