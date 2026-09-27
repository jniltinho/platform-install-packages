"""Finite same-engine display-policy parity; never application/privacy acceptance."""
import copy,json,sys
from pathlib import Path
COHORTS=['original74','display74','exp14statement83','display83']
CASES=[mode+'-'+value for mode in ['bound','array'] for value in ['session-string','serialized','quote','null','integer','boolean']]+['update-repeat','update-repeat']
def need(ok,code):
 if not ok:raise ValueError(code)
def validate(report):
 need(report.get('status')=='OBSERVED_NOT_ACCEPTED','STATUS')
 need(report.get('source_before')=='VERIFIED\n' and report.get('source_after')=='VERIFIED\n','SOURCE')
 need(report.get('runtime_before')==report.get('runtime_after') and type(report.get('runtime_before')) is dict,'RUNTIME')
 rows=report['records'];need([r['cohort'] for r in rows]==COHORTS,'COHORTS')
 need(len({r['db']['datadir'] for r in rows})==4 and len({r['db']['unit'] for r in rows})==4,'FRESH_DATABASES')
 bodies=[]
 for index,row in enumerate(rows):
  need(type(row['execution']['exit']) is int and row['execution']['exit']==0,'NATIVE_EXIT')
  need(json.loads(row['execution']['stdout'])==row['body'],'BODY_BINDING')
  need(row['cleanup']['stopped'] is True and row['cleanup']['stop_exit']==0,'CLEANUP')
  body=row['body'];policy=index%2==1;engine='7.4.' if index<2 else '8.3.'
  need(body['runtime'].startswith(engine) and body['policy'] is policy,'RUNTIME_POLICY')
  pin=report['source_proof']['targets'][index//2]['after_sha256' if policy else 'before_sha256']
  need(body['source_sha256']==pin,'SOURCE_JOIN')
  need([r['case'] for r in body['rows']]==CASES,'CASESET')
  need(body['application_acceptance'] is False and body['inline_literal_visible'] is True,'LIMITS')
  expected=['return',['NULL',None]] if index<2 else ['return',['boolean',True]]
  need(body['dry_run']==expected and body['inline_outcome']==expected,'RETURN_CONTRACT')
  for n,r in enumerate(body['rows']):
   need(r['outcome']==expected,'ROW_RETURN')
   if n<12:
    need(r['display_exact'] is (True if policy else None),'DISPLAY')
    leak=not policy if r['case'].endswith(('serialized','session-string')) else None
    need(r['original_leak'] is leak,'LEAK_CONTROL')
   else:need(r['handled'] is (n==13),'CACHE_CONTROL')
  bodies.append(body)
 for a,b in [(bodies[0],bodies[1]),(bodies[2],bodies[3])]:
  def project(body):
   x=copy.deepcopy(body)
   for key in ['policy','source_sha256']:x.pop(key)
   for row in x['rows']:
    row.pop('display_exact',None);row.pop('original_leak',None)
   return x
  need(project(a)==project(b),'SAME_ENGINE_BEHAVIOR')
 return {'status':'PASS_BOUNDED_DISPLAY_POLICY','cohorts':4,'insert_update_rows':56,'inline_literal_negative_retained':True,'same_engine_native_effects_equal':True,'diagnostic_counts':[len(b['diagnostics']) for b in bodies],'application_acceptance':False,'universal_privacy':False,'installed':False}
if __name__=='__main__':print(json.dumps(validate(json.loads(Path(sys.argv[1]).read_text())),indent=2))
