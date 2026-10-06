import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from tokenlens.contract import new_event, validate, InvalidEvent, finish_usage
from tokenlens.adapters import ADAPTERS
from tokenlens.store import Store
from bridges.measure import collect
from bridges.claude_statusline import normalize
from lab.demo import seed

class ContractTests(unittest.TestCase):
    def test_synthetic_providers_same_contract(self):
        for provider in ('codex','claude_code','antigravity','other'):
            validate(new_event(provider, synthetic=True))

    def test_unknown_fields_rejected_at_every_level(self):
        for section in (None,'task','execution','usage','assessment'):
            e=new_event('codex')
            (e[section] if section else e)['prompt']='private-canary'
            with self.assertRaises(InvalidEvent) as err: validate(e)
            self.assertNotIn('private-canary',str(err.exception))

    def test_model_allowlist(self):
        for value in ('sk-test-secret-canary','person@example.invalid','C:/private/code','custom-customer-model'):
            e=new_event('codex');e['execution']['model']=value
            with self.assertRaises(InvalidEvent): validate(e)

    def test_numeric_safety(self):
        for value in (-1,True,1.5,10**13,'secret'):
            e=new_event('codex');e['usage']['input_tokens']=value
            with self.assertRaises(InvalidEvent): validate(e)

    def test_inconsistent_total_rejected(self):
        e=new_event('codex');e['usage'].update(input_tokens=5,output_tokens=3,total_tokens=15)
        with self.assertRaises(InvalidEvent): validate(e)

    def test_no_double_counting_cache_or_reasoning(self):
        e=new_event('codex');e['usage'].update(input_tokens=100,output_tokens=20,cached_input_tokens=70,reasoning_tokens=10)
        self.assertEqual(finish_usage(e)['usage']['total_tokens'],120)

    def test_codex_projection(self):
        p={'type':'turn.completed','usage':{'input_tokens':100,'output_tokens':10,'cached_input_tokens':50},'email':'private-canary','response':'private-canary'}
        e=ADAPTERS['codex'].normalize(p)[0]
        self.assertEqual(e['usage']['total_tokens'],110)
        self.assertNotIn('private-canary',json.dumps(e))
        self.assertIsNone(e['execution']['success'])

    def test_codex_ignores_messages(self):
        self.assertEqual(ADAPTERS['codex'].normalize({'type':'item.completed','item':{'text':'private-canary'}}),[])

    def test_claude_cache_normalization(self):
        p={'type':'result','usage':{'input_tokens':10,'output_tokens':5,'cache_read_input_tokens':20,'cache_creation_input_tokens':30},'result':'private-canary','modelUsage':{'claude-sonnet-4-6':{}}}
        e=ADAPTERS['claude_code'].normalize(p)[0]
        self.assertEqual(e['usage']['input_tokens'],60)
        self.assertEqual(e['usage']['total_tokens'],65)
        self.assertNotIn('private-canary',json.dumps(e))

    def test_claude_missing_cache_is_unknown(self):
        e=ADAPTERS['claude_code'].normalize({'type':'result','usage':{'input_tokens':10,'output_tokens':5}})[0]
        self.assertIsNone(e['usage']['total_tokens'])

    def test_antigravity_does_not_invent(self):
        self.assertEqual(ADAPTERS['antigravity'].normalize({'tokens':123}),[])

    def test_stream_discards_bad_and_oversize(self):
        payload={'type':'turn.completed','usage':{'input_tokens':10,'output_tokens':2}}
        stream=io.BytesIO(b'private-canary\n'+b'x'*(1024*1024+10)+b'\n'+json.dumps(payload).encode()+b'\n')
        self.assertEqual(len(list(collect(stream,ADAPTERS['codex']))),1)

    def test_statusline_context_is_not_consumption(self):
        e=normalize({'session_id':'private-canary','cwd':'private-canary','model':{'id':'claude-sonnet-4-6'},'context_window':{'total_input_tokens':100,'total_output_tokens':5}})
        self.assertEqual(e['scope'],'context_snapshot')
        self.assertNotIn('private-canary',json.dumps(e))

class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=Store(Path(self.tmp.name)/'test.sqlite3')
    def tearDown(self): self.tmp.cleanup()
    def test_idempotent_ingestion(self):
        e=new_event('codex');self.store.put(e);self.store.put(e)
        self.assertEqual(len(self.store.events()),1)
    def test_demo_isolation_and_seed_idempotence(self):
        seed(self.store);seed(self.store)
        self.assertEqual(len(self.store.events()),0)
        self.assertEqual(len(self.store.events(True)),36)
    def test_rejection_happens_before_write(self):
        e=new_event('codex');e['prompt']='private-canary'
        with self.assertRaises(InvalidEvent): self.store.put(e)
        self.assertNotIn(b'private-canary',self.store.path.read_bytes())
    def test_label_validation(self):
        e=new_event('codex');self.store.put(e)
        with self.assertRaises(InvalidEvent):self.store.label(e['event_id'],'private-canary','low')
        self.assertTrue(self.store.label(e['event_id'],'coding','low'))
        self.assertEqual(self.store.events()[0]['task']['category'],'coding')
    def test_snapshot_replaces_and_preserves_label(self):
        e=new_event('claude_code','claude_statusline','context_snapshot');self.store.snapshot(e)
        self.store.label(e['event_id'],'research','high')
        e['usage']['input_tokens']=20;self.store.snapshot(e)
        self.assertEqual(len(self.store.events()),1)
        self.assertEqual(self.store.events()[0]['task']['category'],'research')
    def test_snapshot_cannot_replace_consumption(self):
        e=new_event('codex');self.store.put(e);e['scope']='context_snapshot'
        with self.assertRaises(ValueError):self.store.snapshot(e)

if __name__=='__main__':unittest.main()
