import hashlib,json,zipfile,io,sys
from pathlib import Path
R=Path('.');O=R/'doc/php83/evidence/serialization-contracts';S=R/'tools/php83/exp13-serialization'
h=lambda b:hashlib.sha256(b).hexdigest();out={}
out['input_pins_sha256']=h((S/'input-pins.json').read_bytes())
pins=json.loads((S/'input-pins.json').read_bytes());out['input_pins_all_match']=all(h((R/p).read_bytes())==v for p,v in pins.items())
out['preparation_sha256']=h((R/'doc/php83/evidence/exp13-serialization/preparation.json').read_bytes())
old=json.loads((O/'r3-stage-identities.json').read_bytes())
zips={'exp12':'../platform-install-packages-php83-artifacts/exp12/Rigel-18.20.0-php83-experimental.exp12.zip','exp13':'../platform-install-packages-php83-artifacts/exp13/Rigel-18.20.0-php83-experimental.exp13.zip'}
out['zip_sha256']={};per={};diff=[]
for a,v in [('exp12','original'),('exp13','candidate')]:
 raw=Path(zips[a]).read_bytes();out['zip_sha256'][a]=h(raw);z=zipfile.ZipFile(io.BytesIO(raw));n=0
 for name,d in old['files'].items():
  if name.startswith(v+'/'):
   n+=1;b=z.read('server-Rigel-18.20.0/'+name.split('/',1)[1])
   if h(b)!=d or h((S/'stage'/name).read_bytes())!=d:diff.append(name)
 per[v]=n
out['sources_per_variant']=per;out['zip_or_stage_mismatch']=diff
m=(S/'stage/identities.json').read_bytes();out['stage_manifest_sha256']=h(m);mj=json.loads(m)
out['stage_files']=len(mj['files']);out['stage_file_hash_mismatch']=[n for n,d in mj['files'].items() if h((S/'stage'/n).read_bytes())!=d]
out['stage_inventory_equals_manifest']={str(p.relative_to(S/'stage')) for p in (S/'stage').rglob('*') if p.is_file()}==set(mj['files'])|{'identities.json'}
out['cachefix_in_stage']=any(n.startswith('cachefix/') for n in mj['files'])
out['probes_equal_R3']={n:mj['files'][n]==old['files'][n] for n in ['probe.php','cache-probe.php','reference-wires.json']}
out['candidate_vs_original_differing_sources']=sorted(n.split('/',1)[1] for n in mj['files'] if n.startswith('candidate/') and mj['files'][n]!=mj['files']['original/'+n.split('/',1)[1]])
r83=json.loads((O/'r3-primary83.json').read_bytes())['records'];x=[r for r in r83 if r['variant']!='cachefix']
out['matrix']={'r3_83_rows':len(r83),'selected':len(x),'by_variant':{v:sum(r['variant']==v for r in x) for v in ['original','candidate']},'reads_by_writer':{w:sum(r['operation']=='read' and r['writer']==w for r in x) for w in ['original83-r2','candidate83-r2','original74']},'cache':sum(r['kind']=='cache' for r in x)}
print(json.dumps(out,indent=1))
