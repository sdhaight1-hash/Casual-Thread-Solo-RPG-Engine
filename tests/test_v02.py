"""v0.2 behavioral tests: transactional truth, replay, hidden info and pacing."""
import copy
import unittest
from causal_thread import (
    campaign, actor, fact, learn, goal, place, start_journal, transact,
    replay_journal, context_oracle, scene_brief, npc_conversation_frame,
    session_brief, pressure_review, validate, route)

class JournalAndPlay(unittest.TestCase):
    def setUp(self):
        self.s=campaign('Gate of Ash','native')
        fact(self.s,'C1','A carved lock has been replaced','established','physical inspection')
        fact(self.s,'R1','The reeve ordered the replacement','rumor','coopers gossip')
        actor(self.s,'PC','Recover the original charter',['ask','inspect'],risk_tolerance=2)
        actor(self.s,'REEVE','Keep villagers safe',['hire guards','send runner'],risk_tolerance=1)
        actor(self.s,'CARTER','Keep toll trade open',['escort','record'],risk_tolerance=1)
        place(self.s,'GATE','Gatehouse','REEVE',leads=['C1','R1'],affordances=['stairs','public passage'])
        place(self.s,'ARCHIVE','Archive','CARTER',leads=['C1'],affordances=['locked vault'])
        goal(self.s,'GOAL','PC','Recover original charter','the original charter is verified and in custody')
        start_journal(self.s)

    def commit(self,ident,ops,**kwargs):
        return transact(self.s,ident,ident,'witnessed action',ops,**kwargs)

    def test_checkpoint_replays(self):
        self.commit('E1',[{'op':'learn_fact','actor':'PC','fact':'C1'}],visible_to=['PC'])
        self.assertEqual(self.s['revision'],1)
        self.assertEqual(replay_journal(self.s)['journal_hash'],self.s['journal_hash'])

    def test_multi_operation_atomic_failure(self):
        initial=copy.deepcopy(self.s)
        with self.assertRaises(ValueError):
            self.commit('E1',[{'op':'learn_fact','actor':'PC','fact':'C1'},
                              {'op':'grant_mean','actor':'MISSING','resource':'keys'}])
        self.assertEqual(self.s,initial)

    def test_validation_failure_atomic(self):
        initial=copy.deepcopy(self.s)
        with self.assertRaises(ValueError):
            self.commit('E1',[{'op':'open_thread','id':'T1','question':'X','visible_to':['nonexistent']}])
        self.assertEqual(self.s,initial)

    def test_stale_write_rejected(self):
        self.commit('E1',[{'op':'learn_fact','actor':'PC','fact':'C1'}])
        with self.assertRaises(ValueError):
            self.commit('E2',[{'op':'advance_time','days':1}],expected_revision=0)

    def test_mutations_outside_journal_detected(self):
        self.s['actors']['PC']['means'].append('false passport')
        with self.assertRaises(ValueError):
            self.commit('E1',[{'op':'advance_time','days':1}])

    def test_journal_tamper_detected(self):
        self.commit('E1',[{'op':'learn_fact','actor':'PC','fact':'C1'}])
        self.s['journal'][0]['description']='forged chronicle'
        with self.assertRaises(ValueError):replay_journal(self.s)

    def test_journal_head_tamper_rejected(self):
        self.commit('E1',[{'op':'advance_time','days':1}])
        self.s['journal'][0]['revision']=900
        with self.assertRaises(ValueError):self.commit('E2',[{'op':'advance_time','days':1}])

    def test_duplicate_event_protection(self):
        self.commit('E1',[{'op':'advance_time','days':1}])
        with self.assertRaises(ValueError):self.commit('E1',[{'op':'advance_time','days':1}])

    def test_unknown_op_rollback(self):
        before=copy.deepcopy(self.s)
        with self.assertRaises(ValueError):self.commit('E1',[{'op':'grant_the_moon'}])
        self.assertEqual(before,self.s)

    def test_relationship_is_directional(self):
        self.commit('E1',[{'op':'set_relation','actor':'REEVE','target':'PC','stance':-1}])
        self.assertEqual(npc_conversation_frame(self.s,'REEVE','PC')['stance'],-1)
        self.assertEqual(npc_conversation_frame(self.s,'PC','REEVE')['stance'],0)

    def test_npc_knows_belief_not_truth(self):
        self.commit('E1',[{'op':'learn_fact','actor':'REEVE','fact':'R1','mode':'believe'}])
        frame=npc_conversation_frame(self.s,'REEVE','PC',['R1'])
        self.assertEqual(frame['known_claim_ids'],[])
        self.assertEqual(frame['believed_claim_ids'],['R1'])

    def test_tbe_social_authority(self):
        self.s['mode']='tbe'  # not committed: only read-only route for test
        self.assertEqual(route(self.s,'social')['authority'],'tbe_intrigue')

    def test_open_thread_only_when_visible(self):
        self.commit('E1',[{'op':'open_thread','id':'T1','site':'GATE','question':'Who changed the gate?',
                           'visible_to':['PC'],'deadline_day':3}])
        self.commit('E2',[{'op':'open_thread','id':'SECRET','site':'GATE','question':'Secret spy?',
                           'visible_to':[],'deadline_day':2}])
        self.assertEqual(scene_brief(self.s,'GATE','PC')['visible_threads'],['T1'])
        self.assertEqual(pressure_review(self.s,'PC')['open_threads'],['T1'])
        self.assertEqual(len(pressure_review(self.s,'PC',referee=True)['open_threads']),2)

    def test_due_deadline_no_auto_resolution(self):
        self.commit('E1',[{'op':'open_thread','id':'T1','site':'GATE','question':'Who changed the gate?',
                           'visible_to':['PC'],'deadline_day':2}])
        self.commit('E2',[{'op':'advance_time','days':1}])
        self.assertEqual(pressure_review(self.s)['due_threads'],['T1'])
        self.assertEqual(self.s['threads']['T1']['status'],'open')

    def test_deadline_in_past_rejected(self):
        self.commit('E1',[{'op':'advance_time','days':2}])
        with self.assertRaises(ValueError):
            self.commit('E2',[{'op':'open_thread','id':'T','question':'X','deadline_day':1}])

    def test_close_thread_needs_evidence(self):
        self.commit('E1',[{'op':'open_thread','id':'T','question':'who?','visible_to':['PC']}])
        with self.assertRaises(ValueError):self.commit('E2',[{'op':'close_thread','thread':'T','evidence':['R1']}])
        self.commit('E2',[{'op':'close_thread','thread':'T','evidence':['C1']}])
        self.assertEqual(self.s['threads']['T']['status'],'closed')

    def test_scene_preview_leads_only_known(self):
        self.assertEqual(scene_brief(self.s,'GATE','PC')['known_leads'],[])
        self.commit('E1',[{'op':'learn_fact','actor':'PC','fact':'C1'}],visible_to=['PC'])
        self.assertEqual(scene_brief(self.s,'GATE','PC')['known_leads'],['C1'])
        self.assertNotIn('R1',scene_brief(self.s,'GATE','PC')['known_leads'])

    def test_summary_hidden_receipts(self):
        self.commit('E1',[{'op':'learn_fact','actor':'PC','fact':'C1'}],visible_to=['PC'])
        self.commit('E2',[{'op':'advance_time','days':1}],visible_to=[])
        summary=session_brief(self.s)
        self.assertEqual(summary['recent_events'],['E1'])
        self.assertIn('A carved lock',summary['known_claims'][0])

    def test_oracle_commits_answer_not_world_outcome(self):
        q=context_oracle(self.s,'O1','courier-arrived','Did courier arrive?',
                         'likely',['C1'],'Road and courier availability allow a likely arrival',8,
                         visible_to=['PC'])
        self.assertEqual(q['answer'],'yes')
        self.assertEqual(self.s['facts']['C1']['claim'],'A carved lock has been replaced')
        self.assertEqual(len(self.s['facts']),2)
        self.assertEqual(replay_journal(self.s)['revision'],1)

    def test_oracle_reroll_same_question_denied(self):
        context_oracle(self.s,'O1','gate-open','Is the gate open?','even',['C1'],'The gate has a new lock',9)
        with self.assertRaises(ValueError):
            context_oracle(self.s,'O2','gate-open','Is the gate open?','likely',['C1'],'Wanted a different answer',2)

    def test_oracle_change_in_context_with_evidence(self):
        context_oracle(self.s,'O1','gate-open','Is the gate open?','even',['C1'],'A replaced lock creates uncertainty',9)
        self.commit('E1',[{'op':'record_fact','id':'C2','claim':'The hinge was loosened','status':'established','provenance':'inspection'}])
        q=context_oracle(self.s,'O2','gate-open','Is the gate open?','likely',['C1','C2'],
                         'Hinge evidence shifts the chance',2,change_reason='A new observation changes the gate condition')
        self.assertEqual(q['answer'],'yes')

    def test_time_only_reroll_with_explicit_temporal_scope(self):
        context_oracle(self.s,'O1','courier-arrived','Has the courier arrived today?',
                       'even',['C1'],'Travel takes time',8,window='day:1')
        self.commit('E1',[{'op':'advance_time','days':1}])
        with self.assertRaises(ValueError):
            context_oracle(self.s,'O2','courier-arrived','Has the courier arrived today?',
                           'even',['C1'],'Just wanted another roll',1,window='fixed',change_reason='')
        q=context_oracle(self.s,'O2','courier-arrived','Has the courier arrived today?',
                         'likely',['C1'],'A full day has passed',1,window='day:2',
                         change_reason='A day of travel has elapsed')
        self.assertEqual(q['answer'],'yes')

    def test_forged_window_rejected(self):
        with self.assertRaises(ValueError):
            context_oracle(self.s,'O1','q','Q?','even',[], 'Unknown yet',1,window='day:900')

    def test_native_routing_tbe_prohibition(self):
        self.s['mode']='tbe'
        with self.assertRaises(ValueError):
            context_oracle(self.s,'O1','q','Q?','even',[], 'Uncertain',4)

    def test_outcome_requires_separate_event(self):
        q=context_oracle(self.s,'O1','message-arrived','Did the message arrive?','likely',[],
                         'Messenger is experienced',4)
        self.assertEqual(q['answer'],'yes')
        self.assertEqual(len(self.s['facts']),2)
        self.commit('E1',[{'op':'record_fact','id':'C2','claim':'Message arrived',
                           'status':'established','provenance':'O1 interpretation'}])
        self.assertIn('C2',self.s['facts'])

    def test_full_session_three_days_replays(self):
        self.commit('E1',[{'op':'learn_fact','actor':'PC','fact':'C1'},
                          {'op':'open_thread','id':'TH1','question':'Who replaced the lock?',
                           'site':'GATE','visible_to':['PC'],'deadline_day':3}],visible_to=['PC'])
        self.commit('E2',[{'op':'advance_time','days':1},
                          {'op':'record_attempt','actor':'REEVE','window':'day2',
                           'action':'send runner','means':['send runner']}])
        self.commit('E3',[{'op':'settle_attempt','index':0,'outcome':'partial','authority':'adjudicated travel conditions'},
                          {'op':'set_relation','actor':'REEVE','target':'PC','stance':-1}])
        self.commit('E4',[{'op':'advance_time','days':1},
                          {'op':'record_fact','id':'C2','claim':'Charter is in archive','status':'established','provenance':'archive inventory'},
                          {'op':'learn_fact','actor':'PC','fact':'C2'}],visible_to=['PC'])
        self.commit('E5',[{'op':'mark_goal','goal':'GOAL','evidence':['C2'],
                          'description':'Found original charter in inventory'}],visible_to=['PC'])
        self.assertEqual(replay_journal(self.s)['journal_hash'],self.s['journal_hash'])
        self.assertEqual(self.s['day'],3)
        self.assertEqual(self.s['goals']['GOAL']['status'],'active')
        self.assertIn('TH1',pressure_review(self.s)['due_threads'])
        self.assertEqual(len(self.s['journal']),5)

