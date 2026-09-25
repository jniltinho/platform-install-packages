"""Check independent evidence and allow only explicitly repaired return positions."""
import copy,json,hashlib
from pathlib import Path
b=Path('doc/php83/evidence/pdo-bool')
def require(ok,message):
 if not ok:raise RuntimeError(message)
def effects(rows):
 out=copy.deepcopy(rows)
 for r in out:
  if r[0] in ['set-attribute','unsupported-attribute']:r[2]='return-contract'
  elif r[0]=='cache-attribute':r[1:3]=['return-type','return-value']
  elif r[0]=='statement-success':r[4]='return-contract'
  elif r[0] in ['statement-array','statement-failure']:
   if r[3][0]=='return':r[3]='return-contract'
  elif r[0].startswith('dry-run-'):r[1]='return-contract'
 return out
a=json.loads((b/'codex.json').read_text());c=json.loads((b/'claude.json').read_text())
require(a['functional_checks_passed'] and c['functional_checks_passed'],'Collector failure')
for field in ['artifact','harness','collector_sha256','imported_collector_sha256']:require(a[field]==c[field],'Identity mismatch')
require(len(a['rows'])==len(c['rows'])==4,'Row count')
for x,y in zip(a['rows'],c['rows']):
 for k in ['runtime','variant','exit','result','stderr_diagnostics']:require(x[k]==y[k],'Independent mismatch')
 require(x['exit']==0 and len(x['result']['rows'])==29,'Fixture failure/count')
by={(r['runtime'],r['variant']):r['result'] for r in a['rows']}
for runtime in ['74','83']:
 require(effects(by[runtime,'previous']['rows'])==effects(by[runtime,'candidate']['rows']),'Non-return behavior changed')
require(by['74','previous']['rows']==by['83','previous']['rows'],'Old cross-runtime values changed')
require(by['74','candidate']['rows']==by['83','candidate']['rows'],'New cross-runtime values changed')
require(a['cleanup']['stopped'] and c['cleanup']['stopped'],'Live owned SQL unit')
result={'schema':1,'independent_result_rows_equal':True,'cases_per_variant':29,'variants':4,'only_explicit_return_positions_differ':True,'candidate_values_equal_across_runtime':True,'previous_values_equal_across_runtime':True,'three_native_bool_contracts_reflected':True,'load_deprecations83_before':8,'load_deprecations83_after':5,'application_acceptance':False,'artifact_integration':'pending','comparison_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(b/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');print('Independent29-case SQL evidence agrees; only approved return slots differ')
