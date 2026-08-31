# UX Product Map

## Primary navigation

- **Assistant**: daily conversational surface; explicit project context; local-session history; grounded status/citations.
- **Dashboard**: portfolio/authority/knowledge/connector health and alerts.
- **Project Mind**: one-project state, sources, supersession and conflict indicators.
- **Knowledge Explorer**: metadata-grounded discovery inside a selected project.
- **Conflicts**: human-review center for structural conflict candidates; no false semantic certainty.
- **Sources & Connections**: connector mode, READ_ONLY boundary and source provenance.

## Responsive behavior

Desktop (`>=900px`): persistent right-side navigation with scrollable destinations and fixed identity/footer.

Narrow (`<900px`): AppBar + Drawer for full navigation + bottom NavigationBar for the four daily core surfaces. The target regression viewport is `390x844` in addition to the `800x600` desktop constrained-height gate.

## Visual semantics

- Current/Resolved/Ready/Healthy: verified state.
- Unknown/Partial/Review/Degraded: requires attention.
- Conflict/Blocking/Fail: critical review state.
- READ_ONLY and WRITES_OFF remain visible on operational surfaces.

Color is never the only carrier of status; every state includes explicit text and/or icon semantics.

## Final Mega Batch product surfaces

New governed surfaces: Planning & Impact, Human Approval Studio, Independent
Verification, Security & Capabilities, Engineering Mode, Repository Intelligence,
Governed Execution Studio, Multi-Agent Orchestration, Development Lifecycle, and
Operations & Recovery. All surfaces display derived/trust/authorization boundaries.
