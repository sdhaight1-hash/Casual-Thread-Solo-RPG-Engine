# CAUSAL THREAD
## Original solo roleplaying engine — controlled interpretation alpha v0.3

**Working title · 11 November 2026 · Original system manuscript**

*Causal Thread* is a solo roleplaying engine for discovering what happens in a persistent fictional world. It supplies its own simple action-resolution method, and it can instead delegate mechanical outcomes to another tabletop RPG. It is **not** an unofficial reprint of PUM, SUM, *The Broken Empires*, or *Worlds Without Number*. All six prompt tables in this manuscript are newly authored for this draft.

**Status:** Working alpha. The core reference implementation and 107 automated tests are included. It has not undergone human multi-session playtesting, independent legal clearance, or balancing across genres. The product name is provisional and has not been cleared as a trademark.

---

> **Historical v0.2 changes:** A replayable transaction journal, contextual question keys, relationship-aware NPC prompts, visible versus private scene context, deadline reviews that never declare victory, and an independently verified three-session example. These additions clarify the original core rather than create more compulsory dice rolls.


# 1. Diagnosis: Why the old architecture remains fragmented

The previous companion achieved substantial integration, but its operating units still compete for the same fictional decision. PUM offers plot interventions; SUM offers scene interventions; Campaign Forge offers faction/setting events; TBE offers official solo events and its own skill, travel, and social procedures. Even when each tool is individually well designed, stacking them creates **multiple authorities** and sometimes contradictory results.

| Existing source / capability | Demonstrated strength | The mismatch | Design response |
|---|---|---|---|
| PUM v9, pp. 2–6 | Plot scopes, nodes, beats, player-centered unfolding | Abstract track position can be mistaken for a fictional accomplishment | Store goals and unresolved situations; progress only through event-backed milestones |
| SUM v8 Rev2, pp. 3–11 | Scene shape, character behavior, reaction and discovery inspiration | An ungrounded result can override a known NPC or location | All prompts are *queries against established context*; never automatic facts |
| WWN, *Creating Your Campaign*, pp. 114–221 | Focused preparation of connected local situations and adventure material | Setting generation can become an encyclopedia before play | Prepare only reachable places, motivated institutions and usable choices |
| TBE, chs. 2, 6, 10–15, 19 | Consequential skill/conflict/travel/magic procedures, goals, official solo tools | A second oracle or experience engine introduces conflicts | Authority adapter delegates all game-mechanical results to TBE |
| Our TBE companion v1.5, Part V-B | Knowledge restrictions, NPC decisions, dated faction attempts | The routines still have separate records and interaction instructions | Use one shared record vocabulary and one action → result → consequence protocol |

**Research cross-check.** Mythic GME 2e organizes questions, scene flow, ongoing lists and events as complementary rather than unrelated modules (Word Mill Games, official publisher description). *Ironsworn* illustrates how tracked objectives can give play direction, although its procedures and move text are not used here. These are outside design comparisons, not source material incorporated into the rules.

The central operating principle is **a fictional change needs a cause**. Causes may be established action, a permitted rules result, ordinary time and physical processes, or an explicitly framed uncertainty resolved by an oracle. A prompt only suggests *how a plausible consequence might appear*. It never substitutes for the cause.

---

# 2. One engine, five records, one decision pipeline

At minimum, keep five linked record types. Each record has a stable identifier so it can be referred to from other records.

| Record | Minimum data | Key restriction |
|---|---|---|
| **Claim** (fact/rumor/proposal) | ID; statement; status; provenance; date | Rumor and proposal are not established truth |
| **Actor** | ID; objective; knowledge and beliefs; available means; restrictions | An actor cannot use information, authority, or resources it lacks |
| **Goal** | ID; owner; desired state; evidence of completion; milestones | A tick or scene count cannot grant success or experience |
| **Place** | ID; location and access; controlling actors; physical affordances; leads | A location cannot silently change when the scene changes |
| **Event** | ID; time; actor/action; adjudication source; recorded effects | A fictional state change has an accountable cause |

Optional *Threads* are references joining an actor, goal, claim, and place. A thread is **not** a parallel plot-authority or a progress-to-victory meter. It is a named unresolved causal relationship; for example, `TH-2: Why has the river gate been relocated?` linked to a surveyor, a mill council, and a canal-side site.

The central play transaction is:

1. **Frame:** Describe where the protagonist is, what they can know, and what they are trying to do.
2. **Check:** Compare the question/action with established claims, capabilities, constraints and elapsed time.
3. **Route:** If the outcome is determined, narrate it. If a game rule decides it, use that rule. If a material unknown remains, use the authorized oracle. If all that is missing is color, use a prompt.
4. **Interpret:** State exactly what the resulting fiction establishes, costs, opens, or leaves unknown.
5. **Commit:** Record the resulting event and update only the claims, actors, goals, resources, locations, and dates it actually changed.
6. **Offer a choice:** Provide at least two plausible next actions when the protagonist would otherwise be stuck. The player remains in control of the protagonist.

### Authority order

**Established world facts / inevitable consequences → Host RPG mechanics (or the Causal Thread native test) → One question oracle for a material uncertainty → Optional descriptive prompt → Committed event.**

Never roll multiple systems to answer the same question. A scene opener does not decide an attack roll. A faction pressure marker does not decide a battle. An NPC action choice does not decide whether the NPC succeeds. An official TBE Random Event is not an invitation to roll another contradictory surprise.

---

# 3. The claim protocol: truth, knowledge, and uncertainty

A Claim may be in exactly one of four states:

