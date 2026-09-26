"""Offline adjudication of unchanged native records; never rewrites original FAIL reports."""
import hashlib,importlib.util,itertools,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
E=HERE.parents[2]/'doc/php83/evidence/xml-lifecycle-fix'
def module(name):
 spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
FUNCTIONAL=module('contract-r2');DIAGNOSTIC=module('diagnostic-contract')
BASE=json.loads((HERE/'baseline-diagnostic-records.json').read_text())
MANIFEST_PIN='c06f54b7dff9035ea1680d96416ab29d7b4669a5dbe26e417bedccf27d742a08'
CHAIN_PIN='5feb006310c2a7da6e790570f71b069738c127bd3374c52aebbf1ee81eed8017'
def same(a,b):return json.dumps(a,sort_keys=True,separators=(',',':'))==json.dumps(b,sort_keys=True,separators=(',',':'))
def require(ok,msg):
 if not ok:raise ValueError(msg)
def reconcile(primary,repeat,chain,manifest):
 require(same(primary,repeat),'independent native records exactly repeated')
 require(primary['manifest_sha256']==MANIFEST_PIN and manifest['phase']=='xml-lifecycle-held-A-r1','frozen stage identity')
 require(primary['status']=='FAIL_RETAINED_OBSERVATIONS','original strict report remains FAIL')
 require(primary['failures']==[['behavior','baseline','callback-throw'],['behavior','candidate','callback-throw']],'only original expected-class failures')
 inventory=[('behavior',v,c) for v,c in itertools.product(('baseline','candidate'),FUNCTIONAL.BEHAVIOR)]+[('scope','candidate',c) for c in FUNCTIONAL.SCOPE]
 rows=primary['records'];require(len(rows)==38 and [(r['kind'],r['variant'],r['case']) for r in rows]==inventory,'exact ordered 38 inventory')
 details=[]
 for row in rows:
  require(type(row['exit']) is int and row['exit']==0,'native integer exit0')
  require(type(row['stdout']) is str and same(json.loads(row['stdout']),row['body']),'parsed body equals raw stdout')
  body=row['body'];FUNCTIONAL.validate(body,row['kind'],row['variant'],row['case'],manifest)
  if row['variant']=='candidate':diags=DIAGNOSTIC.validate_candidate(row)
  else:
   expected=BASE['cases'][row['case']]
   for key in ['diagnostics','runtime','probe_sha256']:require(same(body[key],expected[key]),'unchanged baseline '+key)
   require(type(row['stderr']) is str and row['stderr']==expected['stderr'],'unchanged complete baseline stderr')
   diags={'handler_count':len(body['diagnostics']),'handler_only_count':sum(d['message'] not in row['stderr'] for d in body['diagnostics']),'native_stderr_exact':True,'basis':'unchanged baseline recorded twice'}
  details.append({'kind':row['kind'],'variant':row['variant'],'case':row['case'],'status':'PASS_BOUNDED_CONTRACT_R2','diagnostic_channels':diags})
 require(chain['manifest_sha256']==CHAIN_PIN and chain['product_changed'] is False and chain['acceptance'] is False,'chain instrumentation phase')
 require(len(chain['records'])==2 and [r['variant'] for r in chain['records']]==['baseline','candidate'],'exact causal pair')
 msg="SOAP-ERROR: Parsing WSDL: Couldn't load from 'file:///audit/probe/fixtures/good.wsdl'"
 expected_fault={'class':'SoapFault','message':msg,'chain':[{'class':'SoapFault','message':msg}],'chain_truncated':False}
 thrown={'class':'RuntimeException','message':'SYNTHETIC_LOADER_FAILURE','chain':[{'class':'RuntimeException','message':'SYNTHETIC_LOADER_FAILURE'}],'chain_truncated':False}
 for row in chain['records']:
  require(type(row['exit']) is int and row['exit']==0,'causal native integer exit0')
  require(type(row['stdout']) is str and same(json.loads(row['stdout']),row['body']),'causal body equals raw stdout')
  b=row['body'];require(same(b['exception'],expected_fault),'native SOAP result and complete previous chain')
  require(same(b['resolver_exceptions'],[{'phase':'operation:construct','exception':thrown}]),'actual thrown resolver exception')
  original=next(r['body'] for r in rows if r['kind']=='behavior' and r['variant']==row['variant'] and r['case']=='callback-throw')
  for key in ['loaded','runtime','events','resolver_events','functions','result']:
   require(same(b[key],original[key]),'causal instrumentation unchanged product/runtime/observable '+key)
  require(same(original['exception'],{'class':'SoapFault','message':msg}),'corrected expectation grounded in unchanged primary result')
 return {'status':'PASS_BOUNDED_HELD_CONTRACT_R2','cases':details,'native_primary_processes':38,'native_repeat_processes':38,'native_causal_followup_processes':2,'original_reports_rewritten':False,'original_strict_failures_retained':2,'causal_finding':'native ext/soap yields SoapFault with previous=null for thrown synthetic RuntimeException, identically baseline/candidate','application_acceptance':False,'artifact_selected':False}
def main():
 out=Path(sys.argv[1]);require(not out.exists(),'refuse overwrite')
 primary=json.loads((E/'primary.json').read_text());repeat=json.loads((E/'claude-native-matrix.json').read_text());chain=json.loads((E/'claude-chain-matrix.json').read_text())
 mb=Path('/tmp/php-xml-lifecycle-fix-prep-r1/identities.json').read_bytes();require(hashlib.sha256(mb).hexdigest()==MANIFEST_PIN,'manifest bytes')
 require(hashlib.sha256((E/'primary.json').read_bytes()).hexdigest()==BASE['reference_sha256'],'recorded baseline reference pin')
 require((E/'claude-native.exit').read_text().strip()=='0' and (E/'claude-chain.exit').read_text().strip()=='0','actual CLI terminal exits')
 snapshots=[(E/n).read_bytes() for n in ['primary-runtime-before.json','primary-runtime-after.json','claude-native-before.json','claude-native-after.json','claude-chain-before.json','claude-chain-after.json']]
 require(all(x==snapshots[0] for x in snapshots),'all six runtime snapshots unchanged')
 result=reconcile(primary,repeat,chain,json.loads(mb));result['runtime_snapshot_sha256']=hashlib.sha256(snapshots[0]).hexdigest()
 result['input_sha256']={n:hashlib.sha256((E/n).read_bytes()).hexdigest() for n in ['primary.json','claude-native-matrix.json','claude-chain-matrix.json']}
 result['contract_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/'contract-r2.py',HERE/'diagnostic-contract.py',HERE/'baseline-diagnostic-records.json',Path(__file__)]}
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'cases':len(result['cases']),'application_acceptance':False}))
if __name__=='__main__':main()
