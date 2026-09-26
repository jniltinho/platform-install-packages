#!/usr/bin/env python3
"""Explicit coordinator-authorized exp13 experiment, not application promotion."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[3]
PROPOSAL=ROOT/'doc/php83/evidence/exp13-candidate/proposed-r1'
PIN='b6ec7cc58a1828611d9c4558a8557eaa6fbf57ea72a40ef02e2095d9af177b17'
def sha(b):return hashlib.sha256(b).hexdigest()
def require(ok,msg):
 if not ok:raise ValueError(msg)
def selected(raw):
 require(sha(raw)==PIN,'Frozen proposal mismatch')
 m=json.loads(raw);require(m['selection_approved'] is False and m['status']=='PROPOSED_ONLY_PENDING_SQL_AND_COORDINATOR_SELECTION','Not proposal phase')
 pins=json.loads(Path(__file__).with_name('sql-pins.json').read_bytes())
 for path,pin in pins.items():require(sha((ROOT/path).read_bytes())==pin,'SQL evidence drift: '+path)
 sql=json.loads((ROOT/'doc/php83/evidence/return-contracts-sql/comparison-r2.json').read_bytes())
 require(sql=={'status':'BOUNDED_SQL_CONTRACT_AND_INDEPENDENT_REPEAT','cases_per_cohort':91,'cohorts_per_run':2,'native_repeat_records_exact':True,'diagnostics':[15,4],'application_acceptance':False},'SQL contract not accepted')
 require((ROOT/'doc/php83/evidence/return-contracts-sql/finalreview.exit').read_text().strip()=='0','Final SQL reviewer failure')
 require((ROOT/'doc/php83/evidence/return-contracts-sql/final-r2-tests.exit').read_text().strip()=='0','SQL guard failure')
 # Commit references anchor reviewed phases, not inferred authorization.
 for commit,path,pin in [('fd157eb4','doc/php83/evidence/exp13-candidate/proposed-r1/manifest.json',PIN),('004b75da','doc/php83/evidence/return-contracts-sql/comparison-r2.json',pins['doc/php83/evidence/return-contracts-sql/comparison-r2.json'])]:
  b=subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT);require(sha(b)==pin,'Committed phase mismatch')
 s=copy.deepcopy(m);s.update(status='EXPERIMENTAL_SELECTED_LAB_ONLY_NOT_FOR_PRODUCTION',selection_approved=True)
 s['selection_authorization']={'decision':'Coordinator explicitly authorized exp13 experimental selection and two reproducible builds after SQL primary/Claude repeat and final OpenCode review','proposal_commit':'fd157eb4','proposal_sha256':PIN,'sql_commit':'004b75da','sql_evidence':pins,'build_approved':True,'production_approved':False,'release_approved':False,'package_ci_approved':False,'artifact_runtime_acceptance':False}
 s['pending']=m['pending'][2:]
 s['conditional_families']=[]
 return s

def stage(output):
 require(not output.exists(),'Refuse existing selected phase')
 s=selected((PROPOSAL/'manifest.json').read_bytes())
 patches={}
 for row in s['patches']:
  b=(PROPOSAL/row['patch']).read_bytes();require(sha(b)==row['sha256'],'Proposed patch drift');patches[row['patch']]=b
 require(len(patches)==75,'Patch inventory')
 output.mkdir(parents=True)
 for name,b in patches.items():(output/name).write_bytes(b)
 (output/'manifest.json').write_text(json.dumps(s,indent=2)+'\n')
 return s
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);r=a.parse_args();s=stage(r.output);print(json.dumps({'status':s['status'],'targets':len(s['patches']),'zip_built':False}))