| Status | Meaning | Can an NPC act on it? |
|---|---|---|
| `proposal` | A generated possibility not yet accepted into the fiction | No, unless separately established through observation or information |
| `rumor` | A statement a person or institution has communicated | Yes, as a *belief*, not as proof |
| `established` | Known to be true in the campaign record | Only if the specific NPC actually learned it |
| `refuted` | Earlier claim shown untrue or superseded by evidence | Actors may continue to believe it until corrected |

**The player knows the campaign record; NPCs do not.** Each NPC maintains `known` and `believed` claim IDs. An NPC may sincerely respond to a false rumor, but its action should be based on a documented belief. The actor cannot cite information that belongs only to another party.

To establish a new claim, write a **provenance**: a witnessed action, a native skill result, a TBE mechanic, a recorded oracle answer, or an ordinary consequence of facts already established. If a roll produced only a narrative prompt, the outcome remains a proposal until you commit a contextually valid interpretation.

Do not reroll a committed answer merely because it was inconvenient. A new test is appropriate only if a **material premise changed**, such as the passage of time, a new witness, a broken lock, or newly acquired information. Record what changed.

**Mysteries:** A core clue cannot be gated behind a single successful roll if its discovery is essential to keeping a reasonable inquiry moving. In TBE mode this follows the official investigation advice (TBE ch. 17). Optional rolls decide speed, cost, additional detail, or danger—not whether a reasonable search gets the essential clue.

---

# 4. The standalone Causal Thread oracle

This is a new, lightweight standalone oracle. **Do not use it to replace Ask the Weave while playing in TBE mode.**

First ask a precise yes/no question about something genuinely uncertain. Choose likelihood using existing evidence, not player preference. Roll **1d12**, once.

| Prior likelihood | Yes on d12 | Chance |
|---|---:|---:|
| Remote | 1–2 | 16⅔% |
| Unlikely | 1–4 | 33⅓% |
| Even | 1–6 | 50% |
| Likely | 1–8 | 66⅔% |
| Near certain | 1–10 | 83⅓% |

A `1` is an **exceptionally strong Yes**; a `12` is an **exceptionally strong No**, regardless of the prior likelihood. These results intensify the answer but do **not** automatically summon a second event. If a surprising answer contradicts the established fiction, re-examine the premise; don't erase a known fact.

Examples: `Would the exhausted courier reach the next village today?` (Unlikely, unless a shortcut is known). `Has the steward heard the public accusation?` (Likely if the accusation was made in front of their staff). `Is the sealed deed genuine?` (Even if no evidence exists; an actual authority or skill may instead be required to establish authenticity).

### Limits on asking

- If the answer is already established, **no roll**.
- If a character action has a relevant resolution rule, **use that rule** before asking about success.
- Ask one question per uncertainty. State a specific fictional interpretation and commit it before asking related questions.
- No spontaneous oracle event rolls merely because you feel the story needs motion. Use actual actor pressure, a site lead, or an uncommitted fact.

A pencil-and-paper record is enough: `Q-3 / Day 2 / Likely / 1d12=7 / Yes / A hired messenger reached the surveyor / Committed`.

---

# 5. Standalone character and action resolution

Causal Thread can run without another RPG. This is an intentionally small **narrative conflict engine**, not a tactical battle simulator.

## Character setup

Write a goal, a feared consequence, a bond, and five **Approaches**: **Force, Finesse, Reason, Rapport, Resolve**. Assign **3, 2, 1, 1, 0** in any order. These are broad competencies; specialist fictional training grants permission to attempt expert tasks, not a numerical bonus by default.

When failure matters, state **intent**, **obstacle**, and **stakes** before the roll. Use 2d10 of different colors: one *Effort* die and one *Friction* die. Add the relevant Approach (0–3) to Effort and an obstacle rating (0–4) to Friction. Unusual expertise or impairment may adjust either rating by at most 1, keeping the combined ratings within 0–4. Neither side rolls twice.

**Margin = (Effort + capability) − (Friction + obstacle).**

| Margin | Result | Mandatory interpretation |
|---:|---|---|
| +3 or greater | Clean gain | The declared objective succeeds; update the world coherently |
| 0 to +2 | Gain with cost | The declared objective succeeds, but a previously plausible cost materializes |
| −1 to −3 | Setback with opening | The attempted objective fails or stalls; reveal a usable new route, clue, or leverage |
| −4 or less | Hard setback | The attempted objective fails and the declared consequence takes effect |

**Example:** Mira tries to convince the watch captain to allow a brief inspection before the gate closes. Rapport 2 versus resistance 1; Effort=7 and Friction=6, so margin = (7+2)−(6+1) = **+2**. She is permitted to inspect, but must name her sponsor in front of witnesses. The extra visibility becomes a new established fact; no additional oracle answers the same negotiation.

### Initial probability calibration

The opposed-d10 mechanic has a triangular probability distribution. Enumerating all 100 equally likely Effort/Friction pairs produces the following **exact**, pre-playtest outcome frequencies. These are not a claim of balanced gameplay; they expose the design's current stakes.

| Capability relative to obstacle | Clean gain | Gain with cost | Setback with opening | Hard setback |
|---|---:|---:|---:|---:|
| −2 | 15% | 21% | 28% | 36% |
| −1 | 21% | 24% | 27% | 28% |
| Equal | 28% | 27% | 24% | 21% |
| +1 | 36% | 28% | 21% | 15% |
| +2 | 45% | 27% | 18% | 10% |

