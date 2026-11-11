#!/usr/bin/env python3
"""Causal Thread v0.3 compatible core — original solo RPG reference prototype.

This is a narrow, deterministic reference implementation of state management,
oracle routing, actor options, and faction action safeguards. It is NOT a TBE
rules implementation and does not include third-party oracle tables.
"""
from __future__ import annotations
import argparse
import copy
import json
import random
from pathlib import Path

ODDS = {"remote": 2, "unlikely": 4, "even": 6, "likely": 8, "near_certain": 10}
RANKS = {"proposal", "rumor", "established", "refuted"}


# The only authorization router: the same question cannot be rolled by several engines.
AUTHORITY = {
    "native": {
        "risky_action": "opposed_d10", "yes_no": "d12_context_oracle",
        "scene_start": "one_context_question_if_uncertain",
        "description": "original_prompt_optional",
        "social": "opposed_d10", "travel": "opposed_d10",
        "magic": "opposed_d10_with_fictional_permission",
        "goal_advancement": "native_evidenced_milestone"},
    "tbe": {
        "risky_action": "tbe_core_skill_or_conflict",
        "yes_no": "tbe_ask_the_weave",
        "scene_start": "tbe_subverted_expectations_if_uncertain",
        "description": "original_prompt_optional",
        "social": "tbe_intrigue", "travel": "tbe_journey_or_hexmarch",
        "magic": "tbe_weave_or_divine",
        "goal_advancement": "tbe_goal_xp"}}


def route(state, question_type, established=False):
    """A source-of-truth decision router, not a game-rules substitute."""
    if question_type not in AUTHORITY[state["mode"]]:
        raise ValueError("question_type not recognized")
    if established and question_type != "description":
        return {"authority": "established_world", "roll": False,
                "reason": "The answer is already determined by committed facts"}
    return {"authority": AUTHORITY[state["mode"]][question_type],
            "roll": question_type != "description",
            "reason": "One and only one authority for this question"}

def campaign(name="Untitled", mode="native"):
    if mode not in ("native", "tbe"):
        raise ValueError("mode must be native or tbe")
    return {"engine": "Causal Thread", "version": "0.2", "name": name, "mode": mode,
            "day": 1, "scene": 0, "facts": {}, "actors": {}, "goals": {},
            "sites": {}, "threads": {}, "scenes": [], "events": [], "questions": [],
            "attempts": [], "decisions": []}


def _unique(state, category, identifier):
    if identifier in state[category]:
        raise ValueError(f"duplicate {category} identifier: {identifier}")


def actor(state, identifier, aim, means, limits=None, known=None, believed=None, risk_tolerance=1):
    _unique(state, "actors", identifier)
    if not 0 <= risk_tolerance <= 3:
        raise ValueError("risk_tolerance must be 0..3")
    a = {"id": identifier, "aim": aim, "means": list(means),
         "limits": list(limits or []), "known": list(known or []),
         "believed": list(believed or []), "risk_tolerance": risk_tolerance}
    if any(x not in state["facts"] or state["facts"][x]["status"] != "established" for x in a["known"]):
        raise ValueError("actor cannot know facts that are not established")
    if any(x not in state["facts"] for x in a["believed"]):
        raise ValueError("actor cannot believe an absent record")
    state["actors"][identifier] = a
    return a


def fact(state, identifier, claim, status, provenance, day=None):
    _unique(state, "facts", identifier)
    if status not in RANKS:
        raise ValueError("invalid truth status")
    if not provenance:
        raise ValueError("every fact record needs provenance")
    f = {"id": identifier, "claim": claim, "status": status, "provenance": provenance,
         "day": state["day"] if day is None else day}
    state["facts"][identifier] = f
    return f


def learn(state, actor_id, fact_id, mode="know"):
    a = state["actors"][actor_id]
    f = state["facts"][fact_id]
    if mode == "know":
        if f["status"] != "established":
            raise ValueError("cannot promote a proposal or rumor into knowledge")
        target = a["known"]
    elif mode == "believe":
        target = a["believed"]
    else:
        raise ValueError("mode must be know or believe")
    if fact_id not in target:
        target.append(fact_id)
    return a


def goal(state, identifier, owner_id, target, evidence_of_completion):
    _unique(state, "goals", identifier)
    if owner_id not in state["actors"]:
        raise ValueError("unknown goal owner")
    g = {"id": identifier, "owner": owner_id, "target": target,
         "proof": evidence_of_completion, "status": "active", "milestones": []}
    state["goals"][identifier] = g
    return g



def place(state, identifier, name, authority=None, connected=None, affordances=None, leads=None):
    """Register a reachable location, connected to actual actors and places."""
    _unique(state, "sites", identifier)
    if authority is not None and authority not in state["actors"]:
        raise ValueError("place authority must name a registered actor")
    for neighbor in connected or []:
        if neighbor not in state["sites"]:
            raise ValueError("cannot connect to nonexistent site")
    record = {"id": identifier, "name": name, "authority": authority,
              "connected": list(connected or []), "affordances": list(affordances or []),
              "leads": list(leads or [])}
    state["sites"][identifier] = record
    return record


