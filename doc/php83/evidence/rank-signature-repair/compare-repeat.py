#!/usr/bin/env python3
"""Read-only reproducible cross-executor comparison, stage command allowance only."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'tools/php83/rank-signature-repair'))
import validate
E=Path(__file__).parent
inputs=[E/'primary-r2.json',E/'claude-repeat.json']
a,b=[json.loads(p.read_text()) for p in inputs]
validate.validate(a);validate.validate(b)
for x,y in zip(a['records'],b['records']):
 for key in ['mode','exit','stdout','stderr','body']:assert validate.exact(x[key],y[key]),key
 assert x['command'].replace(a['stage'],'<owned-stage>')==y['command'].replace(b['stage'],'<owned-stage>')
for key in ['files','checksum_manifest_sha256','collector_sha256','source_before','source_after','runtime_before','runtime_after']:
 assert validate.exact(a[key],b[key]),key
assert validate.exact(a['runtime_before'],a['runtime_after'])
assert validate.exact(b['runtime_before'],b['runtime_after'])
print(json.dumps({'executor':'Codex independent stored-record comparison','status':'BOUNDED_REPEAT_MATCH','inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'processes_per_executor':4,'omissions_per_executor':16,'only_excluded_record_field':'command fresh owned-stage path token, all other command bytes exact','metadata74_delta_preserved':True,'raw_stdout_stderr_exact':True,'source_runtime_cross_executor_exact':True,'application_acceptance':False,'rank_positive_body_tested':False,'artifact_selected':False},indent=2))
