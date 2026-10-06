"""Verify a built wheel in isolated import mode, without lab or editable sources."""
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
wheel=next((ROOT/'dist'/'core').glob('*.whl'))
with tempfile.TemporaryDirectory() as folder:
    with zipfile.ZipFile(wheel) as z:z.extractall(folder)
    script="import sys;sys.path.insert(0,sys.argv[1]);from tokenlens.contract import new_event,validate;from tokenlens.store import Store;from pathlib import Path;e=validate(new_event('other',synthetic=True));s=Store(Path(sys.argv[1])/'test.sqlite3');s.put(e);assert len(s.events(True))==1;assert not (Path(sys.argv[1])/'lab').exists();print('Standalone wheel: passed')"
    subprocess.run([sys.executable,'-I','-c',script,folder],check=True,cwd=folder)