def enter_scene(state, site_id, intent, participants, expectation):
    if site_id not in state["sites"]:
        raise ValueError("scene has no registered place")
    if not set(participants).issubset(set(state["actors"])):
        raise ValueError("scene has an unregistered participant")
    state["scene"] += 1
    record = {"scene": state["scene"], "day": state["day"], "site": site_id,
              "intent": intent, "participants": list(participants),
              "expected": expectation, "changes": []}
    state["scenes"].append(record)
    return record


def milestone(state, goal_id, evidence_ids, description):
    """Record evidence for progress; never grant game-system XP automatically."""
    g = state["goals"][goal_id]
    if g["status"] != "active":
        raise ValueError("cannot advance inactive goal")
    if not description or not evidence_ids:
        raise ValueError("milestone requires a description and evidence")
    if any(fid not in state["facts"] or state["facts"][fid]["status"] != "established"
           for fid in evidence_ids):
        raise ValueError("milestone evidence must be established")
    if any(m["description"] == description for m in g["milestones"]):
        raise ValueError("duplicate milestone")
    item = {"day": state["day"], "description": description,
            "evidence": list(evidence_ids)}
    g["milestones"].append(item)
    return item


def complete_goal(state, goal_id, evidence_ids, authority):
    g = state["goals"][goal_id]
    if g["status"] != "active" or not authority or not evidence_ids:
        raise ValueError("goal completion requires active goal, authority and evidence")
    if any(fid not in state["facts"] or state["facts"][fid]["status"] != "established"
           for fid in evidence_ids):
        raise ValueError("goal completion evidence not established")
    g["status"] = "completed"
    g["completion"] = {"day": state["day"], "evidence": list(evidence_ids),
                       "authority": authority}
    return g

def oracle(state, question, odds="even", roll=None, rng=None):
    """Original d12 context oracle. Use outside of TBE adapter mode only."""
    if state["mode"] != "native":
        raise ValueError("TBE adapter: consult the official Ask the Weave procedure instead")
    if odds not in ODDS:
        raise ValueError("unknown odds")
    if any(q["question"].strip().casefold() == question.strip().casefold() and q["committed"]
           for q in state["questions"]):
        raise ValueError("a committed question may not be rerolled without changed premises")
    roll = (rng or random).randint(1, 12) if roll is None else roll
    if not 1 <= roll <= 12:
        raise ValueError("d12 roll must be 1..12")
    answer = roll <= ODDS[odds]
    record = {"question": question, "odds": odds, "roll": roll,
              "answer": "yes" if answer else "no",
              "emphasis": "exceptional" if roll in (1, 12) else "ordinary",
              "committed": False, "day": state["day"]}
    state["questions"].append(record)
    return record


def commit_question(state, index=-1):
    """Mark interpreted and committed; does not assert a new fact on its own."""
    state["questions"][index]["committed"] = True
    return state["questions"][index]


def native_test(effort, friction, capability=0, obstacle=0):
    """Original opposed tens: d10+skill against d10+resistance."""
    if not (1 <= effort <= 10 and 1 <= friction <= 10):
        raise ValueError("effort and friction are d10 (1..10)")
    if not (0 <= capability <= 4 and 0 <= obstacle <= 4):
        raise ValueError("capability and obstacle must be 0..4")
    delta = (effort + capability) - (friction + obstacle)
    if delta >= 3:
        tier = "clean_gain"
    elif delta >= 0:
        tier = "gain_with_cost"
    elif delta >= -3:
        tier = "setback_with_opening"
    else:
        tier = "hard_setback"
    return {"effort": effort, "friction": friction, "capability": capability,
            "obstacle": obstacle, "delta": delta, "tier": tier,
            "applies_world_changes": False}


def decide_actor(state, actor_id, options):
    """Pick feasible action by transparent bounded intent scoring.

    options: {name, means: [], needs: [], impact: 0..3, duty: 0..2,
              risk: 0..3, cost: 0..3, alignment: 0..2}
    """
    a = state["actors"][actor_id]
    visible = set(a["known"] + a["believed"])
    feasible = []
    for option in options:
        if not set(option.get("means", [])).issubset(set(a["means"])):
            continue
        if not set(option.get("needs", [])).issubset(visible):
            continue
        if option.get("risk", 0) > a["risk_tolerance"]:
            continue
        if option["name"] in a["limits"]:
            continue
        for field, upper in (("impact", 3), ("duty", 2), ("risk", 3), ("cost", 3), ("alignment", 2)):
            if not 0 <= option.get(field, 0) <= upper:
                raise ValueError(f"{field} outside allowed range")
        score = (2 * option.get("impact", 0) + option.get("duty", 0)
                 + option.get("alignment", 0) - option.get("risk", 0)
                 - option.get("cost", 0))
        feasible.append((score, option))
    if not feasible:
        result = {"actor_id": actor_id, "chosen": None, "reason": "no feasible known action"}
    else:
        # A tie is resolved conservatively by lower cost then lexicographic name.
        feasible.sort(key=lambda pair: (-pair[0], pair[1].get("cost", 0), pair[1]["name"]))
        score, chosen = feasible[0]
        result = {"actor_id": actor_id, "chosen": chosen["name"], "score": score,
                  "candidates": len(feasible), "reason": "feasibility + goal alignment"}
    state["decisions"].append({"day": state["day"], **result})
    return result


