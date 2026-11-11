"""v0.3 adversarial acceptance tests for proposal, review, approval and commit."""
import copy
import unittest

from causal_thread import (campaign, actor, fact, place, start_journal,
                           transact, context_oracle, record_tbe_question,
                           audit_campaign, replay_journal)
from interpretation import (draft_interpretation, review_interpretation,
                            approve_interpretation, commit_interpretation,
                            viewer_preview, upgrade_to_v03)


def codes(review, severity):
    return {item['code'] for item in review[severity]}


class InterpretationTests(unittest.TestCase):
    def setUp(self):
        self.s = campaign('Gate of Ash')
        fact(self.s, 'F-LOCK', 'The gate lock is new', 'established', 'inspection')
        fact(self.s, 'F-RUMOR', 'The reeve stole the old seal', 'rumor', 'market talk')
        actor(self.s, 'PC', 'Find the original seal', ['inspect', 'ask'], known=['F-LOCK'])
        actor(self.s, 'REEVE', 'Protect the gate', ['messenger', 'guards'])
        place(self.s, 'GATE', 'River Gate')
        start_journal(self.s)
        upgrade_to_v03(self.s)

    def draft(self, event_id='D1', **kwargs):
        d = dict(identifier=event_id, summary='Reeve sends a guard',
                 interpretation='The reeve dispatches one of their available guards.',
                 origin={'kind':'referee', 'reason':'A routine patrol is plausible'},
                 operations=[{'op':'record_attempt', 'actor':'REEVE', 'window':'day1',
                              'action':'patrol gate', 'means':['guards']}],
                 support_ids=[], visible_to=[])
        d.update(kwargs)
        return draft_interpretation(self.s, **d)

    def accept(self, proposal, reviewer='Solo player'):
        r = review_interpretation(self.s, proposal)
        self.assertTrue(r['ready'], r['blockers'])
        approval = approve_interpretation(self.s, proposal, reviewer,
                                          'Fits the known circumstances',
                                          [w['code'] for w in r['warnings']])
        return commit_interpretation(self.s, proposal, approval)

    def test_no_mutation_until_commit(self):
        before = copy.deepcopy(self.s)
        proposal = self.draft()
        review = review_interpretation(self.s, proposal)
        self.assertTrue(review['ready'])
        self.assertEqual(self.s, before)
        receipt = self.accept(proposal)
        self.assertEqual(receipt['revision'], 2)
        self.assertEqual(len(self.s['attempts']), 1)
        self.assertEqual(replay_journal(self.s)['journal_hash'], self.s['journal_hash'])

    def test_unapproved_attempt_never_happens(self):
        proposal = self.draft()
        with self.assertRaises(ValueError):
            commit_interpretation(self.s, proposal, {})
        self.assertEqual(self.s['attempts'], [])

    def test_acknowledge_all_warnings(self):
        p = self.draft()
        with self.assertRaises(ValueError):
            approve_interpretation(self.s, p, 'Player', 'Accepted', [])

    def test_approval_is_draft_bound(self):
        p = self.draft()
        r = review_interpretation(self.s, p)
        approval = approve_interpretation(self.s, p, 'Player', 'Fits', [x['code'] for x in r['warnings']])
        altered = copy.deepcopy(p)
        altered['interpretation'] = 'An entirely different interpretation'
        with self.assertRaises(ValueError):
            commit_interpretation(self.s, altered, approval)

    def test_stale_context_rejected(self):
        p = self.draft()
        transact(self.s, 'OTHER', 'Time passes', 'play', [{'op':'advance_time', 'days':1}])
        self.assertIn('stale_context', codes(review_interpretation(self.s,p),'blockers'))

    def test_hidden_preview_never_reveals_draft(self):
        p = self.draft(interpretation='A secret raid is planned', summary='Private raid plan')
        self.assertEqual(viewer_preview(self.s,p,'PC'), {'available':False})
        self.assertEqual(self.s['attempts'], [])

    def test_player_visible_summary_is_separate(self):
        p = self.draft(visible_to=['PC'], public_summary='A guard appears by the gate.',
                       support_ids=['F-LOCK'])
        self.assertEqual(viewer_preview(self.s,p,'PC')['known_support_ids'],['F-LOCK'])
        self.assertNotIn('operations', viewer_preview(self.s,p,'PC'))
        self.assertNotIn('interpretation', viewer_preview(self.s,p,'PC'))
        self.assertIn('disclosure_review', codes(review_interpretation(self.s,p),'warnings'))

    def test_public_text_is_required_if_visible(self):
        p = self.draft(visible_to=['PC'])
        self.assertIn('no_public_text', codes(review_interpretation(self.s,p),'blockers'))

    def test_unknown_visitor_rejected(self):
        p = self.draft(visible_to=['ghost'], public_summary='Hello')
        self.assertIn('invalid_visibility', codes(review_interpretation(self.s,p),'blockers'))

    def test_omniscience_blocked(self):
        p = self.draft(actor_id='REEVE', support_ids=['F-LOCK'])
        self.assertIn('actor_omniscience', codes(review_interpretation(self.s,p),'blockers'))

    def test_actor_belief_only_can_justify_intention(self):
        transact(self.s,'R1','Heard rumor','witness',
                 [{'op':'learn_fact','actor':'REEVE','fact':'F-RUMOR','mode':'believe'}])
        p = self.draft(actor_id='REEVE', belief_ids=['F-RUMOR'])
        r = review_interpretation(self.s,p)
        self.assertTrue(r['ready'])
        self.assertIn('belief_not_proof', codes(r,'warnings'))

    def test_rumor_does_not_count_as_evidence(self):
        p = self.draft(support_ids=['F-RUMOR'])
        self.assertIn('unproven_evidence', codes(review_interpretation(self.s,p),'blockers'))

    def test_actor_cannot_invent_belief(self):
        p = self.draft(actor_id='REEVE', belief_ids=['F-RUMOR'])
        self.assertIn('invented_belief', codes(review_interpretation(self.s,p),'blockers'))

    def test_missing_oracle_event_blocked(self):
        p = self.draft(origin={'kind':'native_oracle','event':'MISSING','answer':'yes'})
        self.assertIn('missing_oracle_receipt', codes(review_interpretation(self.s,p),'blockers'))

    def test_oracle_no_is_not_yes(self):
        context_oracle(self.s,'O1','courier','Did the courier arrive?','even', ['F-LOCK'],
                       'The road is uncertain',roll=11)
        p = self.draft(origin={'kind':'native_oracle','event':'O1','answer':'yes'})
        self.assertIn('oracle_answer_mismatch', codes(review_interpretation(self.s,p),'blockers'))

    def test_matching_oracle_can_be_proposed_but_not_autocommitted(self):
        context_oracle(self.s,'O1','courier','Did the courier arrive?','even',[],
                       'A coin flip is fair',roll=4)
        p = self.draft(origin={'kind':'native_oracle','event':'O1','answer':'yes'})
        self.assertTrue(review_interpretation(self.s,p)['ready'])
        self.assertEqual(len(self.s['attempts']),0)

    def test_wrong_rules_mode_blocked(self):
        p = self.draft(origin={'kind':'tbe_rule','procedure':'TBE Intrigue', 'result':'success',
                               'citation':'TBE ch. 10'})
        self.assertIn('wrong_rules_mode', codes(review_interpretation(self.s,p),'blockers'))

    def test_native_test_tier_calculated(self):
        p = self.draft(origin={'kind':'native_test',
                  'rolls':{'effort':9,'friction':2,'capability':1,'obstacle':1},
                  'tier':'hard_setback'})
        self.assertIn('native_outcome_mismatch', codes(review_interpretation(self.s,p),'blockers'))

    def test_native_test_valid(self):
        p = self.draft(origin={'kind':'native_test',
                  'rolls':{'effort':9,'friction':2,'capability':1,'obstacle':1},
                  'tier':'clean_gain'})
        self.assertTrue(review_interpretation(self.s,p)['ready'])

    def test_structured_current_fact(self):
        p = self.draft(origin={'kind':'observation','witness':'PC','basis':'inspected the post'},
             operations=[{'op':'assert_state','id':'CTRL-1', 'state_key':'GATE:controller',
                           'value':'REEVE','claim':'The reeve currently controls the gate',
                           'provenance':'inspection', 'replaces':[]}])
        self.accept(p)
        self.assertEqual(self.s['facts']['CTRL-1']['value'],'REEVE')
        self.assertTrue(audit_campaign(self.s))

    def test_conflicting_current_state_requires_replacement(self):
        self.accept(self.draft('D1', operations=[{'op':'assert_state','id':'CTRL-1',
            'state_key':'GATE:controller','value':'REEVE',
            'claim':'Reeve holds the gate','provenance':'inspection','replaces':[]}]))
        p = self.draft('D2',operations=[{'op':'assert_state','id':'CTRL-2',
            'state_key':'GATE:controller','value':'COUNCIL',
            'claim':'Council holds gate','provenance':'inspection','replaces':[]}])
        self.assertIn('invalid_transaction',codes(review_interpretation(self.s,p),'blockers'))

    def test_explicit_state_replacement_preserves_history(self):
        self.accept(self.draft('D1', operations=[{'op':'assert_state','id':'CTRL-1',
            'state_key':'GATE:controller','value':'REEVE',
            'claim':'Reeve holds the gate','provenance':'inspection','replaces':[]}]))
        self.accept(self.draft('D2', operations=[{'op':'assert_state','id':'CTRL-2',
            'state_key':'GATE:controller','value':'COUNCIL',
            'claim':'Council holds the gate now','provenance':'witnessed transfer',
            'replaces':['CTRL-1']}],support_ids=['CTRL-1']))
        self.assertEqual(self.s['facts']['CTRL-1']['superseded_by'],'CTRL-2')
        self.assertEqual(self.s['facts']['CTRL-2']['replaces'],['CTRL-1'])
        self.assertTrue(audit_campaign(self.s))

    def test_redundant_state_change_blocked(self):
        self.accept(self.draft('D1', operations=[{'op':'assert_state','id':'CTRL-1',
            'state_key':'GATE:controller','value':'REEVE',
            'claim':'Reeve holds gate','provenance':'inspection','replaces':[]}]))
        p = self.draft('D2', operations=[{'op':'assert_state','id':'CTRL-2',
            'state_key':'GATE:controller','value':'REEVE',
            'claim':'Reeve still holds gate','provenance':'inspection','replaces':['CTRL-1']}])
        self.assertIn('invalid_transaction',codes(review_interpretation(self.s,p),'blockers'))

    def test_invalid_operation_staged_and_rolled_back(self):
        before = copy.deepcopy(self.s)
        p = self.draft(operations=[{'op':'grant_mean','actor':'GHOST','resource':'gate'}])
        self.assertIn('invalid_transaction',codes(review_interpretation(self.s,p),'blockers'))
        self.assertEqual(self.s,before)

    def test_approval_cannot_skip_actual_transaction_checks(self):
        p = self.draft()
        r = review_interpretation(self.s,p)
        approval = approve_interpretation(self.s,p,'Player','Reasonable', [x['code'] for x in r['warnings']])
        # User edits the proposal after approval; commits must detect it.
        p['operations'][0]['means']=['dragons']
        with self.assertRaises(ValueError):commit_interpretation(self.s,p,approval)

    def test_journal_replay_after_migration_and_interpretation(self):
        self.accept(self.draft())
        self.assertEqual(self.s['version'],'0.3')
        self.assertEqual(replay_journal(self.s)['revision'],2)

    def test_referee_cannot_supply_blank_reason(self):
        p = self.draft(origin={'kind':'referee', 'reason':''})
        self.assertIn('referee_unexplained',codes(review_interpretation(self.s,p),'blockers'))


