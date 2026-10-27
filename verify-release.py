"""Verify generated deliverables without extracting or touching source files."""
from pathlib import Path,PurePosixPath
from zipfile import ZipFile
import hashlib,json
base=Path(__file__).resolve().parent/'release'
for name,manifest_name,required in [
    ('refining-workbench-github.zip','RELEASE_MANIFEST.json',{'README.md','AGENTS.md','package.json','wrangler.jsonc','.github/workflows/checks.yml','dist/bed.html','ARCHITECTURE.md','REVIEW_COMPLETENESS.md'}),
    ('refining-workbench-static.zip','STATIC_MANIFEST.json',{'index.html','bed.html','bed-app.mjs','platform.html','system-audit.json'})
]:
    with ZipFile(base/name) as z:
        assert z.testzip() is None
        names=set(z.namelist());assert required<=names
        for n in names:
            parts=PurePosixPath(n).parts
            assert not n.startswith('/') and '..' not in parts
            assert not set(p.lower() for p in parts)&{'.git','.openai','.sites-runtime','node_modules','.wrangler','release','uploads','jobs','solver-results'}
            assert not any(p=='.env' or p.startswith('.env.') and p!='.env.example' for p in parts)
        records=json.loads(z.read(manifest_name));assert {r['file'] for r in records}==names-{manifest_name}
        for r in records:
            data=z.read(r['file']);assert len(data)==r['bytes'];assert hashlib.sha256(data).hexdigest()==r['sha256']
    print(f'PASS {name}: required source/assets, excluded local state, CRC and per-file hashes')
for line in (base/'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
    digest,name=line.split('  ',1);assert hashlib.sha256((base/name).read_bytes()).hexdigest()==digest
print('PASS archive SHA256 checksums')
