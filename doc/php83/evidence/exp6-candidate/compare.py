import json,hashlib
from pathlib import Path
base=Path('doc/php83/evidence'); load=lambda p:json.loads(p.read_text())
a=load(base/'exp6-api/codex.json');b=load(base/'exp6-api/claude.json')
def req(x):
 if not x:raise RuntimeError('comparison failed')
req(a['functional_checks_passed'] and b['functional_checks_passed'])
api=[]
for x,y in zip(a['records'],b['records']):
 keys=['runtime','tree','returncode','stdout','stdout_whitelisted','diagnostics','signature_failure']
 req(all(x[k]==y[k] for k in keys));api.append({'runtime':x['runtime'],'tree':x['tree'],'independent_equal':True,'diagnostic_groups':len(x['diagnostics']),'diagnostic_events':sum(d['count'] for d in x['diagnostics'])})
prev=next(r for r in a['records'] if r['runtime']=='83' and r['tree']=='exp5')['diagnostics'];cur=next(r for r in a['records'] if r['runtime']=='83' and r['tree']=='exp6')['diagnostics'];removed=[d for d in prev if d not in cur];added=[d for d in cur if d not in prev]
req(not added and len(removed)==2 and sum(d['count'] for d in removed)==84 and all('KalturaActionReflector.php' in d['path'] for d in removed))
(base/'exp6-api/comparison.json').write_text(json.dumps({'independent_rows':api,'removed':removed,'new_or_changed_groups':added,'application_acceptance':False},indent=2)+'\n')
ds={v:load(base/f'exp6-runtime/codex-{v}.json') for v in ['74','83']}; comparisons=[];independent=[];zeros=0;fatals=0
for v,d in ds.items():
 other=load(base/f'exp6-runtime/claude-{v}.json');req(len(d['rows'])==len(other['rows'])==24)
 req(d['harness']==other['harness'] and d['zip_sha256']==other['zip_sha256'])
 for p,h in d['harness'].items():
  local=Path('tools/php83')/p.replace('tests/','patch-tests/',1);req(hashlib.sha256(local.read_bytes()).hexdigest()==h)
 for x,y in zip(d['rows'],other['rows']):
  req(all(x[k]==y[k] for k in x if k!='duration_ns'))
  expected=v=='83' and x['source']=='original' and x['case'] in ['legacy-json','zend-json']
  if expected:req(x['exit']==255 and 'Fatal error' in x['stderr']);fatals+=1
  else:req(x['exit']==0);zeros+=1
  if x['source']=='exp6' and x['case']!='environment':
   orig=next(r for r in ds['74']['rows'] if r['source']=='original' and r['ini']==x['ini'] and r['case']==x['case'])
   one,two=json.loads(x['stdout']),json.loads(orig['stdout'])
   if x['case']=='doc-comment-export':one,two=one['entries'],two['entries']
   req(one==two);comparisons.append({'runtime':v,'ini':x['ini'],'case':x['case'],'typed_output_equal':True})
 independent.append({'runtime':v,'all_24_rows_equal_except_duration':True,'fixture_hashes_verified':True})
(base/'exp6-runtime/parity.json').write_text(json.dumps({'logical_rows':48,'zero_exits':zeros,'expected_original83_fatals':fatals,'candidate_rows_exit0':24,'comparisons':comparisons,'independent':independent,'application_acceptance':False},indent=2)+'\n')
print('API and CLI independent comparisons passed')