if __name__=='__main__':unittest.main(verbosity=2)

# Additional migration and record-integrity checks appended for v0.2.
class MigrationAndIntegrity(unittest.TestCase):
    def test_migrate_existing_v01_at_checkpoint(self):
        s=campaign('Old save');s['version']='0.1'
        start_journal(s)
        self.assertEqual(s['version'],'0.2')
        self.assertTrue(validate(s))

    def test_audit_rejects_hidden_journal_tamper(self):
        from causal_thread import audit_campaign
        s=campaign();actor(s,'PC','Protect',['run']);start_journal(s)
        transact(s,'T1','Move time','elapsed time',[{'op':'advance_time','days':1}])
        self.assertTrue(audit_campaign(s))
        s['journal'][0]['source']='forged'
        with self.assertRaises(ValueError):audit_campaign(s)

class ContextualActorOracle(unittest.TestCase):
    def test_actor_information_changes_answer_scope(self):
        s=campaign();fact(s,'F1','A shipment is late','established','carrier log')
        actor(s,'PC','Get home',['walk']);actor(s,'CLERK','Avoid delays',['issue pass'])
        start_journal(s)
        context_oracle(s,'O1','clerk-help','Will the clerk help?',
                       'unlikely',['F1'],'Clerk is busy',9,actor_ids=['CLERK'])
        with self.assertRaises(ValueError):
            context_oracle(s,'O2','clerk-help','Will the clerk help?',
                           'likely',['F1'],'I want a yes',1,actor_ids=['CLERK'])
        transact(s,'E1','Clerk learns about shipment','witness',
                 [{'op':'learn_fact','actor':'CLERK','fact':'F1'}])
        q=context_oracle(s,'O2','clerk-help','Will the clerk help?',
                         'likely',['F1'],'Clerk now knows the delay',2,actor_ids=['CLERK'],
                         change_reason='Clerk learned what the PC needs')
        self.assertEqual(q['answer'],'yes')

    def test_unregistered_oracle_context_rejected(self):
        s=campaign();actor(s,'PC','x',[]);start_journal(s)
        with self.assertRaises(ValueError):
            context_oracle(s,'O1','q','Q?','even',[], 'No evidence',2, site_ids=['void'])

