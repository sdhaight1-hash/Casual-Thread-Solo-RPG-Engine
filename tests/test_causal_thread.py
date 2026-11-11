"""Behavioral invariants for the independent Causal Thread prototype."""
import copy
import unittest
from causal_thread import (campaign, actor, fact, learn, goal, oracle,
                           commit_question, native_test, decide_actor, route, place, enter_scene, milestone, complete_goal,
                           propose_attempt, settle_attempt, event, validate, demo)

class Rules(unittest.TestCase):
    def setUp(self):
        self.s = campaign()
        fact(self.s, 'F1', 'A bridge collapsed', 'established', 'eyewitnesses')
        fact(self.s, 'R1', 'The mayor caused it', 'rumor', 'market gossip')
        actor(self.s, 'A', 'Restore access', ['send scout', 'negotiate'], risk_tolerance=1)
        actor(self.s, 'B', 'Protect trade', ['pay courier'], risk_tolerance=1)

    def test_clean_demo(self): self.assertTrue(validate(demo()[0]))
    def test_authority_routing_has_single_owner(self):
        self.assertEqual(route(self.s,'yes_no')['authority'],'d12_context_oracle')
        self.assertEqual(route(self.s,'social')['authority'],'opposed_d10')
    def test_known_fact_never_calls_oracle(self):
        self.assertEqual(route(self.s,'yes_no',established=True)['roll'],False)
    def test_tbe_oracle_and_conflict_not_overwritten(self):
        tbe=campaign(mode='tbe')
        self.assertEqual(route(tbe,'yes_no')['authority'],'tbe_ask_the_weave')
        self.assertEqual(route(tbe,'social')['authority'],'tbe_intrigue')
        self.assertEqual(route(tbe,'magic')['authority'],'tbe_weave_or_divine')
        self.assertEqual(route(tbe,'scene_start')['authority'],'tbe_subverted_expectations_if_uncertain')
    def test_prompts_only_add_description(self):
        self.assertEqual(route(self.s,'description')['roll'],False)
    def test_native_probability_enumeration(self):
        order = ["clean_gain", "gain_with_cost", "setback_with_opening", "hard_setback"]
        expected = {0:[28,27,24,21], 1:[36,28,21,15], -1:[21,24,27,28], 2:[45,27,18,10], -2:[15,21,28,36]}
        for edge, values in expected.items():
            capability, obstacle = max(0, edge), max(0, -edge)
            counts = {name:0 for name in order}
            for effort in range(1,11):
                for friction in range(1,11):
                    counts[native_test(effort,friction,capability,obstacle)["tier"]] += 1
            self.assertEqual([counts[k] for k in order],values)
    def test_original_prompt_data_has_six_full_d12_tables(self):
        import json
        from pathlib import Path
        data=json.loads((Path(__file__).parent/'original_tables.json').read_text())
        self.assertEqual(len(data['tables']),6)
        self.assertTrue(all(t['die']=='d12' and len(t['results'])==12 and len(set(t['results']))==12 for t in data['tables']))
    def test_cannot_know_rumor(self):
        with self.assertRaises(ValueError): learn(self.s, 'A', 'R1')
    def test_can_believe_rumor(self):
        learn(self.s, 'A', 'R1', 'believe');self.assertIn('R1', self.s['actors']['A']['believed'])
    def test_cannot_hallucinate_knowledge(self):
        with self.assertRaises(ValueError): actor(self.s, 'X', 'X', [], known=['F-nonexistent'])
    def test_known_truth_requires_provenance(self):
        with self.assertRaises(ValueError): fact(self.s, 'F2', 'A fact', 'established', '')
    def test_duplicate_fact_rejected(self):
        with self.assertRaises(ValueError): fact(self.s,'F1','different','established','source')
    def test_duplicate_actor_rejected(self):
        with self.assertRaises(ValueError): actor(self.s,'A','X',[])
    def test_oracle_thresholds_at_extremes(self):
        self.assertEqual(oracle(self.s,'q1','remote',2)['answer'],'yes')
        self.assertEqual(oracle(self.s,'q2','remote',3)['answer'],'no')
        self.assertEqual(oracle(self.s,'q3','near_certain',10)['answer'],'yes')
        self.assertEqual(oracle(self.s,'q4','near_certain',11)['answer'],'no')
    def test_exceptional_does_not_create_event(self):
        self.assertEqual(oracle(self.s,'q1','even',1)['emphasis'],'exceptional')
        self.assertEqual(oracle(self.s,'q2','even',12)['emphasis'],'exceptional')
        self.assertEqual(len(self.s['events']),0)
    def test_committed_oracle_cannot_reroll(self):
        oracle(self.s,'Does the gate open?', 'even',7)
        commit_question(self.s)
        with self.assertRaises(ValueError):oracle(self.s,'DOES THE GATE OPEN?', 'likely',2)
    def test_invalid_rolls(self):
        for n in (0,13):
            with self.assertRaises(ValueError): oracle(self.s,f'q{n}','even',n)
    def test_tbe_mode_delegates_oracle(self):
        s=campaign(mode='tbe')
        with self.assertRaises(ValueError):oracle(s,'Is the gate open?','even',5)
    def test_native_resolution_four_tiers(self):
        self.assertEqual(native_test(10,1)['tier'],'clean_gain')
        self.assertEqual(native_test(5,5)['tier'],'gain_with_cost')
        self.assertEqual(native_test(5,7)['tier'],'setback_with_opening')
        self.assertEqual(native_test(1,10)['tier'],'hard_setback')
    def test_native_never_mutates_world(self):
        before=copy.deepcopy(self.s)
        self.assertFalse(native_test(8,5)['applies_world_changes'])
        self.assertEqual(before,self.s)
    def test_actor_cannot_do_the_impossible(self):
        result=decide_actor(self.s,'A',[{'name':'seize navy','means':['navy'], 'impact':3}])
        self.assertIsNone(result['chosen'])
    def test_actor_cannot_use_unknown_information(self):
        result=decide_actor(self.s,'A',[{'name':'expose mayor','means':['negotiate'], 'needs':['R1'], 'impact':3}])
        self.assertIsNone(result['chosen'])
    def test_actor_can_react_to_belief(self):
        learn(self.s,'A','R1','believe')
        result=decide_actor(self.s,'A',[{'name':'ask about mayor','means':['negotiate'],'needs':['R1'],'impact':2}])
        self.assertEqual(result['chosen'],'ask about mayor')
    def test_actor_respects_risk(self):
        result=decide_actor(self.s,'A',[{'name':'charge fortress','means':['send scout'],'risk':3,'impact':3}])
        self.assertIsNone(result['chosen'])
    def test_actor_picks_feasible_best_option(self):
        result=decide_actor(self.s,'A',[{'name':'scout','means':['send scout'],'impact':1},
                                             {'name':'negotiate','means':['negotiate'],'impact':3,'risk':1}])
        self.assertEqual(result['chosen'],'negotiate')
    def test_actor_tie_deterministic(self):
        result=decide_actor(self.s,'A',[{'name':'b','means':[],'impact':1}, {'name':'a','means':[],'impact':1}])
        self.assertEqual(result['chosen'],'a')
    def test_no_resource_free_faction_action(self):
        with self.assertRaises(ValueError):propose_attempt(self.s,'B','day2','raise army',['army'])
    def test_faction_attempt_is_only_pending(self):
        a=propose_attempt(self.s,'B','day2','send letter',['pay courier'])
        self.assertEqual(a['status'],'pending');self.assertIsNone(a['outcome'])
    def test_no_duplicate_faction_attempt(self):
        propose_attempt(self.s,'B','day2','send letter',['pay courier'])
        with self.assertRaises(ValueError):propose_attempt(self.s,'B','day2','send another',['pay courier'])
    def test_faction_outcome_requires_authority(self):
        propose_attempt(self.s,'B','day2','send letter',['pay courier'])
        with self.assertRaises(ValueError):settle_attempt(self.s,0,'succeeded','')
    def test_settled_faction_cannot_settle_twice(self):
        propose_attempt(self.s,'B','day2','send letter',['pay courier'])
        settle_attempt(self.s,0,'failed','bridge out')
        with self.assertRaises(ValueError):settle_attempt(self.s,0,'succeeded','rewrite history')
    def test_no_duplicate_events(self):
        event(self.s,'E1','flood',['bridge blocked'],'observed')
        with self.assertRaises(ValueError):event(self.s,'E1','second',['secret'],'imagined')
    def test_goals_require_registered_owner(self):
        with self.assertRaises(ValueError):goal(self.s,'G1','phantom','do it','proof')
    def test_full_validation_catches_unearned_faction_means(self):
        propose_attempt(self.s,'B','day2','send letter',['pay courier'])
        self.s['attempts'][0]['means']=['treasury']
        with self.assertRaises(ValueError):validate(self.s)
    def test_sites_need_registered_authority(self):
        with self.assertRaises(ValueError): place(self.s,'S','Site','UNKNOWN')
    def test_site_cannot_link_unknown_neighbor(self):
        with self.assertRaises(ValueError): place(self.s,'S','Site',connected=['GHOST'])
    def test_scene_requires_existing_site(self):
        with self.assertRaises(ValueError): enter_scene(self.s,'MISSING','Look around',['A'],'Clear road')
    def test_scene_records_place_and_intent(self):
        place(self.s,'S','Bridge',authority='A')
        x=enter_scene(self.s,'S','Find culprit',['A'],'Empty bridge')
        self.assertEqual((x['site'],x['scene']),("S",1))
    def test_milestone_requires_actual_evidence(self):
        goal(self.s,'G','A','Fix bridge','signed repair contract')
        with self.assertRaises(ValueError): milestone(self.s,'G',['R1'],'found proof')
    def test_milestone_never_grants_xp(self):
        goal(self.s,'G','A','Fix bridge','signed repair contract')
        milestone(self.s,'G',['F1'],'surveyed damage')
        self.assertNotIn('xp',self.s['goals']['G'])
    def test_goal_completion_requires_evidence_and_authority(self):
        goal(self.s,'G','A','Fix bridge','signed repair contract')
        with self.assertRaises(ValueError): complete_goal(self.s,'G',['R1'],'native')
        g=complete_goal(self.s,'G',['F1'],'human referee assessed proof')
        self.assertEqual(g['status'],'completed')
    def test_full_validation_catches_unearned_actor_info(self):
        self.s['actors']['A']['known'].append('R1')
        with self.assertRaises(ValueError):validate(self.s)
    def test_tbe_goal_xp_not_automated(self):
        tbe=campaign(mode='tbe');actor(tbe,'PC','goal',['act']);goal(tbe,'G','PC','win charter','original signed copy')
        self.assertNotIn('xp',tbe['goals']['G'])

if __name__ == '__main__': unittest.main(verbosity=2)
