import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from http.server import ThreadingHTTPServer
from tokenlens.store import Store
from tokenlens.contract import new_event
from lab.server import make_handler

class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.store=Store(Path(cls.tmp.name)/'http.sqlite3')
        cls.event=new_event('codex');cls.store.put(cls.event)
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(cls.store))
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.tmp.cleanup()
    def request(self,path='/',method='GET',headers=None,body=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=3)
        c.request(method,path,body=body,headers=headers or {});r=c.getresponse();data=r.read();code=r.status;c.close();return code,data
    def test_page(self):self.assertEqual(self.request()[0],200)
    def test_rebinding_rejected(self):self.assertEqual(self.request(headers={'Host':'evil.invalid'})[0],403)
    def test_cross_origin_rejected(self):self.assertEqual(self.request(headers={'Origin':'https://evil.invalid'})[0],403)
    def test_traversal(self):self.assertEqual(self.request('/../.local/telemetry.sqlite3')[0],404)
    def test_filter(self):
        code,data=self.request('/api/events?provider=claude_code');self.assertEqual(code,200);self.assertEqual(json.loads(data)['events'],[])
    def test_unknown_model_filter(self):
        code,data=self.request('/api/events?model=__unknown__')
        result=json.loads(data);self.assertEqual(code,200)
        self.assertEqual(len(result['events']),1)
        self.assertEqual(result['selected_model'],'__unknown__')
    def test_model_options_survive_empty_category(self):
        _,data=self.request('/api/events?category=research')
        result=json.loads(data)
        self.assertEqual(result['events'],[])
        self.assertEqual(result['models'],['__unknown__'])
    def test_invalid_model_resets_without_hiding_events(self):
        _,data=self.request('/api/events?model=not-available')
        result=json.loads(data)
        self.assertEqual(result['selected_model'],'')
        self.assertEqual(len(result['events']),1)
    def test_label_and_reject_extra(self):
        payload={'event_id':self.event['event_id'],'category':'planning','complexity':'medium'}
        self.assertEqual(self.request('/api/label','POST',{'Content-Type':'application/json'},json.dumps(payload))[0],200)
        payload['prompt']='private-canary'
        code,data=self.request('/api/label','POST',{'Content-Type':'application/json'},json.dumps(payload))
        self.assertEqual(code,400);self.assertNotIn(b'private-canary',data)
