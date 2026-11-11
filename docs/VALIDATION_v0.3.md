# v0.3 verification — 11 November 2026

| Gate | Result | What it does and does not mean |
|---|---|---|
| Inherited unit tests | 77/77 pass | Maintains v0.1 and v0.2 world-state, oracle and replay behavior |
| New adversarial tests | 30/30 pass | Approval binding, source matching, NPC knowledge, conflicting state and stale drafts |
| Total automated tests | **107/107 pass** | This verifies the supplied assertions, not autonomous narrative judgment |
| Example journal | Pass | Migrates the real prior 3-session save via one journaled change, then commits four reviewed interpretations |
| Rejected draft | Pass | Conflicting second current controller rejected without a mutation |
| Campaign JSON schema | Pass | Both v0.2 source save and v0.3 interpreted continuation |
| Proposal JSON schema | Pass | Four accepted proposals and the rejected draft have the expected shape |
| PDF | **28 pages** | Rendered with page rasterizer and checked for empty interior pages |
| PDF links | **138 valid internal links** | Clickable contents and source links resolved; no invalid internal targets |

## What the engine demonstrably checks

- Proposals do not mutate state until explicitly approved and committed.
- The human approval receipt is bound to the proposal digest and campaign revision.
- A journaled event keeps its approved draft digest, warning codes and rationale in its source field.
- Native oracle/test outcomes are matched against committed input values.
- TBE oracle *recorded answers* are matched, but their mechanics are **not** recomputed.
- An acting NPC cannot justify its action with a fact it has not learned.
- Beliefs may explain actions but do not count as world-level proof.
- A structured mutually exclusive property cannot simultaneously have two current values.
- A later property assertion explicitly replaces an older one while preserving historical facts.
- An invalid or stale transaction cannot partially alter the actual campaign state.
- Private proposals do not appear in the player-facing preview.
- Journal replay remains deterministic across the v0.2→v0.3 upgrade.

## Known limits

- A human/host must establish whether narrative evidence *actually entails* the proposed consequence.
- Freeform prose is **not** fully checked for contradictions; use structured properties only where needed.
- A human must check that public summaries do not leak unstated secrets.
- Approval is an audit receipt, **not** cryptographically authenticated approval or a security sandbox.
- Runtime/long-journal performance, multi-client synchronization, release readiness, genre balance and sustained human solo-play have not been validated.
- The system does not implement or replace TBE combat, magic, social, travel, advancement or its proprietary tables.
