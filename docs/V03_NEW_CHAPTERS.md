# 20. Version 0.3: proposals are not events

The old cycle said *interpret, then commit*, but that left an ambiguity: how does the solo player know whether an interpretation contradicts the stored world or claims more than its source establishes? Version 0.3 adds **a reviewable interpretation draft**, separate from both a die result and a lasting event. The purpose is to make one consequential decision auditable without doubling the number of rolls.

**Core rule:** A result is not a consequence. A consequence is not a fact until it is accepted and committed. A rejected draft has no effect on the fictional world.

| Step | Procedure | What changes in the campaign? |
|---|---|---|
| 1. Resolve | Use exactly one authorized rule or oracle; record its actual outcome | Only the resolution record, if one was required |
| 2. Draft | State a proposed consequence, the specific operations it implies and its source | Nothing |
| 3. Review | Compare the proposal with the committed world, the actor's knowledge, permissions and its source | Nothing |
| 4. Adjudicate | Explain why the proposed consequence follows; explicitly acknowledge unresolved review warnings | Nothing |
| 5. Commit | Apply all effects together with the existing transactional journal | Only the listed effects, atomically |
| 6. Reveal | Tell the protagonist only what they could learn, and retain undisclosed causes for referee-side review | No automatic extra facts |

**No obligatory extra roll.** Most ordinary observations need no elaborate draft. Use the full review whenever the change affects a lasting claim, NPC knowledge, ownership/control of a place, goal status, a dangerous promise, or a faction action. For trivial descriptive color, no world-state mutation is necessary.

## A consequence draft

A draft stores an event ID, summary, exact interpretation, source of authority, suggested journal operations, established supporting claims, beliefs that explain motivation, and the world revision it was written against. It may also name an acting NPC and a separate public summary.

The source is exactly one of the following:

| Source | Required evidence of the resolution | Does the engine verify its meaning? |
|---|---|---|
| Observed | Named witness and an inspectable basis | Only that the fields exist |
| Native oracle | Committed context-oracle event and matching Yes/No answer | **Yes**: event and answer are checked |
| TBE oracle | Recorded official Ask the Weave event and matching four-category answer | **Yes**: receipt and answer only; official rules remain external |
| Native test | Actual dice/modifiers and outcome tier | **Yes**: tier is recomputed |
| TBE rule | Official procedure, recorded outcome and rulebook reference | **No**: caller has to adjudicate TBE mechanics |
| Referee ruling | A written explanation | **No**: explicit discretionary judgment |

**A positive oracle does not prove everything that might follow from it.** If Ask the Weave indicates the messenger reached the village, that does not automatically prove the mayor read the letter or agreed to help. Those are different events or necessary additional inferences, and must be assessed separately. Never invent an extra TBE random event because the companion's interpretation feels dramatic.

## Five checks before accepting the draft

1. **Authority:** Is this the engine authorized to answer this question? Does the cited oracle or test receipt exist, and does its recorded result match?
2. **Causality:** Are the proposed effects physically, socially and temporally plausible? The engine can check recorded IDs, but a human or approved host must decide actual implication.
3. **NPC knowledge:** Can the acting NPC cite each fact as something it truly knows, or is it acting only on a recorded belief?
4. **Current world:** Does the proposal contradict a structured current-state fact, or attempt an unsupported resource/goal change?
5. **Disclosure:** Will the public summary reveal something the protagonist could not have observed?

Review produces **blockers** and **warnings**. A blocker prevents a commit: for example a stale world revision, the wrong rules mode, a missing recorded oracle, an unlearned NPC fact, or two current controllers of the same gate. A warning requires judgment: for example uncorroborated observation, belief mistaken for proof, potentially secret wording, or a question of whether the narrative explanation is convincing. Approval must identify a reviewer, explain the decision and explicitly acknowledge the warnings. This is an **audit trail**, not proof that the reviewer reasoned correctly.

## An interpretation is based on a specific world

The draft includes `base_revision` and a state hash. A later event invalidates an earlier uncommitted draft. Rewrite it against the new world instead of automatically applying yesterday's conclusion. The review stage runs a **temporary copy** of the exact journal transaction, checking references and rollback behavior without changing the real state.

The permission boundary is not a security boundary: this prototype has no user authentication and an external script could call the underlying transaction function directly. The approval receipt is not cryptographically signed. These controls are guardrails for honest solo play and application development.

---

# 21. Current facts, evidence, beliefs and history

Freeform statements are often insufficient for detecting contradictions. Consider the sentences *“The reeve controls the River Gate”* and *“The Carter controls the River Gate.”* The prototype cannot reliably identify all semantic contradictions in English. It can, however, enforce one value per explicitly structured property.

Use an **asserted current state** for a material fact that is mutually exclusive at one time. Each assertion supplies a unique record ID, a `state_key`, a scalar `value`, a readable claim and provenance. Examples:

| Property (`state_key`) | Current value | What it represents |
|---|---|---|
| `GATE:controller` | `REEVE` | Named authority controlling the gate |
| `DEED:location` | `ARCHIVE` | Current physical custodian site of the document |
| `BRIDGE:passable` | `true` | Whether the bridge is currently usable |

If the state **changes**, create a new assertion naming exactly the current record(s) it replaces. The former claim remains in history with `superseded_by` linking to its successor. An NPC that learned the old claim retains historical knowledge; it does **not** automatically learn the new truth. Re-check what that NPC knows before deciding its next action.

