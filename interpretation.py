"""Causal Thread v0.3: controlled interpretation before an atomic state commit.

Only explicit, structured constraints are machine-checked. Natural-language
plausibility and whether evidence entails a conclusion remain human decisions.
This module has no persistence layer and delegates final writes to v0.2's
replayable transaction journal.
"""
from __future__ import annotations

import copy
from typing import Any
from causal_thread import (
    _digest, _projection, native_test, transact, audit_campaign,
)

ORIGIN_KINDS = {'observation', 'native_oracle', 'tbe_oracle',
                'native_test', 'tbe_rule', 'referee'}


def _problem(code: str, detail: str) -> dict:
    return {'code': code, 'detail': detail}


def draft_interpretation(state: dict, identifier: str, summary: str,
                         interpretation: str, origin: dict, operations: list,
                         *, support_ids=None, belief_ids=None, actor_id=None,
                         visible_to=None, public_summary='', open_questions=None) -> dict:
    """Make a draft, not a campaign update. All values should be JSON-safe."""
    if 'journal' not in state:
        raise ValueError('start_journal is required before proposing an interpretation')
    if not identifier or not summary.strip() or not interpretation.strip():
        raise ValueError('proposal requires ID, brief title and explicit interpretation')
    return {
        'id': identifier, 'summary': summary, 'interpretation': interpretation,
        'origin': copy.deepcopy(origin), 'operations': copy.deepcopy(operations),
        'support_ids': list(support_ids or []),
        'belief_ids': list(belief_ids or []),
        'actor_id': actor_id, 'visible_to': list(visible_to or []),
        'public_summary': public_summary,
        'open_questions': list(open_questions or []),
        'base_revision': state['revision'], 'base_hash': state['journal_hash'],
    }


def _receipt(state, event_id: str):
    return next((e for e in state['journal'] if e['id'] == event_id), None)