class TBEInterpreterTests(unittest.TestCase):
    def setUp(self):
        self.s=campaign('TBE interpreter','tbe')
        actor(self.s,'PC','Recover deed',['ask'])
        actor(self.s,'WARDEN','Hold post',['guard'])
        place(self.s,'POST','Post')
        start_journal(self.s)
        upgrade_to_v03(self.s)

    def test_host_rule_requires_external_record(self):
        p=draft_interpretation(self.s,'D1','Warden moves','Warden moves',
          {'kind':'tbe_rule','procedure':'','result':'','citation':''},
          [{'op':'move_actor','actor':'WARDEN','site':'POST'}])
        self.assertIn('missing_host_receipt',codes(review_interpretation(self.s,p),'blockers'))

    def test_host_rule_remains_human_verified(self):
        p=draft_interpretation(self.s,'D1','Warden moves','Warden moves',
          {'kind':'tbe_rule','procedure':'Core skill check','result':'Success','citation':'Core rulebook, skills'},
          [{'op':'move_actor','actor':'WARDEN','site':'POST'}])
        r=review_interpretation(self.s,p)
        self.assertTrue(r['ready'])
        self.assertIn('host_not_executed',codes(r,'warnings'))

    def test_official_oracle_outcome_linked(self):
        record_tbe_question(self.s,'OR1','gate','Is the door open?', 'Likely',22,'Yes')
        p=draft_interpretation(self.s,'D1','Warden enters','The post guard enters',
          {'kind':'tbe_oracle','event':'OR1','answer':'Yes'},
          [{'op':'move_actor','actor':'WARDEN','site':'POST'}])
        r=review_interpretation(self.s,p)
        self.assertTrue(r['ready'])
        self.assertIn('tbe_random_event',codes(r,'warnings'))
        self.assertEqual(self.s['actors']['WARDEN'].get('site'),None)


if __name__ == '__main__':
    unittest.main(verbosity=2)
