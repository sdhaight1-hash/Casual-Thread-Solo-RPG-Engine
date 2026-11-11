"""Behavioral tests: v0.4 advice is scoped, revision-bound, and read-only."""
import copy
import unittest

from causal_thread import actor, campaign, fact, start_journal, transact
from interpretation import draft_interpretation, upgrade_to_v03
from evidence_assistant import prepare_advisory, check_advice


class EvidenceAssistantTests(unittest.TestCase):
    def setUp(self):
        self.state = campaign('Gate of Ash')
        fact(self.state, 'VISIBLE', 'The gate was inspected', 'established', 'inspection')
        fact(self.state, 'SECRET', 'The reeve has a spy', 'established', 'referee')
        fact(self.state, 'RUMOR', 'The gate is cursed', 'rumor', 'gossip')
        actor(self.state, 'PC', 'Investigate gate', ['inspect'], known=['VISIBLE'])
        actor(self.state, 'REEVE', 'Keep gate', ['guards'], known=['SECRET'])
        start_journal(self.state)
        upgrade_to_v03(self.state)
        self.proposal = draft_interpretation(
            self.state, 'P1', 'A messenger arrives',
            'The courier carries a letter to the gatehouse.',
            {'kind': 'referee', 'reason': 'The road is open'},
            [{'op': 'record_attempt', 'actor': 'REEVE', 'window': 'day 1',
              'action': 'send courier', 'means': ['guards']}],
            support_ids=['VISIBLE'], visible_to=['PC'],
            public_summary='A courier approaches the gate.')

    def advice(self, packet, **edits):
        a = {'context_digest': packet['context_digest'], 'verdict': 'uncertain',
             'explanation': 'The road is known, not the letter contents.',
             'support_ids': ['VISIBLE'], 'assumptions': [], 'alternatives': []}
        a.update(edits)
        return a

    def test_referee_packet_only_contains_cited_facts(self):
        p = prepare_advisory(self.state, self.proposal)
        self.assertEqual(list(p['facts']), ['VISIBLE'])
        self.assertIn('operations', p)
        self.assertNotIn('SECRET', str(p))

    def test_no_mutation(self):
        before = copy.deepcopy(self.state)
        p = prepare_advisory(self.state, self.proposal)
        check_advice(self.state, self.proposal, self.advice(p))
        self.assertEqual(self.state, before)

    def test_player_packet_redacts_private_interpretation(self):
        p = prepare_advisory(self.state, self.proposal, 'PC')
        self.assertEqual(p['audience'], 'player')
        self.assertNotIn('operations', p)
        self.assertNotIn('interpretation', p)
        self.assertNotIn('review', p)
        self.assertNotIn('SECRET', str(p))
        self.assertNotIn('provenance', str(p))
        self.assertIn('A courier approaches', p['summary'])

    def test_inaccessible_viewer_gets_nothing(self):
        self.assertEqual(prepare_advisory(self.state, self.proposal, 'REEVE'),
                         {'available': False})
        self.assertEqual(check_advice(self.state, self.proposal, {}, 'REEVE'),
                         {'usable': False, 'issues': ['proposal_inaccessible']})

    def test_valid_advice_never_becomes_ruling(self):
        p = prepare_advisory(self.state, self.proposal)
        result = check_advice(self.state, self.proposal, self.advice(p))
        self.assertTrue(result['usable'])
        self.assertTrue(result['advisory_only'])
        self.assertFalse(result['semantic_entailment_verified'])
        self.assertTrue(result['reviewer_approval_required'])
        self.assertEqual(len(self.state['attempts']), 0)

    def test_foreign_citations_rejected(self):
        p = prepare_advisory(self.state, self.proposal)
        for citations in (['SECRET'], ['NOT-A-FACT']):
            with self.subTest(citations=citations):
                r = check_advice(self.state, self.proposal,
                                 self.advice(p, support_ids=citations))
                self.assertIn('out_of_scope_citations', r['issues'])

    def test_uncited_plausible_not_accepted(self):
        p = prepare_advisory(self.state, self.proposal)
        r = check_advice(self.state, self.proposal,
                         self.advice(p, verdict='plausible', support_ids=[]))
        self.assertIn('plausibility_without_citation', r['issues'])

    def test_stale_digest_rejected_after_world_update(self):
        p = prepare_advisory(self.state, self.proposal)
        response = self.advice(p)
        transact(self.state, 'TIME', 'Time passes', 'time',
                 [{'op': 'advance_time', 'days': 1}])
        r = check_advice(self.state, self.proposal, response)
        self.assertIn('stale_or_wrong_context', r['issues'])

    def test_player_cannot_cite_hidden_fact(self):
        p = prepare_advisory(self.state, self.proposal, 'PC')
        r = check_advice(self.state, self.proposal,
                         self.advice(p, support_ids=['SECRET']), 'PC')
        self.assertIn('out_of_scope_citations', r['issues'])

    def test_invalid_advice_shapes_rejected(self):
        p = prepare_advisory(self.state, self.proposal)
        for val in (None, [], 'yes'):
            self.assertIn('malformed_advice',
                          check_advice(self.state, self.proposal, val)['issues'])
        r = check_advice(self.state, self.proposal,
                         self.advice(p, alternatives=['', 9]))
        self.assertIn('invalid_alternatives', r['issues'])


if __name__ == '__main__':
    unittest.main()