def review_interpretation(state: dict, proposal: dict) -> dict:
    """Review structure and recorded premises; never infer natural-language entailment."""
    blockers, warnings = [], []
    def block(code, detail): blockers.append(_problem(code, detail))
    def warn(code, detail): warnings.append(_problem(code, detail))

    if 'journal' not in state:
        block('not_journaled', 'Campaign needs a journal before interpretations can be committed.')
        return {'ready': False, 'blockers': blockers, 'warnings': warnings}
    if state.get('revision') != proposal.get('base_revision') or state.get('journal_hash') != proposal.get('base_hash'):
        block('stale_context', 'World has changed since the proposal was written; create a new draft.')
    if _digest(_projection(state)) != state['journal_hash']:
        block('uncommitted_state', 'A campaign record has been altered outside its journal.')
    if not proposal.get('id') or not proposal.get('summary') or not proposal.get('interpretation'):
        block('missing_narrative', 'Proposal needs an ID, summary and interpretation.')
    if not isinstance(proposal.get('operations'), list) or not proposal['operations']:
        block('no_effects', 'An interpretation needs specific state operations.')
    if _receipt(state, proposal.get('id')) is not None:
        block('duplicate_id', 'This event identifier is already in the journal.')

    origin = proposal.get('origin', {})
    kind = origin.get('kind') if isinstance(origin, dict) else None
    if kind not in ORIGIN_KINDS:
        block('unknown_origin', 'Provide an authoritative origin category.')
    else:
        if kind.startswith('native_') and state['mode'] != 'native':
            block('wrong_rules_mode', 'Native resolution cannot authorize a TBE-mode outcome.')
        if kind.startswith('tbe_') and state['mode'] != 'tbe':
            block('wrong_rules_mode', 'TBE resolution cannot authorize a native-mode outcome.')
        if kind in ('native_oracle', 'tbe_oracle'):
            ref = origin.get('event')
            receipt = _receipt(state, ref)
            tag = 'record_question' if kind == 'native_oracle' else 'record_host_question'
            records = [op['record'] for op in receipt['operations'] if op.get('op') == tag] if receipt else []
            if len(records) != 1:
                block('missing_oracle_receipt', 'Oracle origin must cite a committed matching question event.')
            elif origin.get('answer') != records[0].get('answer'):
                block('oracle_answer_mismatch', 'Declared answer does not match the committed oracle result.')
            if kind == 'tbe_oracle' and records and records[0].get('random_event_pending'):
                warn('tbe_random_event', 'TBE doubles require the official Random Event process; do not silently resolve it here.')
        elif kind == 'native_test':
            try:
                expected = native_test(**origin['rolls'])['tier']
                if origin.get('tier') != expected:
                    block('native_outcome_mismatch', 'Native test tier does not match the recorded dice and modifiers.')
            except (KeyError, TypeError, ValueError):
                block('native_test_invalid', 'Provide valid native test rolls and the resulting tier.')
        elif kind == 'tbe_rule':
            if not all(isinstance(origin.get(k), str) and origin[k].strip()
                       for k in ('procedure', 'result', 'citation')):
                block('missing_host_receipt', 'Record the official procedure, outcome and rulebook reference.')
            warn('host_not_executed', 'TBE results are recorded, not calculated or verified by this software.')
        elif kind == 'observation':
            if not origin.get('witness') or not origin.get('basis'):
                block('observation_unattributed', 'An observation needs a witness and the observed basis.')
        elif kind == 'referee':
            if not origin.get('reason'):
                block('referee_unexplained', 'The referee must explain a discretionary ruling.')

    support = proposal.get('support_ids', [])
    belief = proposal.get('belief_ids', [])
    for ids, label in ((support, 'support'), (belief, 'belief')):
        if len(ids) != len(set(ids)):
            block('duplicate_reference', f'Duplicate {label} references.')
        for fid in ids:
            f = state['facts'].get(fid)
            if f is None:
                block('absent_reference', f'Unknown {label} record {fid}.')
            elif label == 'support' and f['status'] != 'established':
                block('unproven_evidence', f'{fid} is not an established claim.')
            elif label == 'support' and f.get('superseded_by'):
                warn('historical_evidence', f'{fid} was superseded; it may be history, not current state.')
    if set(support) & set(belief):
        block('confused_evidence', 'Do not list the same claim as both proof and mere belief.')

    actor_id = proposal.get('actor_id')
    if actor_id is not None:
        a = state['actors'].get(actor_id)
        if a is None:
            block('unknown_actor', 'The acting NPC must exist.')
        else:
            for fid in support:
                if fid not in a['known']:
                    block('actor_omniscience', f'{actor_id} cannot cite {fid}: not in their known facts.')
            for fid in belief:
                if fid not in a['believed']:
                    block('invented_belief', f'{actor_id} has no recorded belief in {fid}.')
    if belief:
        warn('belief_not_proof', 'An NPC belief justifies intent, never the truth of the believed claim.')

    viewers = proposal.get('visible_to', [])
    if len(viewers) != len(set(viewers)) or not set(viewers).issubset(state['actors']):
        block('invalid_visibility', 'Viewer permissions must be unique registered actors.')
    if viewers and not proposal.get('public_summary', '').strip():
        block('no_public_text', 'A visible event needs a separately authored player-facing summary.')
    if viewers:
        warn('disclosure_review', 'Human review must confirm the public summary reveals no hidden information.')
    if not support and kind in ('observation', 'referee'):
        warn('uncorroborated', 'No established records are cited; verify the narrated consequence manually.')

    # Stage a fully journaled transaction on a *copy*, so the same low-level
    # guards protect review and commit. This is deterministic and side-effect-free.
    if not blockers:
        try:
            candidate = copy.deepcopy(state)
            transact(candidate, proposal['id'], proposal['summary'],
                     f'CT v0.3 interpretation: {kind}', proposal['operations'],
                     evidence=support, visible_to=viewers,
                     expected_revision=proposal['base_revision'])
            audit_campaign(candidate)
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            block('invalid_transaction', str(exc))
    if not any(w['code'] == 'semantic_review' for w in warnings):
        warn('semantic_review', 'A human/host must check causal plausibility, evidence entailment and rule fit.')
    return {'ready': not blockers, 'blockers': blockers, 'warnings': warnings,
            'proposal_hash': _digest(proposal), 'at_revision': state['revision']}


