#!/usr/bin/env python3
"""Exact authorized lab-only metadata transition and fresh staging, not publication."""
import argparse,copy,json
from pathlib import Path
import prepare as p
DRAFT=p.ROOT/'doc/php83/evidence/exp12-candidate/draft-manifest-r3.json'
SELECTED=DRAFT.with_name('selected-manifest.json')
DRAFT_PIN='dfe44db55a34c7ed439d95d82c7565020496f9a32df64f52bbc70e392eaa19a6'

def make_selected(raw):
 p.require(p.sha(raw)==DRAFT_PIN,'Reviewed draft drift');d=json.loads(raw);s=copy.deepcopy(d)
 s['status']='EXPERIMENTAL_SELECTED_LAB_ONLY_NOT_FOR_PRODUCTION';s['selection_approved']=True
 s['selection_authorization']={'decision':'Coordinator explicitly approved reviewed65-target exp12 lab-only source artifact after independent DEBUG72+4 and Criteria4-process composition evidence','reviewed_draft_sha256':DRAFT_PIN,'criteria_composition_commit':'c7cf5fb4c4ea0519de3d279528c0eea8745f84e0','lab_build_approved':True,'production_approved':False,'release_publication_approved':False,'package_ci_integration_approved':False,'artifact_runtime_acceptance':False,'criteria_hierarchy_exemption':'AllowDynamicProperties is deliberate hierarchy-wide compatibility, not marker-only','strict_cross_engine_cache_layout':'FAIL retained; not waived'}
 s['pending']=['Artifact based syntax/API/CLI/additions regressions','All remaining aggregate acceptance gates'];return s

def validate(raw):
 want=make_selected(DRAFT.read_bytes());actual=json.loads(raw);p.require(actual==want,'Unauthorized selected metadata/patch drift');return actual

def stage(original,output):
 p.require(not output.exists(),'Refuse existing stage');draft,proof=p.prepare(original);p.require(draft==json.loads(DRAFT.read_bytes()),'Draft reconstruction drift')
 raw=SELECTED.read_bytes();s=validate(raw);output.mkdir(parents=True,exist_ok=False);(output/'manifest.json').write_bytes(raw)
 for row in s['patches']:
  b=p.prior.repo_bytes(row['source_patch']);p.require(p.sha(b)==row['sha256'],'Stage patch drift');(output/row['patch']).write_bytes(b)
 return {'status':s['status'],'targets':65,'selected_manifest_sha256':p.sha(raw),'strict_replays':len(proof['strict_replays']),'zip_built':False,'runtime_acceptance':False}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--original',type=Path,required=True);a.add_argument('--output',type=Path,required=True);r=a.parse_args();print(json.dumps(stage(r.original,r.output)))