def propose_attempt(state, actor_id, window, action, means, needs=None, result=None):
    """Schedule at most one attempt for a faction per time-window; never auto-victory."""
    if actor_id not in state["actors"]:
        raise ValueError("unknown actor")
    if any(x["actor"] == actor_id and x["window"] == window for x in state["attempts"]):
        raise ValueError("duplicate actor world-turn in same window")
    a = state["actors"][actor_id]
    if not set(means).issubset(set(a["means"])):
        raise ValueError("actor lacks the resources to try this")
    if not set(needs or []).issubset(set(a["known"] + a["believed"])):
        raise ValueError("actor lacks information to try this")
    entry = {"actor": actor_id, "window": window, "action": action,
             "means": list(means), "needs": list(needs or []),
             "status": "pending", "outcome": None, "authority": None,
             "day": state["day"]}
    state["attempts"].append(entry)
    return entry


def settle_attempt(state, index, outcome, authority):
    entry = state["attempts"][index]
    if entry["status"] != "pending":
        raise ValueError("already adjudicated")
    if outcome not in ("succeeded", "failed", "partial", "blocked") or not authority:
        raise ValueError("requires an outcome and adjudication authority")
    entry.update(status="resolved", outcome=outcome, authority=authority)
    return entry


def event(state, identifier, action, effects, source, evidence=None):
    if any(e["id"] == identifier for e in state["events"]):
        raise ValueError("duplicate event ID")
    if not source or not effects:
        raise ValueError("events need source and effect")
    item = {"id": identifier, "day": state["day"], "action": action,
            "effects": list(effects), "source": source, "evidence": list(evidence or [])}
    state["events"].append(item)
    return item


def validate(state):
    if state["mode"] not in ("native", "tbe"):
        raise ValueError("invalid mode")
    facts = state["facts"]
    for a in state["actors"].values():
        for f in a["known"]:
            if f not in facts or facts[f]["status"] != "established":
                raise ValueError("actor knows unsupported truth")
        for f in a["believed"]:
            if f not in facts:
                raise ValueError("actor believes unknown record")
    for owner, a in state['actors'].items():
        if a.get('site') is not None and a['site'] not in state['sites']:
            raise ValueError('actor location missing from site registry')
        if not set(a.get('concealed_from', [])).issubset(state['actors']):
            raise ValueError('concealment refers to unknown observer')
        for other, value in a.get('relations', {}).items():
            if other not in state['actors'] or other == owner or type(value) is not int or not -2 <= value <= 2:
                raise ValueError('invalid directional relationship')
    for thread in state['threads'].values():
        if thread.get('site') is not None and thread['site'] not in state['sites']:
            raise ValueError('thread site not registered')
        if not set(thread.get('visible_to', [])).issubset(state['actors']):
            raise ValueError('thread visible to unknown actor')
        if thread.get('status') not in ('open', 'closed'):
            raise ValueError('invalid thread status')
    for g in state["goals"].values():
        if g["owner"] not in state["actors"]:
            raise ValueError("unknown goal owner")
        if g.get("status") == "completed" and not g.get("completion", {}).get("authority"):
            raise ValueError("completed goal without adjudication")
    for site in state["sites"].values():
        if site["authority"] is not None and site["authority"] not in state["actors"]:
            raise ValueError("site governed by nonexistent actor")
        if not set(site["connected"]).issubset(state["sites"]):
            raise ValueError("site links to nonexistent place")
    for scene in state["scenes"]:
        if scene["site"] not in state["sites"] or not set(scene["participants"]).issubset(state["actors"]):
            raise ValueError("scene references missing entities")
    pairs = [(a["actor"], a["window"]) for a in state["attempts"]]
    if len(pairs) != len(set(pairs)):
        raise ValueError("duplicate world-turn")
    for a in state["attempts"]:
        if a["actor"] not in state["actors"]:
            raise ValueError("unknown attempt actor")
        owner = state["actors"][a["actor"]]
        if not set(a["means"]).issubset(owner["means"]):
            raise ValueError("unearned faction resources")
        if not set(a["needs"]).issubset(owner["known"] + owner["believed"]):
            raise ValueError("unearned faction knowledge")
        if a["status"] == "resolved" and (not a["outcome"] or not a["authority"]):
            raise ValueError("settled action without authority")
        if a["status"] == "pending" and (a["outcome"] or a["authority"]):
            raise ValueError("pending action has outcome")
    # v0.3: structured facts keep historical truth while allowing one current value.
    current_keys = {}
    for identifier, record in facts.items():
        key = record.get('state_key')
        if key is None:
            continue
        if not isinstance(key, str) or not key or record.get('status') != 'established' \
           or type(record.get('value')) not in (str, int, bool):
            raise ValueError('malformed structured state assertion')
        for former in record.get('replaces', []):
            if former not in facts or former == identifier or facts[former].get('state_key') != key \
               or facts[former].get('superseded_by') != identifier:
                raise ValueError('broken state-replacement linkage')
        successor = record.get('superseded_by')
        if successor is not None and (successor not in facts or
            facts[successor].get('state_key') != key or
            identifier not in facts[successor].get('replaces', [])):
            raise ValueError('invalid successor in fact history')
        if not successor:
            if key in current_keys:
                raise ValueError('two conflicting current facts for a single state key')
            current_keys[key] = identifier
    ids = [e["id"] for e in state["events"]]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate event")
    return True


