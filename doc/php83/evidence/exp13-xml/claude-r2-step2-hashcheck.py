import hashlib,json,os,subprocess,sys
from pathlib import Path
sha=lambda b:hashlib.sha256(b).hexdigest()
R=Path('/tmp/exp13-xml-reproduction-r2');L=Path('tools/php83/exp13-xml/stage');REF=Path('tools/php83/exp13-xml/reference')
prep=json.loads(Path('doc/php83/evidence/exp13-xml/preparation.json').read_bytes());rep=json.loads(Path('doc/php83/evidence/exp13-xml/r2-reproduction.json').read_bytes())
ok=True
def chk(c,m):
  global ok
  print(('PASS ' if c else 'FAIL ')+m);ok&=c
chk(sha(Path('doc/php83/evidence/exp13-xml/preparation.json').read_bytes())=='30b70f69246cf542853b79dc3fb3e2f175ce25e5810eb813d70f0d5daa99a5c7','preparation.json pin 30b70f69 unchanged')
hist={'matrix':'c06f54b7dff9035ea1680d96416ab29d7b4669a5dbe26e417bedccf27d742a08','chain':'5feb006310c2a7da6e790570f71b069738c127bd3374c52aebbf1ee81eed8017'}
for k in ['matrix','chain']:
  rm=(R/k/'identities.json').read_bytes();lm=(L/k/'identities.json').read_bytes()
  chk(sha(rm)==sha(lm)==prep['stages'][k]['manifest_sha256']==rep['stages'][k]['manifest_sha256'],f'{k} manifest {sha(rm)[:8]} tmp==local==preparation==r2-report')
  chk(prep['stages'][k]['source_joins']==rep['stages'][k]['source_joins'],f'{k} source_joins identical')
  chk(sha((REF/f'{k}-manifest.json').read_bytes())==hist[k],f'{k} reference manifest == historical pin {hist[k][:8]}')
  files=json.loads(rm)['files']
  for base in (R/k,L/k):
    bad=[p for p,h in files.items() if sha((base/p).read_bytes())!=h]
    extra=sorted(str(p.relative_to(base)) for p in base.rglob('*') if p.is_file() and str(p.relative_to(base)) not in files and p.name!='identities.json')
    links=[str(p) for p in base.rglob('*') if p.is_symlink()]
    chk(not bad and not extra and not links,f'{base}: {len(files)} files rehash clean, unmanifested={extra}, symlinks={links}')
  hm=json.loads((REF/f'{k}-manifest.json').read_bytes())['files']
  for n in hm:
    if n.startswith('fixtures/') or n=='provider.json': chk(sha((REF/n).read_bytes())==hm[n],f'{k} reference/{n} == historical digest')
refs=sorted(str(p) for p in REF.rglob('*') if p.is_file());print('reference inventory:',refs)
tr=subprocess.run(['git','ls-files','tools/php83/xml-lifecycle-fix/behavior.php','tools/php83/xml-lifecycle-fix/behavior-chain.php','tools/php83/xml-lifecycle-fix/scope-probe.php','tools/php83/xml-lifecycle-fix/run-native.sh'],capture_output=True,text=True).stdout.split()
chk(len(tr)==4,'probe/wrapper sources tracked in git: '+str(tr))
d=subprocess.run(['git','diff','--quiet','HEAD','--','tools/php83/xml-lifecycle-fix'],).returncode;chk(d==0,'tracked xml-lifecycle-fix sources unmodified vs HEAD')
sys.exit(0 if ok else 1)
