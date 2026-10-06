import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from bridges import measure
from tokenlens.contract import new_event, validate, InvalidEvent
from tokenlens.store import Store
from scripts.release import allowed, scan

class DistributionTests(unittest.TestCase):
    def test_release_excludes_local_and_generated(self):
        for path in ('.local/data.sqlite3','.venv/config.py','core/build/lib/tokenlens/store.py','core/src/tokenlens_core.egg-info/PKG-INFO','lab/__pycache__/app.pyc','secrets.json'):
            self.assertFalse(allowed(Path(path)))
        self.assertTrue(allowed(Path('lab/static/theme.css')))
    def test_release_detects_secret_without_printing_value(self):
        secret='ghp_'+'a'*40
        with self.assertRaises(ValueError) as exc:scan('fixture.py',secret.encode())
        self.assertNotIn(secret,str(exc.exception))
    def test_reasoning_subset(self):
        e=new_event('codex');e['usage'].update(output_tokens=10,reasoning_tokens=11)
        with self.assertRaises(InvalidEvent):validate(e)
    def test_cache_combined_subset(self):
        e=new_event('claude_code');e['usage'].update(input_tokens=10,cached_input_tokens=6,cache_creation_tokens=6)
        with self.assertRaises(InvalidEvent):validate(e)
    def test_bridge_uses_fake_process_only(self):
        class Fake:
            def __init__(self,*args,**kwargs):
                self.stdin=io.BytesIO();self.stdout=io.BytesIO((json.dumps({'type':'turn.completed','usage':{'input_tokens':100,'output_tokens':10},'response':'private-canary'})+'\n').encode())
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def wait(self):return 0
            def kill(self):pass
        with tempfile.TemporaryDirectory() as temp:
            db=Path(temp)/'synthetic.sqlite3'
            with patch.object(sys,'argv',['measure','codex','--smoke','--db',str(db)]),patch.object(measure.shutil,'which',return_value='FAKE-CLI'),patch.object(measure.subprocess,'Popen',Fake),contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(measure.main(),0)
            events=Store(db).events();self.assertEqual(len(events),1)
            self.assertNotIn('private-canary',json.dumps(events))
    def test_core_command_as_subprocess(self):
        result=subprocess.run([sys.executable,'-m','tokenlens.cli','validate'],input=json.dumps(new_event('other',synthetic=True)).encode(),capture_output=True)
        self.assertEqual(result.returncode,0)
    def test_core_rejects_secret_without_echo(self):
        e=new_event('codex');e['prompt']='private-canary'
        result=subprocess.run([sys.executable,'-m','tokenlens.cli','validate'],input=json.dumps(e).encode(),capture_output=True)
        self.assertEqual(result.returncode,1);self.assertNotIn(b'private-canary',result.stdout+result.stderr)
