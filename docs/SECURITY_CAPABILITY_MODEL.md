# Security and Capability Model

The product applies least privilege and explicit authority boundaries.

- capability discovery/selection does not imply authorization;
- client payloads cannot widen the authority envelope;
- prompt-injection indicators can block high-risk capability use;
- secret-like values are redacted/rejected from evidence paths;
- denied capabilities do not create execution state transitions;
- canonical semantic writes remain outside the default authority;
- audit metadata is structured and provider-neutral.