At parity, the protagonist achieves the declared objective in **55%** of consequential attempts, though nearly half of those gains impose a cost. The important balancing question is not simply how often they succeed, but whether repeated costs and hard setbacks produce a playable campaign. That requires actual playtesting.

### Costs and harm

On a cost result, choose a cost that follows the stated stakes. Time spent, damaged reputation, an obligation, an expended supply, lost access, and physical danger all work. The engine never invents a particular expense that the actor cannot actually pay. A cost may affect a faction or a relationship, but cannot rewrite an established fact.

A standalone character has **Strain 0–4**. Record one Strain when a harsh consequence reasonably exhausts, endangers, or overwhelms them; at 4, they cannot continue risking exertion until helped or given safety and recovery. A safe night's rest and suitable care removes one Strain, unless a serious fictional injury demands specific treatment. Strain is **not** a substitute for the detailed injury system in TBE. In adapter mode, ignore Causal Thread Strain.

Do not roll repeatedly for the identical unchanged approach. A second attempt needs a different tactic, tool, ally, place or new circumstances. For a complex struggle, resolve a sequence only when each exchange poses a new meaningful decision.

### Standalone growth

Record one milestone for a **material, evidenced step** toward a declared personal goal. Once three different milestones have been recorded and their narrative significance is clear, mark one **Growth**. Spend 1 Growth to raise an Approach below 3 by 1, or save it for future advancement. A goal's completion does not require a full track; it requires meeting its actual completion evidence. This is a playtest rule subject to balance revision. **TBE mode never uses this Growth system or Causal Thread Strain.**

---

# 6. NPC agency: decide, attempt, and react

An NPC is not a personality result waiting to happen. It is an agent embedded in a social and physical world.

Record: (a) **what they want**, (b) **what they know**, (c) **what they merely believe**, (d) **what they can actually do**, (e) **what they will not risk**, and (f) **whom they owe or oppose**. The six fields are more important than any appearance or demeanor prompt.

When an NPC must act, consider only **two or three plausible options**. Reject any option for which a capability, requisite knowledge, or tolerable risk is missing. Then score feasible options:

`Action priority = 2 × expected impact (0–3) + obligation (0–2) + goal alignment (0–2) − risk (0–3) − resource cost (0–3).`

Choose the highest score. A tie defaults to the less costly action; the reference program then chooses a stable alphabetical tiebreaker. At the table, an established habit can determine a tie instead. If the NPC has no feasible option, they wait, ask for help, gather information, or retreat; no compulsory drama occurs. Scoring is a **decision aid**, not a social skill or success roll.

**Personality shapes the route, not the permissions.** A proud clerk and a timid clerk might both refuse to release a sealed order because neither has the right to do so. The proud clerk may challenge you openly while the timid clerk quietly suggests which magistrate can sign it.

Actor choices become **attempts**, never automatic accomplishments. A fight, negotiation, pursuit, or spell must still be resolved using the applicable host rules or the standalone action system. Evidence from earlier scenes changes future NPC choices organically, without rerolling their personality.

---

# 7. Faction agency and offscreen time

The world should continue moving when the protagonist is elsewhere—but it should move at the speed of plausible actions, not a narrative countdown.

Each institution has: objective; leadership; agents; physical assets and money; influence; information; rivals; constraints; and **next plausible action**. Institutions are actors with larger resources, not disembodied plot forces. Two connected institutions can have contradictory goals without either being designated the villain.

A **world window** opens only when meaningful in-fiction time passes (hours for a pursuit, days for a city hearing, weeks for a campaign, etc.). The player chooses the appropriate scale before considering events. For each of at most **three currently relevant factions**, allow **one credible attempt per window**.

1. Has this group learned enough to intend the attempt?
2. Does it possess the agents, funds, access and travel time required?
3. What specific thing is it trying to change, and what can oppose it?
4. If it is a routine unopposed consequence of known facts, establish that consequence. Otherwise, route the contested outcome through the native mechanics or host rules / official oracle.
5. Record **pending, succeeded, failed, partial or blocked**, together with its source. Update only actual losses, gains and observations.

**A calendar reaching Day 7 never grants a faction a victory.** A clock may indicate *when they try*, or *when a consequence becomes urgent*, but the success of the attempt remains separate. Opposed factions can invalidate one another's means. A rumor spreading does not grant an actor the underlying truth.

**Information travels.** The PC cannot react to a council's successful private meeting until that outcome has a discoverable path: a witness, public notice, intercepted letter, changed guard orders, or the like. This maintains suspense without requiring the player to pretend an NPC knows everything the system knows.

---

# 8. Scene control and meaningful pacing

A scene exists because a person wants to accomplish something at a place, or because an established world event directly demands attention.

### Opening a scene

Write `Place / Time / PC intention / Present actors / Expected normal situation / Immediate pressure`. If the opening is already determined, play it. For a genuinely uncertain opening in standalone mode, ask one appropriately framed question such as `Is the promised contact here when I arrive?` and interpret it. In TBE mode use **Subverted Expectations** if warranted; never add a second Causal Thread opening roll.

### While playing

Alternate between declared actions and observed consequences. Consult the NPC process when someone else's reaction cannot be inferred. If a place needs an observable detail, use a **Signal** or **Site** prompt. If an action is uncertain, use the authorized rules. Do not roll for decoration if the description already makes sense.

### Close a scene

Write only four lines:

- **What changed?** (event and claim IDs)
- **Who learned it?** (actor IDs; do not confuse rumor with fact)
- **What remains in motion?** (goal, faction attempt or pending question)
- **What can the PC choose next?** (two grounded opportunities)