# --- v0.2: explicit, replayable consequences and context-sensitive solo tools ---
import hashlib

JOURNAL_META = {'checkpoint', 'journal', 'revision', 'journal_hash'}


def _projection(state):
    """A complete campaign state without the checkpoint/journal metadata."""
    return {k: copy.deepcopy(v) for k, v in state.items() if k not in JOURNAL_META}


def _digest(value):
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False,
                         separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def start_journal(state):
    """Freeze an explicit checkpoint. Subsequent *new* changes must use transact.

    Legacy constructors may be used to prepare a campaign before this checkpoint.
    The checkpoint is part of the save file, so it can be independently replayed.
    """
    if 'journal' in state:
        raise ValueError('this campaign already has a journal')
    validate(state)
    if state.get('version') not in ('0.1', '0.2'):
        raise ValueError('only v0.1 and v0.2 campaign records are supported')
    state['version'] = '0.2'  # migrate compatible v0.1 core state before checkpoint
    state['checkpoint'] = _projection(state)
    state['journal'] = []
    state['revision'] = 0
    state['journal_hash'] = _digest(_projection(state))
    return state['journal_hash']


def _require_evidence(state, ids):
    for identifier in ids:
        if identifier not in state['facts'] or state['facts'][identifier]['status'] != 'established':
            raise ValueError('cited evidence must be an established claim')


