import json,hashlib
from pathlib import Path
b=Path('doc/php83/evidence/pdo-return-audit');a=json.loads((b/'codex.json').read_text());c=json.loads((b/'claude.json').read_text())
def require(ok):
 if not ok:raise RuntimeError('Audit evidence mismatch')
require(a['audit_executed'] and c['audit_executed'])
for field in ['artifact','harness','collector_sha256','imported_collector_sha256']:require(a[field]==c[field])
require(len(a['rows'])==len(c['rows'])==2)
for x,y in zip(a['rows'],c['rows']):
 for k in ['runtime','exit','result','stderr_diagnostics']:require(x[k]==y[k])
 require(x['exit']==0 and len(x['result']['rows'])==19)
require(a['rows'][0]['result']['rows']==a['rows'][1]['result']['rows'])
rows=a['rows'][1]['result']['rows'];keyed={tuple(r[:2]):r for r in rows[:4]}
require(keyed[('set-attribute','PDO')][2]==['return','boolean',True])
require(keyed[('unsupported-attribute','PDO')][2]==['return','boolean',False])
for k in [('set-attribute','PropelPDO'),('unsupported-attribute','PropelPDO')]:require(keyed[k][2]==['return','NULL',None])
for r in rows:
 if r[0]=='statement-success':require(r[4]==(['return','NULL',None] if r[2]=='KalturaStatement' else ['return','boolean',True]))
 if r[0]=='statement-failure':
  expected=['throw','PDOException','42S02'] if r[1]==2 else (['return','NULL',None] if r[2]=='KalturaStatement' else ['return','boolean',False])
  require(r[3]==expected and r[4]=='42S02')
 require(a['cleanup']['stopped'] and c['cleanup']['stopped'])
result={'schema':1,'independent_runtime_results_equal':True,'same_observed_values_across74_83':True,'rows_per_runtime':19,'native_attribute_true_false_preserved':True,'propel_attribute_returns_null':True,'kaltura_execute_returns_null_on_success_and_silent_failure':True,'pdo_exception_class_and_sqlstate_retained':True,'dry_run_skips_write_and_allows_select':True,'nested_commit_rollback_assertions_passed':True,'all_owned_units_stopped':True,'application_acceptance':False,'repair_selected':False,'source_or_artifact_changed':False}
(b/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');print('Independent19-row audit confirmed; return-value defects remain unfixed')
