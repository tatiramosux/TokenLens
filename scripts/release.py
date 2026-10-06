"""Explicit source allowlist + distribution inspection. Never traverses local data."""
import hashlib
import json
import re
import tarfile
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOP={'package.json','pnpm-lock.yaml','.gitignore','.gitattributes','README.md','LICENSE','SECURITY.md','CONTRIBUTING.md','CHANGELOG.md','requirements-dev.txt','tokenlens_architecture_handoff_v0.1.json'}
RULES={'core':{'.py','.json','.toml','.in','.md'},'lab':{'.py','.html','.css','.js','.svg'},'bridges':{'.py'},'scripts':{'.py','.ps1','.cjs'},'docs':{'.md'},'.github':{'.md','.yml'}}
BLOCKED={'__pycache__','build','dist','.local','.venv','.git'}
PATTERNS=[re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),re.compile(r'github_pat_[A-Za-z0-9_]{40,}'),re.compile(r'sk-(?:proj-|ant-)?[A-Za-z0-9_-]{30,}'),re.compile(r'(?i)[A-Z]:[\\/]Users[\\/]'),re.compile(r'(?i)/home/[a-z0-9_-]+/')]

def allowed(path):
    parts=path.parts
    if any(p in BLOCKED or p.endswith('.egg-info') for p in parts):return False
    if len(parts)==1:return path.name in TOP
    if path.as_posix() == 'core/LICENSE':return True
    return parts[0] in RULES and path.suffix in RULES[parts[0]]

def source_files():
    # Walk only public directories; prune generated trees before opening files.
    import os
    found=[ROOT/p for p in sorted(TOP) if (ROOT/p).is_file()]
    for directory in RULES:
        for folder,dirs,files in os.walk(ROOT/directory):
            dirs[:]=[d for d in dirs if d not in BLOCKED and not d.endswith('.egg-info')]
            for name in files:
                path=Path(folder)/name
                if allowed(path.relative_to(ROOT)):
                    if path.is_symlink():raise ValueError('Symlink proibido no pacote.')
                    found.append(path)
    return sorted(found)

def scan(path,raw):
    text=raw.decode('utf-8')
    if any(pattern.search(text) for pattern in PATTERNS):
        raise ValueError('Padrao sensivel detectado em arquivo distribuivel: '+str(path))

def inspect_core():
    artifacts=sorted((ROOT/'dist'/'core').glob('*.whl'))+sorted((ROOT/'dist'/'core').glob('*.tar.gz'))
    if len(artifacts)!=2:raise ValueError('Construa exatamente um wheel e um sdist antes do release.')
    for artifact in artifacts:
        if artifact.suffix=='.whl':
            with zipfile.ZipFile(artifact) as z: contents=[(n,z.read(n)) for n in z.namelist() if not n.endswith('/')]
        else:
            with tarfile.open(artifact) as z: contents=[(m.name,z.extractfile(m).read()) for m in z.getmembers() if m.isfile()]
        for name,raw in contents:
            parts=Path(name).parts
            if any(x in parts for x in ('lab','bridges','tests','.local','.venv')) or any(x in name for x in ('.sqlite','.db','.env')):raise ValueError('Conteudo indevido no core.')
            scan(name,raw)
    return artifacts

def main():
    artifacts=inspect_core();files=source_files();out=ROOT/'dist';out.mkdir(exist_ok=True)
    manifest=[]
    with zipfile.ZipFile(out/'tokenlens-lab-source.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            name=path.relative_to(ROOT).as_posix();raw=path.read_bytes();scan(name,raw)
            archive.writestr('TokenLens/'+name,raw)
            manifest.append({'file':name,'sha256':hashlib.sha256(raw).hexdigest()})
    (out/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    sums={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts+[out/'tokenlens-lab-source.zip']}
    (out/'SHA256SUMS.json').write_text(json.dumps(sums,indent=2)+'\n',encoding='utf-8')
    print(f'Distribuicao inspecionada: {len(files)} arquivos publicos; core e lab separados.')

if __name__=='__main__':main()