def _apply_operation(state, operation):
    """Apply a narrowly scoped change. All inputs must be JSON-serializable."""
    op = operation.get('op')
    if op == 'record_fact':
        fact(state, operation['id'], operation['claim'], operation['status'],
             operation['provenance'])
    elif op == 'assert_state':
        # v0.3: mutually exclusive *current* property, with explicit historical replacement.
        identifier, key, value = operation['id'], operation['state_key'], operation['value']
        if not isinstance(key, str) or not key.strip() or type(value) not in (str, int, bool):
            raise ValueError('assert_state requires a named property and a scalar value')
        current = [f for f in state['facts'].values()
                   if f.get('state_key') == key and f['status'] == 'established'
                   and not f.get('superseded_by')]
        replace = list(operation.get('replaces', []))
        if len(replace) != len(set(replace)) or {f['id'] for f in current} != set(replace):
            raise ValueError('state assertion must replace exactly the current prior claim(s)')
        if any(f['value'] == value for f in current):
            raise ValueError('redundant state assertion: no change')
        entry = fact(state, identifier, operation['claim'], 'established',
                     operation['provenance'])
        entry.update(state_key=key, value=value, replaces=replace)
        for previous in current:
            previous['superseded_by'] = identifier
    elif op == 'learn_fact':
        learn(state, operation['actor'], operation['fact'], operation.get('mode', 'know'))
    elif op == 'grant_mean':
        if operation['actor'] not in state['actors']:
            raise ValueError('resource recipient does not exist')
        a = state['actors'][operation['actor']]
        resource = operation['resource']
        if not resource or resource in a['means']:
            raise ValueError('grant requires a new, named resource')
        a['means'].append(resource)
    elif op == 'move_actor':
        if operation['actor'] not in state['actors']:
            raise ValueError('moving actor does not exist')
        if operation['site'] not in state['sites']:
            raise ValueError('destination is not a registered site')
        concealed = list(operation.get('concealed_from', []))
        if not set(concealed).issubset(state['actors']):
            raise ValueError('concealment must name registered observers')
        state['actors'][operation['actor']]['site'] = operation['site']
        state['actors'][operation['actor']]['concealed_from'] = concealed
    elif op == 'set_relation':
        if operation['actor'] not in state['actors']:
            raise ValueError('relationship owner does not exist')
        a = state['actors'][operation['actor']]
        target = operation['target']
        if target not in state['actors'] or target == operation['actor']:
            raise ValueError('relationship target must be another registered actor')
        stance = operation['stance']
        if type(stance) is not int or not -2 <= stance <= 2:
            raise ValueError('stance must be an integer from -2 to 2')
        a.setdefault('relations', {})[target] = stance
    elif op == 'mark_goal':
        milestone(state, operation['goal'], operation['evidence'], operation['description'])
    elif op == 'complete_goal':
        complete_goal(state, operation['goal'], operation['evidence'], operation['authority'])
    elif op == 'upgrade_v03':
        if state.get('version') != '0.2':
            raise ValueError('upgrade requires a v0.2 campaign')
        state['version'] = '0.3'
    elif op == 'advance_time':
        days = operation['days']
        if type(days) is not int or not 1 <= days <= 3650:
            raise ValueError('advance_time requires 1..3650 days')
        state['day'] += days
    elif op == 'link_site':
        a, b = operation['site'], operation['other']
        if a not in state['sites'] or b not in state['sites'] or a == b:
            raise ValueError('both distinct sites must exist')
        for left, right in ((a, b), (b, a)):
            if right not in state['sites'][left]['connected']:
                state['sites'][left]['connected'].append(right)
    elif op == 'open_thread':
        identifier = operation['id']
        _unique(state, 'threads', identifier)
        site = operation.get('site')
        if site is not None and site not in state['sites']:
            raise ValueError('thread site does not exist')
        known_to = list(operation.get('visible_to', []))
        if not set(known_to).issubset(state['actors']):
            raise ValueError('thread visibility must reference real actors')
        if not operation.get('question'):
            raise ValueError('thread requires an unresolved question')
        deadline = operation.get('deadline_day')
        if deadline is not None and (type(deadline) is not int or deadline < state['day']):
            raise ValueError('thread deadline must not precede its opening')
        state['threads'][identifier] = {'id': identifier,
                                         'question': operation['question'], 'site': site,
                                         'visible_to': known_to, 'status': 'open',
                                         'deadline_day': deadline, 'opened_day': state['day']}
    elif op == 'close_thread':
        t = state['threads'][operation['thread']]
        if t['status'] != 'open':
            raise ValueError('thread already closed')
        _require_evidence(state, operation['evidence'])
        t['status'] = 'closed'
        t['closed_day'] = state['day']
        t['evidence'] = list(operation['evidence'])
    elif op == 'record_attempt':
        propose_attempt(state, operation['actor'], operation['window'], operation['action'],
                        operation['means'], operation.get('needs', []))
    elif op == 'settle_attempt':
        settle_attempt(state, operation['index'], operation['outcome'], operation['authority'])
    elif op == 'record_host_question':
        if state['mode'] != 'tbe':
            raise ValueError('host oracle recording is only for TBE mode')
        q = operation['record']
        if any(old.get('key') == q['key'] and old.get('premise_signature') == q['premise_signature']
               for old in state['questions']):
            raise ValueError('official question already recorded under the same premises')
        previous = [old for old in state['questions'] if old.get('key') == q['key']]
        if previous and not q.get('change_reason'):
            raise ValueError('repeating a host question needs an explained material change')
        state['questions'].append(copy.deepcopy(q))
    elif op == 'record_question':
        if state['mode'] != 'native':
            raise ValueError('the TBE adapter owns yes/no question resolution')
        q = operation['record']
        if any(old.get('key') == q['key'] and old.get('premise_signature') == q['premise_signature']
               for old in state['questions']):
            raise ValueError('same question and premises already answered')
        previous = [old for old in state['questions'] if old.get('key') == q['key']]
        if previous and (not q.get('change_reason') or any(
            old.get('premise_signature') == q['premise_signature'] for old in previous)):
            raise ValueError('reroll requires genuinely changed, explained premises')
        state['questions'].append(copy.deepcopy(q))
    else:
        raise ValueError(f'unknown or unsupported state operation: {op}')


