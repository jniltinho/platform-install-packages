"""Independent cohort equality and bounded classification, never acceptance."""
import hashlib,json
from pathlib import Path
base=Path(__file__).resolve().parent
repo=base.parents[3]
def require(ok,message):
    if not ok:raise RuntimeError(message)
load=lambda n:json.loads((base/n).read_text())
names=('primary-r2.json','primary-r2-repeat.json','claude-r2.json')
raw=[(base/n).read_bytes() for n in names]
require(raw[0]==raw[1]==raw[2],'Independent bytes differ')
j=json.loads(raw[0]);old=load('primary.json')
for field in old:
    if field!='builder_sha256':require(j[field]==old[field],'Unexpected phase change: '+field)
require(j['builder_sha256']==hashlib.sha256((repo/'tools/php83/compiler-triage/build.py').read_bytes()).hexdigest(),'Builder drift')
for name,digest in j['inputs'].items():require(hashlib.sha256((repo/name).read_bytes()).hexdigest()==digest,'Input drift: '+name)
require(len(j['rows'])==54,'Cohort denominator drift')
for row in j['rows']:
    h=row['historical_baseline']
    require(type(row['compiler_exit']) is int and row['compiler_exit']==255,'Not compiler rejection')
    require(type(h['php74_exit']) is int and h['php74_exit'] in (0,255),'Invalid baseline status')
    require(type(h['historical_php83_exit']) is int and h['historical_php83_exit']==255,'Invalid historical compiler status')
    require(h['historical_sha256']==row['source_sha256'] and h['status']=='exact_source_identity_match','Unverified baseline identity')
require(sum(r['historical_baseline']['php74_exit']==0 for r in j['rows'])==47,'New failure count')
require(sum(r['historical_baseline']['php74_exit']==255 for r in j['rows'])==7,'Retained failure count')
templates=[r['path'] for r in j['rows'] if r['category']=='unexpanded_generator_skeleton_placeholder']
require(len(templates)==6,'Template denominator')
result={'independent_reports':names,'all_bytes_identical':True,'sha256':hashlib.sha256(raw[0]).hexdigest(),
        'cohort_rows_unchanged_by_status_hardening':True,'rejected_rows':54,'new_php83_rejections':47,
        'retained_baseline_rejections':7,'template_paths':templates,'classification_not_runtime_reachability':True,
        'template_consumer_report_sha256':hashlib.sha256((base/'template-consumers.json').read_bytes()).hexdigest(),
        'template_generation_executed':False,'removed_or_waived':0,'application_acceptance':False,
        'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(base/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print('54 rows independently verified;47new/7baseline,zero waivers')
