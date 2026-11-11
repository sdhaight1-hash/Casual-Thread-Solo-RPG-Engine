# Causal Thread — Solo RPG Engine

An independently authored, consequence-driven solo roleplaying framework.

**Project status:** experimental reference implementation. Not a fully autonomous GM.

## Core principles
- One authoritative, journaled campaign state.
- Fact, belief, actor knowledge, and player-visible information remain distinct.
- Oracles resolve uncertainty once per recorded context.
- NPCs and factions act within actual knowledge, time, and means.
- Narrative interpretations are proposed, reviewed, and approved before an atomic commit.
- A host RPG such as *The Broken Empires* retains authority over its own action-resolution rules.

## Layout
- `causal_thread.py` — journaled world-state core and replay safeguards.
- `interpretation.py` — v0.3 proposal / validation / approval / commit protocol.
- `evidence_assistant.py` — v0.4 evidence-constrained advisory analysis (development branch).
- `tests/` — regression and scenario tests.
- `docs/` — design notes and planned workflows.

## Run tests
```bash
python -m unittest discover -s tests -v
```

No external Python dependencies are required for the reference engine.

## Release and licensing
The system is original work. Third-party systems and rulebooks are comparative references only. There is **no license grant yet**; all rights remain reserved until a license is deliberately selected. Do not copy third-party commercial or Creative Commons rulebooks into this repository.

**Repository URL spelling:** `Casual-Thread-Solo-RPG-Engine` is the existing GitHub repository name; **Causal Thread** is the project name.