def transact(state, identifier, description, source, operations, evidence=None,
             visible_to=None, expected_revision=None):
    """Atomic, replayable campaign change. An interpretive result alone changes nothing.

    A failing operation rolls back the entire transaction. Every committed change
    receives a source, original event ID, revision and before/after content hashes.
    """
    if 'journal' not in state:
        raise ValueError('call start_journal before committing a change')
    if state['journal'] and (state['journal'][-1]['after_hash'] != state['journal_hash']
                              or state['journal'][-1]['revision'] != state['revision']):
        raise ValueError('journal head does not match live state')
    if expected_revision is not None and expected_revision != state['revision']:
        raise ValueError('stale revision: reload before committing')
    if _digest(_projection(state)) != state['journal_hash']:
        raise ValueError('state changed outside the journal')
    if not identifier or not description or not source or not operations:
        raise ValueError('commit requires ID, description, authority and effects')
    if any(e['id'] == identifier for e in state['events']):
        raise ValueError('event ID already used')
    evidence = list(evidence or [])
    visible_to = list(visible_to or [])
    if not set(visible_to).issubset(state['actors']):
        raise ValueError('invalid visibility actor')
    _require_evidence(state, evidence)
    before = state['journal_hash']
    candidate = copy.deepcopy(state)
    for op in operations:
        _apply_operation(candidate, op)
    item = {'id': identifier, 'day': candidate['day'], 'action': description,
            'effects': [op['op'] for op in operations], 'source': source,
            'evidence': evidence}
    candidate['events'].append(item)
    validate(candidate)
    after = _digest(_projection(candidate))
    receipt = {'id': identifier, 'description': description, 'source': source,
               'operations': copy.deepcopy(operations), 'evidence': evidence,
               'visible_to': visible_to, 'revision': state['revision'] + 1,
               'day': candidate['day'], 'before_hash': before, 'after_hash': after}
    candidate['journal'].append(receipt)
    candidate['revision'] += 1
    candidate['journal_hash'] = after
    state.clear()
    state.update(candidate)
    return copy.deepcopy(receipt)


def replay_journal(state):
    """Reconstruct post-checkpoint state solely from stored effects, in strict order."""
    if 'checkpoint' not in state or 'journal' not in state:
        raise ValueError('no checkpoint and journal')
    rebuilt = copy.deepcopy(state['checkpoint'])
    start_journal(rebuilt)
    for recorded in state['journal']:
        fresh = transact(rebuilt, recorded['id'], recorded['description'],
                         recorded['source'], recorded['operations'], recorded['evidence'],
                         recorded['visible_to'], expected_revision=rebuilt['revision'])
        if fresh != recorded:
            raise ValueError('journal tampering or non-deterministic operation')
    if _projection(rebuilt) != _projection(state) or rebuilt['journal_hash'] != state['journal_hash']:
        raise ValueError('live state disagrees with committed journal')
    return rebuilt


def audit_campaign(state):
    """Validate both the world invariants and the complete journal hash chain."""
    validate(state)
    if 'journal' in state:
        replay_journal(state)
    return True


def context_oracle(state, event_id, key, question, odds='even', premise_ids=None,
                   reason='', roll=None, window='fixed', change_reason='', visible_to=None,
                   actor_ids=None, site_ids=None):
    """Commit one binary answer in native mode; never infer fictional consequences.

    The caller states the material premises, odds and explanation. A new answer to
    the same question is permitted only after an explicit *different* premise
    signature plus a written explanation. The procedure cannot judge semantic
    relevance; human/host review is still required.
    """
    if state['mode'] != 'native':
        raise ValueError('TBE mode uses the host Ask the Weave procedure')
    if odds not in ODDS or not key.strip() or not question.strip() or not reason.strip():
        raise ValueError('oracle requires a question key, odds and contextual rationale')
    ids = sorted(set(premise_ids or []))
    for identifier in ids:
        if identifier not in state['facts']:
            raise ValueError('unregistered premise')
    premises = {i: {'status': state['facts'][i]['status'],
                    'claim': state['facts'][i]['claim']} for i in ids}
    if window != 'fixed' and window != f'day:{state["day"]}':
        raise ValueError('window must be fixed or the actual current campaign day')
    actors = {}
    for identifier in sorted(set(actor_ids or [])):
        if identifier not in state['actors']:
            raise ValueError('unregistered actor premise')
        a = state['actors'][identifier]
        actors[identifier] = {k: copy.deepcopy(a.get(k)) for k in
                              ('aim', 'means', 'limits', 'known', 'believed', 'site', 'relations', 'concealed_from')}
    sites = {}
    for identifier in sorted(set(site_ids or [])):
        if identifier not in state['sites']:
            raise ValueError('unregistered site premise')
        site = state['sites'][identifier]
        sites[identifier] = copy.deepcopy(site)
    signature = _digest({'premises': premises, 'actors': actors,
                         'sites': sites, 'window': window})
    rolled = random.randint(1, 12) if roll is None else roll
    if type(rolled) is not int or not 1 <= rolled <= 12:
        raise ValueError('d12 result must be 1..12')
    entry = {'key': key, 'question': question, 'odds': odds, 'roll': rolled,
             'answer': 'yes' if rolled <= ODDS[odds] else 'no',
             'emphasis': 'exceptional' if rolled in (1, 12) else 'ordinary',
             'premises': ids, 'actors': sorted(actors), 'sites': sorted(sites),
             'premise_signature': signature, 'window': window,
             'reason': reason, 'change_reason': change_reason,
             'committed': True, 'day': state['day']}
    transact(state, event_id, f'Oracle: {question}', 'native d12 oracle',
             [{'op': 'record_question', 'record': entry}], visible_to=visible_to)
    return copy.deepcopy(entry)


