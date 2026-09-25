#!/usr/bin/env python3
"""Produce held strict patches from an audited PHPCBF/token-proof report."""
import argparse,base64,hashlib,importlib.util,json,subprocess,tempfile
from pathlib import Path
spec=importlib.util.spec_from_file_location('verify_bytes',Path(__file__).with_name('verify-bytes.py'))
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
sha=lambda data:hashlib.sha256(data).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);p.add_argument('--candidate-output',type=Path,required=True);p.add_argument('--patch-dir',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
repo=Path(__file__).resolve().parents[3];j=json.loads(a.report.read_text());cohort=json.loads((repo/'doc/php83/evidence/compiler-triage/primary-r2.json').read_text())
expected={r['path']:r['source_sha256'] for r in cohort['rows'] if r['category']=='removed_curly_brace_offset'}
rows={r['path']:r for r in j['rows']}
if len(rows)!=len(j['rows']) or set(rows)!=set(expected) or len(rows)!=43:raise ValueError('Not exact43 cohort')
v.validate_report(j)
if a.candidate_output.exists() or any(a.patch_dir.iterdir()):raise ValueError('Refusing existing candidate/patch content')
a.candidate_output.mkdir(parents=True);manifest=[]
with tempfile.TemporaryDirectory(prefix='php83-curly-patch-audit-') as temporary:
 audit=Path(temporary)
 for index,(path,row) in enumerate(sorted(rows.items()),1):
  before=(a.source_root/path).read_bytes();after=base64.b64decode(row['candidate_base64'],validate=True)
  if sha(before)!=expected[path]:raise ValueError('Original cohort drift')
  if type(row['original_compile']['exit']) is not int or row['original_compile']['exit']!=255 or type(row['candidate_compile']['exit']) is not int or row['candidate_compile']['exit']!=0:raise ValueError('Invalid compile control')
  changes=v.verify(before,after,row['proof'])
  candidate=a.candidate_output/path;candidate.parent.mkdir(parents=True,exist_ok=True);candidate.write_bytes(after)
  source=audit/path;source.parent.mkdir(parents=True,exist_ok=True);source.write_bytes(before)
  diff=subprocess.run(['diff','-u','--label','a/'+path,'--label','b/'+path,str(a.source_root/path),str(candidate)],capture_output=True)
  if diff.returncode!=1:raise ValueError('Expected exact source delta')
  leaf=f'{index:04d}-{Path(path).name}.patch';patch=a.patch_dir/leaf;patch.write_bytes(diff.stdout)
  apply=subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(patch.resolve())],cwd=audit,capture_output=True,text=True)
  if apply.returncode or any(term in (apply.stdout+apply.stderr).lower() for term in ['offset','fuzz','reversed','failed']) or source.read_bytes()!=after:raise ValueError('Strict patch application mismatch')
  manifest.append({'path':path,'before_sha256':sha(before),'after_sha256':sha(after),'patch':str(patch.resolve().relative_to(repo)) if patch.resolve().is_relative_to(repo) else str(patch.resolve()),'patch_sha256':sha(diff.stdout),'offset_pairs':changes//2,'changed_bytes':changes})
result={'status':'HELD experimental curly-offset-only43; no full behavior/application acceptance or exp10 selection','upstream_sha256':'58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28','tool':'PHPCompatibility10.0.0-alpha2 / PHPCS4.0.4; targeted RemovedCurlyBraceArrayAccess sniff','source_evidence_sha256':sha(a.report.read_bytes()),'files':manifest,'known_limits':['No runtime caller reachability claim','Candidate74 token/compile and representative behavior independently pending','All non-curly compiler/runtime findings remain open','Held mixed Spyc patch not reused; overlapping futureselection must choose exact compatible transformation']}
(a.patch_dir/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'files':len(manifest),'offset_pairs':sum(r['offset_pairs'] for r in manifest),'changed_bytes':sum(r['changed_bytes'] for r in manifest),'strict_apply':True}))