### Pacing without plot coercion

**Open play:** Review significant changes when scenes end. **Focused play:** Review the active goal after each materially relevant obstacle. **Exploration:** Review at site boundaries or meaningful travel stops. These modes change *when you check the record*, not the world's chances or the character's competence.

If play stalls, don't inject a random adversary. Inspect the nearest outstanding obligation, an actor's feasible action, or a site that genuinely bears on the PC's goal. Make an opportunity *observable* and give the player a choice to pursue or ignore it. If nothing credible is available, advance time and review a faction attempt.

---

# 9. Campaign Forge rebuilt as a causal environment

Start with one reachable district, **two institutions, three useful places, three named NPCs**, and a single current protagonist goal. Add more only because play reaches them. The starting area must contain a safe option, a difficult option and an option that changes the balance between two other actors.

For each place write: **purpose, access, local authority, useful evidence or resource, active pressure, and two approaches**. Then connect it to at least one other place and one actor. A place unconnected to any interest is atmosphere, not campaign infrastructure.

For any important site, use the **three-way site triangle**:

1. **Demand:** Somebody needs something to happen here.
2. **Resistance:** A person, institution, hazard or physical fact prevents easy success.
3. **Leverage:** A clue, alternative access, bargain, ally or weakness can change the terms.

Write two distinct resolutions, not one predicted storyline. For example, a flooded sluice can be approached by gathering a survey team or bargaining with the toll keeper; direct violence is neither assumed nor forbidden. Leave room for tactics the player invents.

### Protected clues

Separate the **essential clue** from its **bonus interpretation**. An essential clue is gained on a reasonable, applicable investigation; a test may instead determine whether the party gets it quietly, quickly, or with added leverage. Bonus information and concealed obstacles may depend on actual system mechanics. This follows the investigation safety principle found in *The Broken Empires* GM guidance, while the site triangle itself is newly authored.

### Worldbuilding consequences

Geography governs feasible roads and delivery times; governance defines legal authority; economics constrains resources; culture shapes whom others trust; religion shapes duties and limits. These are world-state fields, not five additional dice systems. If the base rules contain an explicit legal, travel or magical procedure, use it.

---

# 10. Six original d12 prompt tables

These tables are **optional prompts**. Their results are neither automatic events nor rule outcomes. Use the relevant table once, interpret the result against the campaign record, and reject interpretations that conflict with established facts.

## Table A — Pressure arriving (d12)

| d12 | Prompt |
|---:|---|
| 1 | A scarce resource is promised to two parties |
| 2 | A working arrangement becomes publicly disputed |
| 3 | The person who can authorize action is absent |
| 4 | A routine delay makes an existing deadline matter |
| 5 | An old obligation is called due |
| 6 | A necessary route closes for a mundane reason |
| 7 | Someone refuses a formerly acceptable compromise |
| 8 | A minor failure exposes a larger dependency |
| 9 | A witness cannot safely speak openly |
| 10 | An institution is forced to choose whom to protect |
| 11 | A costly truth reaches an interested outsider |
| 12 | An agreement still exists but its enforcement fails |

## Table B — An opening appears (d12)

| d12 | Prompt |
|---:|---|
| 1 | A neglected record becomes accessible |
| 2 | A rival needs a temporary partner |
| 3 | The responsible official must appear in public |
| 4 | A routine shipment reveals where goods move |
| 5 | A third party will verify a limited claim |
| 6 | A maintenance problem creates safe access |
| 7 | A strained alliance offers one honest conversation |
| 8 | An overlooked route avoids the obvious obstacle |
| 9 | An old promise can be fulfilled in a new way |
| 10 | An opponent's plan relies on a fragile assumption |
| 11 | A neutral specialist is available for hire |
| 12 | A public custom gives the protagonist a hearing |

## Table C — Observable signal (d12)

| d12 | Prompt |
|---:|---|
| 1 | Fresh marks on a familiar object |
| 2 | Two accounts disagree on timing |
| 3 | A guard follows an unusual instruction |
| 4 | A delivery is made to an unexpected door |
| 5 | An official mark appears in the wrong context |
| 6 | A public announcement leaves out one important name |
| 7 | Someone knows a detail they were not told |
| 8 | A repeated sound occurs at an inconvenient hour |
| 9 | A hidden expense appears in ordinary bookkeeping |
| 10 | A journey takes longer than its stated route allows |
| 11 | A witness corrects a seemingly insignificant word |
| 12 | An object is returned carefully altered |

## Table D — Personal motive (d12)

| d12 | Prompt |
|---:|---|
| 1 | Keep a dependent safe from public scrutiny |
| 2 | Avoid losing a role earned through years of service |
| 3 | Repay help received at an inconvenient time |
| 4 | Demonstrate competence to a skeptical superior |
| 5 | Protect a promise made to someone now absent |
| 6 | Prevent outsiders from exploiting a local dispute |
| 7 | Preserve an institution despite disliking its leader |
| 8 | Obtain enough time to repair a past mistake |
| 9 | Earn independent standing rather than borrowed prestige |
| 10 | Keep a damaging but true confession private |
| 11 | Stop a rival from monopolizing necessary knowledge |
| 12 | Avoid repeating the last generation's disaster |

## Table E — Usable place detail (d12)

