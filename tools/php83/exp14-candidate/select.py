#!/usr/bin/env python3
"""Named coordinator-authorized experiment selection; never application approval."""
import argparse,copy,json,subprocess
from pathlib import Path
import prepare as p
PROPOSAL=p.ROOT/'doc/php83/evidence/exp14-candidate/proposed-r1/manifest.json'
PIN='097e0441420b179962feaabb2c1518ac9aa53f93eebb6758468e1680cc1ede9b'
def selected(raw):
 p.need(p.sha(raw)==PIN,'Frozen proposal drift');m=json.loads(raw)
 p.need(m['status']=='PROPOSED_ONLY_NOT_SELECTED' and m['selection_approved'] is False and len(m['patches'])==76,'Wrong phase')
 p.inputs();proof=p.native_proof()
 p.need(p.sha(subprocess.check_output(['git','show','324d14db:doc/php83/evidence/exp14-candidate/proposed-r1/manifest.json'],cwd=p.ROOT))==PIN,'Proposal commit identity')
 for path,digest in proof.items():p.need(p.sha(subprocess.check_output(['git','show','0aed2a32:'+path],cwd=p.ROOT))==digest,'Rank proof commit identity')
 s=copy.deepcopy(m);s['status']='EXPERIMENTAL_SELECTED_LAB_ONLY_NOT_FOR_PRODUCTION';s['selection_approved']=True
 s['selection_authorization']={'decision':'Coordinator explicitly authorized separate exp14 experimental selection and two builds after rank signature primary/actual Claude repeat','proposal_commit':'324d14db','proposal_sha256':PIN,'rank_commit':'0aed2a32','rank_evidence':proof,'build_approved':True,'production_approved':False,'package_ci_approved':False,'release_approved':False,'artifact_runtime_acceptance':False,'rank_positive_body_persistence_tested':False,'metadata74_default_delta_intentional':True}
 s['pending']=m['pending'][1:];return s

def stage(output):
 p.need(not output.exists(),'Refuse existing selection');s=selected(PROPOSAL.read_bytes());patches={}
 for row in s['patches']:
  b=(p.ROOT/row['source_patch']).read_bytes();p.need(p.sha(b)==row['sha256'],'Patch identity');patches[row['patch']]=b
 p.need(len(patches)==76,'Leaf collision');output.mkdir(parents=True)
 for name,b in patches.items():(output/name).write_bytes(b)
 (output/'manifest.json').write_text(json.dumps(s,indent=2)+'\n');return s
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);r=a.parse_args();s=stage(r.output);print(json.dumps({'status':s['status'],'targets':len(s['patches']),'zip_built':False}))
