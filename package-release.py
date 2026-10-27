"""Portable source and static delivery; author changes in the canonical project."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib,json
root=Path(__file__).resolve().parent
release=root/'release'
release.mkdir(exist_ok=True)
excluded={'.git','.openai','.sites-runtime','node_modules','.wrangler','__pycache__','release','uploads','jobs','solver-results'}
def allowed(rel):
    if any(s.lower() in excluded for s in rel.parts):return False
    if any(s.lower()=='.env' or s.lower().startswith('.env.') and s!='.env.example' for s in rel.parts):return False
    if rel.suffix.lower() in {'.log','.cas','.dat','.h5','.gz'}:return False
    if rel.suffix.lower()=='.zip' and rel.parts[0]!='dist':return False
    return True
def bundle(output,base,files,manifest_name):
    manifest=[]
    with ZipFile(output,'w',ZIP_DEFLATED) as z:
        for p in sorted(files):
            rel=p.relative_to(base);data=p.read_bytes()
            z.writestr(rel.as_posix(),data)
            manifest.append({'file':rel.as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
        z.writestr(manifest_name,json.dumps(manifest,ensure_ascii=False,indent=2))
    print(f'{output} ({len(manifest)} files, {output.stat().st_size} bytes)')
bundle(release/'refining-workbench-github.zip',root,[p for p in root.rglob('*') if p.is_file() and allowed(p.relative_to(root))],'RELEASE_MANIFEST.json')
bundle(release/'refining-workbench-static.zip',root/'dist',[p for p in (root/'dist').rglob('*') if p.is_file() and allowed(p.relative_to(root))],'STATIC_MANIFEST.json')
names=['refining-workbench-github.zip','refining-workbench-static.zip']
(release/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256((release/n).read_bytes()).hexdigest()+'  '+n+'\n' for n in names),encoding='utf-8')
(release/'README.md').write_text('''# 交付包使用

唯一源码目录：D:\\Steelmaking\\refining-process-lab\\refining-process。以后的代码修改、检查和打包都在该目录进行。

- refining-workbench-github.zip：解压后把里面的源码文件提交到GitHub仓库，不要只把ZIP作为源码上传。含dist、测试、文档和Cloudflare配置，不含原Sites身份、Git历史和凭据。
- refining-workbench-static.zip：仅网页发布文件，可直接作为Cloudflare Pages静态上传包；不含服务端功能。
- SHA256SUMS.txt：交付包校验值。每包内另有逐文件清单。

没有创建GitHub仓库或部署到你的Cloudflare账户。原私有预览站点单独更新。GPT/CAD/Fluent是规划中的服务，尚未接入。
''',encoding='utf-8')