class ObserverSecrecy(unittest.TestCase):
    def test_concealed_actor_not_revealed_in_scene(self):
        s=campaign();actor(s,'PC','explore',[]);actor(s,'SPY','observe',[])
        place(s,'S','Ruin');start_journal(s)
        transact(s,'E1','Spy slips into ruin','observed in referee context',[
            {'op':'move_actor','actor':'SPY','site':'S','concealed_from':['PC']}])
        self.assertNotIn('SPY',scene_brief(s,'S','PC')['present_actors'])
        self.assertEqual(replay_journal(s)['journal_hash'],s['journal_hash'])
        transact(s,'E2','Spy is exposed','search success',[
            {'op':'move_actor','actor':'SPY','site':'S','concealed_from':[]}],visible_to=['PC'])
        self.assertIn('SPY',scene_brief(s,'S','PC')['present_actors'])

class TBEOwnerBoundary(unittest.TestCase):
    def test_native_mode_refuses_host_ask_the_weave_record(self):
        from causal_thread import record_tbe_question
        s=campaign(); actor(s,'PC','a',[]); start_journal(s)
        with self.assertRaises(ValueError):
            record_tbe_question(s,'O1','q','Are they there?','Likely',44,'Yes')

    def test_tbe_double_reminder_without_extra_event(self):
        from causal_thread import record_tbe_question
        s=campaign(mode='tbe');actor(s,'PC','a',[]);start_journal(s)
        q=record_tbe_question(s,'O1','guard','Is the guard there?','Likely',44,'Yes',visible_to=['PC'])
        self.assertTrue(q['random_event_pending'])
        self.assertEqual(len(s['events']),1)  # one journal receipt, not a generated second event
        self.assertEqual(replay_journal(s)['journal_hash'],s['journal_hash'])

    def test_tbe_non_double_reminder_false_and_duplicate_rejected(self):
        from causal_thread import record_tbe_question
        s=campaign(mode='tbe');actor(s,'PC','a',[]);start_journal(s)
        q=record_tbe_question(s,'O1','guard','Is guard there?','50/50',52,'No')
        self.assertFalse(q['random_event_pending'])
        with self.assertRaises(ValueError):
            record_tbe_question(s,'O2','guard','Is guard there?','Likely',33,'Yes')