| d12 | Prompt |
|---:|---|
| 1 | An entrance used only for maintenance |
| 2 | A public noticeboard with contradictory dates |
| 3 | A room that preserves traces of earlier work |
| 4 | A gathering place outside formal authority |
| 5 | A natural bottleneck with a safe alternative |
| 6 | A locked store whose key is held elsewhere |
| 7 | A work shift during which supervision changes |
| 8 | A visible repair covering older construction |
| 9 | A route whose condition depends on weather |
| 10 | A quiet corner where messages can be exchanged |
| 11 | A communal resource controlled by custom |
| 12 | A vantage point offering information, not safety |

## Table F — Consequence or negotiated cost (d12)

| d12 | Prompt |
|---:|---|
| 1 | Lose time but gain a clear deadline |
| 2 | Owe a favor to an identifiable person |
| 3 | Expose the protagonist's interest to a rival |
| 4 | Use up a specifically recorded supply |
| 5 | Strain an established relationship |
| 6 | Accept a temporary restriction on access |
| 7 | Reveal one secret to obtain another |
| 8 | Bring a neutral party into a public dispute |
| 9 | Accept evidence that damages an ally's standing |
| 10 | Choose which of two commitments takes priority |
| 11 | Surrender a safe position to keep momentum |
| 12 | Leave evidence of the protagonist's involvement |

---

# 11. The Broken Empires adapter: exact boundaries

Causal Thread can be used **alongside The Broken Empires**, but this adapter is not a revised TBE rules engine. It governs *when and why* to consult the rulebook, never *how to alter* its official tests.

| Situation | TBE authoritative procedure | Causal Thread responsibility |
|---|---|---|
| Character wants something risky | Core skill and Success Level procedures, ch. 2 | Make intention, opposition, and state change explicit |
| Goal advancement | Goals and experience, chs. 6–7 | Store the goal, evidence, prior awards; never create alternate XP |
| Uncertain yes/no fiction | Ask the Weave, ch. 19; honor double-trigger Random Events | Record the official answer once and commit its interpretation |
| Uncertain scene start | Subverted Expectations, ch. 19 | Supply established location and expectations; do not reroll |
| Social conflict | Static / Competitive Intrigue, Tolerance, Leverage and SLs, ch. 10 | Supply actual NPC aims, constraints and relationship history |
| Travel | Journey/HexMarch, ch. 12 | Store geography, calendar, discovered routes, rumors and costs |
| Magic | Weave Magic and Divine Magic, chs. 14–15 | Supply motive, observed signs, provenance; never waive Laws, Piety or Fraying |
| Clue investigation | GM advice on core clues, ch. 17 | Keep essential evidence available to reasonable inquiry |
| NPC Tags and continuing events | NPC creation and Empires List, ch. 19 | Store actor-specific knowledge and consequences with stable IDs |

The TBE adapter **disables** the standalone d12 question oracle, 2d10 native conflict test, Strain and Growth rules. An official Ask the Weave double creates the official Random Event once. A descriptive Causal Thread prompt cannot create another Random Event from that same trigger.

For published TBE setting details, distinguish **canon** from proposed local material. A procedural generator may propose a new village, custom, or organization; it cannot rewrite a published nation's law, divine Domain, language or historical event without the player's explicit decision to run an alternate setting.

---

# 12. Worked three-day example: The Glass Canal

This example is **fiction invented for Causal Thread**, not a canonical TBE location. Rolls listed below are fixed illustrative results; the included Python prototype reproduces the relevant oracle and decision records.

### Day 1 — Initial claims

The protagonist wants to learn why village water has vanished. Inspection finds recent tool marks on the canal survey stone (`F-1`, established). A dockworker says the mill council poisoned the wells (`F-2`, rumor). The protagonist knows the tool marks and *believes* the accusation. The council does not automatically know either claim. The goal is `G-1: Determine whether the canal diversion caused the shortage`, with completion evidence specified as original markers and access to the toll sluice.

**Crucial distinction:** The accusation has not become fact merely because the player heard it. It can influence the protagonist's questions and the town's behavior without establishing guilt.

### Day 2 — An NPC makes an informed choice

The keeper wants to prevent another flood. They know about the moved stone and can open records but cannot confiscate a charter. Feasible action `Open records` is selected over infeasible action `Confiscate mill charter`. An NPC choice does not mean the clerk successfully wins the resulting argument. If anyone contests access, use the native contest or TBE Intrigue procedures.

### Day 3 — A faction acts offscreen

The mill council has the funds and messenger to contact an upstream surveyor. Its **one attempt for this window** is recorded as pending. The question `Did the messenger reach the upstream surveyor?` is judged **Likely**; original d12 result **7** means **Yes**. The attempt is settled as *contact made*. The council has gained an appointment, **not** won ownership of the waterway, confiscated evidence, or somehow informed the protagonist.

In a later scene, the PC can question the keeper, seek the surveyor, or inspect the sluice. Those actions are choices; none is the obligatory next plot beat. The campaign has progressed because specific actors did specific things, not because a track advanced.

**Scenario check:** The saved sample state includes claim IDs, separate knowledge/belief lists, a goal, one faction attempt, an adjudication source and a dated resulting event. It deliberately leaves additional setting and combat mechanics out until they are needed.

---

# 13. Quick-play sheet and record templates

### Five-minute campaign setup

| Field | Fill in |
|---|---|
| Protagonist and immediate goal | ______________________________ |
| Starting place and its defining constraint | ______________________________ |
| Two interested actors and what each wants | ______________________________ |
| A discovered truth | ______________________________ |
| A rumor that might be wrong | ______________________________ |
| Two possible actions the PC could take | ______________________________ |
| Immediate fictional date | ______________________________ |

### Session entry