def record_tbe_question(state, event_id, key, question, odds, roll, answer,
                        premise_ids=None, change_reason='', visible_to=None):
    """Record (never calculate) one official TBE Ask the Weave result.

    The official table and any ensuing Random Event must be handled with the
    user's own rulebook. A doubles flag is a reminder, not a second event.
    """
    if state['mode'] != 'tbe':
        raise ValueError('use context_oracle for native-mode uncertainty')
    if odds not in ('Certain', 'Likely', '50/50', 'Unlikely', 'Impossible'):
        raise ValueError('unknown official TBE odds category')
    if answer not in ('Extreme Yes', 'Yes', 'No', 'Extreme No'):
        raise ValueError('record the four-category official answer')
    if type(roll) is not int or not 1 <= roll <= 100 or not key or not question:
        raise ValueError('official roll must be d100 represented as 1..100 (00=100)')
    ids = sorted(set(premise_ids or []))
    for identifier in ids:
        if identifier not in state['facts']:
            raise ValueError('official result cites unknown premise')
    sig = _digest({'premises': {i: {'claim': state['facts'][i]['claim'],
                                    'status': state['facts'][i]['status']} for i in ids}})
    doubles = roll == 100 or roll % 11 == 0
    record = {'key': key, 'question': question, 'odds': odds, 'roll': roll,
              'answer': answer, 'premises': ids, 'premise_signature': sig,
              'change_reason': change_reason, 'committed': True,
              'random_event_pending': doubles, 'authority': 'TBE Ask the Weave',
              'day': state['day']}
    transact(state, event_id, f'Official oracle: {question}',
             'TBE Ask the Weave (player supplied official result)',
             [{'op': 'record_host_question', 'record': record}], visible_to=visible_to)
    return copy.deepcopy(record)


def scene_brief(state, site_id, protagonist_id):
    """Read-only, spoiler-bounded scene preparation; no surprise roll by default."""
    if site_id not in state['sites'] or protagonist_id not in state['actors']:
        raise ValueError('unknown site or protagonist')
    p = state['actors'][protagonist_id]
    site = state['sites'][site_id]
    visible = set(p['known'] + p['believed'])
    leads = [x for x in site['leads'] if x in visible]
    threads = [t for t in state['threads'].values()
               if t.get('status') == 'open' and t.get('site') == site_id
               and protagonist_id in t.get('visible_to', [])]
    others = [a['id'] for a in state['actors'].values()
              if a.get('site') == site_id and a['id'] != protagonist_id
              and protagonist_id not in a.get('concealed_from', [])]
    return {'site': site['name'], 'site_id': site_id,
            'affordances': list(site['affordances']), 'known_leads': leads,
            'visible_threads': [t['id'] for t in threads], 'present_actors': sorted(others),
            'scene_guidance': ('An active local thread may interfere if its actor has a feasible cause.'
                               if threads else 'Follow the expected scene unless new facts justify an interruption.')}


def pressure_review(state, protagonist_id='PC', referee=False):
    """Read-only review of deadlines and real pending attempts, not a victory clock.

    Hidden entries remain hidden in a player-facing review. Review is meaningful
    when campaign time advances or the protagonist enters a relevant location.
    """
    if protagonist_id not in state['actors']:
        raise ValueError('unknown protagonist')
    relevant = [t for t in state['threads'].values()
                if t.get('status') == 'open'
                and (referee or protagonist_id in t.get('visible_to', []))]
    due = [t for t in relevant if t.get('deadline_day') is not None
           and t['deadline_day'] <= state['day']]
    return {'day': state['day'], 'due_threads': sorted([t['id'] for t in due]),
            'open_threads': sorted([t['id'] for t in relevant]),
            'pending_attempts': ([{'actor': a['actor'], 'window': a['window']}
                                  for a in state['attempts'] if a['status'] == 'pending']
                                 if referee else []),
            'resolution': 'A due deadline is a call to examine evidence and feasible actions, not a success trigger.'}


def npc_conversation_frame(state, npc_id, other_id, topic_ids=None):
    """Referee-side prompt: knowledge, beliefs, relationship and current objective.

    It does not decide whether persuasion works; the host mechanics retain that.
    """
    if npc_id == other_id or npc_id not in state['actors'] or other_id not in state['actors']:
        raise ValueError('unknown conversational actors')
    npc = state['actors'][npc_id]
    topic = set(topic_ids or [])
    if not topic.issubset(state['facts']):
        raise ValueError('conversation references an absent fact')
    known = [i for i in npc['known'] if not topic or i in topic]
    believed = [i for i in npc['believed'] if not topic or i in topic]
    stance = npc.get('relations', {}).get(other_id, 0)
    return {'speaker': npc_id, 'listener': other_id, 'objective': npc['aim'],
            'known_claim_ids': known, 'believed_claim_ids': believed,
            'stance': stance,
            'guidance': ('Cooperation is plausible, subject to stakes and limits.' if stance > 0
                         else 'Resistance is plausible, subject to stakes and limits.' if stance < 0
                         else 'Use the NPC objective and current evidence; attitude is undecided.'),
            'resolution': route(state, 'social')['authority']}


