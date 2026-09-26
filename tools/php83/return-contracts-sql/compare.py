#!/usr/bin/env python3
"""Explicit 91-row SQL contract, separate from observation-only collector."""
import argparse,hashlib,json,pathlib
CLASSES=['PDO','PropelPDO','KalturaPDO','DebugPDO']
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def same(a,b):return canonical(a)==canonical(b)
def ret(t,v):return ['return',[t,v]]
YES=ret('boolean',True);ONE=ret('integer',1);ERR=['throw','PDOException',['integer',0]]
def expected_rows():
 rows=[]
 for cls in CLASSES:
  statement={'PDO':'PDOStatement','PropelPDO':'PDOStatement','KalturaPDO':'KalturaStatement','DebugPDO':'DebugPDOStatement'}[cls]
  for mode in [0,2]:
   fail=ret('boolean',False) if mode==0 else ['throw','PDOException',['string','42S02']]
   pairs=[('exec-zero',ret('integer',0)),('exec-one',ONE),('exec-failure',fail),('query-positive',ret('array',[statement,['integer',1]])),('query-failure',fail),('prepare-positive',ret('array',[statement,True,True,['integer',17]])),('prepare-invalid',ret('array',[statement,False]) if mode==0 else fail),('unsupported-attribute',ret('boolean',False))]
   rows.extend([[cls,mode,k,v] for k,v in pairs]);rows.append([cls,mode,'persisted',['array',[1]]])
  trace=[YES,ONE,ERR if cls=='PDO' else YES,['boolean',True],YES,ERR if cls=='PDO' else YES,['boolean',False]]
  rows.append([cls,'nested-commit',trace,['array',[2]]])
  if cls!='PDO':
   rows.append([cls,'nested-rollback',[YES,ONE,YES,YES,['throw','PropelException',['integer',0]],['integer',1],YES,['boolean',False]],['array',[2]]])
   for enabled in [True,False]:rows.append([cls,'cache',enabled,['boolean',True],enabled,['boolean',enabled]])
  rows.append([cls,'no-active',ERR if cls=='PDO' else YES,ERR if cls=='PDO' else YES])
 rows.extend([['KalturaStatement','dry-write','KalturaStatement',YES,['array',[]]],['KalturaStatement','dry-select',YES,['integer',19]]]);return rows

def validate(report,diagnostics):
 authority=pathlib.Path(__file__).resolve().parents[3]/'doc/php83/evidence/return-contracts-sql/preparation-r1/manifest.json'
 raw=authority.read_bytes()
 if hashlib.sha256(raw).hexdigest()!='4fe6843d9a64097b67aa76c9569d682f64001727ed6e381559ffcbaaf918dc07':raise ValueError('Frozen manifest authority drift')
 if report.get('stage_pin')!=hashlib.sha256(raw).hexdigest() or not same(report.get('identities'),json.loads(raw)):raise ValueError('Unapproved report source authority')
 if report.get('status')!='OBSERVED_NOT_ACCEPTED' or report.get('application_acceptance') is not False:raise ValueError('Not complete observation')
 if [r.get('cohort') for r in report['records']]!=['prerequisite','candidate']:raise ValueError('Cohort matrix')
 for key in ['source','runtime']:
  if not report.get(key+'_before') or not same(report[key+'_before'],report.get(key+'_after')):raise ValueError(key+' identity drift')
 for r in report['records']:
  e=r['execution'];b=r['body'];c=r['cleanup'];cohort=r['cohort']
  if type(e['exit']) is not int or e['exit']!=0:raise ValueError('Process failure')
  if c.get('stopped') is not True or type(c.get('stop_exit')) is not int or c.get('stop_exit')!=0 or c.get('state')!='inactive' or type(c.get('state_exit')) is not int or c.get('state_exit') not in (3,4):raise ValueError('Cleanup failure')
  if not same(b['rows'],expected_rows()):raise ValueError('Typed functional oracle mismatch')
  if not same(b['diagnostics'],diagnostics[cohort]):raise ValueError('Diagnostic drift')
  expected_stderr=''.join('Deprecated: '+d[1]+' in '+d[2]+' on line '+str(d[3])+'\n' for d in diagnostics[cohort])
  if e['stderr']!=expected_stderr:raise ValueError('Native stderr differs from explicit diagnostic contract')
  if not same(json.loads(e['stdout']),b):raise ValueError('Retained body/stdout mismatch')
  for name,pin in b['loaded'].items():
   if report['identities']['files'].get(cohort+'/'+name)!=pin:raise ValueError('Loaded source not bound to manifest')
  if set(b['loaded'])!={'vendor/propel/Propel.php','vendor/propel/PropelException.php','vendor/propel/util/PropelConfiguration.php','vendor/propel/util/PropelPDO.php','vendor/propel/util/DebugPDOStatement.php','vendor/propel/util/DebugPDO.php','alpha/apps/kaltura/lib/db/KalturaStatement.php','alpha/apps/kaltura/lib/db/KalturaPDO.php'}:raise ValueError('Loaded class-file inventory drift')
 return True
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('primary',type=pathlib.Path);p.add_argument('repeat',type=pathlib.Path);p.add_argument('--diagnostics',required=True,type=pathlib.Path);a=p.parse_args();x=json.loads(a.primary.read_text());y=json.loads(a.repeat.read_text());d=json.loads(a.diagnostics.read_text());validate(x,d);validate(y,d)
 for left,right in zip(x['records'],y['records']):
  for k in ['body']:assert same(left[k],right[k]),'Independent body mismatch'
  for k in ['exit','stdout','stderr']:assert same(left['execution'][k],right['execution'][k]),'Independent execution mismatch'
 assert same(x['runtime_before'],y['runtime_before']),'Repeat runtime changed'
 assert same(x['identities'],y['identities']),'Repeat stage files changed'
 print(json.dumps({'status':'BOUNDED_SQL_CONTRACT_AND_INDEPENDENT_REPEAT','cases_per_cohort':len(expected_rows()),'cohorts_per_run':2,'native_repeat_records_exact':True,'diagnostics':[len(d[k]) for k in ['prerequisite','candidate']],'application_acceptance':False},indent=2))