| Field | Fill in |
|---|---|
| Scene ID / day / location | ______________________________ |
| Protagonist's intention | ______________________________ |
| Known facts and present actors | ______________________________ |
| Opposition and real stakes | ______________________________ |
| Authority used (known / host / native / oracle / color) | ______________________________ |
| Actual result and provenance | ______________________________ |
| State changed (IDs) | ______________________________ |
| Who learned what | ______________________________ |
| Two player-owned next options | ______________________________ |

### Faction attempt

| Field | Fill in |
|---|---|
| Actor / active time window | ______________________________ |
| Intended action | ______________________________ |
| Means and prerequisite knowledge | ______________________________ |
| Opposition / travel time | ______________________________ |
| Outcome: pending / succeeded / partial / failed / blocked | ______________________________ |
| Rules or evidence supporting resolution | ______________________________ |
| New facts / changed resources / who can observe it | ______________________________ |

---

---

# 14. Version 0.2: the committed world journal

The v0.1 engine could record events but could not rebuild the world from them. That meant a player could accidentally record a change in one place without updating the NPC, goal, or other place it affected. Version 0.2 introduces a **checkpoint plus an append-only journal of transactions**. This is a limited, functioning form of event replay; it does not claim every existing v0.1 editing function has been refactored into event sourcing.

**Two legitimate phases:**

1. **Campaign setup.** Use ordinary constructors to register places, actors, background facts and initial goals. Validate the state. No journal is needed yet.
2. **Campaign play.** Freeze the starting snapshot with `start_journal(state)`. From then on, every lasting change must be a single `transact(...)` call. Direct edits are detectable and blocked on the next commit. `replay_journal(...)` reconstructs everything since that checkpoint.

A transaction has **an event ID, plain-language cause, resolution authority, ordered effects, evidence, visibility, revision number, and before/after hashes**. An attempted action is not its successful consequence. Two effects from the same resolution—such as *the courier reached the gate* and *the guard learned the message*—must be committed together when both are established.

## Supported committed effects

| Effect | Meaning | Guardrail |
|---|---|---|
| `record_fact` | Record a claim with status and provenance | Does not automatically inform any NPC |
| `learn_fact` | Give a specific actor knowledge or a belief | Only established claims may be known as truth |
| `grant_mean` | Add a real resource or capability to an actor | No automatic resource creation from an NPC intention |
| `move_actor` | Establish an actor's location | Destination site must exist |
| `set_relation` | Set one actor's stance toward another | Directional relationship, −2 to +2, not a skill bonus |
| `mark_goal` / `complete_goal` | Record evidenced progress or externally adjudicated completion | Never issues TBE XP |
| `advance_time` | Explicit passage of days | Does not silently advance factions |
| `link_site` | Join two registered places | The link is reciprocal |
| `open_thread` / `close_thread` | Record or conclude an unresolved situation | A deadline prompts review, not a result; closing requires evidence |
| `record_attempt` / `settle_attempt` | Record and adjudicate a faction's attempt | One attempt per actor per declared window; success still needs authority |
| `record_question` | Store a resolved *native-mode* oracle answer | Answer is not a world-state consequence |

**Atomicity example.** The PC witnesses a clerk receiving a signed warning. In one transaction, establish the document, give the clerk knowledge of its contents, and record the resulting relationship change if justified. If the clerk is not a registered actor, the whole transaction fails and none of those changes are saved. This is more reliable than three unrelated notes.

**Replay and integrity.** `audit_campaign` validates references *and* reconstructs the journal from its checkpoint. A forged receipt, direct mutation, missing actor, out-of-order revision, or inconsistent hash rejects the reconstructed state. The hashes are integrity checks, **not cryptographic signatures or a security boundary** against a person deliberately replacing the entire save file.

**Important limit.** This alpha journals changes made through its v0.2 transaction API only. It does not automatically infer updates from freeform prose, adjudicate whether evidence proves a claim, or migrate unrelated companion formats. Compatible v0.1 JSON state can be checkpointed, after which its version is updated to 0.2.

---

# 15. Context-keyed oracles: questions that remember their premises

An oracle's greatest weakness is not random chance; it is *uncontrolled repetition*. Reframing the same unanswered issue until a preferred result appears undermines a persistent world. Version 0.2 gives important questions stable **question keys** and records the specific claims, actors, and sites used to assess likelihood.

1. **Check authority.** Established fact needs no roll; a character action uses game mechanics; a fiction question may need the oracle. TBE mode still uses official *Ask the Weave*, and the native `context_oracle` is disabled.
2. **State the question** and a stable key: `courier-present`, `archive-guard-alert`, etc.
3. **Identify premises.** Cite the facts, and optionally the actor IDs or place IDs, that affect the odds. State the likelihood and a short rationale.
4. **Identify time scope.** Use `fixed` for one-off truths; use the actual `day:N` for a genuinely time-changing situation. Time does not retroactively change historical truth.
5. **Roll once.** The original d12 thresholds remain unchanged. The answer and its emphasis are committed; no world effect follows automatically.
6. **Interpret and commit.** If the answer produces an observable fact, record it in a separate, sourced transaction and share it only with witnesses who learned it.

| Key | Premises | Odds | Roll | Result | What the result does *not* prove |
|---|---|---|---|---|---|
| `courier-present` | Messenger departed at dawn | Likely | 7 | Yes | The courier persuaded anyone to help |
| `charter-genuine` | Only a seal impression is known | Even | 10 | No | Who actually forged it |
| `watch-returned` (day 3) | Watch was sent on day 1 | Likely | 3 | Yes | That the watch survived without loss |

