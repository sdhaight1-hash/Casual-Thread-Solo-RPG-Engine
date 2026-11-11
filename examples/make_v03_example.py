"""Reproducible migration, adjudication and limited-information example."""
from pathlib import Path
import copy
import json
from causal_thread import audit_campaign, context_oracle
from interpretation import (
    draft_interpretation, review_interpretation, approve_interpretation,
    commit_interpretation, viewer_preview, upgrade_to_v03,
)
ROOT = Path(__file__).parent
state = json.loads((ROOT / 'Gate_of_Ash_3_Session_Example.json').read_text())
audit_campaign(state)
upgrade_to_v03(state)
trace = []


def decide(proposal):
    review = review_interpretation(state, proposal)
    assert review['ready'], review
    approval = approve_interpretation(state, proposal, 'Solo player',
        'Accepted after reviewing fictional circumstances and interpretation.',
        [w['code'] for w in review['warnings']])
    preview = viewer_preview(state, proposal, 'PC')
    receipt = commit_interpretation(state, proposal, approval)
    trace.append({'draft': proposal, 'review': review, 'approval': approval,
                  'player_preview_before_commit': preview, 'committed_event': receipt['id']})


context_oracle(state, 'Q-HALL', 'hall-open', 'Is the public record hall accessible today?',
               odds='likely', premise_ids=['C2'],
               reason='Public inventory exists and the village is not under lockdown',
               roll=5, visible_to=['PC'])
proposal = draft_interpretation(state, 'I-HALL',
    'The record hall is open', 'A public records clerk grants ordinary daytime access.',
    {'kind': 'native_oracle', 'event': 'Q-HALL', 'answer': 'yes'},
    [{'op': 'record_fact', 'id': 'C3', 'claim': 'The Record Hall is open to public visitors on day 3',
      'status': 'established', 'provenance': 'native oracle Q-HALL plus player interpretation'},
     {'op': 'learn_fact', 'actor': 'PC', 'fact': 'C3'}],
    support_ids=['C2'], visible_to=['PC'],
    public_summary='The public Record Hall is open today.',
    open_questions=['Will the clerk grant access to the private vault?'])
decide(proposal)

# Observe an existing, independently inspectable detail rather than invent a victory.
proposal = draft_interpretation(state, 'I-CURRENT',
    'The reeve controls the gate', 'Public guard orders name the reeve as gate authority.',
    {'kind': 'observation', 'witness': 'PC', 'basis': 'signed standing-orders plaque'},
    [{'op': 'assert_state', 'id': 'C4', 'state_key': 'GATE:controller',
      'value': 'REEVE', 'claim': 'The reeve currently controls the River Gate',
      'provenance': 'public standing-orders plaque', 'replaces': []},
     {'op': 'learn_fact', 'actor': 'PC', 'fact': 'C4'}],
    support_ids=['C1'], visible_to=['PC'],
    public_summary='A public notice names the reeve as the current gate authority.')
decide(proposal)

# A new signed order can support a change of office; it does not create victory by clock.
proposal = draft_interpretation(state, 'I-ORDER',
    'A signed order is found', 'The PC examines a transfer order signed by the reeve.',
    {'kind': 'observation', 'witness': 'PC', 'basis': 'document on the public counter'},
    [{'op': 'record_fact', 'id': 'C5', 'claim': 'The reeve signed an order transferring gate authority to the Carter',
      'status': 'established', 'provenance': 'direct inspection of dated document'},
     {'op': 'learn_fact', 'actor': 'PC', 'fact': 'C5'}],
    visible_to=['PC'], public_summary='A signed transfer order names the Carter as incoming gate authority.')
decide(proposal)

# This draft is rejected: contradictory current-holder assertion with no replacement.
invalid = draft_interpretation(state, 'I-BAD',
    'Two simultaneous controllers', 'An unsupported second current controller appears.',
    {'kind': 'referee', 'reason': 'A hypothetical invalid example'},
    [{'op': 'assert_state', 'id': 'C6-BAD', 'state_key': 'GATE:controller',
      'value': 'CARTER', 'claim': 'Carter controls the gate',
      'provenance': 'imagined', 'replaces': []}])
blocked = review_interpretation(state, invalid)
assert not blocked['ready']
trace.append({'rejected_draft': invalid, 'blocker_codes': [i['code'] for i in blocked['blockers']]})

proposal = draft_interpretation(state, 'I-TRANSFER',
    'Gate authority transferred',
    'The witnessed handover puts the Carter in charge and preserves the reeve record as history.',
    {'kind': 'observation', 'witness': 'PC', 'basis': 'posted order and witnessed key exchange'},
    [{'op': 'assert_state', 'id': 'C6', 'state_key': 'GATE:controller',
      'value': 'CARTER', 'claim': 'The Carter now controls the River Gate',
      'provenance': 'witnessed key exchange following order C5', 'replaces': ['C4']},
     {'op': 'learn_fact', 'actor': 'PC', 'fact': 'C6'}],
    support_ids=['C4', 'C5'], visible_to=['PC'],
    public_summary='The Carter receives the gate keys and assumes authority.')
decide(proposal)

assert state['facts']['C4']['superseded_by'] == 'C6'
assert state['facts']['C6']['value'] == 'CARTER'
assert audit_campaign(state)
(ROOT / 'Gate_of_Ash_v0.3_Interpreted.json').write_text(json.dumps(state, indent=2, ensure_ascii=False))
(ROOT / 'Gate_of_Ash_v0.3_Review_Trace.json').write_text(json.dumps(trace, indent=2, ensure_ascii=False))
print('v0.3 events after migration', state['revision'], '| current gate controller', state['facts']['C6']['value'])
