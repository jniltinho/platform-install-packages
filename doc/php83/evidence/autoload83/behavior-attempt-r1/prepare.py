#!/usr/bin/env python3
"""Local extraction and hash-pinned patch staging only; never runs application PHP."""
import argparse, hashlib, json, subprocess, zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
PIN='de177e6cbaedf3a3207661c2325f466cce37febb73190f3a49d31f24b740c053'
STAGE='/home/vagrant/php-autoload83-r1'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(ok,msg):
    if not ok: raise ValueError(msg)
def patches():
    out=[]
    for name in ('HTMLPurifier-autoload','symfony-cli-autoload'):
        p=REPO/'patches/php83/held/autoload83'/f'{name}.json'
        row=json.loads(p.read_text()); row['patch']=str(p.parent/row['patch']); row['patch_sha256']=row.pop('sha256'); out.append(row)
    row=next(x for x in json.loads((REPO/'patches/php83/held/symfony-bootstrap.json').read_text())['files'] if x['path'].endswith('/sfCore.class.php'))
    out.append(dict(row,patch=str(REPO/row['patch'])))
    return out
def prepare(archive,dest):
    require(sha(archive)==PIN,'exp10 ZIP identity mismatch')
    require(not dest.exists(),'Refuse existing destination')
    rows=patches()
    for row in rows: require(sha(row['patch'])==row['patch_sha256'],'Held patch identity mismatch')
    with zipfile.ZipFile(archive) as z:
        files=[i for i in z.infolist() if not i.is_dir()]
        prefix=files[0].filename.split('/')[0]+'/'
        selected=[]
        for info in files:
            require(info.filename.startswith(prefix),'Mixed ZIP roots')
            rel=Path(info.filename[len(prefix):])
            require(not rel.is_absolute() and '..' not in rel.parts,'Unsafe ZIP path')
            if str(rel).startswith(('vendor/htmlpurifier/','vendor/symfony/','vendor/symfony-data/')):
                selected.append((str(rel),z.read(info)))
        require(len(selected)>1000,'Incomplete vendor subset')
    import shutil
    dest.mkdir()
    for variant in ('original','candidate'):
        for rel,data in selected:
            path=dest/variant/rel; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
    for row in rows:
        require(sha(dest/'original'/row['path'])==row['before_sha256'],'Before identity mismatch')
        proc=subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',row['patch']],cwd=dest/'candidate',capture_output=True,text=True)
        require(proc.returncode==0 and 'fuzz' not in proc.stdout.lower() and 'offset' not in proc.stdout.lower(),'Patch application not exact')
        require(sha(dest/'candidate'/row['path'])==row['after_sha256'],'After identity mismatch')
    for name in ('probe.php','run.sh'): shutil.copyfile(HERE/name,dest/name)
    shutil.copytree(HERE/'fixtures',dest/'fixtures')
    hashes={p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file()}
    report={'zip_sha256':PIN,'subset':'Complete vendor/htmlpurifier, vendor/symfony and vendor/symfony-data from exp10, not full application','files_per_tree':len(selected),'patches':rows,'stage':STAGE,'hashes':hashes}
    (dest/'identity.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('zip',type=Path); p.add_argument('destination',type=Path); a=p.parse_args()
    r=prepare(a.zip,a.destination); print(json.dumps({'files_per_tree':r['files_per_tree'],'stage':STAGE,'zip_sha256':PIN}))
