"""Causal Thread v0.4: read-only, evidence-scoped advice exchange.

This module does not call an LLM, authenticate reviewers, prove narrative
entailment, or commit game state. A separate model may use the returned packet,
but its claims remain proposals for human review.
"""
from __future__ import annotations

import copy

from causal_thread import _digest
from interpretation import review_interpretation, viewer_preview

VERDICTS = {'plausible', 'uncertain', 'contradicted'}


def prepare_advisory(state: dict, proposal: dict, viewer_id: str | None = None) -> dict:
    """Return a frozen-context evidence packet limited to its intended audience.

    Passing viewer_id=None opens a trusted referee interface. A player-facing
    caller must pass the viewer's ID; never expose referee packets to players.
    """
    if viewer_id is None:
        review = review_interpretation(state, proposal)
        support = list(proposal.get('support_ids', []))
        beliefs = list(proposal.get('belief_ids', []))
        # Only explicitly cited evidence is sent; no broad, hidden-world dump.
        facts = {fid: copy.deepcopy(state['facts'][fid])
                 for fid in support + beliefs if fid in state['facts']}
        packet = {
            'available': True,
            'audience': 'referee',
            'revision': state.get('revision'),
            'proposal_hash': review.get('proposal_hash', _digest(proposal)),
            'summary': proposal.get('summary', ''),
            'interpretation': proposal.get('interpretation', ''),
            'operations': copy.deepcopy(proposal.get('operations', [])),
            'origin': copy.deepcopy(proposal.get('origin', {})),
            'support_ids': support,
            'belief_ids': beliefs,
            'facts': facts,
            'review': copy.deepcopy(review),
        }
    else:
        # The v0.3 visibility boundary remains authoritative.
        visible = viewer_preview(state, proposal, viewer_id)
        if not visible.get('available'):
            return {'available': False}
        ids = visible['known_support_ids']
        facts = {fid: {'id': fid, 'claim': state['facts'][fid]['claim']}
                 for fid in ids if fid in state['facts']
                 and state['facts'][fid]['status'] == 'established'}
        packet = {
            'available': True,
            'audience': 'player',
            'revision': state.get('revision'),
            'proposal_hash': _digest(proposal),
            'summary': visible['summary'],
            'support_ids': list(facts),
            'facts': facts,
            'state_changes_committed': visible['state_changes_committed'],
        }
    packet['context_digest'] = _digest(packet)
    return packet


def check_advice(state: dict, proposal: dict, advice: dict,
                 viewer_id: str | None = None) -> dict:
    """Validate untrusted model advice; never accept it as a game ruling.

    Advice requires context_digest, verdict, explanation, and support_ids.
    Optional assumptions and alternatives are suggestions, never world facts.
    """
    packet = prepare_advisory(state, proposal, viewer_id)
    if not packet.get('available'):
        return {'usable': False, 'issues': ['proposal_inaccessible']}
    issues = []
    if not isinstance(advice, dict):
        return {'usable': False, 'issues': ['malformed_advice']}
    if advice.get('context_digest') != packet['context_digest']:
        issues.append('stale_or_wrong_context')
    if advice.get('verdict') not in VERDICTS:
        issues.append('invalid_verdict')
    if not isinstance(advice.get('explanation'), str) or not advice['explanation'].strip():
        issues.append('missing_explanation')
    cited = advice.get('support_ids')
    if not isinstance(cited, list) or any(not isinstance(x, str) for x in cited):
        issues.append('invalid_citations')
        cited = []
    elif len(cited) != len(set(cited)):
        issues.append('duplicate_citations')
    if not set(cited).issubset(packet['facts']):
        issues.append('out_of_scope_citations')
    if advice.get('verdict') == 'plausible' and not cited:
        issues.append('plausibility_without_citation')
    for key in ('assumptions', 'alternatives'):
        val = advice.get(key, [])
        if not isinstance(val, list) or any(not isinstance(x, str) or not x.strip() for x in val):
            issues.append('invalid_' + key)
    if packet['audience'] == 'referee' and not packet['review']['ready']:
        issues.append('proposal_has_rule_blockers')
    # An assistant's citations can be checked for membership, not entailment.
    return {
        'usable': not issues,
        'issues': issues,
        'advisory_only': True,
        'semantic_entailment_verified': False,
        'reviewer_approval_required': True,
        'context_digest': packet['context_digest'],
    }