| Operation | Meaning | Constraint |
|---|---|---|
| `record_fact` | Original unstructured claim | Has provenance; **no automatic semantic contradiction detection** |
| `assert_state` | One current value under a named property | Rejects a conflicting current value without explicit replacement |
| `learn_fact` | Specific actor learns or believes an existing claim | Does not follow from public visibility by itself |
| `mark_goal` | Records evidence-backed progress | Never grants TBE XP automatically |
| `complete_goal` | Externally adjudicated goal completion | Must satisfy the host game's authority |

A **belief** is not a substitute for evidence. A rumor can motivate a guard to search for a supposed thief, but it cannot establish that the thief exists. When an interpretation is written from an NPC's point of view, its supporting facts must already appear in the NPC's `known` records; its belief references must already appear in `believed`. The reviewer flags an old, superseded fact cited as current evidence.

No property assertion is implied by nearby prose. There is also no built-in ontology proving that `GATE:controller` means exclusive real-world legal ownership, and no general natural-language inference engine. The player names properties precisely and decides when a change merits the extra bookkeeping.

---

# 22. Worked continuation: the Gate of Ash

The included example takes the **existing three-session v0.2 campaign** as its actual starting point, verifies the historical journal, and performs a **journaled v0.3 upgrade**. This preserves previous events instead of rewriting the campaign checkpoint. The new sequence demonstrates a narrow but consequential chain:

1. **An official question of circumstance (native mode).** The PC has evidence that the public inventory identifies a document in the Record Hall. An existing d12 oracle answers *Yes* to whether the hall is open today. The answer is saved; it does **not** yet put the charter in the PC's hands.
2. **Interpretation and visibility.** A proposal establishes only that ordinary public access is available. It is separately reviewed, approved and committed. The PC receives a player-safe description; access to the private vault remains an unresolved question.
3. **The currently controlling actor.** An inspected public notice establishes `GATE:controller = REEVE`. This is an explicit world-state fact, not the product of a plot clock.
4. **A signed transfer order.** A subsequent observation establishes that a transfer order exists. The document alone does not change the gate's controller.
5. **Reject a conflicting draft.** A proposal asserts that the Carter now controls the gate without replacing the currently established controller. Automated review rejects it. Nothing changes.
6. **Accept a witnessed handover.** The actual key exchange is interpreted, reviewed and committed as `GATE:controller = CARTER`, explicitly replacing the older claim. The PC learns the transfer only because the handover was witnessed.

This example deliberately separates **the availability of an opportunity, the physical document, and the actual transfer of control**. It shows why an event, a clue, and a victory condition should not be collapsed into one oracle answer. The protagonist's larger charter-recovery goal remains unresolved unless separate evidence proves completion.

The executable script `make_v03_example.py` writes both `Gate_of_Ash_v0.3_Interpreted.json` and `Gate_of_Ash_v0.3_Review_Trace.json`. The trace includes the rejected proposal, accepted drafts and approval receipts. These files demonstrate software consistency, **not a live human-play campaign**.

## Player-facing versus referee-side views

A private proposal is not visible at all to a player-facing preview. A visible proposal exposes a separately written `public_summary` and only supporting fact IDs already known to that observer; it never returns internal operations or hidden interpretation text. Because the software cannot understand all narrative secrets, a human must still check the public summary before approval.

---

# 23. Tabletop workflow and v0.3 acceptance gates

## The shortest workable procedure

1. **State the intention.** Consult relevant claims, current-state properties and actor knowledge.
2. **Resolve once.** Established outcome, native system, or the host RPG. Don't mix resolution authorities.
3. **Draft only the lasting change.** Say what happened and **what did not happen**; cite any established evidence.
4. **Review.** Resolve blockers; address warnings; supply an explicit human or host adjudication.
5. **Commit atomically.** Save the world update and visible consequences together.
6. **Offer the next choice.** Carry forward unresolved questions rather than inventing plot beats.

## v0.3 review card

| Question | Good answer |
|---|---|
| Which rule decided the uncertainty? | One recorded resolution or an inevitable fact |
| What changed? | Specific valid operations, not just evocative prose |
| Why could that actor do it? | Available means and learned facts or recorded beliefs |
| What remains unknown? | Explicit unresolved question, without an implied answer |
| Could the result contradict current state? | Structured properties checked; prose reviewed manually |
| Who should know? | Separate player-safe summary and actual learning events |
| Can we reconstruct it? | Same journal head and event effects after replay |

## Verified in this build

- All **77 inherited v0.2 tests** continue to pass, alongside **30 new adversarial v0.3 tests** (107 total).
- Old v0.2 save is accepted; the v0.3 change is itself journaled, and the old history still replays.
- Structural contradiction rejection, explicit state supersession and historical replacement links are exercised.
- Oracle receipts and native dice tiers are checked against the actual recorded outcome. TBE results remain external.
- NPC knowledge boundaries, belief separation, hidden previews, stale drafts, acknowledgment of warnings and approval/hash checks are exercised.
- The four accepted interpretation events and one rejected draft in the worked continuation are reproducible.

**Not yet proven:** long-form human playability; whether players consistently choose sensible interpretations; semantic contradiction detection in unconstrained prose; complete tactical or economic resolution; cross-client synchronization; game balance; trademark clearance or general legal suitability for commercial publication.

---

## END OF CAUSAL THREAD v0.3 — CONTROLLED INTERPRETATION ALPHA