def session_brief(state, protagonist_id='PC', limit=4):
    """A player-facing recap, never disclosing referee-only faction attempts."""
    if protagonist_id not in state['actors'] or limit < 1:
        raise ValueError('unknown protagonist or invalid limit')
    p = state['actors'][protagonist_id]
    return {'campaign': state['name'], 'day': state['day'],
            'active_goals': [g['target'] for g in state['goals'].values()
                             if g['owner'] == protagonist_id and g['status'] == 'active'],
            'known_claims': [state['facts'][i]['claim'] for i in p['known']],
            'suspected_claims': [state['facts'][i]['claim'] for i in p['believed']],
            'open_threads': [t['question'] for t in state['threads'].values()
                             if t.get('status') == 'open' and protagonist_id in t.get('visible_to', [])],
            'recent_events': [j['description'] for j in state.get('journal', [])
                              if protagonist_id in j.get('visible_to', [])][-limit:],
            'next_action_prompt': 'Choose one goal-directed action; ask the oracle only for a material unknown.'}



def demo():
    s = campaign("The Glass Canal", "native")
    fact(s, "F-1", "The canal marker was moved recently", "established", "surveyed stone scrape")
    fact(s, "F-2", "The mill council deliberately poisoned the wells", "rumor", "dockside gossip")
    actor(s, "PC", "Learn why village water is disappearing", ["search embankment", "interview locals"], risk_tolerance=2)
    actor(s, "KEEPER", "Prevent another flood", ["open records", "warn villagers"], risk_tolerance=1)
    actor(s, "COUNCIL", "Protect canal toll revenue", ["send messenger", "hire surveyor"], risk_tolerance=1)
    learn(s, "PC", "F-1")
    learn(s, "PC", "F-2", "believe")
    learn(s, "KEEPER", "F-1")
    goal(s, "G-1", "PC", "Determine whether the canal diversion caused the village shortage", "inspect survey marks and inspect toll sluice")
    place(s, "SITE-MILL", "Miller's Lock", "COUNCIL", affordances=["sluice gate", "public inspection path"], leads=["F-1"])
    place(s, "SITE-ARCHIVE", "Village Records", "KEEPER", connected=["SITE-MILL"], affordances=["public index", "sealed original"])
    enter_scene(s, "SITE-MILL", "Inspect moved canal marker", ["PC"], "The inspection path is clear")
    milestone(s, "G-1", ["F-1"], "Found proof survey stone was moved")
    s["day"] = 2
    decision = decide_actor(s, "KEEPER", [
        {"name": "open records", "means": ["open records"], "needs": ["F-1"], "impact": 2, "alignment": 2, "cost": 1, "risk": 0},
        {"name": "confiscate mill charter", "means": ["seize charters"], "needs": ["F-1"], "impact": 3, "risk": 2}])
    s["day"] = 3
    attempt = propose_attempt(s, "COUNCIL", "days-2-3", "send messenger to obtain upstream survey", ["send messenger"])
    q = oracle(s, "Did the messenger reach the upstream surveyor?", "likely", roll=7)
    commit_question(s)
    settle_attempt(s, 0, "succeeded", "Native context oracle; likelihood recorded, d12=7")
    event(s, "E-1", "Council messenger reaches surveyor", ["Council now has an appointment, not a charter or legal victory"], "Q-1 d12=7")
    validate(s)
    return s, decision, attempt, q


def main():
    p = argparse.ArgumentParser(description="Causal Thread v0.2 offline reference runner")
    p.add_argument("command", choices=["demo", "oracle", "native-test", "new", "validate"])
    p.add_argument("--odds", default="even", choices=list(ODDS))
    p.add_argument("--roll", type=int)
    p.add_argument("--effort", type=int, default=5)
    p.add_argument("--friction", type=int, default=5)
    p.add_argument("--capability", type=int, default=0)
    p.add_argument("--obstacle", type=int, default=0)
    p.add_argument("--file")
    p.add_argument("--name", default="New campaign")
    p.add_argument("--mode", choices=["native", "tbe"], default="native")
    args = p.parse_args()
    if args.command == "demo":
        result = demo()[0]
    elif args.command == "oracle":
        result = oracle(campaign(), "Illustrative uncertainty", args.odds, args.roll)
    elif args.command == "native-test":
        result = native_test(args.effort, args.friction, args.capability, args.obstacle)
    elif args.command == "new":
        result = campaign(args.name, args.mode)
    elif args.command == "validate":
        if not args.file:
            p.error("--file required for validate")
        result = {"valid": validate(json.loads(Path(args.file).read_text()))}
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