Questions cannot be asked again with the same key and identical recorded premises (including any selected actor knowledge or site state). After meaningful new evidence or passage of time in an explicitly time-scoped question, a new roll requires a written change reason. Software can detect different **recorded** premises, but it cannot determine whether the new evidence is truly relevant. That remains a player judgment.

**No double event rule:** In native mode, a special die result changes interpretation emphasis only. It never independently generates an extra event. In TBE mode, `record_tbe_question(...)` stores the **player-supplied** official Ask the Weave result without computing it; a double (11, 22, ... 99, or 00 represented as 100) flags the official Random Event as pending. Complete that event using the TBE rulebook. Causal Thread never rolls a second event or calculates TBE probabilities.

---

# 16. Social agency, scene focus and offscreen pressure

## NPCs: enduring aims versus immediate speech

A merchant's long-term aim may be to regain market access, while their present stance toward the PC is distrustful. In today's conversation they might want a guarantee rather than a confession. These are three distinct pieces of information, and the same NPC can change tone without instantly changing allegiance.

Write the following before an important exchange:

| Field | Example | Rule |
|---|---|---|
| Enduring aim | Protect the ferry concession | Persists until evidence changes it |
| Present stance | −1 toward the PC | Directional; records justified shifts only |
| Topic knowledge | Has seen `CL-6`, believes `R-3` | Belief is not truth |
| Immediate intent | Seek an official guarantor | Feasible within their role and means |
| Boundary | Will not forge a public decree | No attitude roll can erase it |
| Response | Offers to help after a witness signs | Social skill or host Intrigue resolves contested persuasion |

The reference engine's `npc_conversation_frame(...)` returns a bounded referee prompt, not dialogue, success, or knowledge from nowhere. The standing relationship is an **interpretive aid**, not a new modifier to TBE's Tolerance, Leverage, or Success Levels. Formal TBE social procedures remain authoritative.

## Scenes: expected first, relevant pressure second

A scene should begin from the protagonist's purpose and the location's established affordances. The read-only `scene_brief(...)` shows **only** known site leads, visible unresolved threads, and non-concealed actors recorded at that site. It does not reveal secret NPC knowledge or hidden threats. If a relevant actor has a feasible reason to interrupt, establish or resolve that action through normal authority. Otherwise play the expected scene.

**Scene stop rule:** End a scene when its intention is fulfilled, becomes impossible, the situation changes location or time, or the protagonist chooses a different course. Do not stretch scenes merely to trigger a complication. For a 60-second recap, write: *intention / result / one changed fact / who knows / next choice*.

## Pressure is a review trigger—not a success meter

When meaningful time passes, `pressure_review(...)` identifies overdue **visible** threads. The optional referee view also shows hidden threads and pending faction attempts. Nothing advances automatically from that list.

**Review a pressure in three questions:** Does the responsible actor know enough to attempt something? Does it have the means and time? What has actually been resolved or observed? If any answer is negative, pressure remains unresolved or the actor changes plan; the countdown never grants victory by itself.

For geographically different experiences, reuse the same decision pipeline but alter **what gets framed**:

- **Social or urban:** immediate objective, who has authority, what each party knows, public evidence, available leverage; invoke host social rules when contested.
- **Travel or wilderness:** declared route, observable terrain, resources, elapsed days, discovered hazards; invoke host travel mechanics. Existing roads and weather matter more than a fresh description roll.
- **Site or danger:** access points, material obstacles, location controller, guaranteed core clues, optional rewards, plausible escape routes. Do not lock a required clue behind one failed roll.

This is inspired by the *scope separation* of specialist solo systems, not a reproduction of any of their procedures.

---

# 17. Originality and comparative research

The following is an **analysis of external solo systems**, not source text adopted into the rules. Distinguishing the sources' actual features from our design response matters: Causal Thread is not a variant of their charts or moves.

| Investigated source | Verified design emphasis | Our independently authored response | Deliberate rejection |
|---|---|---|---|
| *Mythic GME 2e*, publisher description | Contextual yes/no answers; character/thread lists; scene structure; random events; changing Chaos Factor | Stable question keys, visible threads, consistent scene expectations | No escalating universal chaos meter or imported Fate Chart |
| *Ironsworn* / *Starforged*, public rules/SRD | Promises, bonds, travel and progress-oriented challenge resolution | Evidence-based goals, directional relationships, resumable objectives | No copied progress moves, rank tracks or momentum economy |
| *UNE*, publicly available overview | NPC motivation, conversation focus and mood as distinct aids | Enduring objective + directional stance + immediate intent + information boundary | No imported NPC or conversation tables |
| *Scarlet Heroes*, publisher overview | Standalone or overlay play; dedicated solo adventure material; single-hero support | Distinguish social, wilderness and site framing without changing host mechanics | No imported combat scaling or encounter tables |
| *One Page Solo Engine*, publisher description | Very few rules and fast operation; supported digital play tools | Five-line session recap, no mandatory scene roll, read-only summaries | No rolling a new table for every descriptive detail |
| *Motif Oracle*, public toolkit SRD | Distinguishes oracle answer, impact, and other narrative color | Keep the d12 answer distinct from a subsequently committed effect | No copied three-die resolution scheme |
| *CRGE*, public summaries | Unexpected developments and rising pressure | Reviews tied to established deadlines, threats and faction capabilities | No automatic event surge for each question |

**Public primary-source references:**