def approve_interpretation(state: dict, proposal: dict, reviewer: str,
                           decision_note: str, acknowledged_warning_codes: list) -> dict:
    """Explicit approval receipt tied to a specific draft and campaign head."""
    review = review_interpretation(state, proposal)
    if not review['ready']:
        raise ValueError('proposal has blockers: ' + ', '.join(x['code'] for x in review['blockers']))
    if not reviewer.strip() or not decision_note.strip():
        raise ValueError('approval needs a named reviewer and an explicit interpretation rationale')
    codes = {x['code'] for x in review['warnings']}
    if set(acknowledged_warning_codes) != codes:
        raise ValueError('reviewer must acknowledge each current review warning exactly')
    return {'proposal_hash': review['proposal_hash'], 'base_revision': state['revision'],
            'base_hash': state['journal_hash'], 'reviewer': reviewer,
            'decision_note': decision_note, 'acknowledged_warning_codes': sorted(codes)}


def commit_interpretation(state: dict, proposal: dict, approval: dict) -> dict:
    """Commit through the existing atomic journal; a preview never changes state."""
    review = review_interpretation(state, proposal)
    if not review['ready']:
        raise ValueError('interpretation is blocked or based on stale state')
    if not (approval.get('proposal_hash') == review['proposal_hash'] and
            approval.get('base_revision') == state['revision'] and
            approval.get('base_hash') == state['journal_hash'] and
            approval.get('reviewer') and approval.get('decision_note') and
            set(approval.get('acknowledged_warning_codes', [])) ==
            {w['code'] for w in review['warnings']}):
        raise ValueError('approval does not attest to this exact reviewed proposal')
    # Store the human approval alongside the normal event receipt; this is an
    # audit note, not a cryptographic authentication or automated truth proof.
    receipt = transact(state, proposal['id'], proposal['summary'],
                       (f"CT v0.3 {proposal['origin']['kind']} / approved by {approval['reviewer']} "
                        f"/ draft_sha256={approval['proposal_hash']} "
                        f"/ warnings={','.join(sorted(approval['acknowledged_warning_codes']))} "
                        f"/ rationale={approval['decision_note']}"), proposal['operations'],
                       evidence=proposal['support_ids'], visible_to=proposal['visible_to'],
                       expected_revision=approval['base_revision'])
    return receipt


def viewer_preview(state: dict, proposal: dict, viewer_id: str) -> dict:
    """Spoiler-bounded proposal view, never returns hidden operations/interpretation."""
    if viewer_id not in state['actors']:
        raise ValueError('unknown viewer')
    if viewer_id not in proposal.get('visible_to', []):
        return {'available': False}
    known = set(state['actors'][viewer_id]['known'])
    return {'available': True, 'summary': proposal['public_summary'],
            'known_support_ids': [i for i in proposal.get('support_ids', []) if i in known],
            'state_changes_committed': _receipt(state, proposal['id']) is not None}


def upgrade_to_v03(state: dict, event_id='MIGRATE-V03') -> dict:
    """Journal an upgrade rather than silently rewriting checkpoint history."""
    audit_campaign(state)
    if state['version'] != '0.2':
        raise ValueError('upgrade expects a checkpointed v0.2 save')
    return transact(state, event_id, 'Enable v0.3 interpretation layer',
                    'engine migration', [{'op': 'upgrade_v03'}],
                    expected_revision=state['revision'])