- Word Mill Games, *Mythic Game Master Emulator Second Edition*: https://www.wordmillgames.com/page/mythic-gme.html
- Shawn Tomkin's *Ironsworn* public rules (community SRD mirror): https://tedtschopp.github.io/Ironsworn-SRD/Ironsworn%20SRD.html
- *Ironsworn: Starforged* public connection reference: https://rsek.github.io/starforged-srd/moves/connection
- *Universal NPC Emulator*, publicly accessible overview: https://www.christianfoggjohnson.com/docs/DM%20Tips/UNE_The_Universal_NPC_Emulator_%28rev%29.pdf
- Sine Nomine Publishing, *Scarlet Heroes* product overview: https://sine-nomine-publishing.myshopify.com/products/scarlet-heroes
- Inflatable Studios, *One Page Solo Engine*: https://inflatablestudios.itch.io/one-page-solo-engine
- Thought Punks, *Motif Toolkit SRD*: https://keeper.farirpgs.com/resources/thought-police/motif-toolkit-srd/core-oracles/
- Christian Fogg Johnson hosting, *CRGE* public PDF: https://www.christianfoggjohnson.com/docs/DM%20Tips/CRGE_Conjectural_Roleplaying_GM_Emulator.pdf

**Publication boundary:** Causal Thread's v0.2 mechanics, tables, prose and code are independently written. The comparative sources are credited, but none of their protected tables or prose are reproduced here. No claim is made that shared abstract ideas such as oracles, faction actions, or goal tracking can be owned. The earlier PUM/SUM-derived manuals remain separate and carry their own applicable rights.

---

# 18. Worked multi-session use: the Gate of Ash

*This is original illustrative fiction and is not a Broken Empires canon location.*

**Setup:** The PC wants the original river charter. An established fact says a carved lock has been replaced; a separate rumor blames the reeve. The reeve wants safety and can send a runner but cannot arbitrarily rewrite the charter. Two locations exist: the Gatehouse and the Archive. `start_journal(...)` captures this as a checkpoint.

**Session A — investigate the gate:** The PC learns of the replaced lock. A single transaction logs the observation and opens thread `TH1: Who replaced the lock?` at the Gatehouse, with an upcoming review on Day 3. The player's scene view contains this thread, but not a separate secret intelligence thread known only to the reeve.

**Session B — an informed offscreen attempt:** On Day 2, the reeve attempts to send a runner with available personnel. The attempt is pending until travel and access are adjudicated; the final result is only *partial*. A change of attitude toward the PC is logged separately as a justified consequence, not bestowed by an NPC oracle. Neither party has recovered the charter.

**Session C — evidence, not premature victory:** On Day 3, the PC discovers a credible inventory entry showing where the original charter is kept. The PC learns that fact and marks a *goal milestone*. The goal is still active because the charter is not yet recovered or verified. The thread's deadline merely calls for review. No faction gets to move directly from **attempt** to **triumph** because time has passed.

The supplied `Gate_of_Ash_3_Session_Example.json` demonstrates the complete committed record; its checkpoint and five post-checkpoint events can be independently replayed. The player-facing session recap omits hidden actions and gives a clear next choice.

---

# 19. A complete play loop and quick reference

**At the beginning of a session:** Read only the protagonist-facing recap. Choose one active goal, reachable site, and plausible immediate action. Keep a referee-only view of hidden faction intentions if desired, but do not make the protagonist omniscient.

**For each significant decision:**

1. **Intent:** What does the PC or NPC want here, and what outcome would count?
2. **Reality:** What is already established? What does this actor actually know and possess?
3. **Authority:** Certain consequence, host rules/native action test, or one contextual question oracle. Choose only one.
4. **Interpretation:** What precisely changed? What remained uncertain? Who could observe it?
5. **Commit:** Record one transaction containing all and only justified effects. An oracle answer alone does not create a fact.
6. **Next choice:** Provide a route back to player agency—often two credible choices with different costs.

**At a meaningful time break:** Check the current day and due threads. Review at most three active relevant factions. Record attempted offscreen actions, resolve contested ones using the host rules, and make observability explicit.

**At the end:** Validate, replay, and save. The short recap is `goal / latest visible change / relevant pressure / next two choices`.

## Tabletop card: questions to ask before touching dice

| Ask first | If yes | Otherwise |
|---|---|---|
| Is it already true or impossible under the facts? | Narrate, no roll | Check a game rule |
| Is a risky character action being attempted? | Use one native or host mechanic | Consider a fiction oracle |
| Is a meaningful, undecided fact at stake? | Record premises, odds and one answer | Use a detail prompt only if helpful |
| Did the outcome alter the world? | Commit grounded effects and witnesses | Leave the situation unchanged |
| Has real time advanced? | Review feasible faction attempts and deadlines | Continue play without a world turn |

## Historical verification gates for v0.2

The implementation includes 77 unit tests, including 43 carried from v0.1. New tests cover atomic rollback, replay, stale writes, duplicate events, journal integrity, premise-keyed oracle consistency, declared time windows, NPC relationship directionality, player-facing secrecy, factual leads, deadline review, concealed-actor visibility, TBE double recording without duplicate generated events, and a three-session scenario.

**Still not established:** player enjoyment, balance of pacing, performance on very large journals, automatic interpretation of natural-language evidence, complete TBE combat/travel/magic implementations, anti-cheat security, or copyright/trademark clearance. The TBE adapter still delegates those mechanics to the licensed rulebook. The current target for human playtesting is **three full sessions with under one minute of necessary bookkeeping per scene**, followed by a longer campaign that stresses conflicting knowledge and factions.




*An uncertain world; a traceable cause for every lasting change.*


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
